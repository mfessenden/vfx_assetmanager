# mainUI.py by Michael Fessenden (c) 2011
#
# v0.28
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
# v0.29:
# - development version 
#
# v0.16:
# 
#
# TODO List :
# -----------
# -
# ----------------------------------------------------------------------------

import maya.cmds as mc
import sys
from assetmanager.database import returnAllShows, returnAllAssets, queryShow
from assetmanager.lib.shows import ShowObj
from assetmanager.lib.am_os import returnUsername, sprint, sprint, outprint, dprint
from assetmanager.maya.assets import AssetsTab
from assetmanager.maya.system import buildSystemTab
from assetmanager.maya.proj import returnCurrentProject
from assetmanager.maya.browser import buildBrowserTab
from assetmanager.maya.console import buildConsoleTab, updateConsoleOutput

__version__ = '0.29'
__lastupdate__ = 'Aug 09 2011'
__repr__ = 'assetManagerUI'

# remove the system optionVars so that they are regenerated each time
#mc.optionVar(remove=('am2_lib_modules') )
#mc.optionVar(remove=('am2_lib_libraries') )

# declare the variables - eventually to be moved to a different module
shows = returnAllShows()
topMenus = ['File', 'Assets','Model', 'Materials', 'Shots','Camera', 'Admin']
AdminMenu = [('Reset optionVars', 'resetOptVars'),('Display optionVars','optionVarsUI'), ('Toggle debug', 'toggleDebug'), ('Toggle system output', 'toggleSysOut')]

user = returnUsername()
proj = returnCurrentProject()

def am_createHelpLine():
    # call with 'doc = assetManagerUI.__doc__'
    ''' builds the assetManager help line at the bottom of the UI'''
    # help line form
    am_helpForm = mc.formLayout ('am_helpForm',  parent= 'am_paneLayout', numberOfDivisions = 100)
    am_helpLeftFrame = mc.frameLayout( 'am_helpLeftFrame', parent='am_helpForm', height=20,  borderStyle='in', labelVisible=0 )
    am_helpLeftText = mc.text( 'am_helpLeftText', parent='am_helpLeftFrame', font='fixedWidthFont', align='left', label=('Project: '+proj) )
    am_helpRightFrame = mc.frameLayout( 'am_helpRightFrame', parent='am_helpForm',  height=20, borderStyle='in', labelVisible=0 )
    am_helpRightText = mc.text( 'am_helpRightText', parent='am_helpRightFrame', font='fixedWidthFont', align='left', label=('User: ' + user) )
   
    # edit the helpLine formLayout
    mc.formLayout(am_helpForm, edit=True, attachForm=[
                (am_helpLeftFrame, 'left', 2),
                (am_helpLeftFrame, 'bottom', 2),
                (am_helpRightFrame, 'bottom', 2),
                (am_helpRightFrame, 'right', 2),
                (am_helpLeftFrame, 'top', 2),
                (am_helpRightFrame, 'top', 2),
                (am_helpRightFrame, 'right', 2)],
          attachPosition=[
              (am_helpLeftFrame, 'right', 2, 75),
              (am_helpRightFrame, 'left', 2, 76),
              (am_helpRightFrame, 'right', 2, 100)])
    
    return am_helpForm


