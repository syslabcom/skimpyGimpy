"""
	create an encoded text string representation for security
	verification.
"""

# COORDINATE SYSTEM IS ROTATED 90 DEGREES CLOCKWISE!

import math, random

def rotatePoints(points, radians):
    s = math.sin(radians)
    c = math.cos(radians)
    #pr "<br>radians, s, c", (radians, s,c)
    return [ (x*c-y*s, x*s+y*c) for (x,y) in points ]

def shiftPoints(points, vector):
    (vx, vy) = vector
    return [ (x+vx, y+vy) for (x,y) in points ]

def scaleX(points, factor):
    return [ (x*factor, y) for (x,y) in points ]

def scaleY(points, factor):
    return [ (x*factor, y) for (x,y) in points ]

def mixSequence(size):
    "return sequence weights (a,b,c,d) for mixing control points"
    if size<3:
        raise ValueError, "size too small"
    result = []
    delta = (math.pi/2.0)/(size-1)
    for i in range(size):
        # probably could be done with less work if analysed
        x = i*delta
        sinx = math.sin(x)
        cosx = math.cos(x)
        sinx2 = sinx*sinx
        cosx2 = cosx*cosx
        sinx4 = sinx2*sinx2
        cosx4 = cosx2*cosx2
        sinx6 = sinx2*sinx4
        cosx6 = cosx2*cosx4
        c = 3*sinx4*cosx2
        b = 3*cosx4*sinx2
        result.append( (cosx6, b, c, sinx6) )
    return result

class curve:
    def __init__(this, p0, p1, p2, p3, mix, integer=False):
        this.points = [p0, p1, p2, p3]
        this.mix = mix
        this.integer = integer
    def plot(this, delta, scale=1.0):
        if delta<-0.1 or delta>1.1:
            raise ValueError, "delta should be between 0 and 1"
        mix = this.mix
        nmix = len(mix)
        index = int(round( nmix*delta ))
        if index>=nmix:
            index = nmix-1
        if index<0:
            index = 0
        mixcoefficients = mix[index]
        x = y = 0
        for (coef, p) in zip(mixcoefficients, this.points):
            (px, py) = p
            x += px*coef
            y += py*coef
        x = x*scale
        y = y*scale
        if this.integer:
            x = int(round(x))
            y = int(round(y))
        return (x,y)
    def fakeLength(this):
        pts = this.points
        lastp = this.points[0]
        length = 0
        for p in pts[1:]:
            for (a,b) in zip(lastp, p):
                length += abs(a-b)
            lastp = p
        return length

def curveTable(points, size=40, width=8, onclick="alert('click '+%s+', '+%s)",
               bgcolor="yellow", fgcolor="cyan"):
    for p in points:
        for x in p:
            if x<0 or x>size:
                raise ValueError, "point coords must be within 0 to "+repr(size)+"::"+repr(x)
    samples = size*3
    t = mixSequence(samples)
    D = {}
    size1 = size-1.0
    sizep1 = size+1
    lastpoint = None
    if points:
        lastpoint = points[0]
    points = points[1:]
    while lastpoint:
        head = points[:3]
        points = points[3:]
        lh = len(head)
        a = b = c = d = lastpoint
        if lh>0:
            b = c = d = head[0]
            if lh>1:
                c = d = head[1]
                if lh>2:
                    d = head[2]
        lastpoint = d
        c = curve( a, b, c, d, t, integer=True)
        for i in range(samples):
            pt = c.plot(i/(samples-1.0))
            D[pt] = 1
        if not points: break
    L = ["<table>"]
    for i in range(sizep1):
        L.append("<tr>")
        for j in range(sizep1):
            color = bgcolor
            if D.has_key( (i,j) ):
                color = fgcolor
            oc = onclick % (i,j)
            L.append('<td bgcolor="%s" width="%s" height="%s" onclick="%s"></td>' % (color, width, width, oc))
            #L.append('<td bgcolor="%s" width="%s" height="%s" onclick="%s">%s,%s</td>' % (color, width, width, oc, i,j))
        L.append("</tr>")
    L.append("</table>")
    return "\n".join(L)

