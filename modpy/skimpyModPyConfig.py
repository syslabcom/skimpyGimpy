
"""
common configuration parameters for modpy skimpyGimpy tests and demos
"""

import os
import skimpyGimpy.httpTempFile, skimpyGimpy.skimpyAPI

SKIMPY_SOURCE_DIRECTORY = "/skimpyGimpy_1_2"
SKIMPY_SOURCE_DIRECTORY = "/home/awatters/webapps/mod_python/htdocs/skimpyGimpy"

# For WAVE generation, we need to know where the
# ZIP file containing the wave samples lives.
PATH_TO_WAVE_SAMPLES_ZIP = os.path.join(SKIMPY_SOURCE_DIRECTORY, "wave/waveIndex.zip")

# For WAVE and PNG files it is safest to store them as files
# and serve the files from web visible directories.  In this case
# we use a temporary directory which we clear of old files
# automatically.

# the file system path to the http visible temp directory
PATH_TO_TEMP_DIRECTORY = "./skimpyTemp"
PATH_TO_TEMP_DIRECTORY = "/home/awatters/webapps/mod_python/htdocs/skimpyGimpy/skimpyTemp"

# the relative http path to the http visible temp directory
HTTP_PATH_TO_TEMP_DIRECTORY = "../skimpyTemp"


class fakecgidata:
    def __init__(this, v):
        this.value = v
class fakecgiform:
    def __init__(this):
        this.D = {}
    def add(this, name, v):
        this.D[name] = fakecgidata(v)
    def __getitem__(this, name):
        return this.D[name]

def getPaths(extension):
    return skimpyGimpy.httpTempFile.getPathAndRemoveOldFiles(
        PATH_TO_TEMP_DIRECTORY, HTTP_PATH_TO_TEMP_DIRECTORY,
        prefix="temp", suffix=extension)

def getWavePaths():
    return getPaths(".wav")

def getPNGPaths():
    return getPaths(".png")

def makeWaveAndRedirect(word):
    """
    Because wave file generation is expensive, we use a redirect
    to implement waves, just in case the wave file is not actually
    needed.  This implements the cgi functionality for the file
    generation and redirect.
    """
    # this uses a javascript redirect to permit relative paths
    (fpath, hpath) = getWavePaths()
    skimpyGimpy.skimpyAPI.Wave(word, PATH_TO_WAVE_SAMPLES_ZIP).data(fpath)
    Lines = []
    #Lines.append("Location: http://%s" % hpath)
    Lines.append("Content-type: text/html")
    Lines.append("")
    Lines.append("")
    Lines.append('<a href="%s">redirecting to %s</a>' % (hpath, hpath))
    Lines.append('<script> location.href="%s"; </script>' % (hpath))
    return "\r\n".join(Lines)

