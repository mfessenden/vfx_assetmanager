# submitAsset.py by Michael Fessenden (c) 2011
#
# v0.29
#
# Description :
# -------------
# This module creates the Nuke mainUI and builds the necessary UI elements
#
#
# Version History :
# -----------------
# v0.29:
# - development version
#
# TODO List :
# -----------
# 
# ----------------------------------------------------------------------------


__version__ = '0.29'
__lastupdate__ = 'Aug 22 2011'
__amlib__ = 'submitAsset'


# assetManager functions
from assetmanager.lib import shows
from assetmanager.lib import assets
showNames = shows.returnAllShows()

import sys, os.path
import nuke

from PyQt4 import QtCore, QtGui, uic

currentFile = nuke.root()['name'].getValue()
# nuke.root()['name'].setValue('/new/file.nk')

class SubmitAssetWindow(object):
    def __init__(self):
      # Set up the user interface from Designer.
      self.ui = uic.loadUi('C:/Users/michael/workspace/assetmanager/ui/nuke/submitAsset.ui') 
      nuke.addOnCreate(self.onCreateCallback)
      #self.ui.connect(self.ui.showsMenu, QtCore.SIGNAL('activated()'), self.buildAssetsList) # adding QString seems to crash this
      #self.ui.connect(self.ui.updateButton, QtCore.SIGNAL('clicked()'), self.buildAssetsList) 
    
    def showUI(self):
      self.ui.show()
    
    def onCreateCallback(self):
      n = nuke.thisNode()
    

def initSubmitAsset():
  dialog = SubmitAssetWindow()
  dialog.showUI()