class letterPoints:
    def __init__(this, D = None):
        if D is None:
            D = {}
        this.letterToPoints = D
    def __repr__(this):
        L = ["letterPoints( {"]
        a = L.append
        D = this.letterToPoints
        keys = D.keys()
        keys.sort()
        for letter in keys:
            a("%s:   [" % repr(letter))
            pts = D[letter]
            ptstrings = [ repr(p)+"," for p in pts ]
            prefix = "\n     "
            plist = prefix + prefix.join(ptstrings)
            a(plist)
            a("   ],")
        a(" })")
        return "\n".join(L)
    def readFromFile(this, filename="letters.txt"):
        f = open(filename)
        done = False
        while not done:
            # find letter
            letter = ""
            while not letter and not done:
                line = f.readline()
                if not line: done = True
                letter = line.strip()
            #print "letter", letter
            if done:
                break
            if len(letter)>2 and letter[0]==letter[-1]=='"':
                letter = letter[1:-1]
            if len(letter)!=1:
                raise ValueError, "bad letter: "+repr(letter)
            # skip ws
            point = ""
            while not point and not done:
                line = f.readline()
                if not line:
                    done = True
                point = line.strip()
            if done:
                raise ValueError, "found letter %s with no points" % repr(letter)
            # collect all points to next white line
            pointsdata = point
            while point:
                line = f.readline()
                point = line.strip()
                pointsdata += point
            #print "pointsdata", pointsdata
            points = parsePointString(pointsdata)
            #print "points", points
            this.letterToPoints[letter] = points
            if not line:
                done = True

class gimpyString:
    rotateDegreesLimit = 10
    joined = shifted = False
    samples = 100
    scale = 0.5
    scatterFactor = 2.1
    speckleFactor = .1
    mark = "#"
    fontSize = 1
    color = "red"
    scaleFactor = 0.2
    smearLimit = 4.3
    smearRadius = 2.1
    
    def __init__(this, string, points=None):
        if points is None:
            points = basicPoints
        this.points = points
        this.string = string
        l2p = points.letterToPoints
        for ch in string:
            if not l2p.has_key(ch):
                raise ValueError, "no point sequence defined for character: "+repr(ch)
        this.pointSequences = [ l2p[ch] for ch in string ]
        this.joinedPoints = None
        this.maxX = this.maxY = None
        this.pixelDict = {}
    def randomScale(this):
        high = 1+this.scaleFactor
        low = 1-this.scaleFactor
        n = [ scaleX(pts, random.uniform(low,high)) for pts in this.pointSequences ]
        n2 = [ scaleY(pts, random.uniform(low,high)) for pts in n ]
        this.pointSequences = n2
    def randomRotate(this):
        high = this.rotateDegreesLimit * math.pi / 180.0
        low = -high
        newpointSequences = [ rotatePoints(pts, random.uniform(low,high))
                             for pts in this.pointSequences ]
        this.pointSequences = newpointSequences
    def joinPoints(this):
        lastY = 0
        lastX = 0
        joinedPoints = []
        this.joinedPoints = []
        for points in this.pointSequences:
            (firstX, firstY) = points[0]
            # shift firstX to match lastX
            deltaX = lastX-firstX
            # shift X's past lastX
            deltaY = lastY
            vector = (deltaX, deltaY)
            #pr "vector", vector
            spoints = shiftPoints(points, vector)
            (lastX, lastY) = spoints[-1]
            this.joinedPoints.extend(spoints)
        this.joined = True
    def shift(this):
        if not this.joined:
            raise ValueError, "must join first"
        j = this.joinedPoints
        (minX, minY) = j[0]
        for (x,y) in j:
            minX = min(minX, x)
            minY = min(minY, y)
        vector = (-minX, -minY)
        this.joinedPoints = shiftPoints(j, vector)
        this.shifted = True
    def pixelize(this):
        if not this.shifted:
            raise ValueError, "must shift first"
        scale = this.scale
        samples = this.samples
        t = mixSequence(samples)
        pixelDict = {}
        points = list(this.joinedPoints)
        lastpoint = None
        if points:
            lastpoint = points[0]
        points = points[1:]
        while lastpoint:
            head = points[:3]
            points = points[3:]
            lh = len(head)
            a = b = c = d = lastpoint
            if lh>0:
                b = c = d = head[0]
                if lh>1:
                    c = d = head[1]
                    if lh>2:
                        d = head[2]
            lastpoint = d
            c = curve( a, b, c, d, t, integer=True)
            samples = int(c.fakeLength())+3
            for i in range(samples):
                pt = c.plot(i/(samples-1.0), scale=scale)
                pixelDict[pt] = 1
                (x,y) = pt
            if not points: break
        this.pixelDict = pixelDict
    def scatter(this):
        pd = this.pixelDict
        sf = this.scatterFactor
        npd = {}
        for (x,y) in pd.keys():
            x = int(random.uniform(0, sf)+x)
            y = int(random.uniform(0, sf)+y)
            npd[(x,y)] = 1
        this.pixelDict = npd
    def smear(this):
        limit = this.smearLimit
        radius = this.smearRadius
        pd = this.pixelDict
        for (x,y) in pd.keys():
            for i in range(int(random.uniform(0,limit))):
                x1 = int(random.uniform(0, radius)+x)
                y1 = int(random.uniform(0, radius)+y)
                pd[x1,y1] = 1
    def speckle(this):
        pd = this.pixelDict
        lpd = len(pd)
        nspeckle = int(lpd*this.speckleFactor)
        maxX = maxY = 0
        for (x,y) in pd.keys():
            maxX = max(x, maxX)
            maxY = max(y, maxY)
        for i in range(nspeckle):
            x = int(random.uniform(0,maxX))
            y = int(random.uniform(0,maxY))
            pd[(x,y)] = i
    def format(this):
        pixelDict = this.pixelDict
        mark = this.mark
        fs = this.fontSize
        color = this.color
        if not pixelDict:
            raise ValueError, "must pixelize"
        L = ['<pre style="font-size:%spt;color:%s;font-weight:bold;line-height:%spt" ><!-- %s -->' %(
            fs,color,fs, "generated by skimpyGimpy, created by Aaron Watters")]
        a = L.append
        maxX = maxY = 0
        for (x,y) in pixelDict.keys():
            maxX = max(x, maxX)
            maxY = max(y, maxY)
        rY = range(maxY)
        for x in range(maxX+1):
            lineList = [" "] * maxY
            for y in rY:
                if pixelDict.has_key( (x,y) ):
                    lineList[y] = mark
            a("".join(lineList))
        a("</pre>")
        return "\n".join(L)
    def prepare(this):
        this.randomRotate()
        this.randomScale()
        this.joinPoints()
        this.shift()
        this.pixelize()
        this.scatter()
        this.smear()
        this.speckle()
    def formatPNG(this, filename, color=(0x77, 0x77, 0x77), scale=2):
        import KiPNG
        this.prepare()
        pD = this.pixelDict
        D = {}
        for (y,x) in this.pixelDict.keys():
            p = (x,-y)
            D[p] = 1
        KiPNG.DictToPNG(D, filename, color, scale)
    def formatAll(this):
        this.prepare()
        return this.format()

