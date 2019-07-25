
"""
KISS indexed PNG.

following:
http://www.libpng.org/pub/png/spec/1.2/
"""

import zlib, math, random

PNGSIGNATURE = [137, 80, 78, 71, 13, 10, 26, 10]
PNGSIGSTRING = "".join( map(chr, PNGSIGNATURE))

NOFILTER = 0
SUBFILTER = 1
UPFILTER = 2
AVGFILTER = 3
PAETHFILTER = 4

PNGCRCTABLE = [0]*256
for n in range(256):
    c = n
    for k in range(8):
        if c&1:
            c = 0xedb88320L ^ (c >> 1)
        else:
            c = c >> 1
    PNGCRCTABLE[n] = c

def pngCRC(buf):
    c = 0xffffffffL
    for char in buf:
        bufn = ord(char)
        index = (c ^ bufn) & 0xff
        c = PNGCRCTABLE[index]^(c >> 8)
    return c ^ 0xffffffffL

def networkIntToString(integer, nbytes=4):
    #print hex(integer)
    i = integer
    L = []
    for j in xrange(nbytes):
        b = i&0xff
        i = i>>8
        #print hex(b), hex(i)
        L.append(b)
    if i and i!=-1:
        raise ValueError, "%s too large number %s for %s bytes" % (i, integer, nbytes)
    L.reverse()
    Cs = map(chr, L)
    return "".join(Cs)

def stringToNetworkInt(s):
    result = 0
    for c in s:
        result = result<<8
        result = result+ord(c)
    return result

class PNGdata:
    """
    basic structure for PNG data (most semantics elsewhere)
    """
    compresslevel = 2 # THE MAGIC NUMBER? xxxx
    def __init__(this):
        this.chunks = []
    def readString(this, s):
        siglen = len(PNGSIGSTRING)
        sig = s[0:siglen]
        if sig!=PNGSIGSTRING:
            raise ValueError, "bad sig "+repr(sig)
        index = siglen
        slen = len(s)
        while index<slen:
            (ch,index) = readChunk(s, index)
            this.addChunk(ch)
        #prt "nchunks", len(this.chunks)
    def addIHDR(this, width, height,
                 bitDepth=8, colorType=3,
                 compressionMethod=0, FilterMethod=0,
                 interlaceMethod=0):
        L = [
            networkIntToString(width, 4), 
            networkIntToString(height, 4), 
            chr(bitDepth),
            chr(colorType),
            chr(compressionMethod),
            chr(FilterMethod),
            chr(interlaceMethod),
            ]
        d = "".join(L)
        ch = Chunk("IHDR", d)
        this.addChunk(ch)
    def addPLTE(this, paletteSequence):
        if len(paletteSequence)<1:
            raise ValueError, "palette must have one entry"
        L = []
        #pr paletteSequence
        for (r,g,b) in paletteSequence:
            entry = chr(r)+chr(g)+chr(b)
            L.append(entry)
        d = "".join(L)
        ch = Chunk("PLTE", d)
        this.addChunk(ch)
    def addtRNS(this, index=0):
        "specify that palette index is fully transparent"
        ch = Chunk("tRNS", chr(index))
        this.addChunk(ch)
    def addIDAT(this, filteredAndCompressedData):
        ch = Chunk("IDAT", filteredAndCompressedData)
        this.addChunk(ch)
    def addFilteredData(this, filteredData):
        # XXX ???
        filteredAndCompressedData = zlib.compress(filteredData, this.compresslevel)
        this.addIDAT(filteredAndCompressedData)
    def addIEND(this):
        d = ""
        ch = Chunk("IEND", d)
        this.addChunk(ch)
    def addChunk(this, chunk):
        this.chunks.append(chunk)
    def OutputString(this):
        chunkStrings = [c.OutputString() for c in this.chunks]
        L = [PNGSIGSTRING]
        L.extend(chunkStrings)
        return "".join(L)

