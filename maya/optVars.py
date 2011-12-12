# optVars.py by Michael Fessenden (c) 2011
#
# v0.30
#
# Description :
# -------------
# This is the library that manages the various optionVars that assetManager sets
# within Maya
#
#
# Version History :
# -----------------
# v0.32:
# - development version
# v0.18:
# - added the UI function
# v0.17:
# - renamed some of the optVars for the database
# v0.16:
# - initial release
#
# TODO List :
# -----------
# - add UI function
# ----------------------------------------------------------------------------

#=== Syntax ====================================================================
# if mc.optionVar(exists='am2_cfg_root'):
#    print mc.optionVar(query = 'am2_cfg_root')
#
# mc.optionVar(sv=('am2_sys_config', cfg))
# mc.optionVar( remove='defaultTriangles' )
# mc.optionVar(sva=('am2_lib_libraries', name))
#===============================================================================

import maya.cmds as mc
__version__ = '0.32'
__lastupdate__ = 'Dec 09 2011'
__amlib__ = 'optVars'
__status__ = 'design'


def am2_optVars():
    ov = mc.optionVar(list=True)
    am_optVars = []
    for o in ov:
        if o.startswith('am2_'):
            am_optVars.append(o)
    return am_optVars

def removeAmOptVars():
    am2_optVars = am2_optVars()
    
    
def checkOptVarsUI():
    pass
    

