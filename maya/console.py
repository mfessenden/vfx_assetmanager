# console.py by Michael Fessenden (c) 2011
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
#
#
# ----------------------------------------------------------------------------

import maya.cmds as mc
from assetmanager.lib.output import Output

import os, os.path
import posixpath as pp

__version__ = '0.29'
__lastupdate__ = 'Aug 15 2011'
__repr__ = 'browser'
__amlib__ = 'browser'

out = Output('building assetManager maya console tab' )

def buildConsoleTab(parent):
    mc.optionVar(sva=('am2_lib_modules', __name__))
    
    am_consoleTab_outerFrame = mc.frameLayout('am_consoleTab_outerFrame', parent = parent,  borderStyle='etchedIn', labelVisible = False, width=550)
    
    # build the main overview tab form
    am_overForm = mc.formLayout('am_overForm', parent=am_consoleTab_outerFrame)
    
    #am_overPaneLayout = mc.paneLayout('am_overPaneLayout', parent=am_overForm, cn='horizontal2', paneSize=[(1,100,10), (2, 100, 90)])
    am_consoleTabInnerFrame = mc.frameLayout('am_consoleTabInnerFrame', labelVisible = False, parent=am_overForm, borderStyle='in', backgroundColor = [.9,.9,.9])
    am_consoleTabMainFrame = mc.frameLayout('am_consoleTabMainFrame', parent = am_consoleTabInnerFrame, label = 'Console:', labelVisible=True)
    am_consoleTabscrollField = mc.scrollField('am_consoleTabscrollField', height = 700, editable=False, font = 'smallFixedWidthFont', parent=am_consoleTabMainFrame)

    mc.formLayout(am_overForm, edit=True, attachForm=[
                        (am_consoleTabInnerFrame, 'left', 5),
                        (am_consoleTabInnerFrame, 'right', 5),
                        (am_consoleTabInnerFrame, 'bottom', 5),
                        (am_consoleTabInnerFrame, 'top', 5)])
    
    return am_consoleTab_outerFrame

def updateConsoleOutput():
    ''' updates the console tab output area'''
    usr_logs = os.environ['AM2_USER_LOGS']
    usr_output_log = pp.join(usr_logs, 'am_output.txt')
    file = open(usr_output_log , 'r')
    lines = ''.join(file.readlines())
    if mc.scrollField('am_consoleTabscrollField', exists=True):
        mc.scrollField('am_consoleTabscrollField',edit=True, text = lines)
    
    
    
    