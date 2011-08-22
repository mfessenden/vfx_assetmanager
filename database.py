# database.py by Michael Fessenden (c) 2011
#
# v0.28
#
# Description :
# -------------
# This is the module that interfaces with the SQL database
#
#
# Version History :
# -----------------
# v0.28:
# - development version
# v0.26:
# - changed database tables; 'shows' is now 'showGlobals', 'assets' is 'assetGlobals', added 'assetFiles'
#
# v0.23:
# - switched sqlite for MySQLdb
# - added new query functions
#
# v0.18:
# - fleshed out the asset and show classes
#
# v0.17:
# - swapped out the sqlalchemy functions for sqlite
#
# v0.16:
# - initial release
#
# TODO List :
# -----------
# - make queryAsset query ANY column, not just the assetName
# - the new queryAsset function returns results in the wrong order
# - rework the formatSQL function, it's a horrific hack
# ----------------------------------------------------------------------------

showColumnNames = ['showID', 'showName', 'showDesc', 'showPrefix', 'showRoot', 'showAssetRoot', 'showShotRoot', 'showRenderRoot', 'showTexRoot', 
                   'lightRoot', 'animRoot', 'animLayerRoot', 'animCacheRoot', 'animCacheLayerRoot', 'trackRoot', 'shotRenderRoot', 'assetRootModels', 
                   'assetRootMaterials', 'assetRootRig', 'assetRootFur', 'category_actor', 'category_prop', 'category_env', 'category_assem', 'category_extra', 
                   'class_model', 'class_material', 'class_rig', 'class_fx']
assetsColumnNames = ['assetID', 'assetName', 'assetType', 'show_name', 'assetRoot', 'category3D', 'category2D', 'modelLoc', 'rigLoc', 'materialLoc', 
                     'plateRoot', 'trackRoot', 'mayaRoot', 'lightRoot', 'animRoot', 'fxRoot', 'layoutRoot']

showDefaults = ['','','','','@SHOWROOT@/assets','@SHOWROOT@/shots','','@SHOWROOT@/assets/tex','@SHOTROOT@/@SHOT@/maya/light','@SHOTROOT@/@SHOT@/maya/anim/ref',
                '@SHOTROOT@/@SHOT@/maya/anim/ref/@LAYER@','@SHOTROOT@/@SHOT@/maya/anim/ref/cache','@SHOTROOT@/@SHOT@/maya/anim/ref/cache/@LAYER@','@SHOTROOT@/@SHOT@/tracking',
                '@RENDERROOT@/@SHOW@/shots/@SHOT@','@ASSETROOT@/@CATEGORY@/@ASSET@/model','@ASSETROOT@/@CATEGORY@/@ASSET@/material','@ASSETROOT@/@CATEGORY@/@ASSET@/rig',
                '@ASSETROOT@/@CATEGORY@/@ASSET@/fur','actor','props','env','assembly','','','','model','material','rig','fx']
# SQL Syntax
# cursor.execute("""SHOW FULL columns FROM assetGlobals""")
# cursor.fetchall() - returns a tuple with a tuple for EACH COLUMN queried


import MySQLdb as sql
import re

db = sql.connect(host='localhost', user='root', db="assets")
cursor = db.cursor()

__version__ = '0.28'
__lastupdate__ = 'Jul 15 2011'
__repr__ = 'database'

''' This module handles the database connection and queries for the application'''

# create asset class
# given an asset name, look up the asset in the database and return some basic information about it
class Asset(object):
    def __init__(self, name):
        
        # what kind of asset are we talking about? Shot, 3D asset, plate, etc...
        self.name = name
        s = (name,)
        results = cursor.execute('select * from assetGlobals WHERE assetName=?' , s)
        data = [row[0] for row in results.fetchall()]
        for d in data:
            try:
                s = d.strip()
            except AttributeError:
                s = d
            print 'found asset: %s' % s

# pass a show name to this class and it will attempt to locate the show, and return the show information
class Show(object):
   def __init__(self, name):
       self.name = name
       print 'show name is: %s' % name

