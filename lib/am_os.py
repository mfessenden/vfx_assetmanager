# am_os.py by Michael Fessenden (c) 2011
#
# v0.29
#
# Description :
# -------------
# This is the library that manages system functions. It logs directory and file creation/modification
#
#
# Version History :
# -----------------
# v0.29:
# - decprecated; replaced by lib/output
# v0.25:
# - changed listFiles function to use glob to match a file extension regEx
# - added the system error log functions (create and append)
# v0.16:
# - initial release
#
# TODO List :
# - make sure that the returns on the log creation functions are of the right type...sanity check at some point
# - we might want to make listFiles look for a more strict file naming convention (ie: 'model_mouse.m*')
# -----------
# 
# ----------------------------------------------------------------------------


import os, sys
import re
import posixpath as pp
import datetime
from time import strftime
import glob

sys.setrecursionlimit(1500)

global app
app = sys.executable.split('\\')[len(sys.executable.split('\\'))-1]

__version__ = '0.29'
__lastupdate__ = 'Aug 11, 2011'
__amlib__ = 'am_os'


usr_logs = os.environ['AM2_USER_LOGS']
sys_logs = os.environ['AM2_SYSTEM_LOGS']

global usr_output_log
global sys_error_log
global usr_nuke_log

usr_output_log = pp.join(usr_logs, 'am_output.txt')
sys_error_log = pp.join(usr_logs, 'am_errorLog.txt')
usr_nuke_log = pp.join(usr_logs, 'am_nuke.txt')

# create and return the output file
def createUserOutputLog():
    userPrefFile = usr_logs + '/am_output.txt'
    if os.path.exists(userPrefFile):
        file = open(userPrefFile , 'r')
    
    else:
        date = returnDateTime()
        fileList = ['# assetManager output log\n', ('# created ' + date +'\n'), '# output file for all assetManager messages\n\n']
        print('[SYSTEM]: creating assetManager output file: \"' + userPrefFile + '\"')
        file = open(userPrefFile , 'w')
        file.writelines(fileList)
        
    file.close()
    return userPrefFile

# create and return the error log
def createSystemErrorLog():
    userErrorLog = sys_logs + '/am_errorLog.txt'
    if os.path.exists(userErrorLog):
        file = open(userErrorLog , 'r')
    
    else:
        date = returnDateTime()
        fileList = ['# assetManager system error log\n', ('# created ' + date +'\n'), '# error log for all assetManager python errors\n\n']
        print('creating assetManager system error log: \"' + userErrorLog + '\"')
        file = open(userErrorLog , 'w')
        file.writelines(fileList)
        
    file.close()
    return userErrorLog

# create and return the error log
def createUserErrorLog():
    userErrorLog = usr_logs + '/am_errorLog.txt'
    if os.path.exists(userErrorLog):
        file = open(userErrorLog , 'r')
    
    else:
        date = returnDateTime()
        fileList = ['# assetManager user error log\n', ('# created ' + date +'\n'), '# error log for all assetManager python errors\n\n']
        print('creating assetManager user error log: \"' + userErrorLog + '\"')
        file = open(userErrorLog , 'w')
        file.writelines(fileList)
        
    file.close()
    return userErrorLog

# create and return the error log
def createNukeTemp():
    nukeTemp = usr_logs + '/am_nuke.txt'
    if os.path.exists(nukeTemp):
        file = open(nukeTemp , 'r')
    
    else:
        date = returnDateTime()
        fileList = ['# assetManager Nuke temp file\n', ('# created ' + date +'\n'), '# storage for Nuke session variables\n\n']
        print('creating assetManager Nuke temp file: \"' + nukeTemp + '\"')
        file = open(nukeTemp , 'w')
        file.writelines(fileList)
        
    file.close()
    return nukeTemp

# TODO: make these three append functions one
def appendToUserOutputFile(msg):
    ''' this appends the current data to the user output file - the one that assetManager reads for the output tab'''
    newList = []
    msg = [msg,]
    for m in msg:
        newList.append(m + '\n')        
    userPrefFile = createUserOutputLog()
    file = open(userPrefFile, 'a')
    file.writelines(newList)
    file.close()

def appendToUserErrorLog(msg):
    ''' this appends the current data to the user error log'''
    newList = []
    msg = [msg,]
    for m in msg:
        newList.append(m + '\n')   
    userErrorLog = createUserErrorLog()
    file = open(userErrorLog, 'a')
    file.writelines(newList)
    file.close()
    
def appendToSystemErrorLog(msg):
    ''' this appends the current data to the system error log'''
    newList = []
    msg = [msg,]
    for m in msg:
        newList.append(m + '\n')   
    sysErrorLog = createSystemErrorLog()
    file = open(sysErrorLog, 'a')
    file.writelines(newList)
    file.close()
    
def appendToNukeTemp(msg):
    ''' this appends the current data to the user Nuke temp file'''
    newList = []
    msg = [msg,]
    for m in msg:
        newList.append(m + '\n')   
    nukeLog = createNukeTemp()
    file = open(nukeLog, 'a')
    file.writelines(newList)
    file.close()


# returns the username of the currently logged in user
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