def testg(string="test", png=None):
    #import string
    #g = gimpyString(string.lowercase)
    g = gimpyString(string)
    if png is not None:
        print "writing png format to", png
        g.formatPNG(png)
    else:
        print g.formatAll()

def clean(s, points=None):
    if points is None:
        points = basicPoints
    s = s.lower()
    L = []
    for c in s:
        if points.letterToPoints.has_key(c):
            L.append(c)
    return "".join(L)

def test1():
    points = [
        (0,40),
        (40,40),
        (40,0),
        (40,40),
        (30,40),
        (10,10),
        (20,30),
        (0,0),
        ]
    print curveTable(points)

pagetemplate = r"""
<html>
<head>
<title>interpolation experimentation page</title>
<script>
function addpoint(i,j,submit) {
    var myform = document.getElementById("myform");
    myform.points.value = myform.points.value+"\n"+i+","+j+";"
    if (submit) {
        myform.submit();
    }
}
</script>
</head>
<body>
%(table)s
<hr>
<form id="myform" action="%(action)s">
<TEXTAREA Name="points" rows="20" cols="20">%(pv)s</TEXTAREA>
<br>
<input type="submit">
</form>

</body>
</html>
"""
def makePage(action, points=None, submit="true", cgidata=None):
    D = {"action": action}
    if points is None:
        points = []
        if cgidata:
            pointsdata = cgidata["points"].value
            points = parsePointString(pointsdata)
    ps = [ "%s,%s" % (x,y) for (x,y) in points ]
    pv = ";\n".join(ps)
    if pv: pv+=";"
    D["pv"] = pv
    D["table"] = curveTable(points, onclick="addpoint(%s,%s,"+submit+")")
    return pagetemplate % D

def parsePointString(pointsdata):
    points = []
    pointstrings = pointsdata.split(";")
    for ps in pointstrings:
        pss = ps.strip()
        if pss:
            (xs,ys) = pss.split(",")
            x = int(xs.strip())
            y = int(ys.strip())
            points.append((x,y))
    return points

def test2():
    points = [
        (0,40),
        (40,40),
        (40,0),
        (40,40),
        (30,40),
        (10,10),
        (20,30),
        (0,0),
        ]
    print makePage("action", points, "false")

