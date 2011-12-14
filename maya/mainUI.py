# mainUI.py by Michael Fessenden (c) 2011
#
# v0.33
#
# Description :
# -------------
# The Maya UI functions for assetManager
#
# Function Naming:
# ----------------
#    build - builds some UI
#    query - queries some data
#
# Version History :
# -----------------
# v0.33:
# - added menu function to dynamically 
#
# v0.32:
# - changes to the signal/slot pyqt calls
#
# v0.31:
# - added new PyQt interface
# 
# v0.30:
# - Python port of MEL UI 
#
#
# TODO List :
# - read the categories from the studio prefs
# - fix the naming of the AssetManagerUI methods to be consistent...some are based on PyQt actions, others the building of UI elements
# ----------------------------------------------------------------------------

import maya.cmds as mc
from PyQt4 import QtGui, QtCore, uic
import os, sys, sip
import posixpath as pp
import maya.OpenMayaUI as omui

from assetmanager.lib.ui.QColorScheme import QColorScheme

# assetManager functions
from assetmanager.lib import shows
from assetmanager.lib import assets
from assetmanager.lib.users import UserObj
from assetmanager.lib.system import Output, UserPrefs, returnLoadedModules
from assetmanager.lib.shows import ShowObj
from assetmanager.lib.sql import Query

from assetmanager.maya.fileIO import referenceFile

__version__ = '0.33'
__lastupdate__ = 'Dec 11 2011'
__repr__ = 'assetManagerUI'
__status__ = 'production'
__appname__ = 'assetManager'

import __builtin__
__builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ')\n' + __file__ + '\n\n' )


global winTitle
winTitle = (__appname__ + ' v' + __version__ + ' (' + __lastupdate__ + ' - ' + __status__ + ')')

am_loc = os.environ['ASSET_MANAGER_LOC']
uiFile = pp.join(am_loc, 'assetmanager', 'ui', 'common', 'mayaUI.ui')


# TODO: this will eventually be pulled from the studio prefs
categories = ['actor', 'props', 'env', 'assembly']
global currentAssetClasses
showObj = ShowObj()

showNames = showObj.showNames

def getMayaMainWindow():
    """Get the Maya main window as a QmainWindow instance"""
    parentWindow = omui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(parentWindow), QtCore.QObject)

#Load the ui file into the form class
form_class, base_class = uic.loadUiType(uiFile)

