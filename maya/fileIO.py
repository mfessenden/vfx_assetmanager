# fileIO.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This is the module that managers file IO functions for Maya
#
#
# Version History :
# -----------------
# v0.34:
# - development version
#
# TODO List :
# -----------
#
#
# ----------------------------------------------------------------------------

import maya.cmds as mc
import posixpath as pp

__version__ = '0.34'
__lastupdate__ = 'Dec 11 2011'
__repr__ = 'fileIO'
__amlib__ = 'fileIO'
__status__ = 'design'


def referenceFile(filepath, namespace, groupname, group=True):
    ''' references the given maya file into your scene'''
    if pp.exists(filepath):
        sprint('referencing file: %s' % filepath)
        mayaFile = mc.file(filepath, reference = True,  options ='v=0',  ignoreVersion=True,  loadReferenceDepth= 'all',  sharedNodes= 'renderLayersById', namespace = namespace,  groupReference=group,  groupName= groupname, prompt=False)
    else:
        eprint('file does not exist: %s' % filepath) 