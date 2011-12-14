# assetmanager.maya by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This is the loader for the assetmanager Maya utilities
#
#
# Version History :
# -----------------
# v0.34:
# - development version


import posixpath as pp
import os
import maya.cmds as mc
from assetmanager.lib.system import Output

__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__repr__ = 'vfx-assetmanager.maya'
__modulecontents__ = ['assets', 'attrs', '*autoLoad', 'browser', 'optVars', 'system', 'optVars', 'proj', 'system']
namespace = __name__


# this statement will print only on the first load of this module
out = Output('initializing assetManager Maya module...')

am_mainMenuList = ['Assets', 'Scripts', 'Nuke', 'Sequences']

# builds the assetManager main menu
class am_mainMenu(object):
   def __init__(self, name='am_mainMenu', label='assetManager', parent='MayaWindow'):
       self.label = label
       self.name = name
       self.parent = parent

       # Build the UI
       self.__build__()
       
   def __build__(self):
       
       # If the menu already exists, delete it before creating a new one
       if mc.menu(self.name, exists=True): mc.deleteUI(self.name)
       
       # Make the main Maya window editable
       mc.window('MayaWindow', edit=True)
       # Create the window and its contents
       mc.menu(self.name, label=self.label, parent=self.parent)
       


uiObject = am_mainMenu()
 
# add the submenus to the main menu
mc.menu('am_mainMenu', edit=True)
       
for menu in am_mainMenuList:
   mc.menuItem(parent='am_mainMenu', label= menu, sm=True)

    
def assetManagerLoad():
    ''' searches for a config file, reads it and returns a dictionary of absolute show roots & render roots'''
    am_path = os.environ['ASSET_MANAGER_LOC']
    cfg = am_path + '/studio_prefs.ini'
    showsRoot = []
    renderRoot = []
    if pp.exists(cfg):
        mc.optionVar(sv=('am2_sys_config', cfg))
        out = Output(('reading: "%s"' % cfg), sev = 'sys')
        file = open(cfg, 'r')
        data = file.readlines()
        for d in data:
            d = d.strip()
            if not d.startswith('#'):
                if d.startswith('@SHOWSROOT@'):
                    root = d.rsplit('=')[1].strip()
                    if pp.exists(root):
                        out = Output(('found shows root: %s' % root), sev = 'sys')
                        showsRoot.append(root)
                if d.startswith('@RENDERROOT@'):
                    root = d.rsplit('=')[1].strip()
                    if pp.exists(root):
                        out = Output(('found shows render root: %s' % root), sev = 'sys')
                        renderRoot.append(root)
    
    result = dict(zip(('showsRoot', 'rendeRoot'), (showsRoot, renderRoot)))
    return result


def browseShowRoots():
    ''' returns a list of directories in each show root'''
    showsRoots = readConfigFile()
    folders = []
    for root in roots:
        print root
        files = os.listdir(root)
        for file in files:
            if pp.isdir(pp.join(root, file)):
                folders.append(file)
    return folders

assetManagerLoad()