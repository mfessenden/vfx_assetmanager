# shows.py by Michael Fessenden (c) 2011
#
# v0.28
#
# Description :
# -------------
# This is the module that handles all of the logic that resolves show paths, also sets
# all of the optionVars for Maya to reference
#
# Version History :
# -----------------
# v0.29:
# - updated shows class to reflect the showID usage in assets queries
# v0.24:
# - fleshed out the showObj class
# - changes this module to support MySQL
# - tweaked the buildShowGlobals function to set more optionVars
#
# TODO List :

# - import maya.cmds only if the current application is Maya, write optionVars to a nuke tmp file 
# - Make the 'show' a class that we can call, assign attributes and query
# - This will probably be merged with another module; so the database isn't called too often
# - we want to keep the database record returned as a tuple
# - expand 'buildShowGlobals' to resolve shot/layer names in show variables
# ----------------------------------------------------------------------------


global app
from sys import executable
app = executable.split('\\')[len(executable.split('\\'))-1]
if app.startswith('maya'):
    import maya.cmds as mc
    
import MySQLdb as sql
from assetmanager.database import queryShow
import re
from assetmanager.lib.output import Output

__version__ = '0.29'
__lastupdate__ = 'Aug 11 2011'
__amlib__ = 'shows'

out = Output('initializing assetManager common shows library')

db = sql.connect(host='localhost', user='root', db="assets")
cursor = db.cursor()

# get the column names for the shows table
cursor.execute('show columns from shows')
colNames = cursor.fetchall()
columnNames = [col[0] for col in colNames]
cursor.close()

# get the index of the absolute variables in the database
showRootIndex = 0
showRenderRootIndex = 0

showAssetRootIndex = 0
showShotRootIndex = 0
showTexRootIndex = 0

assetRootModelsIndex = 0
assetRootMaterialsIndex = 0
assetRootRigIndex = 0
assetRootFurIndex = 0


for c in columnNames:
    if c == 'showRoot':
        showRootIndex = columnNames.index(c)
    if c == 'showRenderRoot':
        showRenderRootIndex = columnNames.index(c)
    if c == 'showAssetRoot':
        showAssetRootIndex = columnNames.index(c)
    if c == 'showShotRoot':
        showShotRootIndex = columnNames.index(c)
    if c == 'showTexRoot':
        showTexRootIndex = columnNames.index(c)
    if c == 'assetRootModels':
        assetRootModelsIndex = columnNames.index(c)
    if c == 'assetRootMaterials':
        assetRootMaterialsIndex = columnNames.index(c)
    if c == 'assetRootRig':
        assetRootRigIndex = columnNames.index(c)
    if c == 'assetRootFur':
        assetRootFurIndex = columnNames.index(c)
        
        
        
def returnAllShows():
    ''' returns a list of all the current shows'''
    db = sql.connect(host='localhost', user='root', db="assets")
    cursor = db.cursor()
    cursor.execute('select showID, show_name from shows')
    queryData = cursor.fetchall()
    showData = [col for col in queryData]
    showIDs = []
    showNames = []
    for show in showData:
        showIDs.append(int(show[0]))
        showNames.append(show[1])
        
    showsDict = zip(showNames, showIDs)
    return showsDict

        
