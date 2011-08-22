# shots.py by Michael Fessenden (c) 2011
#
# v0.29
#
# Description :
# -------------
# This is the module that creates and manages the System UI
#
#
# Version History :
# -----------------
#
# v0.26:
# - development version
#
# TODO List :
# -----------
# ----------------------------------------------------------------------------


import maya.cmds as mc
from assetmanager.lib.am_os import returnLoadedModules, eprint, sprint, outprint, dprint

__version__ = '0.29'
__lastupdate__ = 'Aug 09 2011'
__repr__ = 'shots'
__amlib__ = 'shots'

sprint('building assetManager maya shots tab')

mc.optionVar(stringValueAppend = ('am_ui_topMenu', 'Shots') )
am_systemMenuItems = ['Project...', 'Config...', 'Admin']

class ShotsTab():
    ''' class that builds the shots tab UI'''
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