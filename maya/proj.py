# proj.py by Michael Fessenden (c) 2011
#
# v0.30
#
# Description :
# -------------
# Support functions for maya
#
#
# Version History :
# -----------------
# v0.32:
# - development version
#
# v0.28:
# - reworked the output functions
# - fixed a bug that formatted AM/PM in the date incorrectly
#
# TODO List :
# 
# ----------------------------------------------------------------------------

import os
import posixpath as pp
from time import strftime
import sys
import maya.cmds as mc
from assetmanager.lib.am_os import returnUsername, eprint, outprint, sprint, dprint
from assetmanager.lib.users import UserObj

__version__ = '0.32'
__lastupdate__ = 'Dec 09 2011'
__repr__ = 'proj'
__amlib__ = 'proj'
__status__ = 'production'

# pull data from the database for the current user
username = returnUsername()
curUser =  UserObj(username)

# returns the current project
def returnCurrentProject():
    proj = mc.workspace(query=True, fullName= True)
    return proj

def projectManagerUI():
    
    # get a list of recent projects
    curProj = curUser.current_proj
    recentProj =  curUser.recent_proj
    recentProj = recentProj.rsplit(',')
    finalProj = []
    for proj in recentProj:
        finalProj.append(proj.strip())
    
    # blow away window prefs
    if mc.window('projMgr', exists=True):
        mc.deleteUI('projMgr', window=True)
    if mc.windowPref('projMgr', exists=True):
        mc.windowPref('projMgr', remove=True)
        
    projWin = mc.window('projMgr', title = 'Project Manager', width=600, height=200)
    projCol = mc.columnLayout(parent = projWin, adjustableColumn = True)
    projForm = mc.formLayout(parent=projCol)
    
    # form contents
    projHeader = mc.frameLayout(parent = projForm, borderStyle = 'out', label = 'Projects', labelVisible = True)
    projList = mc.textScrollList('projList', parent = projForm)
    
    # populate the textScrollList with a list of shows from the database
    for proj in finalProj:
        wsmel = pp.join(proj, 'workspace.mel')
        print wsmel
        if pp.exists(wsmel):
            mc.textScrollList('projList',edit=True, append=proj, selectCommand = setCurrentProj)
        else:
            eprint(('recent project "%s" in database is not valid (no workspace.mel)' % proj))
    #else:
        #mc.textScrollList('projList',edit=True, append='(no shows in database)')

    projSelectBut = mc.button(parent = projForm, label = 'New Project', command = createProj)
    
    # edit the form
    mc.formLayout(projForm, edit=True, attachForm=[
        (projHeader, 'top', 0),
        (projHeader, 'left', 0),
        (projHeader, 'right', 0),
        (projList, 'left', 10)],
        attachControl=[
        (projSelectBut, 'top', 5, projList),
        (projList, 'top', 2, projHeader)],
        attachPosition=[
        (projList, 'right', 2, 95)])
        
    mc.showWindow()
    
def setCurrentProj(*args):
    proj = mc.textScrollList( 'projList', query=True, selectItem=True)[0]
    print '>> setting project: "%s"' % proj
    mc.workspace(proj, openWorkspace=True)
    
def createProj(*args):
    pass
    
    
    
    
    
    
# This is the old setupNewProject procedure in mel   
#===============================================================================
#    
# // takes the given path, sets up a project and switches to it
# global proc sys_setupNewProject(string $path, string $images){
#    curProc("sys_setupNewProject");
#    // KILL THE TRAILING SLASH, IF THERE IS ONE EDIT: 10/23/2010
#    if (`endsWith $path "/"`){
#        $path = `substitute "/$" $path ""`;
#    }
#    string $wsMel = ($path+"/workspace.mel");
#    $wsMel = `substitute "//" $wsMel "/"`;
#    if(`filetest -f $wsMel`){
#        print ("// project exists, setting workspace to: "+$wsMel+" //\n");
#        // set the current project
#        setProject $path;
#        ui_refreshHelpLine();
#    } else {
#        if(!`filetest -d $path`){
#            // create a new workspace
#            curProc("sys_setupNewProject");
#            string $msg = ("creating new project directory: "+$path);
#            outprint($msg, 1, 1, 1);
#            workspace -cr $path;
#        }
#        
#        // set the current project
#        //workspace -o $path;
#        setProject $path;
#        print ("// setting maya project to: "+$path+" //\n");
#        // setup the default directories
#        string $wsotDir[] = {"scenes", "data", "mel", "fur/furShadowMap", "fbx", "DAE_FBX", "fur/furImages"};
#        string $wsrtDir[] = {"clips", "3dPaintTextures", "renderData/depth", "renderData/iprImages", "renderData/mentalRay", "renderData/shaders", "textures", "particles", "sound", "sourceimages", "renderScenes", "images"};
#        string $allWSDir[] = stringArrayCatenate($wsotDir, $wsrtDir);
#        for ($each in $allWSDir){
#            string $dir = $path+"/"+$each;
#            if (!`filetest -d $dir`){
#                string $createMsg = ("creating new folder: "+$dir);
#                outprint($createMsg, 1, 1, 1);
#                workspace -cr $dir;
#                }
#        }
#        // set the file/obj/rendertype directories
#        workspace -ot scene scenes;
#        workspace -fr mel mel;
#        workspace -rt images $images;
#        workspace -rt textures textures;
#        workspace -fr IGES data;
#        workspace -fr DXFexport data;
#        workspace -fr OBJexport data;
#        workspace -fr furShadowMap "fur/furShadowMap";
#        workspace -fr RIBexport data;
#        workspace -fr RIB data;
#        workspace -fr Fbx Fbx;
#        workspace -fr furFiles "fur/furFiles";
#        workspace -fr diskCache data;
#        workspace -fr furAttrMap "fur/furAttrMap";
#        workspace -fr animImport data;
#        workspace -fr DAE_FBX DAE_FBX;
#        workspace -fr furImages "fur/furImages";
#        workspace -fr image images;
#        workspace -fr furEqualMap "fur/furEqualMap";
#        workspace -fr DXF_FBX DXF_FBX;
#        workspace -fr aliasWire data;
#        workspace -fr move data;
#        workspace -fr DXF data;
#        workspace -fr EPS data;
#        workspace -fr animExport data;
#        workspace -fr OBJ data;
#        workspace -fr IGESexport data;
#        
#        workspace -rt clips clips;
#        workspace -rt 3dPaintTextures 3dPaintTextures;
#        workspace -rt depth "renderData/depth";
#        workspace -rt iprImages "renderData/iprImages";
#        workspace -rt mentalRay "renderData/mentalRay";
#        workspace -rt lights "renderData/shaders";
#        workspace -rt particles particles;
#        workspace -rt audio sound;
#        workspace -rt sourceImages sourceimages;
#        workspace -rt renderScenes renderScenes;
#        workspace -rt nuke nuke;
# 
#    
#        // query the project (full path)
#        // workspace -q -fn;
#        // query the project (name only)
#        // workspace -q -act;
#    
#        string $wsRoot = `workspace -q -rd `;
#        print ("// workspace root is "+$wsRoot+" //\n");
#        // save the workspace.mel file
#        workspace -s;
#    }
# 
#        
# }
#===============================================================================