# model.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This is the module that creates and manages Maya objects
#
# Version History :
# -----------------
# v0.34:
# - development version
#
# TODO List :
# - see if the Maya object needs to inherit from any of the Asset classes
# - move the attrs out of this module and into a file (or another module for just attrs)
# - see if we should merge all these classes into a scene class of some sort
# - add attr nice names to the dict
# ----------------------------------------------------------------------------
import re
import maya.cmds as mc
import assetmanager.maya.maya_func as mf
from assetmanager.lib.system import Output, UserPrefs, returnLoadedModules

__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__repr__ = 'model'
__amlib__ = 'model'
__status__ = 'design'



class MayaObject(object):
    """
    Class: MayaObject()
    
        DESCRIPTION
            MayaObject defines any Maya "object" that assetmanager uses. Includes 
            any nodes, meshes or nurbs objects that Maya generates, as well as the
            custom sets and groups.
            
            Sets:
                AM_ROOT_SET:        The root container containing subsets for custom assets
                AM_ROOT_SET:        The root container containing subsets for custom assets
            
        USAGE

    """
    def __init__(self, name = ''):
        
        if name:
            self.__name__ = name
        self.__version__ = __version__
        
        #print 'creating a Maya object'
    

    #selectedMesh = mc.ls(selection=True, dag=True, type='mesh')[0]
    def _cleanDagPath(self, olddag):
        ''' removes namespaces from a given dagpath'''
        newdag = []
        oldList = olddag.split('|')
        for ol in oldList:
            ol = ol.split(':')[-1]
            #newdag.append('|'+ol)
            newdag.append(ol)
        
        newdag = '|'.join(newdag)
        return newdag
    
    def _addAttr(self, obj, attrs, hidden=False):
        """ adds attributes to a transform node. Pass a dictionary
            of attrs where attrs.dict['string'] = string attrs, etc"""
        if mc.objExists(obj):
            for key, val in attrs.iteritems():
                if key == 'string':
                    for v in val:
                        mc.addAttr(obj, longName = v, dataType = 'string', hidden = hidden, storable=True )

                        
                if key == 'int':
                    for v in val:
                        mc.addAttr(obj, longName = v, attributeType = 'long', hidden = hidden, storable=True )    
    
    def _setAttr(self, obj, attr, val):
        """ sets the custom attr"""
        if mf.attributeExists(attr, obj):
            if type(val) is 'str':
                try:
                    mc.setAttr((obj + '.' + attr),  val, type = 'string' )
                except:
                    Output('could not set custom attribute: %s' % (obj + '.' + attr))
        else:
            pass
        
        
    # TODO: at some point we might want to create a dict of objects automatically
    def clean(self):
        """searches the dag for custom AM nodes, and removes the from the scene"""
        all = mc.ls(long=True)
        amObjs = []
        for each in all:
            if mf.attributeExists('am_nodeType', each):
                amObjs.append(each)
                
        try:
            Output('cleaning up assetmanager nodes')
            mc.delete(amObjs)
        except:
            Output('errors deleting AM custom nodes', sev = 'err')  
    
