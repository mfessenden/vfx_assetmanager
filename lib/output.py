# output.py by Michael Fessenden (c) 2011
#
# v0.29
#
# Description :
# -------------
# This is the module that handles all of the output messages from the application
#
#
# Version History :
# -----------------
# v0.29:
# - development version
#
# TODO List :
# -----------
#
# ----------------------------------------------------------------------------

''' classes for user and system output
much of am_os can be replaced by this

Log Files:
    User: User output log, routine and important messages are logged - important messages that pertain to other users are also replicated in the system log
    System: Log that can be accessed by the entire studio; important messages such as when file/folders/assets are created/deleted
    

'''
import os, sys
import re
import posixpath as pp
import datetime
from time import strftime
import glob


__version__ = '0.291'
__lastupdate__ = 'Aug 22 2011'
__amlib__ = 'output'

sys.setrecursionlimit(1500)


def returnUsername():
    if sys.platform == "win32":
        cmd="USERNAME"
    elif sys.platform == "linux2":
        cmd="USER"
        
    user = os.getenv(cmd)
    return user

def returnDateTime(format='nice'):
    ''' gets the current data and time, and formats it for humans'''
    if int(strftime("%H"))> 12:
        suf = 'PM'
    else:
        suf = 'AM'
    
    date=''
    if format=='nice':
        date = strftime("%a %b %d, %Y %I:%M:%S " + suf)
    if format=='short':
        date = strftime("%Y-%m-%d %H:%M:%S")
    return date
    
    
usr_logs = os.environ['AM2_USER_LOGS']
sys_logs = os.environ['AM2_SYSTEM_LOGS']

global usr_log
global sys_log
global app

app = sys.executable.split('\\')[len(sys.executable.split('\\'))-1]

usr_log = pp.join(usr_logs, 'am_output.txt')
sys_log = pp.join(usr_logs, 'am_maya.txt')

#sys_error_log = pp.join(usr_logs, 'am_errorLog.txt')
#usr_nuke_log = pp.join(usr_logs, 'am_nuke.txt')

#for log in (usr_output_log, sys_error_log, usr_nuke_log, usr_maya_log):
for log in (usr_log, sys_log):
    if not os.path.exists(log):
        date = returnDateTime()
        if log is usr_log:
            header = ['# assetManager user log file\n', ('# created ' + date +'\n'), '# storage for output and error messages\n\n']
        if log is sys_log:
            header = ['# assetManager system log file\n', ('# created ' + date +'\n'), '# storage for system-wide output and error messages\n\n']
        print('[SYSTEM]: creating assetManager temp file: \"' + log + '\"')
        file = open(log , 'w')
        file.writelines(header)
        
class Output(object):
    def __init__(self, msg, sev='out', scope='norm'):
        '''
        Class: Output
            The Output object provides a consistent interface to dealing with output messages, exceptions and errors. 
            It expects a string message, a severity level, and a scope (ie. user, group or system), then formats a custom 
            system/error/debugging message and writes it to the appropriate log files.
        
            SEVERITY
                out: simply outputs a message (user log, screen)
                sys: System output (user log, system log, screen)
                db: Debugging output (user log, screen, system log)
                warn: Warning output (user log, screen, system log)
                err: Error (user log, screen, system log)
             
             SCOPE
                 norm: normal scope of message
                 grp: larger scope (whole group)
                 sys: larger scope (system)
        '''
        self.__levels__ = ['out', 'sys', 'db', 'warn', 'err']
        self.__scopes__ = ['norm', 'grp', 'sys']
        self.message = msg
        self.date = returnDateTime()
        self.user = returnUsername()
        self.shortdate = returnDateTime(format='short')
        
        global app
        
        printMsg = ''
        outputMsg = ''
        
        if sev is 'out':
            #file = open(usr_log, 'a')
            printMsg =  ('[OUTPUT]: %s: %s') % (self.shortdate, msg)
            outputMsg =  ('[OUTPUT]: %s: %s (%s)') % (self.date, msg, self.user)
        
        if sev is 'sys':
            #if app.startswith('maya'):
                #file = open(usr_log, 'a')
            file = open(usr_log, 'a')
            printMsg =  ('[SYSTEM]: %s: %s') % (self.shortdate, msg)
            outputMsg =  ('[SYSTEM]: %s: %s (%s)') % (self.date, msg, self.user)
            
        if sev is 'db':
            file = open(usr_log, 'a')
            outputMsg =  ('[DEBUG]: %s: %s (%s)') % (self.date, msg, self.user)
        
        if sev is 'warn':
            file = open(usr_log, 'a')
            printMsg =  ('[WARNING]: %s: %s') % (self.shortdate, msg)
            outputMsg =  ('[WARNING]: %s: %s (%s)') % (self.date, msg, self.user)
            
        if sev is 'err':
            file = open(sys_log, 'a')
            outputMsg =  ('[ERROR]: %s: %s (%s)') % (self.date, msg, self.user)  
                 
        newList = []
        msgList = [outputMsg,]
        
        if sev is not 'out':
            for m in msgList:
                newList.append(m + '\n')
            file.writelines(newList)
            file.close()
            
        print printMsg
            
        


        
