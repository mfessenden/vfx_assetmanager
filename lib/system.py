# system.py by Michael Fessenden (c) 2011
#
# v0.35
#
# Description :
# -------------
# This module manages os environment variables and dealing with the studio-specific preferences
#
#
# Version History :
# -----------------
# v0.35:
# - development version
#
# v0.33:
# - added Catch
#
# v0.31:
# - reworked Output, added StudioPrefs
#
# TODO List :
# -----------
# - implement the 'Group' scope for output messages
# - define __package__
# ----------------------------------------------------------------------------

import os, sys
import re
import posixpath as pp
import datetime
from time import strftime
import glob
import inspect
from xml.etree import ElementTree as ET
from xml.dom import minidom

__version__ = '0.35'
__lastupdate__ = 'Dec 13 2011'
__repr__ = 'assetmanager.lib.system'
__amlib__ = 'system'
namespace = __name__
__status__ = 'development'

# 

# files needed
# am_prefs.py             - session preferences
# am_usr_log.txt          - user output log
# am_usr_db_log.txt       - user debug log
# am_sys_log.txt          - system output log
# am_sys_error_log.txt    - system error log
# am_error_log.txt        - stores errors
# projectSettings.xml     - default project settings (
# studioSettings.xml      - studio-specific settings

#===============================================================================
# --variables needed--
# ASSET_MANAGER_LOC
# PIPELINE_LIB
# PIPELINE_NUKE_LIB
# PIPELINE_MAYA_LIB
# AM_USER_LOGS
# AM_SYSTEM_LOGS
# AM_SETTINGS
#===============================================================================

usr_logs = os.environ['AM_USER_LOGS']       # location of user logs
sys_logs = os.environ['AM_SYSTEM_LOGS']     # location of system logs
settings_loc = os.environ['AM_SETTINGS']    # location of settings files

global prefsfile
global usr_log
global usr_error_log
global usr_db
global sys_log
global sys_error

global prefsfile

global studioSettings
global projectSettings

global allLogs
global app
global user
global envStr

app = sys.executable.split('\\')[len(sys.executable.split('\\'))-1]


usr_log = pp.join(usr_logs, 'am_usr_log.txt')
sys_log = pp.join(sys_logs, 'am_sys_log.txt')
usr_error = pp.join(usr_logs, 'am_error_log.txt')
sys_error = pp.join(sys_logs, 'am_sys_error_log.txt')
usr_db = pp.join(usr_logs, '.am_db_log.txt')
prefsfile = pp.join(usr_logs, 'am_usr_prefs.py')

studioSettings = pp.join(settings_loc, 'studioSettings.xml')
projectSettings = pp.join(settings_loc, 'projectSettings.xml')

allLogs = [usr_log, sys_log, sys_error, usr_error, usr_db]

# environment list (*TODO: eventually this will be read in at load from the projectSettings/studioSettings)
envStr = 'SHOW, SEQ, SHOT, ASSETNAME, SHOW_ROOT, SHOW_SHOT_ROOT, SHOT_RENDER_ROOT, SHOT_COMP_ROOT, SHOT_TRACK_ROOT, NUKE_LAST_FILE, DEBUG, SHOW_ID, SHOT_ID, SHOW_ROOT, SHOW_SHOT_ROOT, SHOW_COMP_ROOT, SHOW_TRACK_ROOT, AM_CURRENT_ASSET'

def returnLoadedModules():
    """ returns a string list of all assetmanager modules currently installed"""
    result = []
    for k, v in sys.modules.items():
        try:
            if (v.__amlib__):
                v = str(v)
                if 'asset' in v:
                    val = v.rsplit('\'')
                    ver = ''
                    try:
                        ver = eval(val[1]+'.__version__')
            
                    except (AttributeError, NameError):
                        pass
                    if ver:
                        ver = (' (v'+ver+')')
                    val[3] = val[3].replace('\\', '/')
                    #for e in list((val[1], val[3], ('-'*60))):
                    result.append(''.join(list(((val[1]+ver+'\n'), (val[3]+'\n'), ('-'*61+'\n')))))
            resultStr = ''.join(sorted(result))
            return resultStr
        except AttributeError:
            pass