'''
optVars.py:
    
    This module provides access to the dynamically set Maya optionVars that
    assetManager uses.
    
    am2_lib_devVersion: current library version               
    am2_lib_repositoryLoc: location of the assetManager repository (deprecated - we have MySQL now)
    am2_lib_optVars_ver: 
    am2_lib_optVars_lastSave: 
    am2_lib_assetCore_ver: 
    am2_lib_assetCore_lastSave: 
    am2_lib_assetManagerUI_ver: 
    am2_lib_assetManagerUI_lastSave: 
    am2_lib_startup_ver: 
    am2_lib_startup_lastSave: 
    am2_lib_libCaching_ver: 
    am2_lib_libCaching_lastSave: 
    am2_lib_libModel_ver: 
    am2_lib_libModel_lastSave: 
    am2_lib_libXML_ver: 
    am2_lib_libXML_lastSave: 
    am2_lib_nuke_ver: 
    am2_lib_nuke_lastSave: 
    am2_lib_nuke_procList: 
    am2_lib_sets_ver: 
    am2_lib_sets_lastSave: 
    am2_lib_config_ver: 
    am2_lib_config_lastSave: 
    am2_lib_devVersion: 
    am2_lib_repositoryLoc: 
    am2_lib_optVars_ver: 
    am2_lib_optVars_lastSave: 
    #am2_lib_assetCore_ver: 
    #am2_lib_assetCore_lastSave: 
    am2_lib_assetManagerUI_ver: 
    am2_lib_assetManagerUI_lastSave: 
    am2_lib_startup_ver: 
    am2_lib_startup_lastSave: 
    am2_lib_libCaching_ver: 
    am2_lib_libCaching_lastSave: 
    am2_lib_libModel_ver: 
    am2_lib_libModel_lastSave: 
    am2_lib_libXML_ver: 
    am2_lib_libXML_lastSave: 
    am2_lib_nuke_ver: 
    am2_lib_nuke_lastSave: 
    am2_lib_nuke_procList: 
    am2_lib_sets_ver: 
    am2_lib_sets_lastSave: 
    am2_lib_config_ver: 
    am2_lib_config_lastSave: 
    
    am2_sys_user: 
    am2_sys_os: 
    am2_sys_mayaVer: 
    # am2_sys_root: this is deprecated, replaced by am2_showsRoot
    am2_sys_rootUnix: 
    am2_sys_rootWin: 
    am2_sys_renderRoot: render root(s)
    am2_sys_renderRootUnix: 
    am2_sys_renderRootWin: 
    am2_sys_lastProj: 
    am2_sys_output: 
    am2_sys_repository: 
    am2_sys_dbLoc: 
    am2_sys_rootErrorLog: 
    am2_sys_rootOutput: 
    am2_sys_curProc: 
    am2_sys_curPath: 
    am2_sys_browseCmd: 
    
    am2_db_debug: prompts the application to output debug messages
    am2_db_xml: 
    am2_db_system: prompts the application to output system messages
    am2_db_proc: 
    am2_db_error: displays error messages
    
    am2_ui_curShow: the currently selected show in the UI
    am2_ui_curTab: the currently selected tab in the main UI
    am2_ui_curShot: 
    am2_ui_animLayer: 
    *am2_ui_curCat: same as 'am2_curAsset_curCat'?
    am2_ui_topMenu: array of menu names for the assetManager top menu
    am2_ui_mainTabLayout: the name of the main tabLayout of the UI **New
    

    
    # show global tags
    am2_sg_showNiceName: 
    am2_sg_showPrefix:
    am2_sg_cat_actor: tag for actor category assets
    am2_sg_cat_env: tag for environment category assets
    am2_sg_cat_prop: tag for prop category assets
    am2_sg_cat_assembly: tag for assembly category assets
    am2_sg_cat_tex: tag for texture category assets
    am2_sg_cat_extra1: for extra tags
    am2_sg_class_model: 
    am2_sg_class_rig: 
    am2_sg_class_material: 
    am2_sg_class_fx: 
    
    am2_curAsset_assetName: name of the current asset selected in the UI
    am2_curAsset_curCat: the category of the current asset; also the asset category selected in the UI
    am2_curAsset_assetClass: the asset class of the current asset (ie: model, rig, material)
    am2_curAsset_root: the root directory of the current asset
    am2_curAsset_catRoot: the asset category root of the current asset (ie: show/assets/actor)
    am2_curAsset_curWrkPath: 
    am2_curAsset_modelRefDir: 
    am2_curAsset_modelPCDir: 
    am2_curAsset_matRefDir: 
    am2_curAsset_rigRefDir: 
    am2_curAsset_rigPCDir: 
    am2_curAsset_rigModelRefDir: 
    am2_curAsset_texDir: 
    am2_curAsset_newTexDir: 
    am2_curAsset_modelXMLfile: 
    am2_curAsset_modelFileType: 
    am2_curAsset_modelMaterialFile: 
    am2_curAsset_submitScene: 
    am2_curAsset_newModelFile: 
    am2_curAsset_newMatFile: 
    am2_curAsset_modelVer: 
    am2_curAsset_matVer: 
    am2_curAsset_rigVer: 
    am2_curAsset_modelPCVer: 
    am2_curAsset_newMatVer: 
    am2_curAsset_newModelPCVer: 
    am2_curAsset_newModelVer: 
    am2_curAsset_rigPCVer: 
    am2_curAsset_newRigVer: 
    am2_curAsset_newRigPCVer: 
    
    am2_relShow_root: relative root directory of the current show... deprecated now?
    am2_relShow_assetRoot: relative asset root directory of the current show
    am2_relShow_tmpAssetRoot: 
    am2_relShow_shotRoot: relative shot directory of the current show
    am2_relShow_renderRoot: relative render root directory of the current show... deprecated now?
    am2_relShow_texRoot: relative texture assets directory for the current show
    am2_relShow_modelRoot: model directory rule
    am2_relShow_matRoot: material directory rule
    am2_relShow_rigRoot: rig directory rule
    am2_relShow_furRoot: fur directory rule
    
    am2_relShot_renderRoot: relative render root of the current show... deprecated now?
    am2_relShot_animRoot: relative maya animation directory for the current show
    am2_relShot_animCacheRoot: relative animation cache root directory
    am2_relShot_animLayerCacheRoot: relative animation cache root directory (for a given animation layer)
    am2_relShot_animLayerRoot: relative animation layer root directory
    am2_relShot_lgtRoot: relative maya lighting directory for the current show
    am2_relShot_trackRoot: relative 3d tracking root for the current show
    
    am2_absShow_root: absolute root of the current show
    am2_absShow_assetRoot: asset root directory of the current show
    *am2_absShow_tmpAssetRoot: 
    am2_absShow_shotRoot: absolute shot root for the current show
    am2_absShow_renderRoot: absolute render root of the current show
    am2_absShow_texRoot: absolute texture root for the current show
    am2_absShow_modelRoot: absolute model root for the current show (do we have this?)
    am2_absShow_matRoot: absolute material root for the current show
    am2_absShow_rigRoot: absolute rig root for the current show
    am2_absShow_furRoot: absolute fur root for the current show
    
    am2_absShot_animCacheRoot: 
    am2_absShot_animLayerCacheRoot: 
    am2_absShot_animLayerRoot: 
    am2_absShot_animRoot: 
    am2_absShot_lgtRoot: 
    am2_absShot_renderRoot: 
    am2_absShot_trackRoot: 
    am2_absShot_curLayer: 
    
    am2_tmp_curShow: 
    am2_tmp_assetName: 
    am2_tmp_curCar: 
    am2_tmp_latestFile: 
    am2_tmp_newAssetDesc: 
    am2_tmp_tagMdl_submit: 
    am2_tmp_cacheSet_info: 
    am2_tmp_addShow_showRoot: 
    am2_tmp_cache_pmv_ics: 
    am2_tmp_cache_pmv_dist: 
    am2_tmp_curAsset_refFile: 
    am2_tmp_fileFormat:
    
    am2_cfg_relShowRoot: 
    am2_cfg_relShowAssetRoot: 
    am2_cfg_relShowTmpAssetRoot: 
    am2_cfg_relShowShotRoot: 
    am2_cfg_relShowRenderRoot: 
    am2_cfg_relShowTexRoot: 
    am2_cfg_relShotLightRoot: 
    am2_cfg_relShotAnimRoot: 
    am2_cfg_relShotAnimLayerRoot: 
    am2_cfg_relShotAnimCacheRoot: 
    am2_cfg_relShotAnimCacheLayerRoot: 
    am2_cfg_relShotATrackRoot: 
    am2_cfg_relShotRenderRoot: 
    am2_cfg_relShowModelRoot: 
    am2_cfg_relShowMaterialRoot: 
    am2_cfg_relShowRigRoot: 
    am2_cfg_relShowFurRoot: 
    
    
    # new for Python version:
    
    am2_doc_desc: 
    am2_lib_libraries
    am2_lib_modules
    am2_sys_showsRoot:(list) the main show search directories
    am2_sys_renderRoot: (list) the main show render search directories
    am2_sys_config: the location of the assetManager config file
    am2_curShow_categories: a list of category tags (list)
    am2_curAsset_classRoot: the current asset class directory (added to give us the current path when something is selected in the 'Asset Class' textScrollList )
    
'''

