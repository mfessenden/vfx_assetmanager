# openexr.py by Michael Fessenden (c) 2011
#
# v0.34
#
# Description :
# -------------
# This module deals with OpenEXR files and examining their contents
#
#
# Version History :
# -----------------
#
# v0.34:
# - development version
#
# TODO List :
# -----------
# - 
# ----------------------------------------------------------------------------

try:
    import OpenEXR
except:
    pass
import Imath
#import Image
import sys

__version__ = '0.34'
__lastupdate__ = 'Dec 08 2011'
__repr__ = 'assetmanager.lib.openexr'
__amlib__ = 'openexr'
namespace = __name__
__status__ = 'development'

def main(exrfile, jpgfile):
    file = OpenEXR.InputFile(exrfile)
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    rgbf = [Image.fromstring("F", size, file.channel(c, pt)) for c in "RGB"]

    extrema = [im.getextrema() for im in rgbf]
    darkest = min([lo for (lo,hi) in extrema])
    lighest = max([hi for (lo,hi) in extrema])
    scale = 255 / (lighest - darkest)
    def normalize_0_255(v):
        return (v * scale) + darkest
    rgb8 = [im.point(normalize_0_255).convert("L") for im in rgbf]
    Image.merge("RGB", rgb8).save(jpgfile)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: exr2jpg <exrfile> <jpgfile>"
    main(sys.argv[1], sys.argv[2])
    

#channels = OpenEXR.InputFile('file.exr').header('channels')

def returnEXRChannels(img):
    rgbChan = []
    xyChan = []
    channels = OpenEXR.InputFile(img).header('channels')
    for key, val in channels.iteritems():
        if key is 'channels':
            for k, v in val.iteritems():
                try:
                    chan, type = k.rsplit('.', 1)
                    if type is 'R' or 'G' or 'B':
                        rgbChan.append(chan)
                    if type is 'X' or 'Y' or 'Z':
                        xyChan.append(chan)
                except ValueError:
                    pass
                    
    rgbChan = list(set(rgbChan))
    xyChan = list(set(xyChan))
    return rgbChan, xyChan
    