def returnUsername():
    """ returns the username, based on OS"""
    if sys.platform == "win32":
        cmd="USERNAME"
    elif sys.platform == "linux2":
        cmd="USER"
        
    user = os.getenv(cmd)
    if user:
        return user
    else:
        outmsg = Output('cannot find a username', sev = 'fatal')

# get the current username
user = returnUsername()


def returnDateTime(format='nice'):
    ''' gets the current data and time, and formats it for humans'''
    if int(strftime("%H"))> 12:
        suf = 'PM'
    else:
        suf = 'AM'
    
    date=''
    if format=='nice':
        #date = strftime("%a %b %d, %Y %I:%M:%S " + suf)
        date = strftime("%a %b %d %I:%M " + suf)
    if format=='short':
        date = strftime("%Y-%m-%d %H:%M:%S")
    return date

def browseDirectory(dir):
    """ general function to look for a given directory and open it (regardless of OS)"""
    if pp.exists(dir):
        if sys.platform.startswith('darwin'):
            os.system('open %s' % dir)
        elif sys.platform.startswith('win'):
            os.system('explorer %s' % dir)
        elif sys.platform.startswith('linux'):
            pass
            #os.system('explorer %s' % dir)
    else:
        print '# directory "%s" does not exist' % dir
        

class StudioPrefs(object):
    """
    Class: StudioPrefs()
    
        DESCRIPTION
            Manages studio-wide preferences. Assetmanager looks for these settings to be stored in 
            two files, located at the environment variable "AM_SETTINGS". The two files are named:
                
                projectSettings.xml        - default project settings (can vary from show to show)
                studioSettings.xml         - preferences that are set globally for all users

        USAGE
            simply call the class; the AM_SETTINGS variable is set in the studio_startup.py
            module that is loaded when Maya and Nuke are launched. If the settings files are
            not found, assetmanager will raise a fatal error.
        

    """
    def __init__(self, show = ''):
        global studioSettings
        global projectSettings

        Output('loading studio preferences...', sev = 'sys')
        
        self.studioPrefs = studioSettings
        self.projSettings = projectSettings
        
        self.shotGlobals = self.defineShotGlobals()
    
    def __repr__(self):
        """ string representation of the object"""
        pass
    
    def defineShotGlobals(self):
        shotGlobals = self.searchTag(self.projSettings, 'shotDependent')
        
        return shotGlobals
            
    
    
    def searchTag(self, xmlFile, tag):
        """ searches for data associated with a given tag """     
        tree = ET.parse(xmlFile)
        result = []
        
        for each in tree.getiterator():
            # find a specific tag
            if each.tag == tag:
                if each.text:
                    buffer = [tex for tex in each.text.split('\n')]
                    for buf in buffer:
                        if buf:
                            result.append(buf.lstrip())
        return result
            
    def printSettings(self, xmlFile):
        """ simply prints the settings file contents""" 
        xmldoc = minidom.parse(xmlFile)
        textout = xmldoc.toxml()
        textout = textout.replace('\t', '    ')
        textout = [str(tex) for tex in textout.split('\n')]
        for tex in textout:
            print tex      



