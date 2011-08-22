# system.py by Michael Fessenden (c) 2011
#
# v0.28
#
# Description :
# -------------
# This is the module that creates and manages the System UI
#
#
# Version History :
# -----------------
#
# v0.26:
# - development version
# v0.20:
# - added the optVars tab and the query function
# v0.17:
# - added tabLayout
# v0.16:
# - initial release
#
# TODO List :
# -----------
# - add a procedure that cleans up optionVars
# - add a searchable optionVars tab (similar to the Browser tab)
# ----------------------------------------------------------------------------


import maya.cmds as mc
from assetmanager.lib.am_os import returnLoadedModules
from assetmanager.lib.output import Output

__version__ = '0.29'
__lastupdate__ = 'Aug 15 2011'
__repr__ = 'system'
__amlib__ = 'system'

out = Output('building assetManager maya system tab' )

mc.optionVar(stringValueAppend = ('am_ui_topMenu', 'System') )
am_systemMenuItems = ['Project...', 'Config...', 'Admin']


def buildSystemModulesTab():
    ''' lists all of the loaded modules and libraries that assetManager has currently loaded'''
    result = returnLoadedModules()
        
    try:
        mc.scrollField('am_sysTab_scrollField', edit=True, text=result)
    except RuntimeError:
        out = Output('cannot edit the system tab', sev='err' )

def buildSystemOptVarsTab(*args):
    ''' queries the current assetManager optionVars, and writes them to a dynamic UI tab'''
    if mc.scrollLayout('am_sysTab_optVarTab_srollLayout', exists=True):
        mc.deleteUI('am_sysTab_optVarTab_srollLayout')
        
    allOptVars = mc.optionVar(list=True)

    am_optVarsLabel = []
    am_optVarsVal = []
    
    for ov in allOptVars:
        if 'am2_' in ov:
            if type(mc.optionVar(q=ov))== unicode:
                am_optVarsLabel.append(ov)
            
                val = mc.optionVar(q=ov)
                am_optVarsVal.append(str(val))
            else:
                try:
                    for o in list(set(mc.optionVar(q=ov))):
                        am_optVarsLabel.append(ov)
                        am_optVarsVal.append(o)
                except TypeError:
                    pass
                    
    if len(am_optVarsLabel):
        am_sysTab_optVarTab_srollLayout = mc.scrollLayout('am_sysTab_optVarTab_srollLayout', hst = 16, vst = 16, parent = 'am_sysTab_optVarFrame' )
        rcl = mc.rowColumnLayout('rcl', parent = am_sysTab_optVarTab_srollLayout, numberOfRows=(len(am_optVarsLabel)), columnSpacing = [7,7])
        
            
        for label in am_optVarsLabel:
            labelName = label +'_LblTxt'
    
            mc.text( font = 'smallFixedWidthFont', label=(label+': '), parent = 'rcl', align = 'right' )
            
        for v in am_optVarsVal:
            vName = v +'_ValTxt'
            mc.text( font = 'smallFixedWidthFont', label=v, parent = 'rcl', align = 'left' )
    else:
        pass
            


def buildSystemTab(parent):
    mc.optionVar(sva=('am2_lib_modules', __name__))
    # TODO: this is a hack, fix
    modules = mc.optionVar(q='am2_lib_modules')
    modules = list(set(modules))
    am_sysTabTabLayout = mc.tabLayout('am_sysTabTabLayout', parent=parent)
    
    am_sysTab_variablesFrame = mc.frameLayout('am_sysTab_variablesFrame',  parent = am_sysTabTabLayout, borderStyle='etchedIn', labelVisible = False, width=550)
    am_sysTab_optVarFrame = mc.frameLayout('am_sysTab_optVarFrame',  parent = am_sysTabTabLayout, borderStyle='etchedIn', labelVisible = False, width=550)
    
    am_sysTab_variablesForm = mc.formLayout('am_sysTab_variablesForm', parent = am_sysTab_variablesFrame)
    am_sysTab_mainCol = mc.columnLayout('am_sysTab_mainCol',  parent = am_sysTab_variablesForm, adjustableColumn = True)
    am_sysTab_scrollField = mc.scrollField('am_sysTab_scrollField', height = 700, editable=False, parent=am_sysTab_mainCol)
    
    buildSystemModulesTab()
    mc.tabLayout('am_sysTabTabLayout', edit=True, tabLabel=((am_sysTab_variablesFrame, 'Modules'), (am_sysTab_optVarFrame, 'Variables')))
    mc.popupMenu(parent = 'am_sysTabTabLayout', button =3)
    mc.menuItem(label='Refresh', command=buildSystemOptVarsTab)
    
  
    
    mc.formLayout(am_sysTab_variablesForm, edit=True, attachForm=[
            (am_sysTab_mainCol, 'left', 2),
            (am_sysTab_mainCol, 'bottom', 2),
            (am_sysTab_mainCol, 'right', 2),
            (am_sysTab_mainCol, 'top', 2)])
    
    buildSystemOptVarsTab()
    return am_sysTabTabLayout



    