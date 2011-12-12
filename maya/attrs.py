# attrs.py by Michael Fessenden (c) 2011
#
# v0.30
#
# Description :
# -------------
# This is the module that builds the custom attrs UI and adds/sets attributes
#
#
# Version History :
# -----------------
# v0.30:
# - development version
#
# TODO List :
# -----------
# - 
# ----------------------------------------------------------------------------

import maya.cmds as mc
import re

__version__ = '0.30'
__lastupdate__ = 'Aug 22 2011'
__repr__ = 'attributes'
__amlib__ = 'attrs'
__status__ = 'design'

# MODEL ATTRS
am_model_attrs = ('s.am_nodeType', 's.assetName', 's.assetClass', 's.assetCat', 's.show', 's.objName', 's.sg','s.refFile', 's.submitScene', 'l.version', 'l.sgVer', 'l.pcVer', 'b.modelExclude', 'b.cache')
am_model_attrsNN = ('Asset Node Type', 'Asset Name', 'Asset Class', 'Asset Category', 'Show', 'Object Name', 'shadingGroup',  'Model Reference File', 'Model Submit Scene', 'Model Version', 'Material Version', 'Precommit Version', 'Exclude from Model Submit', 'Cache status')

# RIG TRANSFORM ATTRS (rigRoot)
am_rig_attrs = ('s.am_nodeType', 's.assetName',  's.assetCat','s.cacheSet', 's.submitScene', 'l.sgVer', 'l.modelVer', 'l.rigVer')
am_rig_attrsNN = ('Asset Node Type', 'Asset Name', 'Asset Category', 'Cache Set', 'Rig Submit Scene', 'Material Version', 'Model Version', 'Rig Version')

am_sg_attrs = ( 's.am_nodeType', 's.assetName','l.modelVersion', 'l.astVer', 'l.materialVersion')
am_sg_attrsNN = ('Asset Node Type', 'Asset Name', 'Model Version', 'Asset Version', 'Material Version')

# CACHESET ATTRS
am_cacheSet_attrs = ( 's.am_nodeType', 's.assetName','s.show', 's.assetCat', 's.refFile', 's.submitScene', 'l.modelVer' )
am_cacheSet_attrsNN = ('Asset Node Type', 'Asset Name', 'Show', 'Asset Category', 'Model Reference File', 'Model Submit Scene',  'Model Version')

# RIGSET ATTRS (am_rigSet)
am_rigSet_attrs = ( 's.am_nodeType', 's.assetName', 's.show', 's.assetCat', 's.refFile', 's.submitScene', 'l.rigVer')
am_rigSet_attrsNN = ('Asset Node Type', 'Asset Name', 'Show', 'Asset Category', 'Model Reference File', 'Model Submit Scene', 'Rig Version')

# TRANSFORM ATTRS
am_transform_attrs = ('s.am_nodeType', 's.assetName', 's.assetClass', 's.assetCat', 's.show', 's.cacheDir', 'l.version')
am_transform_attrsNN = ('Asset Node Type', 'Asset Name', 'Asset Class', 'Asset Category', 'Show', 'Cache Directory', 'Version')

# ROOTSET ATTRS
am_rootSet_attrs = ( 's.am_nodeType', 's.show')
am_rootSet_attrsNN = ('Asset Node Type', 'Show')

all_am_attrs = am_model_attrs + am_rig_attrs + am_sg_attrs + am_cacheSet_attrs + am_rigSet_attrs + am_transform_attrs + am_rootSet_attrs
all_am_attrsNN = am_model_attrsNN + am_rig_attrsNN + am_sg_attrsNN + am_cacheSet_attrsNN + am_rigSet_attrsNN + am_transform_attrsNN + am_rootSet_attrsNN

#print am_model_attrs
#print [re.sub(r'[a-z]\.', '', i) for i in all_am_attrs]
#print all_am_attrsNN

    

class assetObj(object):
    # 'self' refers to the python object, while 'name' is the maya object
    # TODO: blow this away, it's been replace by the AssetBase class
    def __init__(self, name):
        self.name = name
        am_nt = getObjectType(self.name)
        print 'adding "%s" attributes to node: %s' % (am_nt, self.name)
        addCustomAttrs(self.name)
    
    def getAttrs(self, prt=0):
        for attr in all_am_attrs:
            attrname = re.sub(r'[a-z]\.', '', attr)
            if attributeExists(attrname, self.name):
                attrVal = mc.getAttr((self.name+'.'+attrname))
                if prt:
                    print '"%s.%s" value: %s' % (self.name, attrname, attrVal)


