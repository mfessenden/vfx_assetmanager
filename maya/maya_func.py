# maya_func.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This is the module that contains common Maya worker functions. It's meant to be a 
# standalone module, so assetmanager classes are not imported (aside from Output)
#
#
# Version History :
# -----------------
#
# v0.33:
# - development version
#
# TODO List :
#
# ----------------------------------------------------------------------------

import maya.cmds as mc
from assetmanager.lib.system import Output

__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__repr__ = 'maya_func'
__amlib__ = 'maya_func'
__status__ = 'development'

import __builtin__
__builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ')\n' + __file__ + '\n\n' )


#===============================================================================
# SCENE FUNCTIONS
#===============================================================================

def returnSceneName(short=True):
    """
    Returns the name of the current scene
    
    Parameters:
        short - If true, this will not return the file path, only the scene name
    
    Returns:
        String of the current scene name
    """
    sceneName = ''
    if short is True:
        sceneName = mc.file(query = True, sn = True, shn = True)
    else:
        sceneName = mc.file(query = True, sn = True)
        
    return sceneName

def returnPlayback(anim=True):
    """
    Returns a tuple of the animation start/end time (the outer values in the Maya UI)
    
    Parameters:
        anim - Returns the animation start/end time if true, minTime/maxTime if false (the inner values in the Maya UI)
    
    Returns:
        A tuple; start time, end time
    """
    playbackMin = ''
    playbackMax = ''
    
    if anim is True:        
        playbackMin = mc.playbackOptions( query = True, ast = True )
        playbackMax = mc.playbackOptions( query = True, aet = True )
    else:
        playbackMin = mc.playbackOptions( query = True, min = True )
        playbackMax = mc.playbackOptions( query = True, max = True )
    
    playback = tuple([playbackMin, playbackMax])
    
    return playback

def recurseDag(dagpath, number):
    
    path = dagpath.split('|')
    number = len(path)
    while number:
        print 'number: %d' % number
        for p in path:
            curdag = str('|'.join(p))
            print p
            
        number -= 1
        recurseDag(curdag, str(number))
            

    
#===============================================================================
# GEOMETRY FUNCTIONS
#===============================================================================

def returnAllGeo(long=False):
    """ similar to ls, but returns the transform node alongside the shape"""
    if long:
        geo = [str(obj) for obj in mc.ls( dag=True, g=True, long=True, v=True, ni=True  )]
        return geo
    else:
        geo = [str(obj) for obj in mc.ls( dag=True, g=True, ap=True, v=True, ni=True  )]
    
        result = []
        for g in geo:
            i = geo.index(g)
            if not '|' in g:
                res = str(mc.listRelatives(g, parent=True, path=True)[0])
                g = (res + '|' + g)
        
            if mc.objExists(g):
                result.append(g)
        
        return result
        
def returnSelectedGeo(long=True, withtransform=False):
    shapes = [str(obj) for obj in mc.ls(selection=True, leaf=True, dagObjects = True, long=True)]
    return shapes

def returnShapeName(transform):
    ''' given a transform name, return the proper shape name (as Maya does)'''
    suffix = ''
    baseName = ''
    try:
        suffix = re.search('[0-9]$', transform).group(0)
    except AttributeError:
        pass
        
    baseName = re.sub(suffix, '', transform)
    shapeName = baseName + 'Shape' + suffix
    
    return shapeName

def transferShaders(obj1, obj2):
    """ given two shapes, will transfer shaders from obj1 to obj2"""
    pass

def createNode(nodetype, dagpath):
    # get a list
    daglist = dagpath.split('|')
    depth = len(daglist)

    # get the first object
    
    curobj = ''
    for i in range(0,depth):                  
        if i is not depth-1:
            
            if not mc.objExists(curobj + '|' + daglist[i]):
                try:
                    if not curobj:                        
                        curobj = mc.createNode('transform', name=daglist[i])
                        curobj = mc.ls(curobj, long=True)[0]
                        #print 'creating transform: "%s"' % curobj
                    else:
                        curobj = mc.createNode('transform', name=daglist[i], parent=curobj)
                        curobj = mc.ls(curobj, long=True)[0]
                        #print 'creating transform: "%s"' % curobj
                except RuntimeError:
                    pass
            else:
                # the current object does exists, so just set the current object to it
                #print '**object exists: %s, skipping...' % (curobj + '|' + daglist[i])
                curobj = (curobj + '|' + daglist[i])
        else:            
            finalObj = mc.createNode(nodetype, name = daglist[i], parent = curobj)
            finalObj = mc.ls(finalObj, long=True)[0]
            #print 'creating final node: %s' % finalObj
            #print '\n'
            return finalObj

            
            
#===============================================================================
# GENERAL FUNCTIONS
#===============================================================================

def attributeExists(attr, node):
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
   
