#!C:\python25\python.exe -u

# WARNING: WHEN INSTALLING THIS CGI SCRIPT ON A SYSTEM THE
# LINE INDICATING THE PYTHON LOCATION ABOVE ALMOST ALWAYS
# NEEDS TO BE CHANGED.

"""
This CGI script provides a straightforward interface for examining
the CAPTCHA representations for an input word in text, PNG or Wave format.
"""

import cgitb; cgitb.enable()

import sys
import cgi, urllib
from skimpyGimpy import skimpyAPI, skimpyGimpy
import skimpyCGIconfig

# template for page result

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
This CGI script provides a straightforward interface for examining
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
<a href="skimpytest.cgi?wave=%(s0)s">spell %(s)s in audio</a>
<br>
<br><br>
<form action="skimpytest.cgi">
Next word: <input name="s"> <input type="submit" value="go">
</form>
</center>
</body>
</html>
"""

def go():
  data = cgi.FieldStorage()
  # if the request is for a wave file, send a redirect to a wave representation
  if data.has_key("wave"):
    # send wave file redirect
    word = data["wave"].value
    print skimpyCGIconfig.makeWaveAndRedirect(word)
    return
  # find or create a word to present
  s = "example"
  if data.has_key("s"):
    s = data["s"].value
  s = skimpyGimpy.clean(s)
  if not s:
    s = "example"
  color = "ff0000"
  prescale = 1
  pngscale = 2.2
  speckle = 0.1
  word = s
  # present the word as PNG and preformatted text and offer a link to a wave representation.
  (fpath, hpath) = skimpyCGIconfig.getPNGPaths()
  skimpyAPI.Png(word, speckle=speckle, scale=pngscale, color=color).data(fpath)
  D = {}
  D["pct"] = "%"
  D["skimpy"] = skimpyAPI.Pre(word, speckle=speckle, scale=prescale, color=color).data()
  D["img"] = hpath
  D["s"] = repr(s)
  D["s0"] = urllib.quote(s)
  print "content-type: text/html"
  print
  print template % D

if __name__=="__main__":
  go()