# this function formats the passed argument as a debug message
def dprint(msg):
    msg = str(msg)
    global app
    if app.startswith('maya'):
        import maya.cmds as mc
        if mc.optionVar( exists='am2_db_debug' ):
            if mc.optionVar(q='am2_db_debug'):
                print ('DEBUG: %s ') % msg

# this function formats the passed argument as an error message and writes it to the user & error log
# TODO: add these log creation scripts to the __init__ file
def eprint(msg):
    msg = str(msg)
    date = returnDateTime()
    user = returnUsername()
    userErrorLog = createUserErrorLog()
    sysErrorLog = createSystemErrorLog()
    sysError =  ('[ERROR]: %s: %s (%s)') % (date, msg, user)
    usrError =  ('[ERROR]: %s: %s') % (date, msg)
    print '[ERROR]: %s' % msg
    appendToUserErrorLog(usrError)
    appendToSystemErrorLog(sysError)
    
def outprint(msg):
    msg = str(msg)
    date = returnDateTime()
    user = returnUsername()
    outputLog = createUserOutputLog()
    outputMsg =  ('[OUTPUT]: %s: %s (%s)') % (date, msg, user)
    appendToUserOutputFile(outputMsg)
    print ('[assetManager]: %s ') % msg
    
def sprint(msg):
    msg = str(msg)
    shrtDate = returnDateTime('short')
    
    # depending on the type of message, format the output differently
    if not msg.startswith('\n'):
        logMsg = (('[SYSTEM]: %s %s ') % (shrtDate, msg))
        screenMsg = ('[SYSTEM]: %s ' %  msg)
    else:
        msg = re.sub(r'\n', '', msg)
        screenMsg = ('\n# ' + msg.title())
        logMsg = screenMsg
         
    appendToUserOutputFile(logMsg)
    global app
    if app.startswith('maya'):
        import maya.cmds as mc
        if mc.optionVar( exists='am2_db_system' ):
            if mc.optionVar(q='am2_db_system'):            
                print screenMsg
                
sprint('initializing assetManager common OS library')




for directory in [usr_logs,sys_logs]:
    if os.path.exists(directory):
        sprint('reading directory: %s' % directory)
    else:
        os.mkdir(directory)




# SYSTEM PROCS
def createDirectory(dir):
    sprint('creating directory: ' + dir)
    os.mkdir(dir)
    
# return a list of files from the given path
def listFiles(filepath, filetype):
    sprint('reading files from: %s' % filepath)
    resultFiles = []
    if pp.isdir(filepath):
        resultFiles = glob.glob1(filepath, filetype)
    else:
        eprint('the directory specified "%s" does not exist' % filepath)
    return resultFiles
    
#===============================================================================
# myPath = 'Z:/projects/mario/assets/actor/mario/model/ref'
# mayaFiles = glob.glob1(myPath,'*.m*')
# print mayaFiles
#===============================================================================
def listFolders(path, fullpath=0):
    ''''returns a list of folder names in the given directory'''
    files = []
    try:
        files = os.listdir(path)
    except WindowsError:
        eprint('cannot find results in path %s' % path)
    folders = []
    if files:
        for file in files:
            if pp.isdir(pp.join(path, file)):
                folders.append(file)
        return folders
    else:
        return 0
        
    
# TODO: clean this shit up
def createFolder(path):
    sprint('creating directory: ' + path + '\n')
    os.mkdir(path)
    
    
# returns the Windows PATH
def returnWindowsPath():
    '''Returns the Windows PATH environment variable'''
    path = os.environ['PATH']
    list = path.split(";")

    return list
    
# returns the Users' Home directory
def returnUserHome():
    '''Returns the Users' HOME directory'''
    home = os.environ['HOME']

    return home

# returns the username of the currently logged in user
def returnUsername():
    if sys.platform == "win32":
        cmd="USERNAME"
    elif sys.platform == "linux2":
        cmd="USER"
        
    user = os.getenv(cmd)
    return user

def returnLoadedModules():
    result = ['LOADED MODULES:\n\n']
    for k, v in sys.modules.items():
        try:
            if (v.__amlib__):
                v = str(v)
                val = v.rsplit('\'')
                ver = (v.__version__)
                val[3] = val[3].replace('\\', '/')
                #for e in list((val[1], val[3], ('-'*60))):
                result.append(''.join(list(((val[1]+'(v'+ver+')\n'), (val[3]+'\n'), ('-'*61+'\n')))))
            resultStr = ''.join(sorted(result))
            return resultStr
        except AttributeError:
            pass

class DebugObj:
    ''' this creates a debug object'''
    def __init__(self):
        pass




#===============================================================================
# import sys, os, os.path
# import re
# filepath = 'Z:/projects/mario/shots/mario001/maya/light/work/michael/images'
# pattern = 'mario001_lgt_v001'
# 
# fileList = os.listdir(filepath)
# 
# for file in sorted(fileList):
#    if os.path.isfile(os.path.join(filepath,file)):
#        suff, ext = os.path.splitext(file)
#        basename = re.sub(r'\.[0-9]+$', '', suff)
#        print suff
#===============================================================================