class ShowObj(object):
    def __init__(self, showName, shot=''):
        self.showName = showName
        self.curShot = ''
        if shot:
            self.curShot = shot
            
        if showName:
 
            # buildShowGlobals returns all of the paths only
            showGlobals = self.buildShowGlobals()
            showCategories = []
        else:
            out = Output(('"ShowObj" cannot build a query, no show name given'), sev='err')
            

        
    def query(self):
        ''' just runs a simple query on the object and prints out results'''
        
        if self.showName is not None:
            attrs = self.__dict__
            for k in attrs.iteritems():
                if getattr(self, k[0]):
                    print k[0],': ', getattr(self, k[0])
                else:
                    print k[0]
        else:
            print 'no record found in database'
            
    def buildShowGlobals(self):
        ''' path resolution function: builds the show globals for a given show
        returns a list of tuples, the first tuple being the show columnNames'''

        ## NEW WAY    
        cursor = db.cursor()
        cursor.execute('select * from shows where show_name = %s', self.showName)
        relPaths = cursor.fetchall()

        cursor.close()
             
        # define the absolute variables
        self.showRoot = relPaths[0][showRootIndex]
        self.showRenderRoot = relPaths[0][showRenderRootIndex]
        
        # these are also absolute, but dependant on the previous two...let's go ahead and substitute
        self.showAssetRoot = relPaths[0][showAssetRootIndex].replace('@SHOWROOT@', self.showRoot)
        self.showShotRoot = relPaths[0][showShotRootIndex].replace('@SHOWROOT@', self.showRoot)
        
        self.showTexRoot = relPaths[0][showTexRootIndex]
        
        self.assetRootModels = relPaths[0][assetRootModelsIndex]
        self.assetRootMaterials = relPaths[0][assetRootMaterialsIndex]
        self.assetRootRig = relPaths[0][assetRootRigIndex]
        self.assetRootFur = relPaths[0][assetRootFurIndex]
              
        relVars = ['@SHOWROOT@', '@RENDERROOT@', '@ASSETROOT@', '@SHOTROOT@', '@SHOW@'] 
        assetSpecificVars = ['@ASSET@', '@CATEGORY@', '@LAYER@', '@SHOT@']
        
        absVars = [self.showRoot, self.showRenderRoot, self.showAssetRoot, self.showShotRoot, self.showName, '', '', 'LayerA', self.curShot]
        
        
        # if we're in Maya, check to see if there are optionVars set to fill in the rest of the blanks
        global app
        if app.startswith('maya'):       
            mayaVars = ['am2_curAsset_assetName', 'am2_curAsset_curCat', 'am2_ui_curShot', 'am2_ui_animLayer']      
            for mvar in mayaVars:
                if mc.optionVar(exists=mvar):
                    val = mc.optionVar(query = mvar)
                    mvar = mvar.rsplit('_')
                    setattr(self, mvar[len(mvar)-1], val)             
        
        # generate a dummy list to replace the relative values
        absPaths = []
        for x in range(0, len(relPaths[0])):
            absPaths.append('')
        
        relVars = relVars + assetSpecificVars
        
        relPaths = list(relPaths[0])
        for rp in relPaths: # correct
                tmpPath = str(rp)
                for rvar in relVars:
                    if rvar in tmpPath:
                        if absVars[relVars.index(rvar)]:
                            tmpPath = tmpPath.replace(rvar, absVars[relVars.index(rvar)])
                            #print '>> tmpPath: %s' % tmpPath
                        
                    absPaths[relPaths.index(rp)] = tmpPath
                
        
        resolvedPaths = []
        for ap in absPaths:
            if '@' not in ap:
                resolvedPaths.append(ap)
            else:
                resolvedPaths.append('')
        
        showCategories = []
        showClasses = []
        
        showDataListResolved = dict(zip(columnNames, resolvedPaths))
        for key, value in showDataListResolved.iteritems():
            if value:
                if 'category_' in key:
                    showCategories.append(value)
                    
                if 'class_' in key:
                    showClasses.append(value)
                
                setattr(self, key, value)
        
        setattr(self, 'categories', showCategories)
        setattr(self, 'classes', showClasses)
        
        # remove empty items
        resolvedPaths = list(set(resolvedPaths))
        for rp in resolvedPaths:
            pass
            # print rp   

    def allattrs(self):
        ''' gives a list of all of the class attributes'''
        #self.query(1,1)
        self.query()
        
            
#===============================================================================
#            # convert all non-string items to strings
#            newShow = []
#            for s in show:
#                if type(s) != str:
#                    s = ''
#                newShow.append(s)
#            # TODO: fix this, the tuple is being returned out of order
#            zipped = dict(zip(columnNames, newShow))
#            showDataListResolved.append(zipped)
# 
#        for key, value in showDataListResolved[0].iteritems():
#            pass
#  
#        return showDataListResolved[0]
#===============================================================================


#===============================================================================
# relPaths = ('@SHOTROOT@/@SHOT@/tracking', '@SHOTROOT@/@SHOT@/maya/anim/ref/cache/@LAYER@', '@SHOTROOT@/@SHOT@/maya/light', '@ASSETROOT@/@CATEGORY@/@ASSET@/rig', '@ASSETROOT@/@CATEGORY@/@ASSET@/material', '@SHOWROOT@/assets', '@SHOWROOT@/shots','@SHOWROOT@/assets/tex', '@SHOTROOT@/@SHOT@/maya/anim/ref', '@ASSETROOT@/@CATEGORY@/@ASSET@/model')
# relVars = ('@SHOWROOT@', '@RENDERROOT@', '@ASSETROOT@', '@SHOTROOT@', '@CATEGORY@', '@SHOW@', '@ASSET@', '@LAYER@', '@SHOT@')
# absVars = ('Z:/projects/mario', 'Z:/renders/mario', 'Z:/projects/mario/assets', 'Z:/projects/mario/shots', 'props', 'mario', 'bowser', 'LayerA', 'mario001')
# 
# absPaths = []
# for x in range(0, len(relPaths)):
#    absPaths.append('')
# 
# for rp in relPaths:
#    tmpPath = rp
#    for rvar in relVars:
#        if rvar in tmpPath:
#            tmpPath = tmpPath.replace(rvar, absVars[relVars.index(rvar)])
# 
#        absPaths[relPaths.index(rp)] = tmpPath
# 
# absPaths = tuple(absPaths)
# for ap in absPaths:
#    print ap
#===============================================================================
            
#=======================================================================
# # get some temporary shows
# cursor = db.cursor()
# cursor.execute('select assetName from assets where category2D = "shot" and show_name = %s', self.showName)
# showShotData = cursor.fetchall()
# print showShotData
#=======================================================================
            
            

    