class IndexedImage:
    width = height = 0
    bitDepth = 8
    colorType = 3
    compressionMethod = 0
    FilterMethod = 0
    interlaceMethod = 0
    scanLines = None
    rawLines = None
    def __init__(this):
        pass
    def __repr__(this):
        return """IndexedImage(
        width=%s, height=%s, bitDepth=%s
        colorType=%s,
        compressionMethod=%s, interlaceMethod=%s
        )
        """ % (this.width, this.height, this.bitDepth, this.colorType,
               this.compressionMethod, this.interlaceMethod)
    def parseData(this, data):
        for c in data.chunks:
            typeCode = c.typeCode.upper()
            methodName = "parse"+typeCode
            method = getattr(this, methodName, None)
            if method is not None:
                method(c)
            else:
                print "warning: cannot parse "+typeCode
    def parseIHDR(this, chunk):
        data = chunk.data
        rem = data
        (widthS, rem) = (rem[:4], rem[4:])
        (heightS, rem) = (rem[:4], rem[4:])
        (bitDepthS, rem) = (rem[:1], rem[1:])
        (colorTypeS, rem) = (rem[:1], rem[1:])
        (compressionMethodS, rem) = (rem[:1], rem[1:])
        (filterMethodS, rem) = (rem[:1], rem[1:])
        (interlaceMethodS, rem) = (rem[:1], rem[1:])
        if rem:
            raise ValueError, "unknown remainder: "+repr(rem)
        this.width = stringToNetworkInt(widthS)
        this.height = stringToNetworkInt(heightS)
        this.bitDepth = ord(bitDepthS)
        this.colorType = ord(colorTypeS)
        this.compressionMethod = ord(compressionMethodS)
        this.filterMethod = ord(filterMethodS)
        this.interlaceMethod = ord(interlaceMethodS)
    def parseIDAT(this, chunk):
        data = chunk.data
        ddata = this.rawLines = zlib.decompress(data)
        width = this.width
        height = this.height
        bitDepth = this.bitDepth
        if bitDepth<=8:
            #bitDepth = 8
            bytesPerSample = 1
        elif bitDepth==16:
            bytesPerSample = 2
        else:
            raise ValueError, "can't handle bit depth %s" % bitDepth
        colorType = this.colorType
        # determine the scan line size
        if colorType==0:
            # grey scale
            samplesPerPixel = 1
        elif colorType==2:
            # rgb
            samplesPerPixel = 3
        elif colorType==3:
            # palette index
            samplesPerPixel = 1
        else:
            raise ValueError, "can't handle color type %s" % colorType
        bytesPerPixel = samplesPerPixel*bytesPerSample
        scanlinelength = 1 + bytesPerPixel * width
        #print "scan line length", scanlinelength
        size = len(ddata)
        expectedSize = scanlinelength*height
        if size!=expectedSize:
            raise ValueError, "expected size doesn't match size "+repr((size, expectedSize))
        rows = []
        for row in xrange(height):
            thisrow = []
            lstart = row*scanlinelength
            lend = lstart+scanlinelength
            rowdata = ddata[lstart:lend]
            filterchar = rowdata[0]
            filternum = ord(filterchar)
            #print "row", row, "filter is", filternum
            samplesdata = rowdata[1:]
            for col in xrange(width):
                pstart = col*bytesPerPixel
                pend = pstart+bytesPerPixel
                pdata = samplesdata[pstart:pend]
                if samplesPerPixel==1:
                    pixel = sample(pdata)
                elif samplesPerPixel==3:
                    s1 = sample(pdata[:bytesPerSample])
                    s2 = sample(pdata[bytesPerSample:-bytesPerSample])
                    s3 = sample(pdata[-bytesPerSample:])
                    pixel = (s1, s2, s3)
                else:
                    raise "can't handle samples per pixel: "+repr(samplesPerPixel)
                thisrow.append(pixel)
            #print thisrow
            rows.append(thisrow)


def sample(s):
    if len(s)==2:
        return ord(s[0])*256 + ord(s[1])
    else:
        return ord(s)

