"example of skimpyAPI usage"

# import the API interface module
from skimpyGimpy import skimpyAPI

# this is the text we want to encode
WORD = "example text"

#HTML GENERATION:
# these are the parameters we want to use
# for preformatted text
HTMLSPECKLE = 0.1
HTMLSCALE = 0.7
HTMLCOLOR = "001199"
HTMLFILE = "pre/WORD.html"

# create an HTML generator
htmlGenerator = skimpyAPI.Pre(WORD,
                              speckle=HTMLSPECKLE, # optional
                              scale=HTMLSCALE, # optional
                              color=HTMLCOLOR, # optional
                              )
# store the preformatted text as htmlText
htmlText = htmlGenerator.data()

# store the preformatted text as htmlText
# and also write text to file
htmlText = htmlGenerator.data(HTMLFILE)

#PNG GENERATION:
# these are the parameters we want to use
# for PNG image output
PNGSPECKLE = 0.11
PNGSCALE = 2.1
PNGCOLOR = "00EEAA"
PNGFONTPATH = "../fonts/radon-wide.bdf"
PNGFILE = "png/WORD.png"

# create an PNG generator
pngGenerator = skimpyAPI.Png(WORD,
                              speckle=PNGSPECKLE, # optional
                              scale=PNGSCALE, # optional
                              color=PNGCOLOR, # optional
                              fontpath=PNGFONTPATH # optional
                              )

# store the PNG data as pngText
pngText = pngGenerator.data()

# store the PNG data as pngText
# and also write PNG to file
pngGenerator.data(PNGFILE)

#WAVE GENERATION:
# these are the parameters we want to use
# for WAVE audio output
INDEXFILEPATH = "../wave/waveIndex.zip"
WAVEFILE = "wave/WORD.wav"

# create a wave generator
waveGenerator = skimpyAPI.Wave(WORD,
                              indexFile=INDEXFILEPATH # required!
                              )
# generate the wave data as waveText
waveText = waveGenerator.data()

# generate the wave data as waveText
# and also save to file
waveText = waveGenerator.data(WAVEFILE)
