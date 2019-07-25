#!/usr/bin/env python

"""
Uniform command line interface to skimpyGimpy
CAPTCHA generation.

Execute the script with no parameters to see the usage string
(from skimpyAPI.USAGE).
"""

from skimpyGimpy import skimpyAPI
import sys
skimpyAPI.run(sys.argv[1:])

