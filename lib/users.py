# users.py by Michael Fessenden (c) 2011
#
# v0.28
#
# Description :
# -------------
# This is the library that handles all of the user-specific functions
#
#
# Version History :
# -----------------
# v0.28:
# - development version
#
# TODO List :
# -----------
# 
# ----------------------------------------------------------------------------


import MySQLdb as sql
import re
from assetmanager.lib.am_os import returnUsername
from assetmanager.lib.output import Output 

db = sql.connect(host='localhost', user='root', db="assets")
cursor = db.cursor()

cursor.execute('show columns from users')
colNames = cursor.fetchall()
columnNames = [col[0] for col in colNames]


__version__ = '0.28'
__lastupdate__ = 'Jul 25 2011'
__repr__ = 'users'
__amlib__ = 'users'
#mc.optionVar(sva=('am2_lib_libraries', __name__))

out = Output('initializing assetManager common users library')

class UserObj(object):
    '''creates an object for a given user, if his data exists in the users table'''
    def __init__(self, username=''):
        self.username = username

        # raise an error if a username wasn't provided
        if not self.username:
            #raise RuntimeError('please enter a username')
            self.username = returnUsername()
        
        # query the database and get the assetID
        cursor.execute('select * from users where username = %s', self.username)
        queryData = cursor.fetchall()
        cursor.close
        try:
            self.userID = int([data[0] for data in queryData][0])
        except IndexError:
            print '>> error: user not in database'
        
        # if the user exists in the database, set attributes for him or her
        if self.userID:
            userData = [col for col in queryData]
            
            
            # zip the colNames/data into a list of tuples
            userData = zip(columnNames, list(userData[0]))
            for d in userData:
                if not 'userID' in d[0]:
                    setattr(self, d[0], d[1]) 