def assetManagerUI():
    ''' main UI function for assetmanager'''
    func = __repr__
    ver = __version__
    winTitle = func + ' - v' + ver
    
    thisFunc = sys._getframe().f_code.co_name
    ''' builds the assetManager main UI'''
    if mc.window('am_mainWin', exists=True):
        mc.deleteUI('am_mainWin', window=True)
    if mc.windowPref('am_mainWin', exists=True):
        mc.windowPref('am_mainWin', remove=True)
    am_mainWin = mc.window('am_mainWin', title = winTitle, width=550, height=800)
    am_topMenu = am_createTopMenu(am_mainWin)
    
    # dock the UI
    if mc.dockControl('am_mainWinDock', exists=True):
        mc.deleteUI('am_mainWinDock')
    allowedAreas = ['right', 'left']
    am_mainWinDock =mc.dockControl('am_mainWinDock', area='left', floating = True, content=am_mainWin, allowedArea=allowedAreas, label = winTitle )

    #, paneSize=[(1, 100, 20), (2, 100, 60), (3, 100, 20)]
    mc.paneLayout('am_paneLayout',configuration = 'horizontal3', shp=3, paneSize=[(1, 100, 8), (2, 87, 60), (3, 100, 4)],smc=resizeMainPane)
    mc.frameLayout('am_showsMenu_frameLayout',  label='Shows Menu', labelVisible=False, height=60)
    #adding the 'adjustable' attribute to the first column of the rowLayout seemed to activate the alignment
    mc.rowLayout('am_showsMenuRow',nc=3, cw3=[125, 125, 300], cl3=['right', 'left', 'left'], ad3=1)
    mc.text(parent='am_showsMenuRow', label='Shows:', align='right')
   
   # build the shows menu
    am_showsMenu = mc.optionMenu('am_showsMenu', parent='am_showsMenuRow')
    for show in shows:
        mc.menuItem(label=show)
    mc.image(parent='am_showsMenuRow', image='C:/Users/michael/workspace/assetmanager/icons/assetmgr2011.png')
    
    
    am_win_mainTabLayout = mc.tabLayout('am_win_mainTabLayout', parent='am_paneLayout', changeCommand = tabSelect)
    
    # only call the class here because we are referencing the ui method below (which calls 'create')
    assetsMainTab = AssetsTab()
    mc.optionMenu('am_showsMenu', edit = True, changeCommand = assetsMainTab.update)
    assetsMainTab.update()
    
    # build the tabs
    browserTab = buildBrowserTab(am_win_mainTabLayout)
    consoleTab = buildConsoleTab(am_win_mainTabLayout)    
    systemTab = buildSystemTab(am_win_mainTabLayout)
    
    mc.tabLayout('am_win_mainTabLayout', edit=True, tabLabel=( (assetsMainTab.ui, 'Assets'), (browserTab, 'Search'), (systemTab, 'System'), (consoleTab, 'Console')))
    updateConsoleOutput()
    
    am_helpLine = am_createHelpLine()
    
    mc.showWindow()
    mc.dockControl('am_mainWinDock', edit=True, floating=True)
    selTab = ''
    if mc.optionVar(exists='am_ui2_curTab'):
        selTab = mc.optionVar(query = 'am2_ui_curTab')
        mc.tabLayout( 'am_mainTab', edit=True, st = selTab, )
        

def am_createTopMenu(parent):
    if mc.menuBarLayout('am_topMenu', exists=True):
        mc.deleteUI('am_topMenu')
    am_topMenu = mc.menuBarLayout('am_topMenu', parent = parent)\
    
    for topMenu in topMenus:
        menuItems = []
        mc.menu(label = topMenu, parent = am_topMenu)
        if topMenu == 'Admin':
            menuitems = AdminMenu
        
        if menuItems:
            for mi in menuitems:
                mc.menuitem(label = mi[0], command = mi[1])
            
            
    
def resizeMainPane():
    mc.paneLayout('am_paneLayout', edit=True, paneSize=[(1, 100, 8), (2, 87, 60), (3, 100, 4)])
    
def am_createNewAsset():
    pass

# query the show menu and look up the current record
def queryShowsMenu(*args):
    
    # clear the TSLs
    tsls = ['am_assetTab_assetListTSL', 'am_assetTab_assetClassTSL', 'am_assetTab_assetFileTSL']
    
    for tsl in tsls:
        if mc.textScrollList(tsl, exists=True):
            mc.textScrollList(tsl, edit=True,removeAll=True)
    
    '''queries the shows dropdown menu, and builds the rest of the UI'''
    mc.optionVar( remove='am2_curShow_categories' )
    
    curShow = ''
    if mc.optionMenu('am_showsMenu', exists=True):
        #mc.deleteUI('am_showsMenu')
        curShow = str(mc.optionMenu('am_showsMenu', query=True, value = True))        
    
    showObject = ShowObj(curShow)
    mc.optionVar(sv=('am2_ui_curShow', curShow))
    showData = queryShow(curShow)

    
def tabSelect():
    selTab =  mc.tabLayout('am_win_mainTabLayout', query=True, selectTab = True)
    mc.optionVar(sv=('am2_ui_curTab', selTab))