class Output(object):
    # TODO: get rid of the write argument, we might just want to write based on severity
    """
    Class: Output
        The Output object provides a consistent interface to dealing with output messages, exceptions and errors. 
        It expects a string message, a severity level, and a scope (ie. user, group or system), then formats a custom 
        system/error/debugging message and writes it to the appropriate log files.
        
        USAGE
            simply call the class, give it a message to output, the severity, scope and a boolean value for write
            (which will write the selected output to the appropriate log file on disk). A third value, 'Scope', allows
            the system to flag an output to be written to the system log, and therefore visible to the entire studio
        
        SEVERITY
        
            Determines how serious the message is
            
            out:         standard output message (user log, screen)
            sys:         system output (user log, system log, screen)
            db:          debugging output (user db log, screen) 
            warn:        warning output (user log, screen, system log)
            err:         error (user log, screen, system log)
            sqlerr:      sqlerror (all logs)
            info:        info message (screen)
            fatal:       you are so screwed...
            mayaerr:     maya error
             
         SCOPE
         
             Determines who should see the message
             
             norm:   user logs only
             grp:    group logs (not yet implemented)
             sys:    larger scope (system)
    """
    def __init__(self, msg='', sev='out', scope='norm', write=False):
        if not msg:
            global user
            msg = 'they\'re coming to get you, %s' % user.capitalize()
        

        self.createLogs() 
        # return function names to pass to errors
        current_function = inspect.stack()[0][3]
        caller_module = inspect.stack()[1][1]
        caller_method = inspect.stack()[1][3] 
        
        self.__levels__ = ['out', 'sys', 'db', 'warn', 'err', 'sqlerr', 'info', 'fatal']
        self.__scopes__ = ['norm', 'grp', 'sys']
        self.message = msg
        self.date = returnDateTime()
        self.user = returnUsername()
        self.shortdate = returnDateTime()
        self.usr_log = usr_log
        self.sys_log = sys_log # system log
        self.prefsfile = prefsfile    

        # printMsg - output for the script editor
        printMsg = ''
        
        # outputMsg - output for the log file
        outputMsg = ''
        
        # define a list to be passed to the write statement
        logFiles = []
        
        # a scope of 'sys' will add it to the system logs
        outputLogFiles = []
        if scope == 'sys':
            outputLogFiles = [sys_log,]

        if sev is 'info':
            prefix = self.formatMessagePrefix('[AM INFO]')
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            
        if sev is 'out':
            prefix = self.formatMessagePrefix('[AM OUTPUT]')
            logFiles = [usr_log,]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
            file = open(usr_log, 'a')
        
        if sev is 'sys':
            write = True # might want to remove this one
            prefix = self.formatMessagePrefix('[AM SYSTEM]')
            logFiles = [usr_log,]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
            
        if sev is 'db':
            try:
                if os.environ['AM_DEBUG'] == 'On':
                    prefix = self.formatMessagePrefix('[AM DEBUG]')
                    logFiles = [usr_db,]
                    printMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
                    outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
                else:
                    pass
            except:
                pass

        
        if sev is 'warn':
            prefix = self.formatMessagePrefix('[AM WARNING]')
            logFiles = [usr_log,]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
            
        if sev is 'err':
            write = True
            scope = 'sys'
            prefix = self.formatMessagePrefix('[AM ERROR]')
            logFiles = [usr_log, usr_error]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
        
        if sev is 'mayaerr':
            write = True
            scope = 'sys'
            prefix = self.formatMessagePrefix('[MAYA ERROR]')
            logFiles = [usr_log, usr_error]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
        
        if sev is 'sqlerr':
            write = True
            scope = 'sys'
            prefix = self.formatMessagePrefix('[SQL ERROR]')
            logFiles = [usr_log, usr_error]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)

        if sev is 'fatal':
            write = True
            scope = 'sys'
            prefix = self.formatMessagePrefix('[AM FATAL]')
            logFiles = [usr_log, usr_error]
            printMsg =  (prefix + ' %s: %s') % (self.shortdate, msg)
            outputMsg =  (prefix + ' %s: %s (%s)') % (self.date, msg, self.user)
            
        newList = []
        msgList = [outputMsg,]
        
        if logFiles:
            for logFile in logFiles:
                outputLogFiles.append(logFile)
        
        if write:
            if outputLogFiles:
                self.writeToLogs(msgList, outputLogFiles)

        # print the output to the screen
        if printMsg:
            print printMsg
           
        
    def createLogs(self, logfile=''):
        """ creates log files if they are not already created"""
        # if no log file is specified, check and create them all
        global allLogs
        if not logfile:
            logfiles = allLogs
        else:
            logfiles = [logfile,]
            
        for log in logfiles:
            if not os.path.exists(log):
                date = returnDateTime()
                header = ''
                if log is usr_log or usr_error or usr_db:
                    header = ['# assetManager user log file\n', ('# created ' + date +'\n'), '# storage for output and error messages\n\n']
                if log is sys_log or sys_error:
                    header = ['# assetManager system log file\n', ('# created ' + date +'\n'), '# storage for system-wide output and error messages\n\n']
                
                print('[SYSTEM]: creating assetManager temp file: \"' + log + '\"')
                file = open(log , 'w')
                file.writelines(header)
        
    def writeToLogs(self, msgList, logfiles=[]):
        """ write a message to the logfiles in question"""
        # format the message as a single-object list if not already a list
        if type(msgList) is not list:
            msgList = [msgList,]            
        
        newList = []
        # if the user doesn't pass a log file list, assume that it's meant to go to ALL log files
        if not logfiles:
            logfiles = allLogs
            
        for logfile in logfiles:
            # create the logfile, if it's not already there
            if not pp.exists(logfile):
                createLogs(logfile)
            #print '[AM DEBUG]  : writing to log file...'
            file = open(logfile, 'a')
            for msg in msgList:
                newList.append(msg + '\n')
                
            file.writelines(newList)
            file.close()
                
    def clear(self, logfile):
        ''' clears the selected log file'''
        if pp.exists(logfile):
            file = open(logfile, 'a')
            file.close()
    
    def formatMessagePrefix(self, prefixIn, max=13):
        """ adds empty space to properly format output messages
            right now, the max is defined at 13 (the size of '[AM WARNING]' + 1)"""
        spacerLen = '%02d' % (max - len(prefixIn))
        spacer = ''
        if spacerLen != '00':    
            spacer = ('%' + spacerLen + 's') % ' '
            
        prefixOut = (prefixIn + spacer + ':')
        return prefixOut
            
