# assets.py by Michael Fessenden (c) 2011
#
# v0.28
#
# Description :
# -------------
# This is the module that creates and manages the Asset UI
#
#
# Version History :
# -----------------
# v0.28:
# - development version
# v0.24:
# - reworked the functions to build the category menu, along with the assets TSL
# - retired am_buildAssetsTabControlPanel function, replaced by assetsTabControlPanel class
#
# TODO List :
# -----------
# - find out if it's okay to only open the DB connection at the start (if it's not in a function, it'll only get opened once)
# - we should define the ui element clusters(widgets) (specifically assets control panel) as a class, so that we can edit them easily. Currently we have to edit EACH control individually
# - use one function (or class method) to update the assets tab TSLs
# ----------------------------------------------------------------------------


import MySQLdb as sql
import maya.cmds as mc
from vfx-assetmanager.lib.output import Output
from vfx-assetmanager.maya.fileIO import referenceFile
import os
import posixpath as pp
import re
import vfx-assetmanager.database as db
from functools import partial
from vfx-assetmanager.lib.shows import ShowObj

__version__ = '0.29'
__lastupdate__ = 'Aug 22 2011'
__amlib__ = 'assets'

file = __file__

print '[AM2]: loading assets module...'
mc.optionVar(stringValueAppend = ('am_ui_topMenu', 'Assets') )
am_assetsMenuItems = ['New Asset...', 'New Category...', 'Tag Asset...']

db = sql.connect(host='localhost', user='root', db="assets")


