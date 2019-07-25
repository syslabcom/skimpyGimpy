"setup program for xsdbxml"
from distutils.core import setup
import sys

setup(name="skimpyGimpy",
      version="1.2",
      description="xtremely simple XML data base format",
      author="Aaron Watters",
      author_email="aaronwmail-sourceforge@yahoo.com",
      url="http://skimpygimpy.sourceforge.net/",
      packages=['skimpyGimpy', 'skimpyGimpy.erd', 'skimpyGimpy.railroad'],
      scripts = [
          "scripts/skimpy.py",
          ],
     )
    