class UserPrefs(object):
    """ this class manages assetmanager preferences (stored in: /usr/.am/am_usr_prefs.py)"""
    def __init__(self, log=prefsfile):
        global prefsfile, envStr
    
    def createPrefs(self, studioEnv=''):
        ''' returns the preferences file for assetmanager. If none exists, it will create one'''
        
        if os.path.exists(prefsfile):
            file = open(prefsfile , 'r')
        
        else:
            date = returnDateTime()
            if not studioEnv:
                fileList = ['# assetManager preferences\n', ('# created ' + date +'\n'), ('# ENV:%s\n' % envStr)]
            else:
                fileList = ['# assetManager preferences\n', ('# created ' + date +'\n'), ('# ENV:%s\n' % studioEnv)]
                
            print('[SYSTEM]: creating assetManager preferences file: \"' + prefsfile + '\"')
            file = open(prefsfile , 'w')
            file.writelines(fileList)
            
        file.close()
        return prefsfile
    
    # TODO: this is a prefs class...this method belongs in Output class!!
    def createLogs(self, logfiles=''):
        global allLogs
        if not logfiles:
            logfiles =  allLogs 
        
        for logfile in logfiles:
            if not pp.exists(logfile):
                outmsg = Output(('log file "%s" doesn\'t exist, creating...' % logfile), sev = 'sys')
                file = open(logfile , 'w')
                file.writelines(fileList)
                
    # TODO: same as above, doesn't this belong in Output?    
    def append(self, msg, log=prefsfile):
        msgList = [msg,] 
        for m in msgList:
            newList.append(m + '\n')
        file.writelines(newList)
        file.close()
    
    # TODO: this is just copied from output.py - revise it
    def updatePrefsFile(self):
        """ manages user pref files.
            This is pretty self-contained, it just reads enVars from the string, grabs their values and writes the file
        """
        global prefsfile, envStr
        file = open(prefsfile , 'r')
        lines = file.readlines()
        output = []
        for line in lines:
            if '#' in line:
                output.append(line)
    
            if 'ENV:' in line:
                val = line.split(':')
                varList = val[1].split(',')
                
                varList = ([x.strip() for x in varList])
                for var in varList:
                    try:
                        cmd = ('os.environ[\'%s\']' % var)                
                        val = eval(cmd)
                    except KeyError, SyntaxError:
                        val = ''
                        
                    #print 'val: %s' % val
                    if val and val != '(all)' and val != 'Root':
                        cmd2 =  ('os.environ[\'%s\'] = \'%s\'\n' % (var, val))
                        output.append(cmd2)
        file.close()
        file = open(prefsfile , 'w')
        file.writelines(output)
            
        file.close()
    
    def envVars(self):
        """ manages assetmanager's environment variables """
        pass
    
    def checkFiles(self):
        """ checks all of the files needed by assetmanager to run"""
        pass    

class Catch(object):
    """
    Class: Catch()
    
    DESCRIPTION
        Catches and formats errors a little more nicely

    USAGE
        Call this after an 'except' statement, ex:
        
            try:
                <------>
            except Exception, err:
                Catch(err)
            
    """
    def __init__(self, err):
        pass
        
        
        
        
        
if __name__ == '__main__':
    print 'this is a test'