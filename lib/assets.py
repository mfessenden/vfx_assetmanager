# assets.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This is the module that creates and updates asset objects for whichever application is accessing the database
#
# Version History :
# -----------------
# v0.34:
# - development version
#
# v0.31:
# - added the AssetBase class
#
# v0.29:
# - added 'returnShowAssets'
#
# v0.24:
# - fleshed out the showObj class
# - changes this module to support MySQL
# - tweaked the buildShowGlobals function to set more optionVars
#
# TODO List :
# - see if there's a MySQL equivalent to text_factory
# - Make the 'show' a class that we can call, assign attributes and query
# - This will probably be merged with another module; so the database isn't called too often
# - we want to keep the database record returned as a tuple
# - expand 'buildShowGlobals' to resolve shot/layer names in show variables
# ----------------------------------------------------------------------------


import re
from assetmanager.lib.system import Output
from assetmanager.lib.sql import Query

__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__amlib__ = 'assets'
__status__ = 'production'

import __builtin__
try:
    __builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ') - '+ __lastupdate__ +'\n' + __file__ + '\n\n' )
except:
    pass


out = Output('initializing assetManager common assets library')


#===============================================================================
# def returnShowAssets(show):
#    cursor.execute('select asset_name from assets where show_name = %s', show)
#    queryData = cursor.fetchall()
#    showAssetData = [col for col in queryData]
#    assetNames = []
#    for show in showAssetData:
#        assetNames.append(show[0])
#        
#    return assetNames
#===============================================================================

def showAllAssets():
    ''' prints out a list of all the assets in the database'''
    cursor.execute('select asset_name, asset_type, show_name, asset_root from assets')
    allAssets = cursor.fetchall() 
    for asset in allAssets:
        print ('assetName: %s' % asset[0])
        if asset[1]:
            print ('assetType: %s' % asset[1])
        print ('show_name: %s' % asset[2])
        if asset[3]:
            print ('assetRoot: %s' % asset[3])
        print '='*50
                   
                   
