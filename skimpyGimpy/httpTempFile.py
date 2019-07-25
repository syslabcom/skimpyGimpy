"""
create a temporary file in a directory.
Erase all "old" files in that directory of name matching prefix*time_countsuffix
automatically.  Return path to file and http link to the file.
"""

import os, time

def getPathAndRemoveOldFiles(directory, HTTPdirectory, prefix, suffix,
                             killAgeSeconds=60):
    # remove matching old files
    lprefix = len(prefix)
    lsuffix = len(suffix)
    now = time.time()
    filenames = os.listdir(directory)
    for filename in filenames:
        #pr "testing", filename
        if filename.startswith(prefix) and filename.endswith(suffix):
            filetimeS = filename[lprefix:-lsuffix]
            filetimeS = filetimeS.split("_")[0]
            #pr "fileTimeS", filetimeS
            try:
                filetime = float(filetimeS)
                #pr "filetime", filetime
                if now-filetime>killAgeSeconds:
                    #pr "removing", filename
                    filepath = os.path.join(directory, filename)
                    os.unlink(filepath)
                else:
                    #pr "too young", now-filetime
                    pass
            except: # "snip":
                #pr "error", filename
                pass
            else:
                #pr "done with", filename
                pass
        else:
            #pr "no match", (filename, prefix, suffix)
            pass
    done = False
    count = 0
    while not done:
        count += 1
        newFilename = "%s%s_%s%s" % (prefix, now, count, suffix)
        fileSystemPath = os.path.join(directory, newFilename)
        done = not os.path.exists(fileSystemPath)
    httpPath = "%s/%s" % (HTTPdirectory, newFilename)
    return (fileSystemPath, httpPath)

def storeAndRemoveOldFiles(content, directory, HTTPdirectory, prefix, suffix,
                             killAgeSeconds=60, mode="wb"):
    result = getPathAndRemoveOldFiles(directory, HTTPdirectory, prefix, suffix,
                             killAgeSeconds)
    (fileSystemPath, httpPath) = result
    f = file(fileSystemPath, mode)
    f.write(content)
    f.close()
    return result

def test():
    directory = "/tmp/test"
    HTTPdirectory = "/cgi-bin"
    prefix = "junk"
    suffix = ".txt"
    killAgeSeconds=3
    for i in range(20):
        print "test iteration", i
        content = "test content for "+repr(i)
        x = storeAndRemoveOldFiles(content, directory, HTTPdirectory, prefix, suffix,
                             killAgeSeconds)
        print "made", x
        allFileNames = os.listdir(directory)
        print "nfiles in %s: %s" % (directory, len(allFileNames))
        for fn in allFileNames:
            print "    ", fn
        print "sleeping 2"
        time.sleep(2)

if __name__=="__main__":
    test()

    
