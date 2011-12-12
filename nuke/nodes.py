# nodes.py by Michael Fessenden (c) 2011
#
# v0.32
#
# Description :
# -------------
# This module creates specialized classes for custom Nuke nodes
#
#
# Version History :
# -----------------
# v0.32:
# - development version
#
# TODO List :
# -----------
# - pull the ReadNode.type from the database
# ----------------------------------------------------------------------------


''' classes for specialized nuke nodes'''


import nuke
import os
from assetmanager.lib.sql import Query

__version__ = '0.32'
__lastupdate__ = 'Dec 10 2011'
__amlib__ = 'nodes'
__status__ = 'production'

import __builtin__
try:
    __builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ') - '+ __lastupdate__ +'\n' + __file__ + '\n\n' )
except:
    pass



def addCustomKnobs():
    ''' adds custom nodes to a Nuke node on create'''
    curNode = nuke.thisNode()
        
    try:
        curShow = os.environ['SHOW']
    except:
        curShow = ''
           
    try:
        curSeq = os.environ['SEQ']
    except:
        curSeq = ''
        
    try:
        curShot = os.environ['SHOT']
    except:
        curShot = ''
    try:
        curVer = os.environ['VER']
    except:
        curVer = ''
    try:
        showID = os.environ['SHOW_ID']
    except:
        showID = ''
        
    try:
        shotID = os.environ['SHOT_ID']
    except:
        shotID = ''   
        
    node = nuke.thisNode()
    
    # define the knobs
    assetsTab = nuke.Tab_Knob('assets', 'Assets')
    showText = nuke.Text_Knob('show', 'Show: ')
    seqText = nuke.Text_Knob('seq', 'Sequence: ')
    shotText = nuke.Text_Knob('shot', 'Shot: ')
    verText = nuke.Text_Knob('ver', 'Version: ')
    typeText = nuke.Text_Knob('type', 'Asset Type: ')
    showIDText = nuke.Text_Knob('showID', 'Show ID: ')
    shotIDText = nuke.Text_Knob('shotID', 'Shot ID: ')
    
    updateBtn = nuke.PyScript_Knob('Update') 
    updateBtn.setCommand("print 'test'")
    
    

    # add the Assets Tab
    node.addKnob(assetsTab)
    
    # add the knobs
    node.addKnob(showIDText)
    node.addKnob(shotIDText)
    
    node.addKnob(showText)
    node.addKnob(seqText)
    node.addKnob(shotText)
    node.addKnob(verText)
    node.addKnob(typeText)
    
    node.addKnob(updateBtn)
    
    if curShow:
        showText.setValue(curShow)
    if curSeq:
        seqText.setValue(curSeq)
    if curShot:
        shotText.setValue(curShot)
    if curVer:
        verText.setValue(curVer)
    if showID:
        showIDText.setValue(showID)
    if shotID:
        shotIDText.setValue(shotID)
    # TODO: pull this value from the DB
    typeText.setValue('element')

# calls a function when a read node is created by the user
nuke.addOnUserCreate( addCustomKnobs, nodeClass='Read' )
    

class NukeRead(object):
    ''' builds a custom nuke read node with the given element data'''
    def __init__(self, filepath='', format = '', start = 0, end = 0):
        print 'building custom read node...'
        self.node = nuke.createNode('Read')
        self.node['file'].setValue(filepath)
               
        self.node['first'].setValue(start)
        self.node['last'].setValue(end)

class NukeWrite(object):
    ''' builds a custom nuke write node with the given element data'''
    def __init__(self, filepath='', format = '', start = 0, end = 0):
        print 'building custom write node...'
        self.node = nuke.createNode('Write')
        #self.node['file'].setValue(filepath)
               
        #self.node['first'].setValue(start)
        #self.node['last'].setValue(end)

        
    

def listAllFileInputs():
    for n in nuke.allNodes():
        if n.Class() == 'Read':
            print n['name'].value() + ' : ' + n['file'].value()