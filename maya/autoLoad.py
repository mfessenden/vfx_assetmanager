# autoLoad.py by Michael Fessenden (c) 2011
#
# v0.29
#
# Description :
# -------------
# This is the module that automatically loads the assetManager modules and attempts to build the tabs
#
#
# Version History :
# -----------------
#
# v0.29:
# - development version
#
# TODO List :
# -----------
# 
# ----------------------------------------------------------------------------


import maya.cmds as mc
import os
import os.path
from vfx-assetmanager.am_os import outprint, dprint

__version__ = '0.29'
__lastupdate__ = 'Jul 25 2011'
__amlib__ = 'autoLoad'


def am_loadAssetManagerModules():
    ''' This is a modules that dynamically loads the assetManager modules'''
    moduleDir =  __file__
    moduleDir = os.path.split(moduleDir)[0]
    outprint('module directory: %s ' % moduleDir)
    parentUI = mc.optionVar( q = 'am_ui_mainTabLayout' )
    dprint('tabLayout: %s ' % parentUI)
    files = os.listdir(moduleDir)
    am_modules = []
    for file in files:
            if (file.lower().endswith('py') & (file != '__init__.py') & (file !=  'autoLoad.py')):
                am_modules.append (file)
                
    for module in am_modules:
        modName, ext = module.rsplit('.', 1)
        print '>> found module  \'%s\'' % modName
        #eval('import testMayaUI.modules.%s' % modName)
        mymodule = __import__('testMayaUI.modules.%s' % modName, fromlist=['a'])
        funcName = ('testMayaUI.modules.%s.am_build'+modName.title()+'Tab') % modName
        print 'funcName: %s' % funcName
        myFunc = ('am_build'+modName.title()+'Tab')
        my_module = 'testMayaUI.modules.%s' % modName
        #funcName = funcName+'(\'%s\')' % parentUI
        #getattr(my_module, myFunc)(parentUI)

        eval(funcName + '(%s)' % parentUI)
        #eval(funcName)