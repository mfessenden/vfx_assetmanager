# shows.py by Michael Fessenden (c) 2011
#
# v0.32
#
# Description :
# -------------
# This is the module that handles all of the logic that resolves show paths, also sets
# all of the optionVars for Maya to reference
#
# Version History :
# -----------------
# v0.32:
# - added the 'update' method for the ShowObj
#
# v0.29:
# - updated shows class to reflect the showID usage in assets queries
#
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
# - buildShowGlobals should CREATE any directories that it resolves
# ----------------------------------------------------------------------------


global app
from sys import executable
app = executable.split('\\')[len(executable.split('\\'))-1]
if app.startswith('maya'):
    import maya.cmds as mc

import re  
from assetmanager.lib.sql import Query
from assetmanager.lib.system import Output

__version__ = '0.32'
__lastupdate__ = 'Dec 11 2011'
__amlib__ = 'shows'
__status__ = 'design'

import __builtin__
try:
    __builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ') - '+ __lastupdate__ +'\n' + __file__ + '\n\n' )
except:
    pass


class ShowObj(object):
    """
    Class: ShowObj()
    
    DESCRIPTION
        Base show class
        
    ATTRIBUTES
        columnNames:    tuple of names for each column in the show table
        showNames:      tuple of show names, IDs from the database
        
    USAGE
        Simply call the class with the name of the show that you want to get information for.
    
    """
    def __init__(self, showName='', shot=''):
        
        # builds the show columns attribute
        query = 'show columns from shows'
        queryObj = Query(query)
        self.columnNames = [(col[0], col[1]) for col in queryObj.result]
        
        #print self.columnNames
        
        query = 'select show_name, showID from shows'
        queryObj = Query(query)
        showData = queryObj.result
        
        showNames = []

        # add each show name, ID to a tuple, and return the lot as a tuple
        if showData:
            for data in showData:
                showNames.append((data[0], data[1]))
                
        self.showNames = tuple(showNames)
        
        if showName:
            try:
                # if we are given a show name, return a dictionary with all of the columns and data
                query = 'select * from shows where show_name = "%s"' % showName
                queryObj = Query(query)
                result = queryObj.result
                desc = tuple([col[0] for col in queryObj.desc])
                self.showData = dict(zip(desc, result))
                
                try:
                    # set some dynamic attributes
                    for k, v in self.showData.iteritems():
                        setattr(self, k, v)
                        #setattr(self, mvar[len(mvar)-1], val)
                except Exception, err:
                    pass 
            except:
                outmsg = Output('that show doesn\'t exist', sev = 'err')
            
                
                
                
                
        
            

