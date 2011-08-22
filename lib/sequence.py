import os, sys, re
import posixpath as pp

# reRange = re.compile(r"([0-9]+)(?:-([0-9]*)(?:x([0-9]+))?)?$")

print '[AM2]: loading sequence libraries'

class Sequence(object):
    '''defines a sequence of files'''

    def __init__(self, path, pattern=''):
        self.filetype = ''
        self.startframe = ''
        self.endframe = ''
        #self.padding = 0
        fileList = os.listdir(path)
        iter = 0
        for file in sorted(fileList):
            if os.path.isfile(os.path.join(path,file)):
                suff, ext = os.path.splitext(file)
                self.basename = re.sub(r'\.[0-9]+$', '', suff)
                self.filetype = ext
                result = re.search(r'\.[0-9]+$', suff)
                fnum = re.sub('^\.', '', result.group(0))
                self.padding = len(fnum)
                
                if iter == 0:
                    self.startframe = int(fnum)
                    
                iter = iter+1
                    
                


    
    
    