# users.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This is the library that handles all of the user-specific functions
#
#
# Version History :
# -----------------
# v0.34:
# - development version
#
# TODO List :
# -----------
# 
# ----------------------------------------------------------------------------


import re
from assetmanager.lib.system import Output, returnUsername
from assetmanager.lib.sql import Query


__version__ = '0.34'
__lastupdate__ = 'Dec 13 2011'
__repr__ = 'users'
__amlib__ = 'users'
__status__ = 'design'

import __builtin__
try:
    __builtin__.am_mods.append(__name__ + ' - (' + __status__ + '  v' + __version__ + ') - '+ __lastupdate__ +'\n' + __file__ + '\n\n' )
except:
    pass


class UserObj(object):
    """
    Class: UserObj()
      
    DESCRIPTION
        Base user class. It stores information about the current user.
            
    USAGE
        Simply the class; if no username is specified, it is assumed that you 
        are querying the current user
        

    """
    def __init__(self, username=''):
        self.userID = 0
        # raise an error if a username wasn't provided
        if not username:
            self.username = returnUsername()
        else:
            self.username = username
        
        # query the database and get the assetID
        if self.username:
            query = ('select * from users where username = "%s"' % self.username)
            queryObj = Query(query)
            queryData = queryObj.result
            columnNames = tuple(queryObj.desc)
        else:
            outmsg = Output('cannot find a username', sev = 'err')

        try:

         self.userID = str(queryData[0])
         
        except:
            outmsg = Output('error: user "%s" does not have an ID' % self.username, sev = 'err')
        
        # if the user exists in the database, set attributes for him or her
        if self.userID:
            userData = tuple([str(col) for col in queryData])
           
            
            # zip the colNames/data into a list of tuples
            userData = zip(columnNames, list(userData))
            for d in userData:
                if not 'userID' in d[0]:
                    setattr(self, d[0], d[1]) 