def test0():
    msize = 30
    print "<!--"
    print "<pre>"
    t = mixSequence(msize)
    for m in t:
        print m
    print
    c = curve( (0,0), (0,msize), (msize/2,msize/2), (msize,msize), t, integer=True)
    D = {}
    nsize = msize*3
    nsize1 = nsize-1.0
    for i in range(nsize):
        pt = c.plot(i/nsize1)
        D[pt] = i
        print i, pt
    print "</pre>"
    print "<table border>"
    for i in range(msize+1):
        print "<tr>"
        for j in range(msize+1):
            print "<td>"
            test = D.get( (i,j) )
            if test:
                print test
            print "</td>"
        print "</tr>"
    print "</table>"
    print "-->"
    print
    csize = 300
    print '<div style="width:%s;height:%s;background-color:blue;position:absolute;top:0;left:0;">' % (
        csize, csize)
    print "hello"
    csize = 300
    t = mixSequence(csize)
    c = curve( (0,0), (0,csize), (csize/2,csize/2), (csize,csize), t, integer=True)
    D = {}
    for i in range(csize):
        x = i/float(csize)
        p = c.plot(x)
        D[p] = i
    for p in D.keys():
        (px, py) = p
        print ('<div style="width:2px;height:2px;position:absolute;background-color:red;'+
               'clip:rect(0,2px,2px,0);overflow:hidden;'+
               'top:%spx;left:%spx"></div>' %(px, py) )
    print '</div>'

def dumpPoints():
    lp = letterPoints()
    lp.readFromFile()
    print lp
    return ""