class MayaGeometry(MayaObject):
    """
    Class: MayaGeometry()
    
        DESCRIPTION
            class for dealing with assetmanager Maya geometry
            
        USAGE

    """
    def __init__(self, name=''):
        MayaObject.__init__(self, name)
        
        inputshapes = mf.returnAllGeo()
        inputDagShape = mf.returnAllGeo(long=True)
        
        self.__objects__ = inputshapes
        self.__dagObjects__ = inputDagShape
        
        self.__tempshapes__ = []
        self.__objSets__ = dict()
        
        if name:
            # TODO: should this just be "name"? Are we even talking about assets yet?
            self.__assetName__ = name
            
            sel =  False
            if mc.ls(selection=True):
                sel = True
            
            # get the objects
    
            
            # create the god node for this object
            self.__godNode__ = self.createGodNode()
            
            # create the master set for this object
            self.__objSets__ = MayaSet.createBaseSets()
            
            # get the asset name and show
            
            # get the filepath for the object
            
            # export shaders
            
            # loop through the objects
        
        modelAttrs = dict()    
        modelAttrs['string'] = ['am_nodeType', 'assetName', 'showName', 'assetCategory', 'assetRoot']
        modelAttrs['int'] =  ['version','assetID','fileID', 'showID']
        
        # loop through the shapes, and create temp shapes 
        for inputshape in inputshapes:
            if mc.nodeType(inputshape) == 'mesh' or mc.nodeType(inputshape) == 'nurbsSurface':
                inputshapelong = inputDagShape[inputshapes.index(inputshape)]
                newdag = self._cleanDagPath(inputshape)
                newdag = (self.__godNode__ + '|' + newdag)
                
                emptyshape =  mf.createNode('mesh', newdag)
                temptrans = str(mc.listRelatives(emptyshape, parent=True, fullPath=True)[0])
                # add attrs to the temp transform nodes
                self._addAttr(temptrans, modelAttrs)
                
                # need to pass the long shape here, as we now have TWO objects that share the same short DAG
                tempshape = self.connectTempShape(inputshapelong, temptrans, emptyshape)
                
                cacheSet = self.__objSets__['cacheSet']
                
                Output('adding %s to cacheSet: %s' % (temptrans, cacheSet), sev='info' )
                
                mc.sets(temptrans, edit=True, forceElement=cacheSet )
                self.__tempshapes__.append(tempshape)


    def createGodNode(self):
        if self.__name__:
            godNode = ('|model_' + self.__name__)
            if not mc.objExists(godNode):
                Output('creating Maya Model master group')
                mc.group(empty=True, world=True, name=godNode)

        else:
            outmsg = Output('please pass a model name if you want a GOD node', sev='warn')
                
        # define the model group attrs
        modelAttrs = dict()     
        modelAttrs['string'] = ['am_nodeType', 'assetName', 'showName', 'assetCategory', 'assetRoot']
        modelAttrs['int'] =  ['version','assetID','fileID', 'showID']
        
        # add the custom attrs to the object
        self._addAttr(godNode, modelAttrs)
        return godNode
    
   
    def connectTempShape(self, inputshape, temptrans, tempshape):
        """
        Creates a temp shape for each mesh passed to it and creates a temp shape for geoCaching.
        The polyUnite is a deformer, so shapes that are animated only will still be properly cached.
        
        oldPath: dagPath for the old mesh (ending with transform/shape)
        newPath: new parent for the heirarchy to be created under (likely "cacheGroup|grp1|")
        
        Parameters:
            shape - the dagPath of shape node that is going to be cached
            shapeName - the "nice name" of the shape
            transform - the name of the object (transform) to be passed as the cache name later)
            cacheGroup - the parent cacheGroup in the scene
            
        Returns:
            The new shape node and polyUnite
        """
        newShape = ''
        newTrans = ''
        tmpUnite = ''
        
        mc.sets(tempshape, edit=True, forceElement='initialShadingGroup' )

        if mc.nodeType(inputshape) == 'nurbsSurface':
            
            # nurbs are a little different, since we need to use a nurbsToPoly operation to create the "inputshape"
            # We don't need to put a polyUnite on the object however            
            tess = mc.createNode('nurbsTessellate')
            mc.setAttr((tess+'.format'), 3)
            mc.connectAttr((inputshape+'.worldSpace[0]'), (tess + '.inputSurface'), force = True)
            mc.connectAttr((tess + '.outputPolygon'), (tempshape+'.inMesh'), force = True)
            mc.setAttr((tempshape+'.displaySmoothMesh'), True)
            mc.setAttr((tempshape+'.smoothLevel'), 1)
            
           
            
        #Output('input shape: \'%s\'' % inputshape, 'info')
        #Output('empty shape: \'%s\'' % tempshape, 'info')
        
        if mc.nodeType(inputshape) == 'mesh':
 
            # add a polyUnite, and attach the old shape
            tmpUnite = mc.createNode('polyUnite')  
            
            mc.connectAttr((inputshape+'.worldMatrix[0]'), (tmpUnite+'.inputMat[0]'), force = True)
            mc.connectAttr((inputshape+'.worldMesh[0]'), (tmpUnite+'.inputPoly[0]'), force = True)
            
            mc.connectAttr((tmpUnite+'.output'), (tempshape+'.inMesh'), force = True)
            mc.setAttr ((temptrans+'.inheritsTransform'), False)

        return tempshape
    
    def returnAllShaders(self, shape):
        """ return all the shaders attached to the selected meshes """
        sg = mc.listSets(object = (shape + '.f[*]'), type=1)
        return sg  
        
    def exportShaderSet(self):
        """ exports a shader set for application to the base model"""
        pass




