
"""
tools for manipulating BDF font format.

Very basic --
Primarily intended for vanilla ASCII fonts.
Chinese characters are not supported, for example.
"""

def _bitIndices(ch):
    result = []
    h = int(ch, 16)
    bit = 8
    for i in range(4):
        if h&bit:
            result.append(i)
        bit = bit>>1
    return result

bitIndexMap = {}
for c in "0123456789abcdef":
    bitIndexMap[c] = _bitIndices(c)

def bits(hexLine, result=None):
    "return indices of bits (unsorted) read left to right"
    #print "hexline", repr(hexLine)
    offset = 0
    hexLine = hexLine.lower()
    if result is None:
        result = {}
    for c in hexLine:
        imap = bitIndexMap.get(c, None)
        if imap is None:
            raise ValueError, "no mapping for "+repr(c)
        for b in imap:
            result[b+offset] = c
        offset += 4
    return result

class glyph:
    swidth = 1000
    sheight = 0
    dwidth = dheight = None
    def __init__(this, name, xwidth, yheight, dx, dy):
        this.name = name
        this.bounds(xwidth, yheight, dx, dy)
        this.lines = []
        this.shifter = None
    def bounds(this, xwidth, yheight, dx, dy):
        this.xwidth = xwidth
        this.yheight = yheight
        this.dx = dx
        this.dy = dy
    def resolution(this, xres, yres):
        this.xres = xres
        this.yres = yres
    def sWidth(this, swx, swy):
        this.swidth = dwx
        this.sheight = dwy
    def dWidth(this, dwx, dwy):
        this.dwidth = dwx
        this.dheight = dwy
    def addBits(this, hexLine):
        "add bits but put line at the first position (x=0 position)"
        theBits = bits(hexLine).keys()
        this.lines.insert(0, theBits)
        this.shifter = None
    def shiftDict(this):
        result = []
        dx = this.dx
        dy = this.dy
        y = dy
        for line in this.lines:
            #print "line = ", line
            sLine = [x+dx for x in line]
            result.append(sLine)
            y += 1
        return result
    def addPixels(this, xstart, ystart, D=None):
        if D is None:
            D = {}
        shifter = this.shifter
        if shifter is None:
            shifter = this.sDict = this.shiftDict()
        y = this.dy
        for sLine in shifter:
            sy = y+ystart
            for x in sLine:
                D[(x+xstart, sy)] =  1
            y += 1
        xend = xstart+this.dwidth
        yend = ystart+this.dheight
        return (xend, yend, D)
    def display(this):
        lines = list(this.lines)
        lines.reverse()
        for line in lines:
            mline = max(line)
            for x in range(mline+1):
                if x in line:
                    print "#",
                else:
                    print " ",
            print "\t", line
 
class pixelation:
    def __init__(this, font, s):
        this.font = font
        this.s = s
        this.PD = None
    def pixelDict(this, xstart=0, ystart=0, recompute=False):
        result = this.PD
        if not recompute and result is not None:
            return result
        for c in this.s:
            g = this.font.getGlyph(c)
            (xstart, ystart, result) = g.addPixels(xstart, ystart, result)
            #print xstart, ystart
            #xstart=ystart=0
        this.PD = result
        return result
    def width(this):
        PD = this.pixelDict()
        xs = [x for (x,y) in PD.keys()]
        width = max(xs)
        return width
    def drawToCanvas0(this, startx, starty, canvas, radius, scaleFactor=1.0):
        D = this.pixelDict()
        for (x,y) in D.keys():
            sx = startx+scaleFactor*x
            sy = starty+scaleFactor*y
            canvas.addCircle(sx, sy, radius)
    def drawToCanvas(this, startx, starty, canvas, radius, scaleFactor=1.0):
        D = this.pixelDict()
        canvas.plotDict(startx, starty, D, radius, scaleFactor)
    def display(this, mark="#", blank=" "):
        D = this.pixelDict()
        setPixels = D.keys()
        xs = [x for (x,y) in setPixels]
        ys = [y for (x,y) in setPixels]
        maxx = max(xs)
        minx = min(xs)
        maxy = max(ys)
        miny = min(ys)
        resultList = []
        xr = range(minx, maxx+1)
        for y in xrange(miny, maxy+1):
            yline = list(xr)
            i = 0
            for x in xr:
                c = blank
                if D.has_key( (x,y) ):
                    c = mark
                yline[i] = c
                i+=1
            ystring = "".join(yline)
            resultList.insert(0, ystring)
        return "\n".join(resultList)
    def toPNG(this, filename, color=(0x0f,0x11,0xaf), scale=2, speckle=0.3):
        import KiPNG
        D = this.pixelDict()
        return KiPNG.DictToPNG(D, filename, color, scale, speckle)
    
