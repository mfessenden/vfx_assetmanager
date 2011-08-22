''' classes for MySQL database queries'''

import MySQLdb as sql
from re import  sub
from assetmanager.lib.output import Output
__amlib__ = 'mysql'
__version__ = '0.29'


# TODO, build this out to cover more complex statements
class Query(object):
    '''
    Class: Query()
    
    DESCRIPTION
        This provides a simplified interface to the MySQL database. Instead of importing the module
        each time, calling this class with a series of keyword arguments gets around having to rewrite
        the SQL connect strings each time (and ensures that the database connection is terminated properly 
        each time).
        
    USAGE
        Call the Query class with keyword arguments to construct the SQL statement. 'From' is a protected
        word, so call the table name directly with 'table'.
        
            query = Query(select='*', table='table1', where=['name=fred', age=40])
    
    '''
    def __init__(self,  **kwargs):
        db = sql.connect(host='localhost', user='root', db="assets")
        cursor = db.cursor()
        
        
        #print kwargs
        selList = []
        fromList = [' FROM ']
        whereList = []
        tableName = ''
        
        for k, v in kwargs.iteritems():
            if 'select'  in k:
                if type(v) is list:
                    for each in v:
                        selList.append(each)
                else:
                    selList.append(v)
            if 'table' in k:
                if type(v) is list:
                    for each in v:
                        fromList.append(each)
                else:
                    fromList.append(v)
                    tableName = str(v) # expand this for multiple table queries
                                      
            if 'where' in k:
                if type(v) is list:
                    for each in v:
                        tmp = each.rsplit('=') # TODO: add support for > < type statements
                        result = (tmp[0] + ' = "' + tmp[1] + '"' + ' AND ')
                        whereList.append(result)
                
        selList = ', '.join(selList)
        selList = ('SELECT ' + selList)
        
        try:
            sqlstr = ('show columns from %s' % tableName)
            cursor.execute(sqlstr)
            colNames = cursor.fetchall()
            self.columnNames = [col[0] for col in colNames]
        except:
            pass
        
        fromList = ''.join(fromList)
        
        queryPart1 = (selList + fromList)
        if len(whereList):
            queryPart2 = ''.join(whereList)
            queryPart2 = sub(r' AND $', '', queryPart2)
            queryStr = (queryPart1 + ' WHERE ' + queryPart2)
        else:
            queryStr = queryPart1
            
        dbResult = []
        #print 'Query String: %s' % queryStr
        
        try:
            cursor.execute(queryStr)
            dbResult = cursor.fetchall()
            self.result = dbResult
        except:
            out = Output('Invalid MySQL query', sev = 'err')
            self.result = ''
        
        cursor.close()
         
        # set the custom attributes
        #for k, v in result.iteritems():
            #setattr(self, key, value)