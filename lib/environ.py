# environ.py by Michael Fessenden (c) 2011
#
# v0.33
#
# Description :
# -------------
# This is the module that manages the assetmanager environment variables
#
#
# Version History :
# -----------------
# v0.33:
# - development version
#
# TODO List :
# -----------
# 
# ----------------------------------------------------------------------------

import os
import maya.cmds as mc

from assetmanager.lib.system import Output

__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__repr__ = 'assetmanager.lib.environ'
__amlib__ = 'environ'
namespace = __name__
__status__ = 'development'


#SHOW, SEQ, SHOT, ASSETNAME, SHOW_ROOT, SHOW_SHOT_ROOT, SHOT_RENDER_ROOT, SHOT_COMP_ROOT, SHOT_TRACK_ROOT, NUKE_LAST_FILE, DEBUG, SHOW_ID, SHOT_ID, SHOW_ROOT, SHOW_SHOT_ROOT, SHOW_COMP_ROOT, SHOW_TRACK_ROOT

# os.environ['PIPELINE_LIB']             : common library location for all apps
# os.environ['PIPELINE_NUKE_LIB']        : common library location for Nuke-specific libraries
# os.environ['PIPELINE_MAYA_LIB']        : common library location for Maya-specific libraries
# os.environ['ASSET_MANAGER_PY_LOC']     : assetmanager application directory


class Environ(object):
    """
    Class: Environ()
    
    DESCRIPTION
        this class maintains, reads and sets environment variables used by the application.
        Allows the user to set & retrieve boolean environment variables
        
    USAGE
        Simply call the class.
    
    """
    def __init__(self):
        print 'loading environment module'
    
    @staticmethod
    def set(**kwargs):
        for arg in kwargs:
            print arg
            
    @staticmethod
    def exists(env):
        try:
            val = os.environ[env]
            return 1
        except:
            return 0
            
    @staticmethod
    def get(env):
        """ just get the environment variable"""
        if env:
            try:
                var = os.environ[env]
                if var == '0':
                    return 0
                if var == '1':
                    return 1
            except:
                var = 0
            return var
        else:
            return 0
            
    
    def _update(self):
        """ updates all of the envVars"""
        print 'updating environment variables'