basicPoints = letterPoints( {
' ':   [

     (40, 0),
     (40, 40),
   ],
'-':   [

     (40, 0),
     (20, 10),
     (20, 10),
     (20, 10),
     (20, 30),
     (20, 30),
     (20, 30),
     (21, 10),
     (21, 10),
     (21, 10),
     (21, 30),
     (21, 30),
     (21, 30),
     (22, 10),
     (22, 10),
     (22, 10),
     (22, 30),
     (22, 30),
     (22, 30),
     (23, 10),
     (23, 10),
     (23, 10),
     (23, 30),
     (23, 30),
     (23, 30),
     (40, 40),
   ],
'.':   [

     (34, 0),
     (34, 22),
     (34, 22),
     (34, 22),
     (38, 22),
     (38, 22),
     (38, 18),
     (38, 18),
     (35, 18),
     (35, 18),
     (35, 21),
     (35, 21),
     (37, 21),
     (37, 21),
     (37, 19),
     (37, 19),
     (36, 19),
     (36, 19),
     (36, 20),
     (36, 20),
     (34, 40),
   ],
'/':   [

     (29, 0),
     (29, 17),
     (40, 0),
     (40, 0),
     (40, 0),
     (4, 36),
     (4, 36),
     (4, 36),
     (39, 0),
     (39, 0),
     (39, 0),
     (3, 36),
     (3, 36),
     (3, 36),
     (38, 0),
     (38, 0),
     (38, 0),
     (2, 36),
     (2, 36),
     (2, 36),
     (16, 21),
     (29, 40),
   ],
'0':   [

     (40, 0),
     (39, 22),
     (37, 32),
     (32, 34),
     (20, 36),
     (9, 33),
     (4, 29),
     (2, 20),
     (3, 13),
     (8, 5),
     (24, 3),
     (32, 5),
     (39, 21),
     (29, 35),
     (19, 34),
     (11, 33),
     (5, 30),
     (4, 29),
     (5, 28),
     (6, 27),
     (31, 10),
     (32, 9),
     (31, 9),
     (30, 10),
     (40, 21),
     (40, 22),
     (40, 23),
     (40, 40),
   ],
'1':   [

     (36, 0),
     (37, 23),
     (38, 24),
     (39, 24),
     (40, 23),
     (40, 15),
     (39, 15),
     (39, 17),
     (39, 30),
     (39, 33),
     (40, 33),
     (40, 32),
     (40, 24),
     (40, 23),
     (39, 22),
     (38, 22),
     (2, 23),
     (1, 23),
     (0, 24),
     (0, 23),
     (6, 18),
     (6, 17),
     (5, 17),
     (4, 17),
     (2, 22),
     (1, 23),
     (0, 23),
     (0, 24),
     (39, 23),
     (39, 24),
     (37, 24),
     (37, 40),
   ],
'2':   [

     (31, 0),
     (40, 35),
     (39, 35),
     (38, 34),
     (37, 33),
     (40, 4),
     (38, 3),
     (37, 3),
     (36, 3),
     (37, 35),
     (38, 36),
     (39, 35),
     (39, 33),
     (38, 3),
     (38, 3),
     (38, 3),
     (38, 3),
     (14, 31),
     (14, 31),
     (14, 31),
     (5, 33),
     (0, 26),
     (1, 13),
     (9, 3),
     (9, 3),
     (9, 3),
     (9, 3),
     (4, 11),
     (1, 21),
     (0, 25),
     (0, 27),
     (6, 31),
     (14, 31),
     (30, 14),
     (30, 14),
     (30, 14),
     (30, 14),
     (40, 40),
   ],
'3':   [

     (31, 0),
     (32, 28),
     (40, 18),
     (34, 6),
     (33, 6),
     (33, 7),
     (34, 8),
     (40, 17),
     (40, 25),
     (38, 29),
     (33, 32),
     (27, 32),
     (22, 28),
     (19, 22),
     (18, 15),
     (18, 11),
     (18, 11),
     (18, 11),
     (18, 11),
     (17, 22),
     (14, 27),
     (12, 28),
     (9, 28),
     (6, 28),
     (3, 25),
     (1, 21),
     (1, 14),
     (5, 6),
     (6, 6),
     (7, 7),
     (3, 14),
     (2, 19),
     (3, 25),
     (8, 28),
     (14, 27),
     (19, 17),
     (19, 17),
     (24, 30),
     (35, 30),
     (34, 40),
   ],
'4':   [

     (35, 0),
     (35, 26),
     (38, 26),
     (40, 25),
     (39, 24),
     (2, 25),
     (1, 25),
     (0, 26),
     (1, 26),
     (17, 26),
     (18, 26),
     (19, 25),
     (19, 24),
     (18, 9),
     (18, 8),
     (18, 8),
     (18, 8),
     (1, 16),
     (1, 16),
     (1, 16),
     (1, 16),
     (18, 8),
     (18, 8),
     (18, 8),
     (18, 8),
     (19, 25),
     (19, 25),
     (19, 25),
     (19, 25),
     (40, 26),
     (40, 26),
     (40, 26),
     (40, 26),
     (36, 40),
   ],
'5':   [

     (40, 0),
     (40, 21),
     (39, 18),
     (38, 13),
     (32, 7),
     (31, 6),
     (31, 6),
     (31, 6),
     (40, 19),
     (40, 21),
     (37, 26),
     (26, 29),
     (21, 23),
     (20, 10),
     (18, 7),
     (16, 6),
     (13, 6),
     (2, 6),
     (2, 6),
     (2, 6),
     (2, 6),
     (7, 25),
     (7, 25),
     (7, 25),
     (7, 25),
     (2, 6),
     (2, 6),
     (2, 6),
     (2, 6),
     (17, 6),
     (18, 7),
     (19, 9),
     (21, 22),
     (25, 26),
     (36, 24),
     (39, 40),
   ],
'6':   [

     (40, 0),
     (40, 19),
     (40, 22),
     (38, 29),
     (33, 33),
     (29, 33),
     (25, 30),
     (22, 23),
     (26, 14),
     (30, 13),
     (36, 16),
     (39, 22),
     (39, 22),
     (39, 22),
     (30, 12),
     (28, 11),
     (26, 9),
     (13, 7),
     (8, 9),
     (1, 19),
     (1, 26),
     (1, 26),
     (1, 26),
     (1, 26),
     (5, 13),
     (7, 10),
     (11, 8),
     (17, 8),
     (23, 9),
     (31, 13),
     (39, 21),
     (39, 23),
     (39, 26),
     (40, 40),
   ],
'7':   [

     (40, 0),
     (40, 16),
     (40, 16),
     (40, 16),
     (40, 16),
     (2, 29),
     (2, 29),
     (2, 29),
     (2, 29),
     (3, 9),
     (3, 9),
     (3, 9),
     (3, 9),
     (5, 7),
     (5, 7),
     (5, 7),
     (3, 9),
     (3, 9),
     (3, 9),
     (2, 29),
     (2, 29),
     (2, 29),
     (2, 29),
     (20, 23),
     (20, 23),
     (20, 23),
     (20, 23),
     (20, 13),
     (20, 13),
     (20, 32),
     (20, 32),
     (20, 23),
     (20, 23),
     (20, 23),
     (20, 23),
     (40, 17),
     (40, 17),
     (40, 17),
     (40, 17),
     (40, 40),
   ],
'8':   [

     (40, 0),
     (39, 20),
     (37, 28),
     (31, 32),
     (26, 32),
     (22, 29),
     (19, 21),
     (18, 15),
     (16, 9),
     (13, 5),
     (8, 4),
     (3, 11),
     (1, 19),
     (2, 28),
     (10, 33),
     (13, 33),
     (17, 26),
     (21, 9),
     (27, 5),
     (31, 5),
     (37, 8),
     (40, 26),
     (40, 32),
     (40, 40),
   ],
'9':   [

     (40, 0),
     (40, 18),
     (40, 18),
     (40, 18),
     (40, 18),
     (6, 30),
     (6, 30),
     (6, 30),
     (6, 30),
     (1, 26),
     (0, 17),
     (6, 7),
     (15, 7),
     (19, 13),
     (15, 20),
     (6, 30),
     (6, 30),
     (6, 30),
     (6, 30),
     (40, 16),
     (40, 16),
     (40, 16),
     (40, 16),
     (40, 40),
   ],
':':   [

     (40, 0),
     (14, 22),
     (14, 22),
     (14, 22),
     (18, 22),
     (18, 22),
     (18, 18),
     (18, 18),
     (15, 18),
     (15, 18),
     (15, 21),
     (15, 21),
     (17, 21),
     (17, 21),
     (17, 19),
     (17, 19),
     (16, 19),
     (16, 19),
     (16, 20),
     (16, 20),
     (34, 22),
     (34, 22),
     (34, 22),
     (38, 22),
     (38, 22),
     (38, 18),
     (38, 18),
     (35, 18),
     (35, 18),
     (35, 21),
     (35, 21),
     (37, 21),
     (37, 21),
     (37, 19),
     (37, 19),
     (36, 19),
     (36, 19),
     (36, 20),
     (36, 20),
     (40, 40),
   ],
'@':   [

     (31, 0),
     (27, 10),
     (27, 10),
     (27, 10),
     (5, 20),
     (5, 20),
     (5, 20),
     (17, 25),
     (17, 25),
     (17, 25),
     (17, 14),
     (17, 14),
     (17, 14),
     (17, 25),
     (17, 25),
     (17, 25),
     (28, 29),
     (28, 29),
     (28, 29),
     (22, 34),
     (10, 36),
     (1, 29),
     (0, 20),
     (1, 11),
     (8, 6),
     (17, 4),
     (30, 9),
     (32, 19),
     (26, 31),
     (31, 40),
   ],
'_':   [

     (18, 0),
     (20, 5),
     (20, 5),
     (20, 5),
     (20, 35),
     (20, 35),
     (20, 35),
     (21, 5),
     (21, 5),
     (21, 5),
     (21, 35),
     (21, 35),
     (21, 35),
     (22, 5),
     (22, 5),
     (22, 5),
     (22, 35),
     (22, 35),
     (22, 35),
     (23, 5),
     (23, 5),
     (23, 5),
     (23, 35),
     (23, 35),
     (23, 35),
     (18, 40),
   ],
'a':   [

     (40, 0),
     (40, 10),
     (40, 10),
     (3, 21),
     (3, 21),
     (3, 21),
     (23, 28),
     (23, 28),
     (23, 28),
     (21, 16),
     (21, 16),
     (21, 16),
     (22, 28),
     (22, 28),
     (22, 28),
     (40, 32),
     (40, 32),
     (40, 40),
   ],
'b':   [

     (40, 0),
     (40, 9),
     (40, 9),
     (40, 9),
     (2, 14),
     (2, 14),
     (2, 14),
     (3, 29),
     (10, 32),
     (19, 26),
     (19, 13),
     (19, 13),
     (19, 13),
     (20, 23),
     (25, 30),
     (33, 32),
     (40, 24),
     (40, 9),
     (40, 9),
     (40, 9),
     (40, 40),
   ],
'c':   [

     (40, 0),
     (19, 8),
     (7, 15),
     (4, 22),
     (8, 28),
     (8, 28),
     (8, 28),
     (4, 22),
     (9, 13),
     (25, 8),
     (38, 13),
     (40, 21),
     (40, 26),
     (33, 33),
     (33, 33),
     (38, 29),
     (40, 40),
   ],
'd':   [

     (40, 0),
     (40, 8),
     (40, 8),
     (40, 8),
     (3, 13),
     (3, 13),
     (3, 13),
     (0, 23),
     (7, 32),
     (22, 34),
     (37, 29),
     (40, 20),
     (40, 8),
     (40, 8),
     (40, 8),
     (40, 40),
   ],
'e':   [

     (40, 0),
     (40, 10),
     (40, 10),
     (40, 10),
     (35, 30),
     (35, 30),
     (35, 30),
     (40, 10),
     (40, 10),
     (40, 10),
     (20, 10),
     (20, 10),
     (20, 10),
     (20, 25),
     (20, 25),
     (20, 25),
     (20, 10),
     (20, 10),
     (20, 10),
     (0, 10),
     (0, 10),
     (0, 10),
     (5, 30),
     (5, 30),
     (5, 30),
     (0, 10),
     (0, 10),
     (0, 10),
     (40, 10),
     (40, 10),
     (40, 10),
     (40, 40),
   ],
'f':   [

     (40, 0),
     (40, 10),
     (40, 10),
     (40, 10),
     (2, 14),
     (2, 14),
     (2, 14),
     (1, 29),
     (1, 29),
     (1, 29),
     (2, 14),
     (2, 14),
     (2, 14),
     (18, 12),
     (18, 12),
     (18, 12),
     (17, 28),
     (18, 12),
     (18, 12),
     (18, 12),
     (32, 6),
     (40, 40),
   ],
'g':   [

     (40, 0),
     (19, 8),
     (7, 15),
     (4, 22),
     (8, 28),
     (8, 28),
     (8, 28),
     (4, 22),
     (9, 13),
     (25, 8),
     (38, 13),
     (40, 21),
     (40, 26),
     (33, 33),
     (33, 33),
     (26, 33),
     (26, 33),
     (26, 33),
     (26, 20),
     (26, 33),
     (40, 40),
   ],
'h':   [

     (40, 0),
     (40, 6),
     (40, 6),
     (40, 6),
     (1, 13),
     (1, 13),
     (1, 13),
     (20, 10),
     (20, 10),
     (20, 10),
     (18, 28),
     (18, 28),
     (18, 28),
     (40, 25),
     (40, 25),
     (40, 25),
     (0, 30),
     (0, 30),
     (0, 30),
     (40, 40),
   ],
'i':   [

     (40, 0),
     (40, 21),
     (40, 21),
     (40, 21),
     (37, 12),
     (37, 12),
     (37, 12),
     (38, 15),
     (38, 15),
     (38, 15),
     (2, 20),
     (2, 20),
     (2, 20),
     (1, 17),
     (1, 17),
     (1, 17),
     (3, 24),
     (3, 24),
     (3, 24),
     (2, 20),
     (2, 20),
     (2, 20),
     (40, 15),
     (40, 15),
     (40, 15),
     (40, 40),
   ],
'j':   [

     (40, 0),
     (40, 21),
     (30, 7),
     (30, 7),
     (30, 7),
     (38, 13),
     (40, 18),
     (29, 29),
     (5, 33),
     (5, 33),
     (5, 33),
     (3, 26),
     (3, 26),
     (8, 40),
     (8, 40),
     (6, 33),
     (25, 28),
     (40, 40),
   ],
'k':   [

     (40, 0),
     (40, 8),
     (40, 8),
     (40, 8),
     (3, 13),
     (3, 13),
     (3, 13),
     (21, 11),
     (21, 11),
     (21, 11),
     (1, 32),
     (1, 32),
     (21, 11),
     (21, 11),
     (21, 11),
     (40, 27),
     (40, 27),
     (40, 27),
     (35, 35),
     (40, 40),
   ],
'l':   [

     (36, 0),
     (22, 7),
     (4, 11),
     (0, 10),
     (3, 9),
     (33, 6),
     (33, 6),
     (33, 6),
     (27, 33),
     (29, 33),
     (29, 33),
     (29, 33),
     (32, 6),
     (32, 6),
     (32, 6),
     (36, 40),
   ],
'm':   [

     (40, 0),
     (40, 8),
     (40, 8),
     (40, 8),
     (3, 13),
     (3, 13),
     (3, 13),
     (29, 19),
     (29, 19),
     (29, 19),
     (2, 32),
     (2, 32),
     (2, 32),
     (40, 30),
     (40, 30),
     (40, 30),
     (40, 40),
   ],
'n':   [

     (40, 0),
     (40, 8),
     (40, 8),
     (40, 8),
     (3, 13),
     (3, 13),
     (3, 13),
     (40, 27),
     (40, 27),
     (40, 27),
     (3, 34),
     (3, 34),
     (3, 34),
     (40, 27),
     (40, 27),
     (40, 27),
     (40, 40),
   ],
'o':   [

     (40, 0),
     (40, 17),
     (38, 28),
     (25, 36),
     (14, 35),
     (1, 24),
     (1, 12),
     (13, 2),
     (35, 5),
     (40, 19),
     (40, 26),
     (40, 40),
   ],
'p':   [

     (40, 0),
     (40, 15),
     (40, 15),
     (40, 15),
     (3, 18),
     (3, 18),
     (1, 25),
     (1, 32),
     (6, 35),
     (13, 35),
     (19, 26),
     (19, 22),
     (16, 17),
     (16, 17),
     (16, 17),
     (40, 15),
     (40, 15),
     (40, 15),
     (40, 40),
   ],
'q':   [

     (40, 0),
     (40, 17),
     (38, 28),
     (34, 32),
     (34, 32),
     (34, 32),
     (24, 17),
     (38, 40),
     (38, 40),
     (34, 32),
     (34, 32),
     (34, 32),
     (23, 36),
     (7, 34),
     (1, 22),
     (3, 8),
     (13, 2),
     (30, 2),
     (40, 16),
     (40, 40),
   ],
'r':   [

     (40, 0),
     (40, 8),
     (40, 8),
     (40, 8),
     (3, 13),
     (3, 13),
     (3, 13),
     (3, 26),
     (10, 32),
     (18, 31),
     (20, 23),
     (20, 11),
     (20, 11),
     (20, 11),
     (40, 29),
     (40, 29),
     (40, 29),
     (40, 40),
   ],
's':   [

     (40, 0),
     (40, 22),
     (33, 5),
     (33, 5),
     (33, 5),
     (40, 17),
     (36, 31),
     (28, 34),
     (17, 22),
     (7, 13),
     (1, 13),
     (0, 25),
     (8, 34),
     (8, 34),
     (8, 34),
     (2, 22),
     (5, 13),
     (8, 13),
     (30, 31),
     (40, 37),
   ],
't':   [

     (40, 0),
     (40, 21),
     (40, 21),
     (40, 21),
     (37, 12),
     (37, 12),
     (37, 12),
     (38, 15),
     (38, 15),
     (38, 15),
     (2, 20),
     (2, 20),
     (2, 20),
     (1, 4),
     (1, 4),
     (1, 4),
     (3, 36),
     (3, 36),
     (3, 36),
     (2, 20),
     (2, 20),
     (2, 20),
     (40, 15),
     (40, 15),
     (40, 15),
     (40, 40),
   ],
'u':   [

     (40, 0),
     (40, 21),
     (40, 21),
     (40, 21),
     (38, 14),
     (31, 8),
     (24, 5),
     (12, 6),
     (1, 10),
     (1, 10),
     (1, 10),
     (16, 5),
     (22, 5),
     (30, 8),
     (38, 17),
     (39, 25),
     (37, 31),
     (24, 37),
     (11, 36),
     (11, 36),
     (11, 36),
     (1, 32),
     (23, 35),
     (40, 38),
     (40, 40),
   ],
'v':   [

     (40, 0),
     (40, 21),
     (40, 21),
     (40, 21),
     (1, 4),
     (1, 4),
     (1, 4),
     (40, 21),
     (40, 21),
     (40, 21),
     (1, 38),
     (1, 38),
     (1, 38),
     (40, 21),
     (40, 21),
     (40, 21),
     (40, 40),
   ],
'w':   [

     (40, 0),
     (39, 3),
     (33, 7),
     (8, 10),
     (6, 9),
     (8, 8),
     (33, 7),
     (38, 10),
     (39, 13),
     (39, 15),
     (37, 17),
     (34, 19),
     (20, 23),
     (13, 23),
     (11, 21),
     (13, 20),
     (18, 20),
     (36, 20),
     (38, 24),
     (39, 28),
     (39, 32),
     (26, 36),
     (14, 36),
     (11, 34),
     (10, 33),
     (9, 32),
     (11, 32),
     (38, 37),
     (40, 40),
   ],
'x':   [

     (40, 0),
     (13, 7),
     (3, 4),
     (1, 2),
     (1, 1),
     (3, 2),
     (11, 13),
     (19, 19),
     (22, 19),
     (25, 17),
     (39, 3),
     (38, 3),
     (36, 4),
     (3, 38),
     (3, 39),
     (4, 39),
     (17, 21),
     (19, 19),
     (23, 19),
     (31, 22),
     (38, 31),
     (39, 39),
   ],
'y':   [

     (40, 0),
     (40, 20),
     (40, 20),
     (40, 20),
     (13, 19),
     (13, 19),
     (13, 19),
     (2, 8),
     (2, 8),
     (2, 8),
     (13, 19),
     (13, 19),
     (13, 19),
     (0, 32),
     (0, 32),
     (0, 32),
     (13, 19),
     (13, 19),
     (13, 19),
     (40, 20),
     (40, 20),
     (40, 20),
     (40, 40),
   ],
'z':   [

     (40, 0),
     (40, 31),
     (39, 32),
     (38, 32),
     (38, 31),
     (38, 7),
     (38, 6),
     (39, 6),
     (40, 7),
     (8, 33),
     (9, 34),
     (10, 33),
     (10, 30),
     (5, 1),
     (6, 0),
     (8, 1),
     (8, 3),
     (8, 31),
     (8, 32),
     (9, 33),
     (10, 32),
     (37, 7),
     (38, 6),
     (38, 7),
     (38, 9),
     (38, 40),
   ],
 })

def getparm(L, name, default=None, getValue=True):
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

def main():
    import sys
    args = sys.argv
    png = getparm(args, "--png")
    if len(args)<2:
        print "please provide a word to encode"
    else:
        testg(args[1].lower(), png)


if __name__=="__main__":
    #dumpPoints()
    main()