class Chunk:
    def __init__(this, typeCode, data, crc=None):
        this.typeCode = typeCode
        if len(typeCode)!=4:
            raise ValueError, "typecode must be 4 bytes: "+repr(typeCode)
        this.data = data
        this.length = len(data)
        this.crc = crc
    def OutputString(this):
        payload = this.typeCode+this.data
        crc = pngCRC(payload)
        crcStr = networkIntToString(crc)
        lenStr = networkIntToString(len(this.data))
        result = "%s%s%s" % (lenStr, payload, crcStr)
        #prt "crc=", crc
        #if this.crc and this.crc!=crc:
            #prt "   EXPECTED CRC DOESN'T MATCH ON"
            #prt repr(payload)
        #else:
            #prt "   expected crc matches"
        #prt repr(result)
        return result

def readChunk(s, index):
    startindex = index
    lenEnd = index+4
    lenStr = s[index:lenEnd]
    index = lenEnd
    codeEnd = index+4
    typeCode = s[index:codeEnd]
    index = codeEnd
    length = stringToNetworkInt(lenStr)
    #prt "type=", repr(typeCode), "length=", length
    dataEnd = index+length
    data = s[index:dataEnd]
    #prt "data", repr(data)
    index = dataEnd
    crcEnd = index+4
    crcStr = s[index:crcEnd]
    crc = stringToNetworkInt(crcStr)
    crcback = networkIntToString(crc)
    #if crcStr!=crcback:
        #prt "   crc re-encoding failed", (crc, crcStr, crcback)
    #prt "crc", repr(crc)
    payload = typeCode+data
    crc1 = pngCRC(payload)
    #if crc!=crc1:
        #prt 'EXPECTED %s GOT %s' % (crc1, crc)
    #else:
        #prt "     crc checks on", repr(payload)
    ch = Chunk(typeCode, data, crc)
    #prt repr(ch.OutputString())
    return (ch, crcEnd)

def blackBox(size=40, outfile="black.png", palette=True, transparent=True):
    "black box test"
    palette = [ (0,0,0), (0,200,100) ]
    filterFlag = chr(NOFILTER)
    #scanline = filterFlag + (chr(0)*size)
    #data = scanline*size
    c0 = chr(0)
    c1 = chr(1)
    L = []
    for i in xrange(size):
        scanline = filterFlag + (c0*i)+(c1*(size-i))
        L.append(scanline)
    data = "".join(L)
    png = PNGdata()
    if palette:
        png.addIHDR(size, size)
        png.addPLTE(palette)
    else:
        png.addIHDR(size, size, colorType=0)
    if transparent:
        png.addtRNS()
    png.addFilteredData(data)
    png.addIEND()
    outfile = file(outfile, "wb")
    outfile.write(png.OutputString())

