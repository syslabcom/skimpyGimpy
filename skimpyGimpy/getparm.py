

def getparm(L, name, default=None, getValue=True):
    "get a parameter fromt the command line L --this or --name value"
    v = default
    if name in L:
        i = L.index(name)
        v = True
        if getValue:
            try:
                v = L[i+1]
            except IndexError:
                raise ValueError, "parameter %s requires a value" % repr(name)
            del L[i+1]
        del L[i]
    return v

usage = """
To place a png representing "text" into outfile.png:

% python getparm.py --path [directory containing bdf.py] --png outfile.png text

The directory should also contain cursive.bdf
  
"""

def run():
    import sys, os
    args = sys.argv
    path = getparm(args, "--path")
    if path:
        sys.path.insert(0, path)
    else:
        print usage
        raise ValueError, "--path [directory containing bdf.py] missing"
    import bdf
    png = getparm(args, "--png")
    if not png:
        print usage
        raise ValueError, "--png outfile.png missing"
    try:
        s = args[1]
    except:
        print usage
        raise ValueError, "text missing"
    fn = bdf.font()
    fontpath = os.path.join(path, "cursive.bdf")
    fn.loadFilePath(fontpath)
    p = bdf.pixelation(fn, s)
    p.toPNG(png)

if __name__=="__main__":
    run()
