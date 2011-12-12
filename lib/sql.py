# sql.py by Michael Fessenden (c) 2011
#
# v0.32
#
# Description :
# -------------
# Query is simple a wrapper for connecting to the MySQL database
#
#
# Version History :
# -----------------
# v0.33:
# - development version
#
# v0.31:
# - added the Query class, simplified the command structure
#
# TODO List :
# - make sure that we figure out the method for closing the connection, else we get connections
#   open all over the place
# - think about a return function that detects empty on the fly and returns a consistent type (ie always a tuple, not a tuple with one tuple)
# ----------------------------------------------------------------------------
''' classes for MySQL database queries'''
try:
    import MySQLdb as sql
except:
    pass
from re import  sub
from assetmanager.lib.system import Output

__amlib__ = 'sql'
__version__ = '0.33'
__lastupdate__ = 'Dec 11 2011'
__status__ = 'development'

import __builtin__
try:    
    __builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ') - '+ __lastupdate__ +'\n' + __file__ + '\n\n' )
except:
    pass


class Query(object):
    '''
    Class: Query()
    
    DESCRIPTION
        This is a simple wrapper class for the MySQLdb connection, mostly providing error handling
        and output functions, with extra functionality for returning column names for each value
        returned.
        
    USAGE
        Simply call the class and pass it a SQL statement. Passsing the table in as a string after
        the query string will return a tuple of column names
    
    '''
    # set an attribute to track how many open connections we have going
    queries = 0
    
    def __init__(self,  query='', table=''):
        outmsg = Output('opening connection to database...', sev='db')
        
        Query.queries += 1
        
        db = ''
        cursor = ''
        # open a connection to the database
        try:
            db = sql.connect(host='localhost', user='root', db="assets")
            cursor = db.cursor()
            self.connected = True
            
            # return the columns if a table is called
            if table:
                self.allColumns = self.returnAllColumns(table)
                self.table = table
            
            Output(msg = 'Successfully connected to the database', sev = 'db')
        except:
            # if we can't connect, write out an error to the logs
            Output(sev='err', msg = 'Could not connect to the database', write=True)
            self.connected = False
            
        if self.connected:
            if query:
                Output(msg = ('Query: %s' % query), sev = 'db')
                try:
                    Output(msg = 'querying the database', sev='db')
                    cursor.execute(query)
                    result = cursor.fetchall()
                    desc = [col[0] for col in cursor.description]
                    self.desc = desc
                    
                    # we're storing the "results_dirty" attribute in case the filter method returns a bad result
                    self.result_dirty = result
                    self.result = self.filterResult(result)
                    
                # unless there's an error in the SQL query...format it and pass it to the user
                except Exception, err:
                      outmsg =  Output('Error: %d: %s' % (err.args[0],err.args[1]), sev = 'sqlerr')
            else:
                outmsg = Output(msg = 'please enter a query')
    
    def close(self, cursor):
        """ closes the connection (if open)"""
        if self.cursor.connection():
            self.connected = False
            self.cursor.close()
            
        

    
    def returnAllColumns(self, table):
        """ returns a list of the columNames from the given table"""
        # TODO: figure out a way to define the cursor globally so that we don't have to keep opening it
        cursor = ''
        db = ''
        try:
            db = sql.connect(host='localhost', user='root', db="assets")
            cursor = db.cursor()
        except Exception, err:
            outmsg =  Output('Error: %d: %s' % (err.args[0],err.args[1]), sev = 'sqlerr')
            
        msg = 'show columns from %s' % table
        out = Output(msg)
        try:
            cursor.execute('show columns from %s',  table)
            colNames = cursor.fetchall()
            desc = [col[0] for col in colNames]
            self.allColumns = desc
        except Exception, err:
            outmsg =  Output('Error: %d: %s' % (err.args[0],err.args[1]), sev = 'sqlerr')

    def filterResult(self, indata):
        #print '\n INDATA: (%d)' % len(indata)
        #print indata
        """ filters the sql result into a nice tuple without any empty items"""
        outdata = []
        if len(indata) > 1:
            #print 'RETURNING INDATA AS IS:'
            #print indata
            return indata

        else:
            # we have a list or tuple with only one object 
            if type(indata[0]) is list or tuple:
                if len(indata[0]) > 1:
                    for data in indata[0]:
                        #print 'APPENDING: %s' % str(data)
                        outdata.append(data)
                    
            if outdata:
                #print 'RESULT: returning filtered outdata: (%d)' % len(outdata)
                outdata = tuple(outdata)
                #print outdata
                
                return outdata
                    
                    
        
        
    #===========================================================================
    # def filterResult(self, indata):
    #    print '\n INDATA:'
    #    print indata
    #    print 'filterResult: indata list size: %d \n' % len(indata)
    #    """ filters the sql result into a nice tuple without any empty items"""
    #    outdata = []
    #    if len(indata):
    #        
    #        for data in indata:
    #            print  'data: %s' % str(data) 
    #            if type(data) is list or tuple:
    #                if len(data) is 1:
    #                     
    #                    for each in data:
    #                        print 'filterResult: appending data from tuple: %s' % each
    #                        outdata.append(each)
    #                else:
    #                    print 'RESULT: returning data:'
    #                    print indata
    #                    print '\n\n'
    #                    # return data # this was returning just a tuple of the first result
    #                    return indata
    #    
    #    if outdata:
    #        outdata = tuple(outdata)
    #        print 'RESULT: returning filtered outdata:'
    #        print outdata
    #        print '\n\n'
    #        return outdata
    #    else:
    #        print 'RESULT: returning SQL indata'
    #        print indata
    #        print '\n\n'
    #        return indata
    #===========================================================================
        
        
#===============================================================================
# # from StackOverflow
# from MySQLdb.cursors import Cursor
# old_execute = Cursor.execute
# def new_execute(self, query, args):
#   return old_execute(self, query.replace("?", "%s"), args) 
# Cursor.execute = new_execute
#===============================================================================