class AssetsTab():
    ''' class that builds the assets tab UI'''
    def __init__(self):
        # this attribute is defined so that we can reference the UI element elsewhere
        
        # query the shows menu to start
        currentShow = str(mc.optionMenu('am_showsMenu', query=True, value = True))
        self.showName = currentShow
        self.Show = ShowObj(currentShow)
        self.categories = self.Show.categories
        self.classes = self.Show.classes
        self.assetRoot = self.Show.showAssetRoot
        
        self.ui = self.create()
        
    
    def updateAll(self):
        '''function to update all contained UI elements'''
        pass
    
    def queryAssetsTabAssetFileTSL(self):
        assetClass = mc.textScrollList( 'am_assetTab_assetClassTSL', query=True, selectItem=True)[0]
        assetName = mc.textScrollList( 'am_assetTab_assetListTSL', query=True, selectItem=True)[0]
        
        #controlPanel.update()
        # update the control panel
    
    def buildAssetsTabAsset_FilesTSL(self):
        print 'Blah!'
        ''' build the assets tab assets file textScrollList'''
        mc.textScrollList('am_assetTab_assetFileTSL',edit=True,removeAll=True)
        show = str(mc.optionMenu('am_showsMenu', query=True, value = True))
        curAssetRoot = mc.optionVar(query = 'am2_curAsset_root')
        
        # get selected item in class list
        category = str(mc.optionMenu('am_assetsTab_categoryMenu', query=True, value = True))
        curAsset = mc.textScrollList( 'am_assetTab_assetListTSL', query=True, selectItem=True)[0]
        assetClass = mc.textScrollList( 'am_assetTab_assetClassTSL', query=True, selectItem=True)[0]
        
        filepath = pp.join(self.assetRoot, category, curAsset, assetClass)
        self.curAsset_classpath = filepath
        
        if not pp.exists(filepath):
            out = Output(('asset filepath not found on disk: %s' % filepath), sev = 'sys')
        
        # query the database
        cursor = db.cursor()
        cursor.execute('select filename, filepath from files where show_name = %s and asset_category = %s and asset_name = %s and asset_class = %s', (self.showName, category, curAsset, assetClass))
        queryResult = cursor.fetchall()
        #print queryResult
        cursor.close()
            
        
        
        if len(queryResult):
            for q in queryResult:
                fileName = q[0]
                filepath = q[1]
                assetFile = filepath + '/' + fileName
                mc.textScrollList('am_assetTab_assetFileTSL',edit=True, append=fileName, annotation = assetFile, selectCommand = self.queryAssetsTabAssetFileTSL)
                mc.popupMenu(button=3)
                mc.menuItem(label='browse...')
        else:
                mc.textScrollList('am_assetTab_assetFileTSL',edit=True, append='(no files found)')
    
            
        # set the Maya optionVars
        mc.optionVar(sv=('am2_curAsset_classRoot', filepath))
        
        
    def buildAssetsTab_AssetClassTSL(self):
        ''' build the assets tab assets class textScrollList'''
        # clear the other two TSLs
        mc.textScrollList('am_assetTab_assetClassTSL',edit=True,removeAll=True)
        mc.textScrollList('am_assetTab_assetFileTSL',edit=True,removeAll=True)
        
        curAssetRoot = mc.optionVar(query = 'am2_curAsset_root') # ??
        
        # get the currently selected asset name
        curAsset = mc.textScrollList( 'am_assetTab_assetListTSL', query=True, selectItem=True)[0]
        print 'selected asset: %s' % curAsset
        mc.optionVar(sv=('am2_curAsset_assetName', curAsset))
        #mc.optionVar(sv=('am2_curAsset_root', (assetCatRoot+'/'+curAsset))) # ??

        myOrder = [1, 3, 0, 2]
        assetClasses = [ self.classes[i] for i in myOrder]
        
        showAssetRoot = self.assetRoot
        showAssetCatRoot = pp.join(showAssetRoot, curAsset)
        print '>> show asset category: %s' % showAssetCatRoot
        
        
        
        for cl in assetClasses:
            mc.textScrollList('am_assetTab_assetClassTSL',edit=True, append=cl, selectCommand = self.buildAssetsTabAsset_FilesTSL)
        
        #path = assetCatRoot+'/'+curAsset
        #assetClassFolders = listFolders(path)
   
    
    def buildAssetsTab_AssetsTSL(self, *args):
        ''' build the assets tab assets assets textScrollList'''
        # pull some values from the UI
        category = str(mc.optionMenu('am_assetsTab_categoryMenu', query=True, value = True))
       
        
        # build the search path
        showAssetRoot = self.assetRoot
        print '>> show asset root: %s' % showAssetRoot
        
        
        # query the database
        cursor = db.cursor()
        cursor.execute('select assetName from assets where show_name = %s and category = %s', (self.showName, category))
        queryResult = cursor.fetchall()
        cursor.close()
        
        assetList = []
        mc.textScrollList('am_assetTab_assetListTSL',edit=True,removeAll=True)
        for asset in queryResult:
           assetList.append(asset[0])
        
        for asset in assetList:
            mc.textScrollList('am_assetTab_assetListTSL',edit=True, append=asset, selectCommand = self.buildAssetsTab_AssetClassTSL)
            
        # set Maya optionVars
        mc.optionVar(sv=('am2_curAsset_catRoot', (showAssetRoot+'/'+category)))  # ??
        mc.optionVar(sv=('am2_curAsset_curCat', category))


    def create(self):
        ''' function to create the assets tab. All UI commands go here'''
        #print '>> building assetManager assets tab...'
        self.am_assetsTab_InnerFrame = mc.frameLayout(parent = 'am_win_mainTabLayout',  borderStyle='etchedIn', labelVisible = False, width=550)
        
        # build the main assets tab form
        am_assetsForm = mc.formLayout('am_assetsForm', parent=self.am_assetsTab_InnerFrame)
        
        am_assetPaneLayout = mc.paneLayout('am_assetPaneLayout', parent=am_assetsForm, cn='top4', paneSize=[(1,33,50), (2, 33, 50), (3, 33, 50), (4,97,50)])
        am_assetsListPane = mc.formLayout('am_assetsListPane', parent=am_assetPaneLayout)
        am_assetsListHeader = mc.text('am_assetTab_assetListHeader', parent = am_assetsListPane, label='Asset Name:', font='boldLabelFont')
        am_assetTab_assetListTSL = mc.textScrollList('am_assetTab_assetListTSL', font = 'fixedWidthFont', parent = am_assetsListPane, allowMultiSelection=False)
        
        mc.formLayout(am_assetsListPane, edit=True, attachForm=[
                            (am_assetsListHeader, 'top', 5),
                            (am_assetTab_assetListTSL, 'left', 5),
                            (am_assetTab_assetListTSL, 'right', 5),
                            (am_assetTab_assetListTSL, 'bottom', 5),
                            (am_assetsListHeader, 'left', 5)],
                            attachControl=[
                            (am_assetTab_assetListTSL, 'top', 5, am_assetsListHeader)])
        
        # build the main asset class tab form
        am_assetClassListPane = mc.formLayout('am_assetClassListPane', parent=am_assetPaneLayout)
        am_assetClassListHeader = mc.text('am_assetClassListHeader', parent = am_assetClassListPane, label='Asset Class:', font='boldLabelFont')
        am_assetTab_assetClassTSL = mc.textScrollList('am_assetTab_assetClassTSL', font = 'fixedWidthFont', parent = am_assetClassListPane, allowMultiSelection=False)
        
        mc.formLayout(am_assetClassListPane, edit=True, attachForm=[
                            (am_assetClassListHeader, 'top', 5),
                            (am_assetTab_assetClassTSL, 'left', 5),
                            (am_assetTab_assetClassTSL, 'right', 5),
                            (am_assetTab_assetClassTSL, 'bottom', 5),
                            (am_assetClassListHeader, 'left', 5)],
                            attachControl=[
                            (am_assetTab_assetClassTSL, 'top', 5, am_assetClassListHeader)])
                            
        # build the main asset class tab form
        am_assetFileListPane = mc.formLayout('am_assetFileListPane', parent=am_assetPaneLayout)
        am_assetFileListHeader = mc.text('am_assetFileListHeader', parent = am_assetFileListPane, label='File:', font='boldLabelFont')
        am_assetTab_assetFileTSL = mc.textScrollList('am_assetTab_assetFileTSL', font = 'fixedWidthFont', parent = am_assetFileListPane, allowMultiSelection=False)
        
        mc.formLayout(am_assetFileListPane, edit=True, attachForm=[
                            (am_assetFileListHeader, 'top', 5),
                            (am_assetTab_assetFileTSL, 'left', 5),
                            (am_assetTab_assetFileTSL, 'right', 5),
                            (am_assetTab_assetFileTSL, 'bottom', 5),
                            (am_assetFileListHeader, 'left', 5)],
                            attachControl=[
                            (am_assetTab_assetFileTSL, 'top', 5, am_assetFileListHeader)])
        
    
        
        #category menu - should be a child of 'am_assetsForm'
        am_assetTabCategoryRow = mc.rowLayout('am_assetTabCategoryRow', nc=2, parent=am_assetsForm)
        am_assetTabCategoryText = mc.text('am_assetTabCategoryText', parent = am_assetTabCategoryRow, font = 'smallBoldLabelFont', label = 'Asset Category:')
        # edit the main form
        mc.formLayout(am_assetsForm, edit=True, attachForm=[
                            (am_assetTabCategoryRow, 'top', 8),
                            (am_assetTabCategoryRow, 'left', 30),
                            (am_assetPaneLayout, 'bottom', 2),
                            (am_assetPaneLayout, 'left', 2),
                            (am_assetPaneLayout, 'right', 2)],
                            attachControl=[
                            (am_assetPaneLayout, 'top', 2, am_assetTabCategoryRow)])             
        
        # we have to build the class UI element last
        categoriesMenu = self.buildCategoriesMenu()
        
        controlPanel = self.buildAssetsTabControlPanel()

        return self.am_assetsTab_InnerFrame

 
    def buildCategoriesMenu(self):
        ''' builds the assets tab categories menu'''
        
        # query the database
        cursor = db.cursor()

        # delete the children of the optionMenu
        if mc.optionMenu('am_assetsTab_categoryMenu', exists=True):
            mc.optionMenu('am_assetsTab_categoryMenu', edit=True) 
            menus = mc.optionMenu('am_assetsTab_categoryMenu', query=True, ils=True)
            try:
                for menu in menus:
                    mc.deleteUI(menu)
            except TypeError:
                pass
        else:
            #print 'building the assets tab categories menu'
            self.am_assetsTab_categoryMenu = mc.optionMenu('am_assetsTab_categoryMenu', parent='am_assetTabCategoryRow', changeCommand = self.buildAssetsTab_AssetsTSL)
        
        # edit the categories menu
        mc.optionMenu('am_assetsTab_categoryMenu', edit=True)
        myOrder = [2,5,1,3,4,0]
        try:
            catList = [ self.categories[i] for i in myOrder]
        except IndexError:
            catList = self.categories
        
        # validate the categories and add the menuitems        
        for cat in catList:
            cursor.execute('select * from assets where show_name = %s and category = %s', (self.showName, cat))
            queryResult = cursor.fetchall()
            if len(queryResult):           
                mc.menuItem(label = cat, parent=self.am_assetsTab_categoryMenu)
                
        cursor.close()
        return self.am_assetsTab_categoryMenu 

    def update(self, *args):
        # edited out *args
        # clear the TSLs 
        mc.textScrollList('am_assetTab_assetClassTSL',edit=True,removeAll=True)
        mc.textScrollList('am_assetTab_assetListTSL',edit=True,removeAll=True)
        mc.textScrollList('am_assetTab_assetFileTSL',edit=True,removeAll=True)
        # query the shows menu
        currentShow = str(mc.optionMenu('am_showsMenu', query=True, value = True))
        #print '>> current show is: %s' % currentShow
        self.showName = currentShow
        self.Show = ShowObj(currentShow)
        self.categories = self.Show.categories
        self.classes = self.Show.classes
        self.assetRoot = self.Show.showAssetRoot
        
        # rebuild the categories menu
        self.buildCategoriesMenu()
        self.buildAssetsTab_AssetsTSL()


    # Control Panel
    def buildAssetsTabControlPanel(self):
        ''' function to build the assets tab preview area'''
        #print '>> building the assets tab control panel...'
        am_assetsTab_cp_buttonFrame = mc.frameLayout('am_assetsTab_cp_buttonFrame', parent = 'am_assetPaneLayout',  borderStyle='out', label= 'Model Options:', mh =3, mw=3, labelVisible = True, width=550)
        am_assetsTab_cp_form = mc.formLayout('am_assetsTab_cp_form', parent=am_assetsTab_cp_buttonFrame)
        am_assetsTab_cp_buttonRow = mc.rowLayout('am_assetsTab_cp_buttonRow', nc=6, co6 = [5,5,5,5,5,5], ct6 = ['left', 'left', 'left', 'left', 'left', 'left'], parent=am_assetsTab_cp_form)
        am_assetsTab_cp_button1 = mc.button('am_assetsTab_cp_button1', parent = am_assetsTab_cp_buttonRow, label = 'Reference Model',enable = True, command = self.referenceAssetFile,  annotation='Reference this model into your scene')   
        am_assetsTab_cp_button2 = mc.button('am_assetsTab_cp_button2', parent = am_assetsTab_cp_buttonRow, label = 'Check Out Model',enable = False,  annotation='Copy the current ref into your work directory to edit')   
        am_assetsTab_cp_button3 = mc.button('am_assetsTab_cp_button3', parent = am_assetsTab_cp_buttonRow, label = 'Rig Model', enable = False, annotation='Reference model and creates your rigging work folder')
        am_assetsTab_cp_button4 = mc.button('am_assetsTab_cp_button4', parent = am_assetsTab_cp_buttonRow, label = 'Reserved1', annotation='', vis=False)
    
        am_assetsTab_cp_checkBox1 = mc.checkBox('am_assetsTab_cp_checkBox1', parent = am_assetsTab_cp_buttonRow, label='include materials')
        am_assetsTab_cp_checkBox2 = mc.checkBox('am_assetsTab_cp_checkBox2', parent = am_assetsTab_cp_buttonRow, label='option1')
        am_assetsTab_cp_notesScrollField = mc.scrollField('am_assetsTab_cp_notesScrollField', parent = am_assetsTab_cp_form, font='smallObliqueLabelFont', ww=1, text='no file selected')
    
        mc.formLayout(am_assetsTab_cp_form, edit=True, attachForm=[
                           (am_assetsTab_cp_buttonRow, 'left', 10),
                           (am_assetsTab_cp_buttonRow, 'right', 10),
                           (am_assetsTab_cp_notesScrollField, 'left', 5),
                           (am_assetsTab_cp_notesScrollField, 'right', 5),
                           (am_assetsTab_cp_notesScrollField, 'bottom', 5)],
                           attachControl=[
                          (am_assetsTab_cp_notesScrollField, 'top', 5, am_assetsTab_cp_buttonRow)])
        return am_assetsTab_cp_buttonFrame
    
    def referenceAssetFile(self, *args):        
        # get the asset class (for the namespace)
        assetClass = mc.textScrollList( 'am_assetTab_assetClassTSL', query=True, selectItem=True)[0]
        assetName = mc.textScrollList( 'am_assetTab_assetListTSL', query=True, selectItem=True)[0]
        namespace = (assetClass + '_' + assetName)
        groupname = namespace + '_GRP'
        # backup: assetFile = mc.textScrollList( 'am_assetTab_assetFileTSL', query=True, selectItem=True)[0] 
        filepath = mc.textScrollList( 'am_assetTab_assetFileTSL', query=True, annotation=True)
        referenceFile(filepath, namespace, groupname)
