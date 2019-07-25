
"""
Replace line endings with Unix style line endings so the CGI files
will work under Unix systems, like Linux, etc.
"""

import glob, os
cgifilenames = glob.glob("*.cgi")
for fn in cgifilenames:
    lines = file(fn).readlines()
    outfilename = fn+".temp"
    outfile = file(outfilename, "wb")
    for line in lines:
        outfile.write(line)
    outfile.close()
    print "copied ", (fn, outfilename), " using newline only line endings"
    print "unlinking", fn
    os.unlink(fn)
    print "moving", (outfilename, fn)
    os.rename(outfilename, fn)
