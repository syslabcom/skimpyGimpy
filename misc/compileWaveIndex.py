
"create a compressed index file"

indexfilename = "waveIndex.zip"

import waveTools

def go():
    index = waveTools.getIndex()
    index.dumpZip(indexfilename)

if __name__=="__main__":
    go()
    
