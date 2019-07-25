#!c:\python25\python -u


# WARNING: WHEN INSTALLING THIS CGI SCRIPT ON A SYSTEM THE
# LINE INDICATING THE PYTHON LOCATION ABOVE ALMOST ALWAYS
# NEEDS TO BE CHANGED.

"""
CGI script for constructing letter representations for preformatted text.
"""

import cgitb; cgitb.enable()

import sys
import cgi
from skimpyGimpy import skimpyGimpy

data = cgi.FieldStorage()

#raise "test error"

print "content-type: text/html"
print

points = None

print skimpyGimpy.makePage("interpolate.cgi", points, "true", cgidata=data)


