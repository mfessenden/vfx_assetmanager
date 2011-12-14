# mainUI.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This module creates the Nuke mainUI and builds the necessary UI elements
#
#
# Version History :
# -----------------
# v0.34:
# - development version
#
# v0.31:
# - moved 'returnLoadedModules' to lib/output.py
#
# v0.30:
# - fixed updateElement function to work with the new QtreeWidget
#
# TODO List :
# -----------
# - add proper size hint functionality for the QTreeWidgets...allow the user to set them and persist
# - merge all Nuke functions into a separate module so that this UI can be loaded in Maya
# - get a working compile of OpenEXR Python bindings that will work with Nuke (http://excamera.com/sphinx/articles-openexr.html#openexrpython)
# - get the show currentID in the updateUI method...easier to find this way (on second thought, that might not be possible)
# ----------------------------------------------------------------------------

# assetManager functions
from assetmanager.lib import shows
from assetmanager.lib import assets

# from assetmanager.lib.output import Output, updatePrefsFile, returnLoadedModules
from assetmanager.lib.system import Output, UserPrefs, returnLoadedModules
import MySQLdb as sql
from assetmanager.lib.users import UserObj 
from assetmanager.nuke.nodes import NukeRead, NukeWrite
from assetmanager.lib.sql import Query

import sys, os
import posixpath as pp

import nuke
from PyQt4 import QtCore, QtGui, uic

__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__amlib__ = 'mainUI'
__status__ = 'production'
__appname__ = 'assetManager'

import __builtin__
__builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ') - '+ __lastupdate__ +'\n' + __file__ + '\n\n' )


global winTitle
winTitle = (__appname__ + ' v' + __version__ + ' (' + __lastupdate__ + ' - ' + __status__ + ')')


showNames = shows.returnAllShows()

global seqIndex

seqIndex = 0