import maya.cmds as mc

# declare the global optVars for the application
global am2_lib_optVars
global am2_sys_optVars
global am2_db_optVars
global am2_ui_optVars
global am2_sg_optVars
global am2_curAsset_optVars
global am2_relShow_optVars
global am2_relShot_optVars

# dependent on "am2_ui_curShot" having a value
global am2_absShow_optVars
global am2_absShot_optVars

global am2_tmp_optVars
global am2_cfg_optVars
global am2_doc_optVars
global am2_all_optVars

#am2_lib_optVars = ['am2_lib_devVersion', 'am2_lib_repositoryLoc', 'am2_lib_optVars_ver', 'am2_lib_optVars_lastSave', 'am2_lib_assetCore_ver', 'am2_lib_assetCore_lastSave', 'am2_lib_assetManagerUI_ver', 'am2_lib_assetManagerUI_lastSave', 'am2_lib_startup_ver', 'am2_lib_startup_lastSave', 'am2_lib_libCaching_ver', 'am2_lib_libCaching_lastSave', 'am2_lib_libModel_ver', 'am2_lib_libModel_lastSave', 'am2_lib_libXML_ver', 'am2_lib_libXML_lastSave', 'am2_lib_nuke_ver', 'am2_lib_nuke_lastSave', 'am2_lib_nuke_procList', 'am2_lib_sets_ver', 'am2_lib_sets_lastSave','am2_lib_config_ver', 'am2_lib_config_lastSave']
am2_sys_optVars = ['am2_sys_user', 'am2_sys_os', 'am2_sys_mayaVer', 'am2_sys_root',  'am2_sys_rootUnix', 'am2_sys_rootWin', 'am2_sys_renderRoot', 'am2_sys_renderRootUnix', 'am2_sys_renderRootWin', 'am2_sys_lastProj', 'am2_sys_output', 'am2_sys_repository', 'am2_sys_dbLoc', 'am2_sys_rootErrorLog', 'am2_sys_rootOutput', 'am2_sys_curProc', 'am2_sys_curPath', 'am2_sys_browseCmd']
am2_db_optVars = ['am2_db_debug', 'am2_db_xml', 'am2_db_system', 'am2_db_proc']
am2_ui_optVars = ['am2_ui_curShow', 'am2_ui_curTab', 'am2_ui_curShot', 'am2_ui_animLayer', 'am2_ui_curCat']
am2_sg_optVars = ['am2_sg_showNiceName', 'am2_sg_showPrefix', 'am2_sg_cat_actor', 'am2_sg_cat_env', 'am2_sg_cat_prop', 'am2_sg_cat_assembly', 'am2_sg_class_model', 'am2_sg_class_rig', 'am2_sg_class_material', 'am2_sg_class_dyn']