class customAttrsUI:
    ''' builds the UI for the custom attribute checker UI'''
    def __init__(self):
        self.name = 'customAttrsUI'
        self.title = 'Check Custom Attrs'
        
        if (mc.window(self.name, q=1, exists=True)): mc.deleteUI(self.name)
        if (mc.windowPref(self.name, q=True, exists=True)): mc.windowPref(self.name, remove=True)
        self.window = mc.window(self.name, title=self.title, width=430, height=650)
        
        chkAttr_mainFormLayout = mc.formLayout('chkAttr_mainFormLayout', parent = self.window)
        chkAttr_mainTabLayout = mc.tabLayout('chkAttr_mainTabLayout', innerMarginWidth=5, innerMarginHeight=5)
        chkAttr_buttonConsoleRow = mc.rowLayout('chkAttr_buttonConsoleRow', parent = chkAttr_mainFormLayout, numberOfColumns=2)
        chkAttr_refreshButton = mc.button('chkAttr_refreshButton', label = 'Refresh', command = 'checkAttrsRefresh')
        
        mc.formLayout(chkAttr_mainFormLayout, edit = True, attachForm=[
                    (chkAttr_mainTabLayout, 'top', 2),
                    (chkAttr_mainTabLayout, 'left', 2),
                    (chkAttr_mainTabLayout, 'right', 2),
                    (chkAttr_buttonConsoleRow, 'bottom', 2)],
                    attachControl=[
                    (chkAttr_mainTabLayout, 'bottom', 2, chkAttr_buttonConsoleRow )])
        
        # build the check attrs tab
        chkAttr_chkScrollLayout = mc.scrollLayout('chkAttr_chkScrollLayout', parent = chkAttr_mainTabLayout, hst = 0)
        chkAttr_chkColumnLayout = mc.columnLayout('chkAttr_chkColumnLayout', parent = chkAttr_chkScrollLayout)
        
        # build the edit attrs tab
        chkAttr_editScrollLayout = mc.scrollLayout('chkAttr_editScrollLayout', parent = chkAttr_mainTabLayout, hst = 0)
        chkAttr_editColumnLayout = mc.columnLayout('chkAttr_editColumnLayout', parent = chkAttr_chkScrollLayout)
    
        # build the group edit tab
        chkAttr_geditScrollLayout = mc.scrollLayout('chkAttr_geditScrollLayout', parent = chkAttr_mainTabLayout, hst = 0)
        chkAttr_geditColumnLayout = mc.columnLayout('chkAttr_geditColumnLayout', parent = chkAttr_chkScrollLayout)
    
        # edit the tabLayout
        mc.tabLayout(chkAttr_mainTabLayout, edit = True, tabLabel=((chkAttr_chkScrollLayout, 'Check Attrs'), (chkAttr_editScrollLayout, 'Edit Attrs'), (chkAttr_geditScrollLayout, 'Group Edit')))
        
        mc.showWindow(self.window)
        
    def refreshCheckAttrs(self):
        selObj = mc.ls(selected=True, exactType = 'transform', exactType = 'shadingEngine', exactType = 'objectSet')

        
        
    class widget:
        def __init__(self):
            self.name = ''
            self.column = mc.columnLayout(self.name)
    
def getObjectType(obj):
    '''returns a more detailed nodeType for assetManager to use in adding attributes'''
    nt = mc.nodeType(obj)
    am_nodeType = ''
    if nt == 'transform':
        child = mc.listRelatives(obj, children = True, fullPath = True)
        if mc.nodeType(child[0]) == 'mesh':
            am_nodeType = 'am_mesh_transform'
        elif mc.nodeType(child[0]) == 'nurbsSurface':
            am_nodeType = 'am_nurbs_transform'
    
    if nt == 'shadingEngine':
        am_nodeType = 'am_sg'
        
    return am_nodeType
    
    
def addCustomAttrs(obj):
    am_nt = getObjectType(obj)
    customAttrs = ()
    customAttrsNN = ()
    if am_nt == 'am_mesh_transform' or 'am_nurbs_transform':
        customAttrs = am_model_attrs
        customAttrsNN = am_model_attrsNN
    
    for attr in customAttrs:
        attrname = re.sub(r'[a-z]\.', '', attr)
        
        if not attributeExists(attrname, obj):
            # add a string attr if it doesn't exist already
            if 's.' in attr:
                mc.addAttr(obj, longName = attrname, niceName = customAttrsNN[customAttrs.index(attr)], dataType = 'string', hidden = False, storable=True )


def attributeExists(attr,node):
    '''function to mimic what the 'attributeExists' procedure does in mel'''
    if (attr or node):
       if (mc.objExists(attr)): return 0
       attrList = mc.listAttr(node,shortNames=True)
       for i in attrList:
         if( attr == i ):
           return 1
       attrList = mc.listAttr(node)
       for i in attrList:
         if( attr == i ):
           return 1
       return 0

class attrWidget:
    def __init__(self):
        self.name = 'attrWidget'
        self.title = 'MyUI'
        

#===========================================================================
# // old mel version
# if ($type=="objectSet"){
#    if  (`match "am_assetSets" $node`!=""){  // (`attributeExists "am_nodeType" $node` ||
#        $am_nodeType = "am_rootSet";
#    }
#    if (`match "am_cacheSet" $node`!=""){
#            $am_nodeType = "am_cacheSet";
#    }
#    if (`match "am_rig_cacheSet" $node`!=""){
#            $am_nodeType = "am_rigSet";
#    }
#
#===========================================================================

    
    
    
    