class font:
    verbose = False
    def __init__(this):
        this.charMap = {}
    def bounds(this, xwidth, yheight, dx, dy):
        this.xwidth = xwidth
        this.yheight = yheight
        this.dx = dx
        this.dy = dy
    def getGlyph(this, c):
        return this.charMap[c]
    def newGlyph(this, name, ordinal):
        char = unichr(ordinal)
        result = this.charMap[char] = glyph(name, this.xwidth, this.yheight, this.dx, this.dy)
        return result
    def loadFilePath(this, path):
        f = file(path)
        this.loadFile(f)
    def loadFile(this, f):
        lines = f.readlines()
        this.loadLines(lines)
    def loadLines(this, lines, index=0):
        "load BDF representation as a sequence of lines"
        line = None
        nlines = len(lines)
        while index<nlines:
            line = lines[index]
            line = line.strip()
            if not line:
                index += 1
                continue # ignore white line
            sline = line.split()
            indicator = sline[0].upper()
            methodname = "do"+indicator
            method = getattr(this, methodname, None)
            if method:
                index = method(lines, index)
            else:
                if this.verbose: print "warning: no handler %s" % methodname
                index+=1
    def doSTARTFONT(this, lines, index):
        return index+1
    def doCOMMENT(this, lines, index):
        return index+1
    def doFONT(this, lines, index):
        return index+1
    def doSIZE(this, lines, index):
        line = lines[index]
        sstrings = line.split()[1:]
        sizes = map(int, sstrings)
        (this.points, this.xres, this.yres) = sizes
        return index+1
    def doFONTBOUNDINGBOX(this, lines, index):
        line = lines[index]
        bboxstrings = line.split()[1:]
        bbox = map(int, bboxstrings)
        (xwidth, yheight, dx, dy) = bbox
        this.bounds(xwidth, yheight, dx, dy)
        return index+1
    def doSTARTPROPERTIES(this, lines, index):
        line = None
        while line != "ENDPROPERTIES":
            index+=1
            line = lines[index].strip().upper()
        return index+1
    def doCHARS(this, lines, index):
        return index+1
    def doSTARTCHAR(this, lines, index):
        line = lines[index]
        sline = line.split()
        charname = " ".join(sline[1:])
        done = False
        g = encoding = bbx = dwidth = swidth = None
        while not done:
            line = lines[index].strip()
            if not line:
                index += 1
                continue # ignore all white line
            sline = line.split()
            indicator = sline[0].upper()
            if indicator=="ENDCHAR":
                done = True
            elif indicator=="ENCODING":
                encoding = int( sline[1] )
                index += 1
            elif indicator=="SWIDTH":
                swidth = map( int, sline[1:] )
                index += 1
            elif indicator=="DWIDTH":
                dwidth = map( int, sline[1:] )
                index += 1
            elif indicator=="BBX":
                bbx = map( int, sline[1:] )
                index += 1
            elif indicator=="BITMAP":
                if encoding is None:
                    raise ValueError, "no encoding for "+repr(charname)
                if bbx is None:
                    raise ValueError, "no bbx for "+repr(charname)
                if dwidth is None:
                    raise ValueError, "no dwidth for "+repr(charname)
                g = this.newGlyph(charname, encoding)
                (xwidth, yheight, dx, dy) = bbx
                g.bounds(xwidth, yheight, dx, dy)
                (dwx, dwy) = dwidth
                g.dWidth(dwx, dwy)
                index += 1
                line = lines[index].strip().upper()
                while line!="ENDCHAR":
                    g.addBits(line)
                    index += 1
                    line = lines[index].strip().upper()
            else:
                if this.verbose:
                    print "don't understand charline", repr(line)
                index += 1
        if g is None:
            raise ValueError, "STARTCHAR failed to generate a glyph: "+repr(charname)
        return index+1
    def doENDFONT(this, lines, index):
        return index+1

def test1():
    ks = bitIndexMap.keys()
    ks.sort()
    for k in ks:
        print bitIndexMap[k]
    fn = font()
    fn.loadFilePath("cursive.bdf")
    g = fn.getGlyph("w")
    g.display()
    
def test0():
    from getparm import getparm
    import sys
    args = sys.argv
    png = getparm(args, "--png")
    s = args[1]
    fn = font()
    fn.loadFilePath("cursive.bdf")
    p = pixelation(fn, s)
    #print dir(sys)
    if png:
        p.toPNG(png)
    else:
        print p.display()

if __name__=="__main__":
    test0()
