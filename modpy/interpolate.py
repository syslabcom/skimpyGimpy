

"""
ModPy program for constructing letter representations for preformatted text.
"""

import sys
p = "/home/awatters/webapps/mod_python/htdocs/skimpyGimpy"
if p not in sys.path:
	sys.path.insert(0,p)

import skimpyModPyConfig
from skimpyGimpy import skimpyGimpy
        
def go(req, points="", **others):
    cgidata = skimpyModPyConfig.fakecgiform()
    cgidata.add("points", points)
    return skimpyGimpy.makePage("go", None, "true", cgidata=cgidata)

if __name__=="__main__":
    print(go(""))