userPrefFile = UserPrefs()

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
             
        try:
            am2_loc = os.environ['ASSET_MANAGER_LOC']
        except KeyError:
            out = Output(('"ASSET_MANAGER_LOC" environment variable not set'), sev='err', write=True)
            
        uiFile = pp.join(am2_loc, 'assetmanager', 'ui', 'common', 'nukeUI.ui')
           
        # Set up the user interface from Designer.
        global winTitle
        self.ui = uic.loadUi(uiFile) 
        nuke.addOnCreate(self.onCreateCallback)
        self.ui.setWindowTitle(winTitle)
        
        self.ui.connect(self.ui.showsMenu, QtCore.SIGNAL('currentIndexChanged(int)'), self.buildSeqMenu) # adding QString seems to crash this
        self.ui.connect(self.ui.seqMenu, QtCore.SIGNAL('currentIndexChanged(int)'), self.buildShotsList) # adding QString seems to crash this
        
        self.ui.connect(self.ui.shotsMenu, QtCore.SIGNAL('currentIndexChanged(int)'), self.buildElementsList) 
        self.ui.connect(self.ui.shotsMenu, QtCore.SIGNAL('currentIndexChanged(int)'), self.buildFilesList)
        self.ui.connect(self.ui.elementDetailTree, QtCore.SIGNAL("itemClicked(QTreeWidgetItem*,int)"), self.formatElementInfo)
        self.ui.connect(self.ui.fileDetailTree, QtCore.SIGNAL("itemClicked(QTreeWidgetItem*,int)"), self.formatFileInfo)
        
        
        # TODO: fix this so that self.updateElement can pass an argument
        self.ui.connect(self.ui.updateElementButton, QtCore.SIGNAL('clicked()'), self.updateElement )
        self.ui.connect(self.ui.loadElementButton, QtCore.SIGNAL('clicked()'), self.loadElement )
        self.ui.connect(self.ui.loadFileButton, QtCore.SIGNAL('clicked()'), self.loadFile )
        self.ui.connect(self.ui.importFileButton, QtCore.SIGNAL('clicked()'), self.importFile )
        self.ui.connect(self.ui, QtCore.SIGNAL("lastWindowClosed()"), self.ui, QtCore.SLOT("quit()"))
      
        self.ui.fileMenu = self.ui.menuBar().addMenu('&File')

    
    
    def showUI(self):
        self.ui.show()
        filename = nuke.root().name()
        if filename is not 'Root':
            os.environ['NUKE_LAST_FILE'] = filename
    
    def onCreateCallback(self):
        n = nuke.thisNode()
    
    def buildShowsMenu(self):
        curShow = ''
        curIndex = 0
        try:
          curShow = os.environ['SHOW']
        except KeyError:
          pass        
        
        # build a list from the dict returned from shows library
        for show in showNames:
            # showID is show[1]
            self.ui.showsMenu.addItem(show[0], show[1]) # add the current showID to the QComboBox userData
            if curShow == str(show[0]):
                #print 'setting show index: %s' % curShow
                curIndex = showNames.index(show)
        
            
        self.ui.showsMenu.setCurrentIndex(curIndex)
            

    def buildSeqMenu(self):
        ''' builds the Sequence UI QComboBox'''
        global seqIndex
        item = self.ui.seqMenu
        item.clear()
        
        currentShow = self.ui.showsMenu.currentText()
        currentShowIndex = self.ui.showsMenu.currentIndex()     
    
        curSeq = ''
        curIndex = ''
        
        if currentShow:
            try:
              curSeq = os.environ['SEQ']
            except KeyError:
              pass
             
            
            # get the current showID from the userData
            # TODO: move this to the updateUI method...as is used in the Maya UI
            currentID = self.ui.showsMenu.itemData(self.ui.showsMenu.currentIndex() ) 
            currentID = int(currentID.toPyObject())
            
            os.environ['SHOW_ID'] = str(currentID)
            os.environ['SHOW'] = str(currentShow)
            
            # query the database
            db = sql.connect(host='localhost', user='root', db="assets")
    
            cursor = db.cursor()
            cursor.execute('select show_sequences from shows where showID = %s', currentID)
            queryResult = cursor.fetchall()
            cursor.close()
            
            seqNames = ['(all)']
            
            try:
                queryResult = queryResult[0][0].rsplit(', ')
                for qr in queryResult:
                    seqNames.append( qr.rsplit(':')[0])
                
                # map the list to a QStringList
                qlist = QtCore.QStringList(map(QtCore.QString, seqNames))
                qlistStr = list(qlist)
                
                for seqName in qlistStr:
                    if seqName and seqName != '(all)':
                        seqStr = str(seqName)
                        if seqStr == curSeq:
                            seqIndex = int(qlistStr.index(seqName))
                            #print 'matched sequence index: %d' % seqIndex
                    
                self.ui.seqMenu.addItems(qlist) 
            
            except AttributeError:
                out = Output(('show: "%s" has no sequences' % currentShow), sev = 'sys')
            
            if seqIndex:
                self.ui.seqMenu.setCurrentIndex(seqIndex)
            else:
                self.ui.seqMenu.setCurrentIndex(0)
                
            self.updateProject()
            userPrefFile.updatePrefsFile()
        
    def loadFile(self):
        currentName = self.ui.fileDetailTree.currentItem().text(0)
        currentPath = self.ui.fileDetailTree.currentItem().toolTip(0)
        currentFile = currentPath + '/' + currentName
        out = Output( 'loading file: %s' %   currentFile, sev = 'sys', write=True)
        nuke.scriptOpen(str(currentFile))
        
            
        filename = nuke.root().name()
        os.environ['NUKE_LAST_FILE'] = filename
        userPrefFile.updatePrefsFile()
        
        # update the console tab   
        self.updateConsoleOutput()
        
    def importFile(self):
        currentName = str(self.ui.fileDetailTree.currentItem().text(0))
        currentPath = str(self.ui.fileDetailTree.currentItem().toolTip(0))
        currentFile = currentPath + '/' + currentName
        out = Output( 'importing file: %s' %   currentFile, sev = 'sys', write=True)
        nuke.nodePaste(currentFile)
        
        # update the console tab   
        self.updateConsoleOutput()
        # group the elements
        #nuke.makeGroup()
        
    def loadElement(self, update=False):
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        currentElem = ''
        currentPath = ''
        try:
            currentElem = self.ui.elementDetailTree.currentItem().text(0)
            currentPath = self.ui.elementDetailTree.currentItem().toolTip(0)
        except AttributeError:
            out = Output('nothing is selected', sev = 'warn')
            return
        
        sequence = str(currentPath) + '/' + str(currentElem) #TODO: sanity check this
        out = Output(('loading element: %s' %   sequence), sev = 'sys', write=True)
        
        format = str(self.ui.elementDetailTree.currentItem().toolTip(4))
        range = str(self.ui.elementDetailTree.currentItem().text(5))
        
        range = range.rsplit(' - ')
        
        frame_start = int(range[0])
        frame_end = int(range[1])

        nuke.addFormat(format)
        
        if not update:
            readNode = NukeRead(filepath = sequence, format = format, start = frame_start, end = frame_end)
            #readNode = nuke.nodes.Read(file = sequence, format = format)
            
        else:
            readNode = nuke.selectedNode()
            print 'updating %s...' % readNode
            if not readNode:
                out = Outprint('please select a read node', sev = 'warn')
                return
            
        # update the console tab   
        self.updateConsoleOutput()
        
    def updateElement(self):
        ''' updates a render element in the current script'''
        readNode = nuke.selectedNode()
        print 'updating "%s"...' % readNode.fullName()
        if not readNode:
            out = Output(('please select a read node'), sev='err')
            return
        
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        currentElem = ''
        currentPath = ''
        try:
            currentElem = self.ui.elementDetailTree.currentItem().text(0)
            currentPath = self.ui.elementDetailTree.currentItem().toolTip(0)
        except AttributeError:
            out = Output('nothing is selected', sev = 'warn')
            return
        
        sequence = str(currentPath) + '/' + str(currentElem) #TODO: sanity check this
        out = ('updating element: %s' %   sequence)
        
        db = sql.connect(host='localhost', user='root', db="assets")
        # query the database
        cursor = db.cursor()
        cursor.execute('select frame_start, frame_end from files where show_name = %s and asset_category = "element" and filename = %s', (currentShow,  currentElem))
        framerangeResult = cursor.fetchall()
        cursor.execute('select show_format from shows where show_name = %s', currentShow)
        formatResult = cursor.fetchall()
        cursor.close()
        frame_start = int(framerangeResult[0][0])
        frame_end = int(framerangeResult[0][1])
        format =  formatResult[0][0]
        print format
        nuke.addFormat(format)
        
        readNode['file'].setValue(sequence)
        
        readNode['first'].setValue(frame_start)
        readNode['last'].setValue(frame_end)
        readNode['origfirst'].setValue(frame_start)
        readNode['origlast'].setValue(frame_end)
        readNode['format'].setValue(format)
        
        # update the console tab   
        self.updateConsoleOutput()
        
    def formatDate(self, datetime):
        ''' gives us a more readable date'''
        # date comes from the db in this format: 2011-08-09 11:08:00
        datetime = datetime.rsplit()
        date = datetime[0]
        date = date.rsplit('-')
        month = int(date[1])
        months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month = months[month]
        niceDate = (month + ' ' + date[2] + ', ' + date[0])
        
        time = datetime[1]
        time = time.rsplit(':')
        hour = int(time[0])
        minute = int(time[1])
        minute = '%02d' % minute
        timeSuf = ''
        if hour > 12:
            niceHour = hour - 12
            niceHour = '%02d' % niceHour
            timeSuff = 'PM'
        else:
            niceHour = '%02d' % hour
            niceHour = str(niceHour)
            timeSuff = 'AM'
        
        
        niceTime = (niceHour + ':' +str( minute) + ' ' + timeSuff)
        result = niceDate + ' ' + niceTime
        
        return result
    
    def buildElementsList(self):
        ''' builds the Element List QTreeWidget UI'''
        
        self.ui.elementDetailTree.clear()
        
        # TODO: sizing is kind of a hack, fix this later 
        self.ui.elementDetailTree.setColumnWidth(0, 210)
        self.ui.elementDetailTree.setColumnWidth(1, 50)
        self.ui.elementDetailTree.setColumnWidth(2, 160)
        self.ui.elementDetailTree.setColumnWidth(3, 80)
        self.ui.elementDetailTree.setColumnWidth(4, 90)
        self.ui.elementDetailTree.setColumnWidth(5, 60)
        self.ui.elementDetailTree.setColumnWidth(6, 40)
        
        #print 'building elements list...'
        currentShow = str(self.ui.showsMenu.currentText())
        currentShot = str(self.ui.shotsMenu.currentText())
        
        currentID = self.ui.showsMenu.itemData(self.ui.showsMenu.currentIndex() ) 
        currentID = int(currentID.toPyObject())
        
        currentShotID = self.ui.shotsMenu.itemData(self.ui.shotsMenu.currentIndex() )
        
        try: 
            currentShotID = int(currentShotID.toPyObject())
            os.environ['SHOT_ID'] = str(currentShotID) 
        except TypeError:
            pass        
          
        os.environ['SHOT'] =  str(currentShot)        
        userPrefFile.updatePrefsFile()
        
        # query the database for all elements related to the shot
        db = sql.connect(host='localhost', user='root', db="assets")
        cursor = db.cursor()
        cursor.execute('select fileID, filepath, filename, submitdate, createdBy, frame_start, frame_end, format, version, asset_class, shotID from files where showID = %s and asset_category = "element" and asset_base_name = %s', (currentID, currentShot))
        queryResult = cursor.fetchall()
     
      
        for row in queryResult:
           
            parent = QtGui.QTreeWidgetItem(self.ui.elementDetailTree)
            parent.setSizeHint(0, QtCore.QSize(300, 16)) # works for height, but not width
                      
            date = str(row[3])
            date = self.formatDate(date)
            range = (str(row[5]) + ' - ' + str(row[6]))
            
            # TODO: use studio prefs here
            version = '%03d' % row[8]
            assetclass = str(row[9])
            showID = int(row[10])
            
            # get the sequence 
            # TODO: get this with a join
            cursor.execute('select shot_name, shot_sequence, shot_comp_root, shot_roto_root, shot_plate_root, shot_desc from shots where shotID = %s', showID)
            assetInfo = cursor.fetchall()
                        
            assetName = ''
            assetType = ''
            shot_sequence = ''
            compRoot = ''
            rotoRoot = ''
            plateRoot = ''
            asset_desc = ''
      
            shot_sequence = assetInfo[0][1]
            
            format = row[7]
            format = format.rsplit()
            format = ( format[0] + ' x ' + format[1] )
            
            parent.setText(0, row[2])
            parent.setText(1, version)
            parent.setText(2, date)
            parent.setText(3, row[4])
            parent.setText(4, format)
            parent.setText(5, range)
            parent.setText(6, assetclass)
            try:
                if os.environ['SEQ'] == '(all)':
                    whereStr =  ('category=shot assetName=%s show_name=%s' % (currentShot ,currentShow)).rsplit()
                    query = Query(select = 'shot sequence', table = 'assets', where = whereStr)
                    print query.result
            except KeyError:
                pass
            
            # assign the file path to a tooltip
            parent.setToolTip(0, row[1])
            parent.setToolTip(4, row[7])
            parent.setToolTip(6, shot_sequence) # pass the sequence


        cursor.close()   
        self.updateProject()
       
    def buildShotsList(self):
        ''' builds the shots UI menu'''
        # clear the UI
        self.ui.shotsMenu.clear()
        self.ui.elementDetailTree.clear()
        self.ui.fileDetailTree.clear()
        
        currentShow = self.ui.showsMenu.currentText()
        currentSeq = self.ui.seqMenu.currentText()
        currentSeq = str(currentSeq)
        
        # get the current showID from the userData
        currentID = self.ui.showsMenu.itemData(self.ui.showsMenu.currentIndex() ) 
        currentID = int(currentID.toPyObject())
        
        if currentSeq != '(all)':
            os.environ['SEQ'] = str(currentSeq)
            userPrefFile.updatePrefsFile()
        
        curShot = ''
        
        try:
          curShot = os.environ['SHOT']
        except KeyError:
          pass
        
        # query the database
        db = sql.connect(host='localhost', user='root', db="assets")
        cursor = db.cursor()
        if currentSeq:
            
            # if 'All' is selected in the Sequence menu, return all shots in the show
            if currentSeq == '(all)':
                cursor.execute('select shot_name, shotID from shots where showID = %s', currentID)
                queryResult = cursor.fetchall()
            else:
                #cursor.execute('select asset_base_name from assets where show_name = %s and shot_sequence = %s and category = "shot"', (currentShow, currentSeq))
                cursor.execute('select shot_name, shotID from shots where showID = %s and shot_sequence = %s', (currentID, currentSeq))
                queryResult = cursor.fetchall()
            
            cursor.close()
            shots = []
            shotIDs = []
            if queryResult:
                for row in queryResult:
                    shots.append(row[0])
                    shotIDs.append(row[1])
        
            shotInfo = zip(shots, shotIDs)
            
            
            curIndex = 0
             
            for info in shotInfo:
                # showID is show[1]
                self.ui.shotsMenu.addItem(info[0], info[1]) # add the current showID to the QComboBox userData
                if curShot == str(info[0]):
                    #print 'setting show index: %s' % curShow
                    curIndex = shotInfo.index(info)
                
             
        self.updateProject()
        
    def buildFilesList(self):
        self.ui.fileDetailTree.clear()
        
        # TODO: sizing is kind of a hack, fix this later 
        self.ui.fileDetailTree.setColumnWidth(0, 240)
        self.ui.fileDetailTree.setColumnWidth(1, 55)
        self.ui.fileDetailTree.setColumnWidth(2, 80) # owner
        self.ui.fileDetailTree.setColumnWidth(3, 90) # date
        self.ui.fileDetailTree.setColumnWidth(4, 240)
        
        #print 'building elements list...'
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        os.environ['SHOT'] =  str(currentShot)        
        
        # query the database
        db = sql.connect(host='localhost', user='root', db="assets")
        cursor = db.cursor()
        cursor.execute('select filepath, filename, submitdate, createdBy, frame_start, frame_end, format, version, file_comments from files where show_name = %s and asset_type = "nuke_script" and asset_base_name = %s', (currentShow, currentShot))
        queryResult = cursor.fetchall()
        cursor.close()
        for row in queryResult:
            item = QtGui.QListWidgetItem(row[1])
            
            parent = QtGui.QTreeWidgetItem(self.ui.fileDetailTree)

            parent.setSizeHint(0, QtCore.QSize(300, 16)) # works for height, but not width

            date = str(row[2])
            date = self.formatDate(date)    
            range = (str(row[4]) + ' - ' + str(row[5]))
            
            # TODO: use studio prefs here
            version = '%03d' % row[7]
            owner = str(row[3])
            comments = str(row[8])
            
            parent.setText(0, row[1])
            parent.setText(1, version)
            parent.setText(2, owner)
            parent.setText(3, date)
            parent.setText(4, comments)
            
            # assign the file path to a tooltip
            parent.setToolTip(0, row[0])


            
        self.updateProject()
       

    def updateUI(self):
        self.buildShotsList()
        self.buildElementsList()
        self.buildFilesList()
        self.updateProject()
        self.updateAdminTab()
        self.updateHelpTab()
        self.updateConsoleOutput()
    
    
    def formatElementInfo(self):
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        try:
            currentElement = str(self.ui.elementDetailTree.currentItem().text(0))
            currentVersion = str(self.ui.elementDetailTree.currentItem().text(1))
            currentSequence = str(self.ui.elementDetailTree.currentItem().toolTip(6))
            print 'currentSequence: %s' % currentSequence
            os.environ['SEQ'] = currentSequence
            os.environ['VER'] =  str(int(currentVersion))
            self.ui.elementInfo.clear()
            db = sql.connect(host='localhost', user='root', db="assets")
            # query the database
            cursor = db.cursor()
            cursor.execute('select filepath, filename, createdBy, submitfile, submitdate, frame_start, frame_end, file_desc, file_comments from files where show_name = %s and asset_base_name = %s and filename = %s and asset_category = "element"', (currentShow, currentShot, currentElement))
            queryResult = cursor.fetchall()
            cursor.close()
            data = queryResult[0]
            formattedData = []
            columnNames = ['Path: ', 'Name: ', 'Submitted by: ', 'File submitted: ', 'Date: ', 'Frame start: ', 'Frame end: ', 'Desc: ','Artist Notes: ']
            #formattedData = [((columnNames[data.index(d)] + d)) for d in data]
            for d in data:
                #if columnNames[data.index(d)] is 'Frame range: ':
                formattedData.append(columnNames[data.index(d)] + str(d))
                
            S = '\n'.join(formattedData)
            
            self.ui.elementInfo.setText(S)
        except AttributeError:
            pass
        
        userPrefFile.updatePrefsFile()
        
    def formatFileInfo(self):
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        try:
            currentFile = str(self.ui.fileDetailTree.currentItem().text(0))
            self.ui.fileInfo.clear()
            
            # query the database
            db = sql.connect(host='localhost', user='root', db="assets")
            cursor = db.cursor()
            cursor.execute('select filepath, filename, createdBy, version,  submitdate, frame_start, frame_end, file_desc, file_comments from files where show_name = %s and asset_base_name = %s and filename = %s and asset_category = "comp"', (currentShow, currentShot, currentFile))
            queryResult = cursor.fetchall()
            cursor.close()
            data = queryResult[0]
            formattedData = []
            columnNames = ['Path: ', 'Name: ', 'Submitted by: ', 'Version: ', 'File submitted: ', 'Date: ', 'Frame start: ', 'Frame end: ', 'Desc: ','Artist Notes: ']
            #formattedData = [((columnNames[data.index(d)] + d)) for d in data]
            for d in data:
                #if columnNames[data.index(d)] is 'Frame range: ':
                formattedData.append(columnNames[data.index(d)] + str(d))
                
            S = '\n'.join(formattedData)
            
            self.ui.fileInfo.setText(S)
        except AttributeError:
            pass
            
    def updateAdminTab(self):
        amLoc = os.environ['ASSET_MANAGER_LOC']
        result = []
        for mod in __builtin__.am_mods:
            mod = mod.replace('\\', '/')
            result.append(mod)
            
        lines = ''.join(result)
        self.ui.moduleText.setPlainText(lines)
        
                 
    def updateProject(self):
        """updates the project tab (variables)"""
        curShow = ''
        curSeq = ''
        curShot = ''
        assetManagerLoc = ''
        pipelineLibLoc = ''
        pipelineNukeLibLoc = ''
        pipelineMayaLibLoc = ''
        
        try:
            curShow = os.environ['SHOW']
            curSeq = os.environ['SEQ']
            curShot = os.environ['SHOT']
            assetManagerLoc = os.environ['ASSET_MANAGER_LOC']
            pipelineLibLoc = os.environ['PIPELINE_LIB']
            pipelineNukeLibLoc = os.environ['PIPELINE_NUKE_LIB']
            pipelineMayaLibLoc = os.environ['PIPELINE_MAYA_LIB']
            
        except KeyError:
            pass
        
        db = sql.connect(host='localhost', user='root', db="assets")
        
        # query the database
        show = shows.ShowObj(curShow, shot=curShot)
        
        if show.showRoot:
            self.ui.showRootText.setText(show.showRoot)
            os.environ['SHOW_ROOT'] = show.showRoot 
        if show.showShotRoot:
            self.ui.showShotRootText.setText(show.showShotRoot)
            os.environ['SHOW_SHOT_ROOT'] = show.showShotRoot
        try:
            if show.shotCompRoot:
                self.ui.shotCompRootText.setText(show.shotCompRoot)
                os.environ['SHOT_COMP_ROOT'] = show.shotCompRoot
        except AttributeError:
            #out = Output(('no current shot environment variable set, skipping path resolution for shotCompRoot'), sev='warn')
            self.ui.shotCompRootText.setText('')
            
        try:
            if show.shotRenderRoot:
                self.ui.shotRenderRootText.setText(show.shotRenderRoot)
                os.environ['SHOT_RENDER_ROOT'] = show.shotRenderRoot
        except AttributeError:
            #out = Output('no current shot environment variable set, skipping path resolution for shotRenderRoot', sev='warn')
            self.ui.shotRenderRootText.setText('') 
       
        try:
            if show.trackRoot:
                self.ui.shotTrackRootText.setText(show.trackRoot)
                os.environ['SHOT_TRACK_ROOT'] = show.trackRoot
        except AttributeError:
            #out = Output('no current shot environment variable set, skipping path resolution for shotTrackRoot', sev='warn')
            self.ui.shotTrackRootText.setText('')
               
        user = UserObj().username
        role = UserObj().user_role
        user_os = sys.platform
        home = os.environ['HOME'] 
        usrLog = os.environ['AM_USER_LOGS'] 
        sysLog = os.environ['AM_SYSTEM_LOGS'] 
        
        self.ui.curShowText.setText(curShow)
        if curSeq != '(all)':
            self.ui.curSeqText.setText(curSeq)
        self.ui.curShotText.setText(curShot)
        self.ui.curUserText.setText(user)  
        self.ui.curRoleText.setText(role)
        self.ui.osText.setText(user_os)
        self.ui.homeText.setText(home) 
        self.ui.usrLogText.setText(usrLog)
        self.ui.sysLogText.setText(sysLog)
        self.ui.assetManagerLocTextfield.setText(assetManagerLoc)
        self.ui.pipelineLibTextfield.setText(pipelineLibLoc)
        self.ui.pipelineNukeLibTextfield.setText(pipelineNukeLibLoc)
        self.ui.pipelineMayaLibTextfield.setText(pipelineMayaLibLoc)    
        
        
        self.updateConsoleOutput()
        userPrefFile.updatePrefsFile()
        
    def updateConsoleOutput(self):
        ''' updates the console tab output area'''
        usr_logs = os.environ['AM_USER_LOGS']
        usr_output_log = pp.join(usr_logs, 'am_usr_log.txt')
        
        try:
            file = open(usr_output_log , 'r')
            lines = ''.join(file.readlines())
            self.ui.moduleList.setPlainText(lines)
            
        except IOError:
            out = Output(('user output log deleted, please contact the administrator'),  sev='err')
            
    def updateHelpTab(self):
        helpText = help(__name__)
        self.ui.helpText.setPlainText(helpText)
          
        
def initMain():
  window = MainWindow()
  window.showUI()
  
  # build the initial shows menu
  window.buildShowsMenu()
  window.updateAdminTab()
  #dialog.updateUI()
  window.updateProject()
  window.updateConsoleOutput()
  window.updateHelpTab
  
  
  

if __name__ == "__main__":
    print 'importing __builtin__ module'
    import __builtin__
    __builtin__.am_mods = []
    os.environ['AM_USER_LOGS'] = ''
    # if launched from a command line (outside of nuke or maya)
    app = QtGui.QApplication(sys.argv)
    os.environ['AM_USER_LOGS'] = (os.environ['HOME']+'/'+'.am')
    os.environ['AM_SYSTEM_LOGS'] = 'C:/Users/michael/workspace/assetmanager/logs'
    main_window = MainWindow()
    main_window.showUI()
    # Enter the main loop
    app.exec_()
    
    
    
    
    
# self.centralwidget.setSortingEnabled(__sortingEnabled)