def returnAllColumns(table):
    ''' this returns a list of the columNames from the given table'''
    msg = """SHOW columns FROM %s""" % table
    dprint(msg)
    cursor.execute("""SHOW columns FROM %s""" % table)
    colNames = cursor.fetchall()
    desc = [col[0] for col in colNames]
    return desc


def formatSQL(data, column=False):
    '''detects and formats tuples and lists as strings to pass to the MySQL statement'''
    if type(data) == tuple:
        data = str(data)
    elif type(data) == list:
        data = str(tuple(data))
        
    if column:
        data = re.sub('\'', '', data)
        print 'columns: %s' % data
        return data
    else:
        if '\'' in data:
            data = re.sub('\'', '"', data)
        else:
            data = '"' + data + '"'
        data = re.sub('""', '"', data)
        return data
    

def genericQuery(query):
    db = sql.connect(host='localhost', user='root', db="assets")
    c = db.cursor()
    cursor.execute(query)
    results = [] 
    queryData = cursor.fetchall()
    for data in queryData:
        results.append(data)
    # do we need to convert the results back into a tuple
    results=tuple(results)
    return queryData
    
def insertRow(table, columns, values):
    ''' given a table and a formatted list of columns and values, insert
    columns should be formatted as: (col1, col2, col3)
    values should be formatted as: ("val1", "val2", "val3")'''
    db=MySQLdb.connect(host='localhost', user='root', db="assets")
    c=db.cursor()
    c.execute("""INSERT INTO %s %s VALUE %s"""  % (table, columns, values))
    db.commit()
    
# TODO: should this be returned as a tuple?
def returnAllShows():
    ''' returns a list of shows from the database'''
    cursor.execute("""SELECT show_name FROM showGlobals""")
    results = [] 
    showData = cursor.fetchall()
    for data in showData:
        results.append(data[0])
    return results


def returnAllAssets():
    ''' returns a list of all asset names in the database'''
    cursor.execute("""SELECT * from assetGlobals""")
    results = cursor.fetchall()
    result = []
    for row in results:
        result.append(row[1])
    return result

def returnAllShowAssets(show):
    ''' returns a list of assets from the database given a show argument'''
    # convert the show name to a tuple
    s = (show,)
    results = cursor.execute('select assetName from assetGlobals WHERE show=?' , s)
    data = [row[0] for row in results.fetchall()]
    result = []
    for d in data:
        s = d.strip()
        result.append(s)
    return result

def queryAsset(asset):
    # TODO: make this query ANY column, not just assetName
    ''' queries the database for the given asset name(s), returns a list with a dictionary for each entry found'''
    desc = returnAllColumns('assets')
    asset = formatSQL(asset, column=False)
    msg = ("""select * from assets where assetName like %s or show_name like %s""" % (asset, asset))
    dprint(msg)
    cursor.execute("""select * from assets where assetName like %s or show_name like %s""" % (asset, asset))
    
    
   
    results = []
    # results is a tuple of tuples containing a single asset
    showData = cursor.fetchall()
    for show in showData:
        # convert all non-string items to strings
        newShow = []
        for s in show:
            if type(s) != str:
                s = ''
            newShow.append(s)
        # TODO: fix this, the tuple is being returned out of order
        #newShow = tuple(newShow)   
        zipped = dict(zip(desc, newShow))
        results.append(zipped)
    return results

def queryShow(show):
    ''' path resolution function: builds the show globals for a given show
    returns a list of tuples, the first tuple being the show columnNames'''
    show = unicode(show)
    show = formatSQL(show, column=False)
    desc = returnAllColumns('shows')
    dprint("""select * from shows where show_name = %s""" % (show))
    cursor.execute("""select * from shows where show_name = %s""" % (show))
    results = []
    showsResult = cursor.fetchall()
       
    for show in showsResult:
            # convert all non-string items to strings
            newShow = []
            for s in show:
                if type(s) != str:
                    s = ''
                newShow.append(s)
            # TODO: fix this, the tuple is being returned out of order
            #newShow = tuple(newShow)   
            zipped = dict(zip(desc, newShow))
            results.append(zipped)
    return results


class showWidget(object):
    def __init__(self):
        pass