def DictToPNG0(D, color=(0xff,0xff,0xff), scale=1, speckle=0,
               colorDict=None, transparentIndex=0, speckIndex=1,
               minx=None, miny=None, maxx=None, maxy=None,
               ):
    palette = [ (0,0,0), color ]
    if colorDict:
        # sanity check
        colorValues = D.values()+[speckIndex]
        for ci in colorValues:
            if ci!=0 and ci!=1 and not colorDict.has_key(ci):
                raise ValueError, "no map for color index "+repr(ci)
        if not colorDict.has_key(0):
            colorDict[0] = (0,0,0)
        if not colorDict.has_key(1):
            colorDict[1] = color
        indices = colorDict.keys()
        maxindex = max(indices)
        if maxindex>=256:
            raise ValueError, "max color index too large "+repr(maxindex)
        palette = [ (0,0,0) ] * (maxindex+1)
        for index in indices:
            palette[index] = colorDict[index]
    filterFlag = chr(NOFILTER)
    points = D.keys()
    if scale>1:
        rscale = range(int(round(scale)))
        newpoints = {}
        for p in points:
            (x,y) = p
            for j in rscale:
                for i in rscale:
                    newpoints[ (x*scale+i, y*scale+j) ] = p
        points = newpoints.keys()
    else:
        newpoints = {}
        for p in points:
            newpoints[p] = p
    xs = [ x for (x,y) in points ]
    ys = [ y for (x,y) in points ]
    if maxx is None:
        maxx = int(math.ceil(max(xs)))
    if minx is None:
        minx = int(math.floor(min(xs)))
    if maxy is None:
        maxy = int(math.ceil(max(ys)))
    if miny is None:
        miny = int(math.floor(min(ys)))
    ID = {}
    for p1 in points:
        (x,y) = p1
        p0 = newpoints[p1]
        ix = int(round(x))
        iy = int(round(y))
        ID[(ix,iy)] = D[p0]
    if speckle:
        nspecks = int(speckle*len(ID))
        for k in xrange(nspecks):
            x = int(random.uniform(minx, maxx))
            y = int(random.uniform(miny, maxy))
            ID[ (x,y) ] = speckIndex
    c0 = chr(0)
    c1 = chr(1)
    ry = range(miny,maxy+1)
    rx = range(minx,maxx+1)
    L = []
    rowtemplate = [filterFlag]+list(rx)
    for y in ry:
        c = 1
        row = list(rowtemplate)
        for x in rx:
            p = (x,y)
            cc = c0
            if ID.has_key(p):
                #print p
                if colorDict:
                    ci = ID[p]
                    cc = chr(ci)
                else:
                    cc = c1
            row[c] = cc
            c+=1
        rowstring = "".join(row)
        L.append(rowstring)
    L.reverse()
    data = "".join(L)
    png = PNGdata()
    png.addIHDR(len(rx), len(ry))
    #print "adding palette", palette
    png.addPLTE(palette)
    if transparentIndex is not None:
        #print "adding trnsrns", repr(transparentIndex)
        png.addtRNS(transparentIndex)
    png.addFilteredData(data)
    png.addIEND()
    return png

def DictToPNG(D, outfile, color=(0xff,0xff,0xff), scale=1, speckle=0,
              colorDict=None, transparentIndex=0, speckIndex=1,
              minx=None, miny=None, maxx=None, maxy=None):
    #pr "color is", color
    png = DictToPNG0(D, color, scale, speckle, colorDict,
                     transparentIndex=transparentIndex,
                     speckIndex=speckIndex,
                     minx=minx, miny=miny, maxx=maxx, maxy=maxy)
    outString = png.OutputString()
    if outfile is not None:
        out = open(outfile, "wb")
        out.write(outString)
    return outString

def testD(fn="circle.png", npoints=100, factor=20):
    D = {}
    delta = 2*math.pi/npoints
    for i in range(npoints):
        theta = delta*i
        x = math.sin(theta)*factor
        y = math.cos(theta)*factor
        D[ (x,y) ] = i%3+1
    print  "creating", fn
    colorD = {1: (0,0,0xff), 2: (0,0xff,0), 3:(0xff,0,0)}
    DictToPNG(D, fn, colorDict=colorD, scale=4)

def readBlack(fn="black.png"):
    s = open(fn, "rb").read()
    png = PNGdata()
    png.readString(s)
    img = IndexedImage()
    img.parseData(png)
    print img

def readWhite():
    fn = "white.png"
    s = open(fn, "rb").read()
    png = PNGdata()
    png.readString(s)
    outfile = file("whitecopy.png", "wb")
    s2 = png.OutputString()
    outfile.write(s2)
    if s!=s2:
        print "input doesn't match output"
        for (i, a, b) in zip(range(len(s)), s, s2):
            if a!=b:
                print "first diff at", (i, a, b)
                return
        print "lengths differ", len(s), len(s2)
    img = IndexedImage()
    img.parseData(png)
    print img
    return png

if __name__=="__main__":
    testD()
    #readBlack("circle.png")
    #readWhite()
    #blackBox()
    #readBlack()