class MayaSet(object):
    """
    Class: MayaSet()
    
        DESCRIPTION
            class for managing  assetmanager Maya objectSets
            
        USAGE
            rig:    - if 'rig this asset' is chosen in the UI, pass a value to create a rig master set
    """
    def __init__(self, rig=False):

        self.__objSets__ = dict()
        sel = mc.ls(selection=True)
        mc.select(clear=True)
        
        mc.select(sel)
    
    @ staticmethod
    def createBaseSets(rig=False):
        mc.select(clear=True)
        rootSet = 'AM_ROOT_SET'
        cacheSet = ''
        rigSet = ''
        sgSet = ''
        
        resultSets = dict()
        
        outmsg = Output('creating AM objectSets')
        if not mc.objExists(rootSet):
            sgSet = mc.sets(name='AM_SG_SET')
            cacheSet = mc.sets(name='AM_CACHE_SET')
            
            # if we are rigging an asset, create a rig master set and give it the other two sets
            # TODO: is it better to create all sets parented to nothing and then force them in?
            if rig:
                rigSet = mc.sets(name='AM_RIG_SET')
                rootSet = mc.sets( cacheSet, sgSet, rigSet, n="AM_ROOT_SET" )
                resultSets['rigSet'] = rigSet
            else:
                rootSet = mc.sets( cacheSet, sgSet, n="AM_ROOT_SET" ) 
            
            resultSets['rootSet'] = rootSet
            resultSets['sgSet'] = sgSet
            resultSets['cacheSet'] = cacheSet
            
          
            # define the master set attrs
            rootSetAttrs = dict()
            rootSetAttrs['string'] = ['am_nodeType', 'assetName', 'showName', 'assetCategory', 'assetRoot']
            rootSetAttrs['int'] =  ['version','assetID','fileID', 'showID']
            #self._addAttr(rootSet, rootSetAttrs)
            
            sgSetAttrs = dict()
            sgSetAttrs['string'] = ['am_nodeType', 'assetName']    
            sgSetAttrs['int'] = ['modelVersion', 'assetVersion', 'materialVersion']
            #self._addAttr(sgSet, sgSetAttrs)
           
            cacheSetAttrs = dict()
            cacheSetAttrs['string'] = ['am_nodeType', 'assetName', 'showName', 'assetCategory', 'refFile', 'submitScene']    
            cacheSetAttrs['int'] = ['modelVersion']
            #self._addAttr(cacheSet, cacheSetAttrs)
        
        return resultSets
            

   
    # TODO: add this to maya_func, sanity check with 'attributeExists'
    def _addAttr(self, obj, attrs, hidden=False):
        """ adds attributes to a transform node. Pass a dictionary
            of attrs where attrs.dict['string'] = string attrs, etc"""
        if mc.objExists(obj):
            for key, val in attrs.iteritems():
                if key == 'string':
                    for v in val:
                        if not mf.attributeExists(v, obj):
                            mc.addAttr(obj, longName = v, dataType = 'string', hidden = hidden, storable=True )
                        else:
                            outmsg = Output('attribute: "%s" already exists for node: "%s"', v, obj)

                        
                if key == 'int':
                    for v in val:
                        if not mf.attributeExists(v, obj):
                            mc.addAttr(obj, longName = v, attributeType = 'long', hidden = hidden, storable=True )   
                        else:
                            outmsg = Output('attribute: "%s" already exists for node: "%s"', v, obj)
                            
    def _addObj(self, set, obj):
        """ adds an object to the specified set (if nothing is specified, add whatever is selected.
            Where possible, pass the method a long name """
        pass
    
    
class MayaDagpath(object):
    """
    Class: MayaDagpath()
    
        DESCRIPTION
            class to manage DAG paths
            
        USAGE
        
    """
    def __init__(self, node):
        
        self.node = node
        
        
            