
"""
This is the primary unified interface for generating
WAVE, PNG or HTML formatted Captcha strings using SkimpyGimpy
from a python program.
"""

#import waveTools
#import bdf
#import skimpyGimpy
import sys

class Wave:
    def __init__(this, word, indexFile):
        "prepare to generate a wave representation for a word."
        this.word = word.lower()
        this.indexFile = indexFile
    def data(this, toFilePath=None):
        "return the wave representation for the word, write it to the path if provided"
        import waveTools
        index = waveTools.LettersIndex()
        index.loadZip(this.indexFile)
        instring = this.word.lower()
        m = waveTools.Mixer(instring, index)
        m.doProcess()
        samples = waveTools.fit(m.mix, waveTools.MIN8, waveTools.MAX8)
        result = waveTools.samplesToString(samples, sampwidth=1)
        if toFilePath is not None:
            f = open(toFilePath, "wb")
            f.write(result)
            f.close()
        return result

def hexColorTupleFromString(s):
    if s.startswith("0x"):
        s = s[2:]
    if len(s)!=6:
        raise ValueError, "hex color specifications must have 6 hex digits: "+repr(s)
    d1 = s[0:2]
    d2 = s[2:4]
    d3 = s[4:6]
    t = ( int(x,16) for x in (d1,d2,d3) )
    return tuple(t)

class Png:
    scale = 2.0 # size of letters
    speckle = 0.3 # amount of "noise" to add
    color = "0f11af" # color for letter interiors (background is transparent)
    fontpath = None # location of BDF format font file to use
    def __init__(this, word, speckle=None, scale=None, color=None, fontpath=None):
        "prepare to generate a Png representation for a word."
        this.word = word
        if speckle is not None:
            this.speckle = float(speckle)
        if scale is not None:
            this.scale = float(scale)
        if color is not None:
            this.color = color
        if fontpath is not None:
            this.fontpath = fontpath
        this.hcolor = hexColorTupleFromString(this.color)
    def data(this, toFilePath=None):
        import bdf
        "return the PNG representation for the word, write it to the path if provided"
        if this.fontpath is not None:
            fn = bdf.font()
            fn.loadFilePath(this.fontpath)
        else:
            import cursive # this is an expensive import
            fn = cursive.CursiveFont
        p = bdf.pixelation(fn, this.word)
        #pr "hcolor is", this.hcolor
        result = p.toPNG(toFilePath, color=this.hcolor, scale=this.scale, speckle=this.speckle)
        return result

class Pre:
    scale = 0.7 # size of letters
    speckle = 0.1 # amount of "noise" to add
    color = "0f11af" # color for letter interiors
    def __init__(this, word, scale=None, speckle=None, color=None):
        this.word = word.lower()
        if speckle is not None:
            this.speckle = float(speckle)
        if scale is not None:
            this.scale = float(scale)
        if color is not None:
            this.color = color
            
    def data(this, toFilePath=None):
        import skimpyGimpy
        g = skimpyGimpy.gimpyString(this.word)
        g.scale = this.scale
        g.speckleFactor = this.speckle
        g.color = this.color
        result = g.formatAll()
        if toFilePath is not None:
            f = open(toFilePath, "w")
            f.write(result)
            f.close()
        return result

USAGE = """
USAGE
=====
This program generates a WAVE, PNG or HTML Captcha for a word.

There are three command lines depending on the output format.

    skimpy.py --pre [ --filename OUTPUTFILENAME | --stdout ]
       [ --speckle NUMBER ] [ --scale NUMBER ] [ --color HEX6DIGITS ] WORD
    skimpy.py --png [ --filename OUTPUTFILENAME | --stdout ]
       [ --speckle NUMBER ] [ --scale NUMBER ] [ --color HEX6DIGITS ]
       [ --fontpath BDFFILE ] WORD
    skimpy.py --wave [ --filename OUTPUTFILENAME | --stdout ]
      [ --indexfile PATH_TO_WAVE_SAMPLE_INDEX_FILE ] WORD

--filename OUTPUTFILENAME determines output file to recieve the file content.
--stdout specifies that the content should be written to the standard output.

One or both of --filename and --stdout are required for all command line
variants.

--speckle NUMBER determines the ratio of noise pixels added to the
  captcha (like 0.2).
--scale NUMBER determines the font scale (like 2.1).
--color HEX6DIGITS determines the RGB color value (like 7effa1).
--fontpath BDFFILE specifies the location of a BDF font file to use for
  the PNG image.
--indexfile PATH_TO_WAVE_SAMPLE_INDEX_FILE specifies the location of the
  waveIndex.zip sample file.

"""

waveExample = r"""
skimpyAPI.py --wave testword --filename test.wav --indexfile C:\tmp\skimpyGimpy_1_2\wave\waveIndex.zip
"""
preExample = r"""
skimpyAPI.py --pre testword --filename test.html --scale 1.1 --speckle 0.11 --color a01ee1 --stdout
"""
pngExample = r"""
skimpyAPI.py --png testword --filename test.png --fontpath C:\tmp\skimpyGimpy_1_2\fonts\mlmfonts\monoell.bdf --scale 1.1 --speckle 0.11 --color a01ee1
"""

def getword(args):
    if len(args)>1:
        raise ValueError, "some arguments not understood "+repr(args)
    if len(args)<1:
        raise ValueError, "no word found"
    return args[0]

def run(args):
    cargs = list(args)
    from getparm import getparm
    done = False
    try:
        isPre = getparm(args, "--pre", False, False)
        isPng = getparm(args, "--png", False, False)
        isWave = getparm(args, "--wave", False, False)
        fileName = getparm(args, "--filename")
        stdout = getparm(args, "--stdout", False, False)
        if not fileName and not stdout:
            raise ValueError, "must specify --filename OUTFILE or --stdout or both"
        if [isPre, isPng, isWave].count(True)!=1:
            raise ValueError, "must specify exactly one of --pre, --png, or --wave"
        if isPre:
            speckle = getparm(args, "--speckle")
            scale = getparm(args, "--scale")
            color = getparm(args, "--color")
            word = getword(args)
            generator = Pre(word, scale, speckle, color)
        if isPng:
            speckle = getparm(args, "--speckle")
            scale = getparm(args, "--scale")
            color = getparm(args, "--color")
            fontpath = getparm(args, "--fontpath")
            word = getword(args)
            generator = Png(word, speckle, scale, color, fontpath)
        if isWave:
            indexFile = getparm(args, "--indexfile")
            word = getword(args)
            if not indexFile:
                raise ValueError, "--indexfile FILENAME is required to generate WAVE files"
            generator = Wave(word, indexFile)
        result = generator.data(fileName)
        if stdout:
            sys.stdout.write(result)
        done = True
    finally:
        if not done:
            print "CAPTCHA generation failed for", cargs
            print
            print USAGE
            
if __name__=="__main__":
    run(sys.argv[1:])
        
