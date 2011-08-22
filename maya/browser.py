# browser.py by Michael Fessenden (c) 2011
#
# v0.28
#
# Description :
# -------------
# This is the module that creates and manages the asset browser UI tab
#
#
# Version History :
# -----------------
#
# v0.28:
# - development version
#
# TODO List :
# - need to change this to use the AssetObj class
# - try and build this one in pyQt, so that Nuke can use it
# - modify this one to use the assetObj from lib
#
# ----------------------------------------------------------------------------

import maya.cmds as mc
from assetmanager.lib.output import Output
from assetmanager.database import queryAsset
import os, os.path

__version__ = '0.29'
__lastupdate__ = 'Aug 15 2011'
__repr__ = 'browser'
__amlib__ = 'browser'

out = Output('building assetManager maya browser tab' )

def buildBrowserTab(parent):
    mc.optionVar(sva=('am2_lib_modules', __name__))
    
    am_overTab_outerFrame = mc.frameLayout('am_overTab_outerFrame', parent = parent,  borderStyle='etchedIn', labelVisible = False, width=550)
    
    # build the main overview tab form
    am_overForm = mc.formLayout('am_overForm', parent=am_overTab_outerFrame)
    
    #am_overPaneLayout = mc.paneLayout('am_overPaneLayout', parent=am_overForm, cn='horizontal2', paneSize=[(1,100,10), (2, 100, 90)])
    am_overTabtextField = mc.textFieldGrp('am_overTabtextField', width = 90, parent=am_overForm, label='Search assets: ', changeCommand = buildSearchFrame)
    am_overTabInnerFrame = mc.frameLayout('am_overTabInnerFrame', labelVisible = False, parent=am_overForm, borderStyle='in', backgroundColor = [.9,.9,.9])
    am_overTabSearchMainFrame = mc.frameLayout('am_overTabSearchMainFrame', parent = am_overTabInnerFrame, label = 'Search results:', labelVisible=False)
    #am_overTabSearchMainCol = mc.columnLayout('am_overTabSearchMainCol', parent = am_overTabSearchMainFrame,  adjustableColumn = True)

    mc.formLayout(am_overForm, edit=True, attachForm=[
                        (am_overTabtextField, 'top', 5),
                        (am_overTabtextField, 'left', 5),
                        (am_overTabtextField, 'right', 5),
                        (am_overTabInnerFrame, 'left', 5),
                        (am_overTabInnerFrame, 'right', 5),
                        (am_overTabInnerFrame, 'bottom', 5)],
                        attachControl=[
                        (am_overTabInnerFrame, 'top', 5, am_overTabtextField)])
    
    return am_overTab_outerFrame


  
def buildSearchFrame(*args):
    ''' builds a dynamic search results frame in the UI'''
    # FIX updating this UI is causing a crash
    if mc.scrollLayout('am_browseTab_scrollLayout', exists=True):
        mc.deleteUI('am_browseTab_scrollLayout')
        
    frameWidth = mc.frameLayout('am_overTabSearchMainFrame', query=True, width=True)    
    am_browseTab_scrollLayout = mc.scrollLayout('am_browseTab_scrollLayout', hst = 16, vst = 16, parent = 'am_overTabSearchMainFrame' )

    # get the search text
    assetName = mc.textFieldGrp('am_overTabtextField', query = True, text = True)
    if not assetName:
        mc.frameLayout('am_overTabSearchMainFrame', edit=True, labelVisible=False)
    else:
        assetName = '"%' + assetName + '%"'
    
    #mc.paneLayout('am_paneLayout', edit=True, paneSize=[(1, 100, 8), (2, 87, 60), (3, 100, 4)])    
    #sfwidth = mc.window('am_mainWin', query=True, width=True)
    
    if assetName:
        assets = queryAsset(assetName)
        columns = []
        for a in assets:
            assetText = []
        
            # 'a' is a dict, so redfine 'a' as a tuple
            # reorder the items
            newList = a.items()
            #myorder=[6, 10, 4,1,11,14,7, 8, 0, 12, 2, 13, 3, 16, 9, 15 ,5]
            myorder=[11, 4, 12, 1, 8, 9, 7, 3, 0, 13, 2, 14, 6, 16, 15, 10, 5]
            newList = [ newList[i] for i in myorder]        
            keyList = []
            valueList = []
            for k, v in newList:
                if v:
                    keyList.append(k)
                    valueList.append(v)
            listSize = len(keyList)
            # build the dynamic UI
            index = assets.index(a)
            rcl = 'rcl_%s' % index
            frl = 'frl_%s' % index
            searchCol = mc.columnLayout(parent =am_browseTab_scrollLayout,  width = frameWidth, adjustableColumn = True)
            mc.frameLayout(frl, cll=True, mw=5, mh=17,parent = searchCol, borderStyle = "in", labelVisible=False)
            mc.rowColumnLayout(rcl, numberOfRows=listSize, columnSpacing = [7,7], parent=frl)
            for key in keyList:
                mc.text(parent = rcl, align='right', font = 'fixedWidthFont', label=(key + ':'))
            for val in valueList:
                mc.text(parent = rcl,align='left', font = 'fixedWidthFont', label=val)
                try:
                    if os.path.exists(val):
                        mc.popupMenu(button=3)
                        mc.menuItem(label='browse...')
                except TypeError:
                        pass
                    
            #mc.separator(parent = 'am_overTabSearchMainCol',  height =20, visible=True )           

      
'''
text -q "am2_ui_curTab_ValTxt"

optionVar -q "am2_ui_curTab"

parent = 'am_overTabSearchMainCol'
children = mc.columnLayout('am_overTabSearchMainCol', query=True, childArray=True)
try:
    if len(children):
        for child in children:
            mc.deleteUI(child)
except TypeError:
    pass


Table Result Order
0 - trackRoot
1 - assetRoot
2 - lightRoot
3 - fxRoot
4 - show
5 - assetID
6 - assetType
7 - plateRoot
8 - mayaRoot
9 - materialLoc
10 - assetName
11 - category_2d
12 - animRoot
13 - layoutRoot
14 - category_3d
15 - rigLoc
16 - modelLoc



10 - assetName
6 - assetType
4 - show
1 - assetRoot
11 - category_2d
14 - category_3d
7 - plateRoot
8 - mayaRoot
0 - trackRoot
12 - animRoot
2 - lightRoot
13 - layoutRoot
3 - fxRoot
16 - modelLoc
9 - materialLoc
15 - rigLoc
5 - assetID


Table Result Order (MySQL)
0 - assetID 
1 - assetName 
2 - assetType 
3 - show_name 
4 - assetRoot 
5 - category3D 
6 - category2D 
7 - modelLoc 
8 - rigLoc 
9 - materialLoc 
10 - plateRoot 
11 - trackRoot 
12 - mayaRoot 
13 - lightRoot 
14 - animRoot 
15 - fxRoot 
16 - layoutRoot

1 - assetName
2 - assetType 
3 - show_name
4 - assetRoot 
5 - category3D 
6 - category2D
10 - plateRoot 
12 - mayaRoot
11 - trackRoot
14 - animRoot 
13 - lightRoot 
16 - layoutRoot
15 - fxRoot 
7 - modelLoc 
8 - rigLoc 
9 - materialLoc
0 - assetID 

11 - assetName
4 - assetType
12 - show_name
1 - assetRoot
8 - category3D
9 - category2D
7 - plateRoot
3 - mayaRoot
0 - trackRoot
13 - animRoot
2 - lightRoot
14 - layoutRoot
6 - fxRoot
16 - modelLoc
15 - rigLoc
10 - materialLoc
5 - assetID





 


'''