am2_curAsset_optVars = ['am2_curAsset_assetName', 'am2_curAsset_curCat', 'am2_curAsset_assetClass', 'am2_curAsset_root', 'am2_curAsset_catRoot',   'am2_curAsset_curWrkPath', 'am2_curAsset_modelRefDir', 'am2_curAsset_modelPCDir', 'am2_curAsset_matRefDir',  'am2_curAsset_rigRefDir', 'am2_curAsset_rigPCDir', 'am2_curAsset_rigModelRefDir', 'am2_curAsset_texDir', 'am2_curAsset_newTexDir', 'am2_curAsset_modelXMLfile', 'am2_curAsset_modelFileType', 'am2_curAsset_modelMaterialFile', 'am2_curAsset_submitScene', 'am2_curAsset_newModelFile','am2_curAsset_newMatFile', 'am2_curAsset_modelVer', 'am2_curAsset_matVer', 'am2_curAsset_rigVer', 'am2_curAsset_modelPCVer',  'am2_curAsset_newMatVer', 'am2_curAsset_newModelPCVer', 'am2_curAsset_newModelVer', 'am2_curAsset_rigPCVer', 'am2_curAsset_newRigVer', 'am2_curAsset_newRigPCVer']
am2_relShow_optVars = ['am2_relShow_root', 'am2_relShow_assetRoot', 'am2_relShow_tmpAssetRoot','am2_relShow_shotRoot', 'am2_relShow_renderRoot','am2_relShow_texRoot',  'am2_relShow_modelRoot', 'am2_relShow_matRoot', 'am2_relShow_rigRoot', 'am2_relShow_furRoot']
am2_relShot_optVars = ['am2_relShot_renderRoot', 'am2_relShot_animRoot', 'am2_relShot_animCacheRoot', 'am2_relShot_animLayerCacheRoot', 'am2_relShot_animLayerRoot','am2_relShot_lgtRoot', 'am2_relShot_trackRoot']
am2_absShow_optVars = ['am2_absShow_root', 'am2_absShow_assetRoot', 'am2_absShow_tmpAssetRoot', 'am2_absShow_shotRoot', 'am2_absShow_renderRoot','am2_absShow_texRoot',  'am2_absShow_modelRoot', 'am2_absShow_matRoot', 'am2_absShow_rigRoot', 'am2_absShow_furRoot']
am2_absShot_optVars = ['am2_absShot_animCacheRoot', 'am2_absShot_animLayerCacheRoot', 'am2_absShot_animLayerRoot', 'am2_absShot_animRoot', 'am2_absShot_lgtRoot', 'am2_absShot_renderRoot', 'am2_absShot_trackRoot', 'am2_absShot_curLayer' ]
am2_tmp_optVars = ['am2_tmp_curShow', 'am2_tmp_assetName', 'am2_tmp_curCar', 'am2_tmp_latestFile', 'am2_tmp_newAssetDesc', 'am2_tmp_tagMdl_submit', 'am2_tmp_cacheSet_info', 'am2_tmp_addShow_showRoot', 'am2_tmp_cache_pmv_ics', 'am2_tmp_cache_pmv_dist', 'am2_tmp_curAsset_refFile', 'am2_tmp_fileFormat']

am2_cfg_optVars = ['am2_cfg_relShowRoot', 'am2_cfg_relShowAssetRoot', 'am2_cfg_relShowTmpAssetRoot','am2_cfg_relShowShotRoot', 'am2_cfg_relShowRenderRoot', 'am2_cfg_relShowTexRoot', 'am2_cfg_relShotLightRoot', 'am2_cfg_relShotAnimRoot', 'am2_cfg_relShotAnimLayerRoot', 'am2_cfg_relShotAnimCacheRoot', 'am2_cfg_relShotAnimCacheLayerRoot', 'am2_cfg_relShotATrackRoot', 'am2_cfg_relShotRenderRoot', 'am2_cfg_relShowModelRoot', 'am2_cfg_relShowMaterialRoot', 'am2_cfg_relShowRigRoot', 'am2_cfg_relShowFurRoot']
am2_doc_optVars = ['am2_doc_desc']

am2_all_optVars =  am2_sys_optVars +  am2_db_optVars +  am2_ui_optVars +  am2_sg_optVars +  am2_curAsset_optVars +  am2_relShow_optVars +  am2_relShot_optVars +  am2_absShow_optVars +  am2_absShot_optVars +  am2_tmp_optVars +  am2_cfg_optVars +  am2_doc_optVars
