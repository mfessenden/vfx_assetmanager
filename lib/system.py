import posixpath as pp

__version__ = '0.29'
__lastupdate__ = 'Aug 11 2011'
__repr__ = 'system'
__amlib__ = 'system'
namespace = __name__



usr_logs = os.environ['AM2_USER_LOGS']

global prefsfile

prefsfile = pp.join(usr_logs, 'am_prefs.py')

class AMPrefs(object):
    
    def __init__(self, log=prefsfile):
        pass
        
    def append(self, msg, log=prefsfile):
        msgList = [msg,] 
        for m in msgList:
            newList.append(m + '\n')
        file.writelines(newList)
        file.close()
        
        
        

#===============================================================================
# for k, v in sys.modules.iteritems():
#    if 'asset' in k:
#        if not 'None' in str(v):
#            print v.__name__, v.__file__
#===============================================================================    