class AssetBase(object):
    """
    Class: AssetBase()
      
    DESCRIPTION
        This is the base asset class. It pulls data from the database and stores important attributes 
        about the asset.
            
    USAGE
        Call the class with with the name of the asset and the show that the asset belongs to.
        

    """
    def __init__(self, name='', show=''):
        self.assetName = name
        self.show_name = show
        
        # if the user didn't give any information, throw an error
        if (not self.assetName) or (not self.show_name):
            raise RuntimeError('not enough information given, please input an assetName and the show_name')
        
        # query the database and get the assetID
        cursor.execute('select assetID from assets where asset_name = %s and show_name = %s', (self.assetName, self.show_name))
        queryData = cursor.fetchall()

        # if there is an assetID value, then this asset must exist in the database
        # TODO: we need to figure out how to handle a len(queryData) higher than one (ie: more than one assetName of the same name in the same show)
        if len(queryData):
            
            print '\n>> asset name: %s, show: %s' % (self.assetName, self.show_name)
            
            for data in queryData:
                self.assetID = data[0]
            
            # get the columnNames
            
            cursor.execute('show columns from assets')
            colQuery = cursor.fetchall()
            colNames = [col[0] for col in colQuery]
            
            # get the columnData
            # TODO: see why this returns a list of tuples? (columnNames comes back as a list) 
            cursor.execute('select * from assets where assetID = %s', self.assetID)
            assetQuery = cursor.fetchall()
            assetData = [col for col in assetQuery]
            # zip the colNames/data into a list of tuples
            assetData = zip(colNames, list(assetData[0]))
            
            # set some attributes dynamically for this class
            # TODO: see if this is feasible or whether we need to set some base attrs manually
            for d in assetData:
                if not 'assetID' in d[0]:
                    setattr(self, d[0], d[1]) 
            
            # print the results
            self.query(0)
            
            
        # else, return an error
        else:
            self.assetName = None
            self.show_name = None
            print '>> sorry, there is no asset called "%s" in show "%s". Try using the "addAsset" method to add a new asset' % (name, show)
            

    def query(self, refresh = 1, allattrs = 0):
        ''' runs a simple query on the object and prints out results'''
        
        if self.assetName is not None:
            if refresh:
                print '\n>> database values for object: %s' % self.assetName
                # refresh the object
                self.refresh()
                
            attrs = self.__dict__
            for k in attrs.iteritems():
                if not allattrs:
                    if getattr(self, k[0]):
                        print k[0],': ', getattr(self, k[0])
                else:
                    print k[0]
        else:
            print 'no record found in database'

          
    def update(self, assetID, *kwargs):
        ''' Update the asset record in the database, where "updateData" is a list of "column = data" strings'''
        newData = []
        
        # do a little formatting, in case the user has entered a single attribute as a string
        if type(updateData) is str:
            updateData = [updateData,]
            
        print 'assetID: %s' % self.assetID
        for ud in updateData:
            values = ud.split('=')
            # make sure to format the data with quotes, leave it alone if it has been
            try:
                v = re.sub(r'""', '"', ('"' + values[1] + '"')) 
                newData.append(values[0]+'='+v)
            except IndexError:
                print '>> something is wrong, check the columnName that you have submitted. Use the \'allattrs()\' method to see all of the database columns'

        updateStatement = ', '.join(newData)
        print updateStatement
        if self.assetID:
            print '>> updating asset %s...' % self.assetName
            cursor.execute('update assets set %s where assetID = %s' % (updateStatement, self.assetID))
            db.commit()
            # refresh the object
            self.query()
        
    def addAsset(self, assetName, show_name, filerules=[]):
        ''' Add a new asset record in the database, where "filerules" is a list of "column = data" strings.
        The new asset is considered "dirty" until the required directories are created and resolved'''
        
        # get all of the shows
        cursor.execute('select show_name from shows')
        showsQuery = cursor.fetchall()
        allShows = [sh[0] for sh in showsQuery]
        
        if show_name not in allShows:
            print '>> warning, this asset belongs to a show that is not in the database'
        
        # get the columns
        cursor.execute('show columns from assets')
        colQuery = cursor.fetchall()
        colNames = [col[0] for col in colQuery] # TODO: see if we can exclude the 'assetID' columnName if we can
        
        # sort out the valid columnNames
        rules = ['assetName', 'show_name', 'isDirty']
        values = [('"' + assetName + '"'), ('"' + show_name + '"'), 1]

        validRules = []
        
        # if the user gave us some file rules:
        for f in filerules:
            if (not 'assetName' in f) and (not 'show_name' in f):
                rules.append(f.split('=')[0])
                values.append(re.sub(r'""', '"', ('"' + (f.split('=')[1].strip())+ '"')))
            
            
        for f in rules:
            if f in colNames:
                validRules.append(f)

        columnNamesString = '(' + ', '.join(validRules) + ')'
        valueString = '(' + ', '.join( map( str, values ) ) + ')'  # use 'map' since we have an int in there

        self.assetName = assetName
        self.show_name = show_name
        
        self.isDirty = 1
        print '>> adding new asset: "%s" for show "%s"'  % (self.assetName, self.show_name)
        cursor.execute('insert into assets %s value %s'  % (columnNamesString, valueString))
        db.commit()
        
        # FIX: we need to re-query the database to get the assetID in order to refresh the object
        cursor.execute('select assetID from assets order by assetID desc limit 1')
        astID = cursor.fetchall()
        self.assetID = int(astID[0])
        # refresh the object
        self.query()



    def delete(self, assetName='', show_name=''):
        ''' Remove an asset from the database'''
        if assetName:
            self.assetName = assetName
        if show_name:
            self.show_name = show_name
        
        print '>> deleting asset: "%s" from show "%s"'  % (self.assetName, self.show_name) 
        cursor.execute('delete from assets where asset_name = "%s" and show_name = "%s"'  % (self.assetName, self.show_name))
        db.commit()
        self.assetName = 'deleted'
        self.show_name = 'deleted'


    def refresh(self):
        ''' Updates the class attributes'''

        try:
            cursor.execute('select * from assets where assetID = %s ' % self.assetID)
        except AttributeError:
            cursor.execute('select assetID from assets where asset_name = %s and show_name = %s', (self.assetName, self.show_name))
        finally:
            cursor.execute('select assetID from assets where asset_name = %s and show_name = %s', (self.assetName, self.show_name))
            
        queryData = cursor.fetchall()
        
        if queryData:  
            for data in queryData:
                #self.assetID = data[0]
                pass
            
            cursor.execute('show columns from assets')
            colQuery = cursor.fetchall()
            colNames = [col[0] for col in colQuery]
    
            cursor.execute('select * from assets where assetID = %s', self.assetID) # asset ID won't be present if this is a new asset
            assetQuery = cursor.fetchall()
            assetData = [col for col in assetQuery]
    
            assetData = zip(colNames, list(assetData[0]))
    
            for d in assetData:
                if not 'assetID' in d[0]:
                    setattr(self, d[0], d[1])
        else:
            print '>> cannot refresh, no record found in the database' 
     
     
     
    def allattrs(self):
        ''' gives a list of all of the class attributes'''
        self.query(1,1)