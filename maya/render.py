__version__ = '0.32'
__lastupdate__ = 'Dec 09 2011'
__repr__ = 'render'
__amlib__ = 'render'
__status__ = 'design'


import maya.cmds as mc

def returnVrayRenderElements():
    elem = mc.ls(type = 'VRayRenderElement')
    channels = []
    
    for e in elem:
        attrs = mc.listAttr(e)
        for attr in attrs:
            if 'vray_name' in attr:
                val = mc.getAttr(e + '.' + attr)
                channels.append(str(val))
    
    return channels