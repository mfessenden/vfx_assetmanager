# mainUI.py by Michael Fessenden (c) 2011
#
# v0.292
#
# Description :
# -------------
# This module creates the Nuke mainUI and builds the necessary UI elements
#
#
# Version History :
# -----------------
# v0.29:
# - development version
#
# TODO List :
# -----------
# - merge all Nuke functions into a separate module so that this UI can be loaded in Maya
# - get a working compile of OpenEXR Python bindings that will work with Nuke (http://excamera.com/sphinx/articles-openexr.html#openexrpython)
# ----------------------------------------------------------------------------

# assetManager functions
from assetmanager.lib import shows
from assetmanager.lib import assets
showNames = shows.returnAllShows()
from assetmanager.lib.am_os import listFolders, listFiles
from assetmanager.lib.output import Output

import MySQLdb as sql
from assetmanager.lib.users import UserObj 
from assetmanager.lib.output import Output 
from assetmanager.nuke.nodes import NukeRead
from assetmanager.lib.db import Query

import sys, os
import posixpath as pp

import nuke
from PyQt4 import QtCore, QtGui, uic

__version__ = '0.292'
__lastupdate__ = 'Aug 22 2011'
__amlib__ = 'mainUI'



class MainWindow(object):
    def __init__(self):
        
      try:
          am2_loc = os.environ['ASSET_MANAGER_PY_LOC']
      except KeyError:
          out = Output(('"ASSET_MANAGER_PY_LOC" environment variable not set'), sev='err')
          
      uiFile = pp.join(am2_loc, 'ui', 'common', 'mainUI.ui')   
      # Set up the user interface from Designer.
      self.ui = uic.loadUi(uiFile) 
      nuke.addOnCreate(self.onCreateCallback)
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
      self.ui.connect(self.ui, QtCore.SIGNAL("lastWindowClosed()"), self.ui, QtCore.SLOT("quit()"))

    def showUI(self):
      self.ui.show()
    
    def onCreateCallback(self):
      n = nuke.thisNode()
    
    def buildShowsMenu(self):
        for show in showNames:
            ind = int(showNames.index(show))         
            self.ui.showsMenu.addItem(show[0], show[1]) # add the current showID to the menu

    def buildSeqMenu(self):

        item = self.ui.seqMenu
        item.clear()
        currentShow = self.ui.showsMenu.currentText()
        
        # get the current showID from the userData
        currentID = self.ui.showsMenu.itemData(self.ui.showsMenu.currentIndex() ) 
        currentID = int(currentID.toPyObject())

        os.environ['SHOW'] = str(currentShow)
        db = sql.connect(host='localhost', user='root', db="assets")

        # query the database
        cursor = db.cursor()
        cursor.execute('select sequences from shows where showID = %s', currentID)
        queryResult = cursor.fetchall()
        cursor.close()
        
        seqNames = ['(all)']
        try:
            queryResult = queryResult[0][0].rsplit(', ')
            for qr in queryResult:
                seqNames.append( qr.rsplit(':')[0])
            
            qlist = QtCore.QStringList(map(QtCore.QString, seqNames))
            self.ui.seqMenu.addItems(qlist) 
        except AttributeError:
            out = Output(('show: "%s" has no sequences' % currentShow), sev = 'sys')
   
        self.updateProject()
        
    def loadFile(self):
        currentName = self.ui.fileDetailTree.currentItem().text(0)
        currentPath = self.ui.fileDetailTree.currentItem().toolTip(0)
        currentFile = currentPath + '/' + currentName
        print 'loading file: %s' %   currentFile
        nuke.scriptOpen(str(currentFile))
    
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
        out = Output(('loading element: %s' %   sequence), sev = 'sys')
        
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
        
    
    def formatDate(self, datetime):
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
        os.environ['SHOT'] =  str(currentShot)   
        currentID = self.ui.showsMenu.itemData(self.ui.showsMenu.currentIndex() ) 
        currentID = int(currentID.toPyObject())     
        
        # query the database
        db = sql.connect(host='localhost', user='root', db="assets")
        cursor = db.cursor()
        cursor.execute('select fileID, filepath, filename, submitdate, createdBy, frame_start, frame_end, format, version, asset_class from files where showID = %s and asset_category = "element" and asset_name = %s', (currentID, currentShot))
        queryResult = cursor.fetchall()
        cursor.close()
        for row in queryResult:
           
            parent = QtGui.QTreeWidgetItem(self.ui.elementDetailTree)
            parent.setSizeHint(0, QtCore.QSize(300, 16)) # works for height, but not width
            
            #firstchild = QtGui.QTreeWidgetItem(parent, 'child1')
            #secondchild = QtGui.QTreeWidgetItem(parent, 'child2')
            #parent.addChild(firstchild)
            #parent.addChild(secondchild)
            
            date = str(row[3])
            date = self.formatDate(date)
            range = (str(row[5]) + ' - ' + str(row[6]))
            
            # TODO: use studio prefs here
            version = '%03d' % row[8]
            assetclass = str(row[9])
            
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
            
            if os.environ['SEQ'] == '(all)':
                whereStr =  ('category=shot assetName=%s show_name=%s' % (currentShot ,currentShow)).rsplit()
                query = Query(select = 'shot sequence', table = 'assets', where = whereStr)
                #print query.result
            
            # assign the file path to a tooltip
            parent.setToolTip(0, row[1])
            parent.setToolTip(4, row[7])
            parent.setToolTip(6, row[1]) # pass the sequence


            
        self.updateProject()
       
    def buildShotsList(self):
        # clear the UI
        self.ui.shotsMenu.clear()
        self.ui.elementDetailTree.clear()
        self.ui.fileDetailTree.clear()
        
        currentShow = self.ui.showsMenu.currentText()
        currentSeq = self.ui.seqMenu.currentText()
        currentSeq = str(currentSeq)
        
        os.environ['SEQ'] = str(currentSeq)
        db = sql.connect(host='localhost', user='root', db="assets")
        # query the database
        cursor = db.cursor()
        if currentSeq:
            if currentSeq == '(all)':
                cursor.execute('select assetName from assets where show_name = %s and category = "shot"', currentShow)
                queryResult = cursor.fetchall()
            else:
                cursor.execute('select assetName from assets where show_name = %s and shot_sequence = %s and category = "shot"', (currentShow, currentSeq))
                queryResult = cursor.fetchall()
            
            cursor.close()
            shots = []
            if queryResult:
                for row in queryResult:
                    shots.append(row[0])
        
                # new code
                item = self.ui.shotsMenu
                qlist = QtCore.QStringList(map(QtCore.QString, shots))
                self.ui.shotsMenu.addItems(qlist)    
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
        cursor.execute('select filepath, filename, submitdate, createdBy, frame_start, frame_end, format, version, file_comments from files where show_name = %s and asset_type = "nuke_script" and asset_name = %s', (currentShow, currentShot))
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
    
    
    def formatElementInfo(self):
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        try:
            currentElement = str(self.ui.elementDetailTree.currentItem().text(0))
            currentVersion = str(self.ui.elementDetailTree.currentItem().text(1))
            os.environ['VER'] =  str(int(currentVersion))
            self.ui.elementInfo.clear()
            db = sql.connect(host='localhost', user='root', db="assets")
            # query the database
            cursor = db.cursor()
            cursor.execute('select filepath, filename, createdBy, submitfile, submitdate, frame_start, frame_end, file_desc, file_comments from files where show_name = %s and asset_name = %s and filename = %s and asset_category = "element"', (currentShow, currentShot, currentElement))
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
        
    def formatFileInfo(self):
        currentShow = self.ui.showsMenu.currentText()
        currentShot = self.ui.shotsMenu.currentText()
        try:
            currentFile = str(self.ui.fileDetailTree.currentItem().text(0))
            self.ui.fileInfo.clear()
            
            # query the database
            db = sql.connect(host='localhost', user='root', db="assets")
            cursor = db.cursor()
            cursor.execute('select filepath, filename, createdBy, version,  submitdate, frame_start, frame_end, file_desc, file_comments from files where show_name = %s and asset_name = %s and filename = %s and asset_category = "comp"', (currentShow, currentShot, currentFile))
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
        
    def returnLoadedModules(self):
        ''' returns a string list of all assetmanager modules currently installed'''
        result = []
        for k, v in sys.modules.items():
            try:
                if (v.__amlib__):
                    v = str(v)
                    if 'asset' in v:
                        val = v.rsplit('\'')
                        ver = ''
                        try:
                            ver = eval(val[1]+'.__version__')
                
                        except (AttributeError, NameError):
                            pass
                        if ver:
                            ver = (' (v'+ver+')')
                        val[3] = val[3].replace('\\', '/')
                        #for e in list((val[1], val[3], ('-'*60))):
                        result.append(''.join(list(((val[1]+ver+'\n'), (val[3]+'\n'), ('-'*61+'\n')))))
                resultStr = ''.join(sorted(result))
                return resultStr
            except AttributeError:
                pass
            
    def updateProject(self):
        curShow = os.environ['SHOW']
        curSeq = os.environ['SEQ']
        curShot = os.environ['SHOT']
        
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
        usrLog = os.environ['AM2_USER_LOGS'] 
        sysLog = os.environ['AM2_SYSTEM_LOGS'] 
        
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
        
        self.updateConsoleOutput()
        
    def updateElement(self):
        readNode = nuke.selectedNode()
        print 'updating "%s"...' % readNode.fullName()
        if not readNode:
            out = Output(('please select a read node'), sev='err')
            return
        
        currentShow = str(self.ui.showsMenu.currentText())
        currentElem = str(self.ui.elementList.currentItem().text())
        currentPath = str(self.ui.elementList.currentItem().toolTip())
        sequence = currentPath + '/' + currentElem
        print 'updating element: %s' %   sequence
        
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
        
    def updateConsoleOutput(self):
        ''' updates the console tab output area'''
        usr_logs = os.environ['AM2_USER_LOGS']
        usr_output_log = pp.join(usr_logs, 'am_output.txt')
        
        try:
            file = open(usr_output_log , 'r')
            lines = ''.join(file.readlines())
            self.ui.moduleList.setPlainText(lines)
            
        except IOError:
            out = Output(('user output log deleted, please contact the adminstrator'),  sev='err')
        


        
def initMain():
  dialog = MainWindow()
  dialog.showUI()
  dialog.buildShowsMenu()
  dialog.updateUI()
  dialog.updateProject()
  
  
  

if __name__ == "__main__":
    # if launched from a command line (outside of nuke or maya)
    app = QtGui.QApplication(sys.argv)
    os.environ['AM2_USER_LOGS'] = (os.environ['HOME']+'/'+'.am')
    os.environ['AM2_SYSTEM_LOGS'] = 'C:/Users/michael/workspace/assetmanager/logs'
    main_window = MainWindow()
    main_window.showUI()
    # Enter the main loop
    app.exec_()
    
    
    
    
    
# self.centralwidget.setSortingEnabled(__sortingEnabled)
