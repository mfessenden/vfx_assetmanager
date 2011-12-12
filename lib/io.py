# io.py by Michael Fessenden (c) 2011
#
# v0.33
#
# Description :
# -------------
# This is the module that defines classes for parsing directories
#
# Version History :
# -----------------
# v0.33:
# - ** name changed from "browser" to "io"
#
# TODO List :
# -
# ----------------------------------------------------------------------------

__version__ = '0.33'
__lastupdate__ = 'Dec 09 2011'
__amlib__ = 'browser'
__status__ = 'design'

import os, re

import __builtin__
try:
    __builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ')\n' + __file__ + '\n\n' )
except:
    pass



class FileObj(object):
    """
    Class: FileObj()
      
    DESCRIPTION
        File I/O class. Manages system operations independant of OS. Call this instead of posixpath.
        Correctly passes system paths to and from Maya/Nuke/Houdini. It will alert you if a directory
        does not exist and/or permissions are not set
            
    USAGE
        Simply call the class
        

    """
    def __init__(self, path='', extension=''):
        pass
    
    
    
    
def removeJeditFiles(path):
    ''' removes those annoying "~" files that JEdit leaves behind when editing files'''
    results = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = (root+'/'+file)
            filepath = filepath.replace('\\', '/')
            result = re.search(r'\.[a-zA-Z]+~$', filepath)
            try:
                if result.group(0):
                    results.append(filepath)
            except:
                pass
    
    
    for result in results:
        try:
            os.remove(result)
            print 'removing: %s' % result
        except:
            print 'cannot remmove: %s, perhaps the file is open?' % result 
    