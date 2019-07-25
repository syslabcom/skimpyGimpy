"""
This modPython program provides a straightforward interface for examining
the CAPTCHA representations for an input word in text, PNG or Wave format.
"""

import sys
p = "/home/awatters/webapps/mod_python/htdocs/skimpyGimpy"
if p not in sys.path:
	sys.path.insert(0,p)
	
import  urllib
from skimpyGimpy import skimpyAPI, skimpyGimpy
import skimpyModPyConfig

template = """
<html>
<head>
<title>skimpyGimpy test page</title>
</head>
<body>
<center>
<h1>skimpyGimpy test page</h1>
<br>
<table width="60%(pct)s">
<tr><td>
This ModPy program provides a straightforward interface for examining
the CAPTCHA representations for an input word in text, PNG or Wave format
using the <a href="http://skimpygimpy.sourceforge.net">skimpyGimpy</a>
CAPTCHA generators.
</td></tr>
</table>
<br><br>
<b>Below is the preformatted text skimpy for %(s)s</b>
<br>
%(skimpy)s
<br>
Image version: <img src="%(img)s">
<br>
<br><br>
<a href="go?wave=%(s0)s">spell %(s)s in audio</a>
<br>
<br><br>
<form action="go">
Next word: <input name="s"> <input type="submit" value="make captcha">
</form>
</center>
</body>
</html>
"""


def go(req, s="example", wave=None, **others):
        if wave is not None:
                # redirect to wave file if wave is requested
                return skimpyModPyConfig.makeWaveAndRedirect(wave)
	s = skimpyGimpy.clean(s)
	if not s:
		s = " "
	D = {}
        color = "ff0000"
        prescale = 1
        pngscale = 2.2
        speckle = 0.1
        word = s
        # present the word as PNG and preformatted text and offer a link to a wave representation.
        (fpath, hpath) = skimpyModPyConfig.getPNGPaths()
        skimpyAPI.Png(word, speckle=speckle, scale=pngscale, color=color).data(fpath)
        D = {}
        D["pct"] = "%"
        D["skimpy"] = skimpyAPI.Pre(word, speckle=speckle, scale=prescale, color=color).data()
        D["img"] = hpath
        D["s"] = repr(s)
        D["s0"] = urllib.quote(s)
	return template % D

if __name__=="__main__":
        print go(None)