class AssetManagerUI(base_class, form_class):
    """
    Class: AssetManagerUI
        
        Builds the Maya main assetmanager UI
            
        USAGE
            
        

    """
    openWin = 0
    
    def __init__(self, parent= getMayaMainWindow()):
        '''A custom window with a demo set of ui widgets'''
        
        AssetManagerUI.openWin += 1
        
        super(base_class, self).__init__(parent)
        #uic adds a function to our class called setupUi, calling this creates all the widgets from the .ui file
        self.setupUi(self)
        #The following is overwriting what's been setup in the .ui file
        self.setObjectName('assetmanager')
        self.setWindowTitle(winTitle)
        self.show()
        self.amLogo.pixmap = pp.join(am_loc, 'assetmanager', 'icons', 'vfx-assetmanager_logo-maya.png')
        #print 'pixmap:', self.amLogo.pixmap
        # populate the UI
        
        # simpler syntax for signal/connect
        self.assetList.clicked.connect(self.selectAssetList)
        self.fileList.clicked.connect(self.buildInfoBrowser)
            
        self.connect(self.showsMenu, QtCore.SIGNAL('currentIndexChanged(int)'), self.buildCategoriesMenu) # adding QString seems to crash this
        self.connect(self.categoriesMenu, QtCore.SIGNAL('currentIndexChanged(int)'), self.buildAssetList)
        
        
        

        global currentAssetClasses
        
        self.updateUI()
        
        
        
    def updateUI(self):
        self.buildShowsMenu()        
        self.updateConsoleOutput()
        self.updateProjectTab()
        self.buildModulesBrowser()
        #self.buildAssetList()
        


        
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
            self.showsMenu.addItem(show[0], show[1]) # add the current showID to the QComboBox userData
            if curShow == str(show[0]):
                curIndex = showNames.index(show)
                
        #self.buildCategoriesMenu()
        self.buildInfoArea('show')
        
    def selectAssetList(self):
        selected = ''
        currentAsset = ''
        selitem = self.assetList.selectedItems()
        if selitem is not None:
            selected = self.assetList.selectedItems()[0]
            currentAsset = str(selected.text())
            
        if currentAsset:
            os.environ['AM_CURRENT_ASSET'] = currentAsset
            self.currentAsset = currentAsset
            self.updateUI()
        
        currentCategory = self.categoriesMenu.currentText()
        os.environ['AM_CURRENT_ASSET_CATEGORY'] = str(currentCategory)
        self.currentCategory = currentCategory
        
        # build the classMenu        
        currentID = self.showsMenu.itemData(self.showsMenu.currentIndex() ) 
        currentID = int(currentID.toPyObject())
        self.currentShowID = str(currentID) # TODO: declare this earlier?
        
        
        # clear the UI
        self.classMenu.clear()
        self.fileList.clear()
        self.assetsInfo.clear()
        self.assets_btn_imp.setEnabled(False)
        self.assets_btn_ref.setEnabled(False)
        
        
        query = 'select class_model, class_material, class_rig, class_fx from shows where showID = %s' % str(currentID)
        dbQuery = Query(query)
        try:
            showClasses = dbQuery.result
            for showClass in showClasses:
                self.classMenu.addItem(showClass)
        except:
            pass
        
        self.buildFileList()

    
    def buildFileList(self):
        """ this builds the file list"""
        self.fileList.clear()
        # get the asset name
        currentAsset = self.currentAsset
        currentCategory = self.currentCategory
        currentShowID = self.currentShowID
        currentClass = self.classMenu.currentText()
        #filename, filepath, fileID, assetID, submitDate, createdBy, file_desc, file_comments
        # TODO: whittle this down, we are going to make another DB call in a moment
        query = ('select filename, fileID from files where asset_base_name = "%s" and showID = %s and asset_category = "%s" and asset_class = "%s"' % (currentAsset, currentShowID, currentCategory, currentClass))
        dbQuery = Query(query)
        
        result = ['(no files found)']
        try:
            if len(dbQuery.result):
                #print dbQuery.result
                result = [dbQuery.result[0]]
                self.currentAssetID = str(dbQuery.result[1]) # assetID is the second item in the tuple
                #print 'assetId: ', self.currentAssetID
                
            self.fileList.addItems(result)
        except:
            pass
        
    
    def buildCategoriesMenu(self):
        # clear the menu before we populate it
        self.categoriesMenu.clear()
        self.fileList.clear()
        currentShowCategories = []
        currentShow = self.showsMenu.currentText()
        currentShowIndex = self.showsMenu.currentIndex()  
        
        # get the show ID
        # query the database

        currentID = self.showsMenu.itemData(self.showsMenu.currentIndex() ) 
        currentID = int(currentID.toPyObject())
        
        os.environ['AM_SHOW_ID'] = str(currentID)
        os.environ['AM_SHOW'] = str(currentShow)
        
        # TODO: use the new Query object to do this
        query = 'select category_actor, category_prop, category_env, category_tex, category_assem, category_extra from shows where showID = %s' % currentID
        sqlQuery = Query(query)
        if sqlQuery.result:
            for result in sqlQuery.result:
                if result:
                    currentShowCategories.append(result)
        
        ####
        
        for cat in currentShowCategories:
            # showID is show[1]
            self.categoriesMenu.addItem(cat) # add the current showID to the QComboBox userData

   
    def buildAssetList(self):
        self.assetList.clear()
        self.fileList.clear()
        currentAssetCategory = self.categoriesMenu.currentText()
        
        # get the current showID
        #currentID = self.showsMenu.itemData(self.showsMenu.currentIndex() ) # TODO: figure out why this stopped working
        currentID = self.showsMenu.itemData(self.showsMenu.currentIndex()).toInt()[0]

        
        # TODO: why is this itemText and not itemData?
        currentCategory = self.categoriesMenu.itemText(0)
        currentClass = self.classMenu.itemText(0)
        
        #self.currentID = int(currentID.toPyObject()) # TODO: see above, why is this working differently?
        self.currentID = currentID
             
        # get the asset information based on the current show and category
        query = ('select assetID, asset_base_name from assets where showID = %s and category = "%s"' % (str(self.currentID), currentAssetCategory))
        sqlObj = Query(query)
        queryResult = sqlObj.result
        assetListTmp = []
        if queryResult:
            for result in queryResult:
                assetListTmp.append(result[1])

        # add it to the assetList        
        qlist = QtCore.QStringList(map(QtCore.QString, assetListTmp))
        
        # need to add the assetID here as well as the name of the asset
        self.assetList.addItems(qlist)
     
     
    def buildModulesBrowser(self):
        """ searches for loaded modules and adds them to the system tab"""
        amLoc = os.environ['ASSET_MANAGER_LOC']
        result = []
        for mod in __builtin__.am_mods:
            mod = mod.replace('\\', '/')
            result.append(mod)
            
        lines = ''.join(result)
        self.moduleList.setPlainText(lines)
           
    def buildInfoBrowser(self):
        self.assetsInfo.clear()
        if self.currentAssetID:
            selected = ''
            currentFile = ''
            
            # get the result of the selected item in the file list
            selitem = self.assetList.selectedItems()
            if selitem is not None:
                selected = self.fileList.selectedItems()[0]
                currentFileName = str(selected.text())
                

            filename = self.currentAsset
            currentAssetName = 'model_' + self.currentAsset 
            query = 'select  filepath, assetID, submitDate, submitfile, createdBy, file_desc, file_comments from files where fileID = %s' % self.currentAssetID
            prefix = ['Filepath\n', 'Asset ID', 'Date Submitted', 'File Submitted\n', 'Owner', 'Asset Description\n', 'Comments\n']
            desc = ['File:' ]
            dbQuery = Query(query)
            info = dict()
            
            # build the filename for the maya file
            try:
                filename = pp.join(dbQuery.result[0], currentFileName)
                
                # activate the buttons: assets_btn_imp, assets_btn_ref
                if pp.exists(filename):
                    self.assets_btn_imp.setEnabled(True)
                    self.assets_btn_ref.setEnabled(True)
                    
                    self.assets_btn_ref.pressed.connect(referenceFile(filename, currentAssetName, currentAssetName))
                
                self.currentFile =  filename
                info['File'] = filename
            except:
                pass
            
            # build strings for the info area of the file
            for res in dbQuery.result[1:]:
                info[prefix[dbQuery.result.index(res)]] = str(res)



                
                #print res, ',', type(res)
        
        browserText = []
        for k, v in info.iteritems():
            browserText.append(str(k+': '+ v))
        
        self.assetsInfo.setPlainText('\n'.join(browserText))
        #cursor.close()
        
    #===========================================================================
    #     PROJECT TAB
    #===========================================================================

    def updateProjectTab(self):
        curShow = ''
        curSeq = ''
        curShot = ''
        
        try:
            curShow = os.environ['SHOW']
            curSeq = os.environ['SEQ']
            curShot = os.environ['SHOT']
        except KeyError:
            pass
        
       
        # query the database
        show = shows.ShowObj(curShow, shot=curShot)

        try:
            if show.showRoot:
                self.showRootText.setText(show.showRoot)
                os.environ['SHOW_ROOT'] = show.showRoot 
            if show.showShotRoot:
                self.showShotRootText.setText(show.showShotRoot)
                os.environ['SHOW_SHOT_ROOT'] = show.showShotRoot

            if show.shotCompRoot:
                self.shotCompRootText.setText(show.shotCompRoot)
                os.environ['SHOT_COMP_ROOT'] = show.shotCompRoot
        except AttributeError:
            #out = Output(('no current shot environment variable set, skipping path resolution for shotCompRoot'), sev='warn')
            self.shotCompRootText.setText('')
            
        try:
            if show.shotRenderRoot:
                self.shotRenderRootText.setText(show.shotRenderRoot)
                os.environ['SHOT_RENDER_ROOT'] = show.shotRenderRoot
        except AttributeError:
            #out = Output('no current shot environment variable set, skipping path resolution for shotRenderRoot', sev='warn')
            self.shotRenderRootText.setText('') 
       
        try:
            if show.trackRoot:
                self.shotTrackRootText.setText(show.trackRoot)
                os.environ['SHOT_TRACK_ROOT'] = show.trackRoot
        except AttributeError:
            #out = Output('no current shot environment variable set, skipping path resolution for shotTrackRoot', sev='warn')
            self.shotTrackRootText.setText('')
               
        user = UserObj().username
        role = UserObj().user_role
        user_os = sys.platform
        home = os.environ['HOME'] 
        usrLog = os.environ['AM_USER_LOGS'] 
        sysLog = os.environ['AM_SYSTEM_LOGS']
        try:
            curAssetName = os.environ['AM_CURRENT_ASSET']
        except:
            curAssetName = 'no asset selected'
        amLoc = os.environ['ASSET_MANAGER_LOC']
        pipelineLib = os.environ['PIPELINE_LIB']
        pipelineNukeLib = os.environ['PIPELINE_NUKE_LIB']
        pipelineMayaLib = os.environ['PIPELINE_MAYA_LIB']
        
        self.curShowText.setText(curShow)
        #self.curAssetText.setText(curSeq)
        self.curUserText.setText(user)  
        self.curRoleText.setText(role)
        self.osText.setText(user_os)
        self.homeText.setText(home) 
        self.usrLogText.setText(usrLog)
        self.sysLogText.setText(sysLog)
        self.curAssetText.setText(curAssetName)
        self.assetManagerLocTextfield.setText(amLoc)
        self.pipelineLibTextfield.setText(pipelineLib)
        self.pipelineNukeLibTextfield.setText(pipelineNukeLib)
        self.pipelineMayaLibTextfield.setText(pipelineMayaLib)
        
    def updateConsoleOutput(self):
        ''' updates the console tab output area - modified from Nuke'''
        usr_logs = os.environ['AM_USER_LOGS']
        usr_output_log = pp.join(usr_logs, 'am_usr_log.txt')
        
        try:
            file = open(usr_output_log , 'r')
            lines = ''.join(file.readlines())
            self.consoleList.setPlainText(lines)
            
        except IOError:
            out = Output(('user output log deleted, please contact the administrator'),  sev='err')
            
    def buildInfoArea(self, type):
        """ builds the info area at the bottom of the UI"""
        if type == 'show':
            pass
            
            

