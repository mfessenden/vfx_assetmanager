''' classes for specialized nuke nodes'''


import nuke
import os
from assetmanager.lib.db import Query


def addCustomKnobs():
    
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
    
    node = nuke.thisNode()

    assetsTab = nuke.Tab_Knob('assets', 'Assets')
    showText = nuke.Text_Knob('show', 'Show: ')
    seqText = nuke.Text_Knob('seq', 'Sequence: ')
    shotText = nuke.Text_Knob('shot', 'Shot: ')
    verText = nuke.Text_Knob('ver', 'Version: ')
    typeText = nuke.Text_Knob('type', 'Asset Type: ')
    
    updateBtn = nuke.PyScript_Knob('Update') 
    updateBtn.setCommand("print 'test'")
    
    node.addKnob(assetsTab)
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


        
    

def listAllFileInputs():
    for n in nuke.allNodes():
        if n.Class() == 'Read':
            print n['name'].value() + ' : ' + n['file'].value()