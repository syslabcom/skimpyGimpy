"""
KISS 2D canvas for drawing indexed PNG images
Many optimization opportunities studiously ignored.
"""

# set for extreme boundary case checking
PARANOID = False

# No antialiasing, sorry.
# Rendering of text is particularly slow.
# Lots of unrotated rectangle and a little text are pretty fast, tho.

# Some inspiration drawn from the Adobe Acrobat Portable Document Format
# internal drawing operations.

CORNERS = ( (1,1),(0,1),(1,0),(0,0), )

FILLLIMIT = 111111

import math

def clockwise(points):
    "reverse the points if they aren't clockwise"
    result = list(points)
    testarea = 0
    lastpoint = points[-1]
    for nextpoint in points:
        (x1, y1) = lastpoint
        (x2, y2) = nextpoint
        width = x2-x1
        height = y2+y1
        #print width, height
        testarea += width*height
        lastpoint = nextpoint
    #p "testarea", testarea
    if testarea<0:
        result.reverse()
    return result

class Shape:
    def __init__(this):
        raise ValueError, "virtual superclass"
    def testFunction(this, point):
        raise ValueError, "virtual superclass"
    def convert(this, point):
        "for transforms"
        return point
    def rconvert(this, point):
        return point
    def pixelTest(this,point):
        "return negative if outside, positive inside, 0 if crossing"
        (x,y) = point
        vertices = [ (x+cx, y+cy) for (cx,cy) in CORNERS ]
        tests = map(this.testFunction, vertices)
        maxtest = max(tests)
        mintest = min(tests)
        if maxtest<0:
            return maxtest
        if mintest>0:
            return mintest
        return 0
    def scanLines(this, xmin=None, xmax=None, ymin=None, ymax=None):
        "return y-->( (xon, xoff), (xon2, xoff), ... )"
        from math import floor, ceil
        # brute force implementation using testFunction
        if xmin is None:
            ( (xmin, ymin), (xmax, ymax) ) = this.bbox()
            xmin = int(floor(xmin))
            ymin = int(floor(ymin))
            xmax = int(ceil(xmax))
            ymax = int(ceil(ymax))
        #pr "min/max", ( (xmin, ymin), (xmax, ymax) ) 
        xr = xrange(xmin, xmax+1)
        yr = xrange(ymin, ymax+1)
        #pr "ranges", xr, yr
        result = {}
        for y in yr:
            firstx = None
            line = []
            for x in xr:
                test = this.pixelTest( (x,y) )
                if firstx is None:
                    if test>=0:
                        firstx = x
                else: # firstx is set
                    if test<0:
                        lastx = x
                        line.append( (firstx, lastx) )
                        firstx = None
            if firstx is not None:
                line.append((firstx, xmax))
            if line:
                result[y] = line
##        if 1:
##            ys = result.keys()
##            ys.sort()
##            #pr "dumping scanlines"
##            for y in ys:
##                #pr y, result[y]
        return result
    def points(this, mapValue, xmin=None, xmax=None, ymin=None, ymax=None):
        D = {}
        scanLines = this.scanLines(xmin, xmax, ymin, ymax)
        ##pr "scanlines", scanLines
        for y in scanLines.keys():
            for (xstart, xend) in scanLines[y]:
                for x in xrange(xstart, xend):
                    D[(x,y)] = mapValue
        return D
    def bbox(this):
        raise ValueError, "virtual superclass"

class Circle(Shape):
    def __init__(this, center, radius):
        ##pr "circle", (center,radius)
        (this.centerx, this.centery) = center
        this.radius = radius
        this.radius2 = radius*radius
    def testFunction(this, point):
        "return negative if outside, positive inside"
        (x,y) = point
        dx = x-this.centerx
        dy = y-this.centery
        d2 = dx*dx+dy*dy
        return this.radius2-d2
    def bbox(this):
        r = this.radius
        cx = this.centerx
        cy = this.centery
        return ( (cx-r-1,cy-r-1), (cx+r+1,cy+r+1) )
    def scanLines_old(this, xmin=None, xmax=None, ymin=None, ymax=None):
        # this is a hack... there is an off by one issue
        result1 = Shape.scanLines(this, xmin, xmax, ymin, ymax)
        result = {}
        for y in result1.keys():
            pairs = result1[y]
            result[y] = [ (x1+1,x2) for (x1,x2) in pairs ]
        return result
    def scanLines(this, xmin=None, xmax=None, ymin=None, ymax=None):
        from math import ceil, floor, sqrt
        if xmin is None:
            ( (xmin,ymin), (xmax,ymax) ) = this.bbox()
            xmin = int(floor(xmin))
            xmax = int(ceil(xmax))
            ymin = int(floor(ymin))
            ymax = int(ceil(ymax))
        cx = this.centerx
        cy = this.centery
        ##pr "center", (cx,cy)
        result = {}
        radius2 = this.radius2
        for y in xrange(ymin, ymax+1):
            dy = y-cy
            dx2 = radius2 - dy*dy
            ##pr "(dy,dx2,radius2)", (y,dy,dx2, radius2)
            if dx2>0:
                dx = sqrt(dx2)
                x1 = int(round(cx-dx))
                x2 = int(round(cx+dx))+1
                if x1<x2:
                    result[y]= [ (x1,x2) ]
        return result

class Rectangle(Shape):
    epsilon = 0.001 # fuzz factor to prevent floating point threshholding issues.
    def __init__(this, lowerLeft, width, height):
        ##pr "rect", (lowerLeft, width, height)
        (llx, lly) = (this.llx, this.lly) = lowerLeft
        if width<0:
            raise ValueError, "width must be positive "+repr(width)
        if height<0:
            raise ValueError, "height must be positive "+repr(height)
        this.width = width
        this.height = height
        this.wx = llx+width
        this.hy = lly+height
        ##pr "rect end", (this.wx, this.hy)
    def pixelTest(this,point):
        eps = this.epsilon
        (x,y) = point
        x1 = x+1
        y1 = y+1
        xm = x-1
        ym = y-1
        llx = this.llx
        wx = this.wx
        lly = this.lly
        hy = this.hy
        if x1<llx-eps or y1<lly-eps or xm>wx+eps or ym>hy+eps:
            #pr "out", (x,y)
            #pr x1<llx, y1<lly, x>wx, y>hy
            return -1
        if y1<hy-eps and ym>lly+eps and x1<wx-eps and xm>llx+eps:
            #pr "inside", (x,y)
            #pr y1<hy, y>lly, x1<wx, x>llx
            return 1
        ##pr "border", (x,y)
        ##pr x1<llx, y1<lly, x>wx, y>hy
        ##pr y1<hy, y>lly, x1<wx, x>llx
        return 0
    # someday optimize scanlines
    def testFunction(this,point):
        #pr "testing", point
        eps = this.epsilon
        (x,y) = point
        llx = this.llx
        lly = this.lly
        if x<llx-eps: return -1
        if y<lly-eps: return -1
        if x>llx+this.width+eps: return -1
        if y>lly+this.height+eps: return -1
        return 1
    def bbox(this):
        llx = this.llx
        lly = this.lly
        bbox = ( (llx, lly), (llx+this.width, lly+this.height) )
        #pr "bbox", bbox
        #raise ValueError
        return bbox

def LineSegment(startPoint, endPoint, width, StartCapSize=None, EndCapSize=None,
        epsilon=0.1):
    #pr "LineSegment", (startPoint, endPoint, width, StartCapSize, EndCapSize)
    import math
    if StartCapSize is None:
        StartCapSize = 0
    if EndCapSize is None:
        EndCapSize = StartCapSize
    (x1, y1) = startPoint
    (x2, y2) = endPoint
    dx = x2-x1
    dy = y2-y1
    d2 = (x1-x2)**2 + (y1-y2)**2
    halfwidth = width/2.0
    if d2<1:
        # 0 length segment
        return Rectangle((x1-halfwidth, -StartCapSize), width, EndCapSize)
    d = math.sqrt(d2)
    (v1, v2) = unitvector = (dx/d, dy/d)
    (u1, u2) = (-v2, v1)
    #pr "units", unitvector, (u1, u2)
    # compute the lower left corner for the rectangle, unrotated, untranslated
    xL = x1 - v1*(StartCapSize) - u1*(halfwidth)
    yL = y1 - v2*(StartCapSize) - u2*(halfwidth)
    LL = (xL, yL)
    cd = max(0, d+EndCapSize+StartCapSize)
    #pr "Rectangle", ( (0,0), cd, width )
    Rect = Rectangle( (0,0), cd, width )
    #pr "rotate", unitvector
    RotateRect = RotateV( Rect, unitvector )
    #pr "translate", LL
    ShiftRect = Translate( RotateRect, LL )
    return ShiftRect

class Affine0(Shape):
    "affine, not optimized for composition (see Affine)"
    def __init__(this, shape, coef, rcoef):
        this.shape = shape
        this.coef = coef
        this.rcoef = rcoef
        ((this.ax, this.bx, this.cx), (this.ay, this.by, this.cy)) = coef
        ((this.rax, this.rbx, this.rcx), (this.ray, this.rby, this.rcy)) = rcoef
    def testFunction(this, point):
        p0 = this.rconvert(point)
        return this.shape.testFunction(p0)
    def pixelTest(this,point):
        p0 = this.rconvert(point)
        return this.shape.pixelTest(p0)
    def convert(this, point):
        (x0,y0) = point
        x = this.ax*x0 + this.bx*y0 + this.cx
        y = this.ay*x0 + this.by*y0 + this.cy
        return (x,y)
    def rconvert(this, point):
        (x0,y0) = point
        x = this.rax*x0 + this.rbx*y0 + this.rcx
        y = this.ray*x0 + this.rby*y0 + this.rcy
        return (x,y)
    def bbox(this):
        from math import floor, ceil
        (p1, p2) = ((x1,y1), (x2,y2)) = this.shape.bbox()
        vertices = (p1, p2, (x1,y2), (x2,y1))
        ##pr "vertices", vertices
        mvertices = map(this.convert, vertices)
        #print "mvertices", mvertices
        xs = [x for (x,y) in mvertices]
        ys = [y for (x,y) in mvertices]
        minx = floor(min(xs))
        maxx = ceil(max(xs))
        miny = floor(min(ys))
        maxy = ceil(max(ys))
        return ( (minx, miny), (maxx, maxy) )

def compose(coef1, coef2):
    "aka affine matrix multiplication"
    (cx, cy) = coef1
    m2 = (cx, cy, (0,0,1))
    (cx, cy) = coef2
    m1 = (cx, cy, (0,0,1))
    r3 = range(3)
    mout = [ [0]*3, [0]*3, [0]*3 ]
    for i in r3:
        for j in r3:
            s = 0
            for k in r3:
                s += m1[i][k]*m2[k][j]
            mout[i][j] = s
    #print mout[2]
    return mout[:2]

def Affine(shape, coef, rcoef):
    import math
    coefFinal = coef
    rcoefFinal = rcoef
    shapeFinal = shape
    if isinstance(shape, Affine0):
        coefFinal = compose(shape.coef, coef)
        rcoefFinal = compose(rcoef, shape.rcoef)
        shapeFinal = shape.shape
    elif isinstance(shape, Circle):
        # XXXX OPTIMIZATION ASSUMING TRANSFORMATION IS NOT DEFORMING
        test = Affine0(shapeFinal, coefFinal, rcoefFinal)
        (cx, cy) = center0 = (shape.centerx, shape.centery)
        radius0 = shape.center
        rhs0 = (cx+radius0, cy)
        center = test.convert(center0)
        rhs = test.convert(rhs0)
        dx = center[0]-rhs[0]
        dy = center[1]-rhs[1]
        d2 = dx*dx+dy*dy
        radius = math.sqrt(d2)
        return Circle(center, radius)
    return Affine0(shapeFinal, coefFinal, rcoefFinal)

def Translate(shape, vector):
    (dx, dy) = vector
    coef = ((1,0,dx), (0,1,dy))
    rcoef = ((1,0,-dx), (0,1,-dy))
    return Affine(shape, coef, rcoef)

def Rotate(shape, theta):
    "rotate by radians"
    import math
    s = math.sin(theta)
    c = math.cos(theta)
    return RotateV(shape, (c,s))

def RotateV(shape, vector):
    "rotate (and scale) by vector"
    (c,s) = vector
    coef = ( (c, -s, 0), (s, c, 0) )
    rcoef = ( (c, s, 0), (-s, c, 0) )
    return Affine(shape, coef, rcoef)

class Canvas:
    fontRadiusEnhancement = 0.1
    minx = maxx = miny = maxy = None
    filename = "example.png"
    def __init__(this):
        # index to colors
        white = (0xff,0xff,0xff)
        this.colors = {0: (1,1,1), 1:white}
        this.rcolors = rcolors = {white: 1}
        this.fontNameToPath = {}
        this.fontNameToFont = {}
        this.lineWidth = 2
        this.lineCap = 2
        this.paintColor = None
        this.pixels = {}
        this.stateStack = []
        this.fontName = None
        this.fontScale = 1.0
        this.fontRadius = 1.1
        this.transformTracker = Rectangle( (0,0), 1,1) # dummy object
        this.backgroundColor = None
        # javascript callbacks
        this.backgroundCallback = None
        this.foregroundCallback = None
        this.callbacks = {}
    def setBackgroundCallback(this, callBackString):
        this.backgroundCallback = callBackString
    def setCallBack(this, callBackString):
        this.foregroundCallback = callBackString
    def resetCallBack(this):
        this.foregroundCallback = None
    def setBackgroundColor(this, r, g, b):
        this.backgroundColor = (r,g,b)
    def crop(this, minx, miny, maxx, maxy):
        if minx>=maxx or miny>=maxy:
            raise ValueError, "bad bounds: "+repr((minx, miny, maxx, maxy))
        this.minx = minx 
        this.miny = miny
        this.maxx = maxx
        this.maxy = maxy
    def addFont(this, name, path):
        import os
        if not os.path.exists(path):
            raise ValueError, "no such file "+repr(path)
        this.fontNameToPath[name] = path
        if this.fontName is None:
            this.setFont(name)
    def getFont(this, name):
        import bdf
        fontpath = this.fontNameToPath.get(name, None)
        if fontpath is None:
            raise ValueError, "no such font name added "+repr(name)
        font = this.fontNameToFont.get(name, None)
        if font is None:
            font = bdf.font()
            font.loadFilePath(fontpath)
            this.fontNameToFont[name] = font
        return font
    def setFont(this, name, scale=1.0, radius=None):
        fontpath = this.fontNameToPath.get(name, None)
        if fontpath is None:
            raise ValueError, "no such font name added "+repr(name)
        if scale<=0:
            raise ValueError, "too small scale "+repr(scale)
        if radius is None:
            radius = scale/2.0 + this.fontRadiusEnhancement
        this.fontRadius = radius
        this.fontScale = scale
        this.fontName = name
    def saveState(this):
        state = {}
        state["paintColor"] = this.paintColor
        state["lineCap"] = this.lineCap
        state["lineWidth"] = this.lineWidth
        state["transformTracker"] = this.transformTracker
        state["fontName"] = this.fontName
        state["fontScale"] = this.fontScale
        state["fontRadius"] = this.fontRadius
        state["foregroundCallback"] = this.foregroundCallback
        this.stateStack.append(state)
    def restoreState(this):
        if not this.stateStack:
            raise ValueError, "no state saved on state stack"
        state = this.stateStack[-1]
        del this.stateStack[-1]
        this.paintColor = state["paintColor"] 
        this.lineCap = state["lineCap"]
        this.lineWidth = state["lineWidth"]
        this.transformTracker = state["transformTracker"]
        this.fontName = state["fontName"]
        this.fontScale = state["fontScale"]
        this.fontRadius = state["fontRadius"]
        this.foregroundCallback = state["foregroundCallback"]
    def convert(this, point):
        t = this.transformTracker
        return t.convert(point)
    def translate(this, dx, dy):
        t = this.transformTracker
        this.transformTracker = Translate(t, (dx, dy))
    def rotateRadians(this, theta):
        t = this.transformTracker
        this.transformTracker = Rotate(t, theta)
    def rotate(this, degrees):
        import math
        radians = (math.pi*degrees)/180.0
        this.rotateRadians(radians)
    def transformShape(this, shape):
        t = this.transformTracker
        if isinstance(t, Affine0):
            coef = t.coef
            rcoef = t.rcoef
            shape = Affine0(shape, coef, rcoef)
        return shape
    def setColor(this, r,g,b):
        this.setColorV((r,g,b))
    def setColorV(this, rgb):
        #print "setColorV", rgb
        for i in rgb:
            if i!=int(i):
                raise ValueError, "color component must be int: "+repr(i)
            if i<0 or i>255:
                raise ValueError, "bad color component "+repr(i)
        if this.rcolors.has_key(rgb):
            colorIndex = this.rcolors[rgb]
        else:
            colorIndex = len(this.colors)
            if colorIndex>255:
                raise ValueError, "too many colors at "+repr(rgb)
            this.rcolors[rgb] = colorIndex
            this.colors[colorIndex] = rgb
        this.paintColor = colorIndex
    def setCap(this, lineCap):
        if lineCap<0:
            raise ValueError, "lineCap cannot be negative "+repr(lineCap)
        this.lineCap = lineCap
    def setWidth(this, width):
        if width<0:
            raise ValueError, "width cannot be negative "+repr(width)
        this.lineWidth = width
    def addLine(this, startPoint, endPoint):
        width = this.lineWidth
        cap = this.lineCap
        L = LineSegment(startPoint, endPoint, width, cap)
        this.plot(L)
    def addLines(this, points, closed=False):
        if not points:
            return
        width = this.lineWidth
        cap = this.lineCap
        thiscap = cap
        if closed:
            points = points+ [ points[0] ]
            thiscap = cap = 0
        recentpoint = points[0]
        halfwidth = width/2.0
        for nextpoint in points[1:-1]:
            L = LineSegment(recentpoint, nextpoint, width, thiscap, 0)
            this.plot(L)
            # add circle at end
            if halfwidth>=0.5:
                C = Circle(nextpoint, halfwidth)
                this.plot(C)
            thiscap = 0
            recentpoint = nextpoint
        lastpoint = points[-1]
        L = LineSegment(recentpoint, lastpoint, width, thiscap, cap)
        this.plot(L)
        if closed and halfwidth>=0.5:
            C = Circle(lastpoint, halfwidth)
            this.plot(C)
    def fillPolygon(this, points):
        points = clockwise(points)
        # find border points
        borders = {} # integerx --> [integery]
        lastpoint = points[-1]
        lastlinepoint = None
        for point in points:
            (x1,y1) = point
            (x2,y2) = lastpoint
            firstx = int(math.ceil(x1))
            lastx = int(math.ceil(x2))
            increment = 1
            #p
            #p "point", point
            #p "last", lastpoint
            #p "firstx", firstx, "lastx", lastx
            dx = x2-x1
            adx = abs(dx)
            #if adx<0.001:
            #    increment = 0
            if x1>x2:
                #(firstx, lastx) = (lastx, firstx)
                increment = -1
                xs = xrange(lastx, firstx)
            else:
                xs = xrange(firstx, lastx)
            for x in xs:
                ys = borders.get(x)
                if ys is None:
                    ys = {}
                if adx>0.01:
                    y = (y2*(x-x1) + y1*(x2-x))/dx
                else:
                    y = y1
                y = int(y)
                ys[y] = ys.get(y,0)+increment
                #p "point", (x,y), increment
                borders[x] = ys
            lastpoint = point
        # plot pixels between border points
        D = {}
        color = this.paintColor
        xs = borders.keys()
        xs.sort()
        for x in xs:
            xborders = borders[x]
            debugitems = xborders.items()
            ys = xborders.keys()
            #ys.sort()
            # since polygon is clockwise, first point should always be
            #p "plotting", x#, ys
            #p debugitems
            summation = 0
            miny = min(ys)
            maxy = max(ys)
            #p "running from", miny, maxy
            for y in range(miny, maxy+1):
                if summation<0:
                    pass
                    #raise ValueError, "negative summation? at "+ repr((x,y))
                    #p "WARNING: negative summation? at "+ repr((x,y, summation))
                summation += xborders.get(y, 0)
                if xborders.has_key(y) or summation>0:
                    point = (x,y)
                    D[ point ] = color
                    #p "point", point, summation
            if summation:
                #p "for", x, "final sum is", summation
                items = xborders.items()
                items.sort()
                #p "bad summation %s %s"%(summation,items)
                raise "bad summation %s %s"%(summation,items)
        this.updatePixels(D)
    def addRect(this, llx, lly, width, height):
        #print "rect", (llx, lly, width, height)
        R = Rectangle((llx, lly), width, height)
        this.plot(R)
    def addCircle(this, cx, cy, radius):
        #print "circle", (cx,cy,radius)
        C = Circle((cx,cy), radius)
        this.plot(C)
    def addText(this, x, y, text, shiftWidth=0.0):
        import bdf
        fontName = this.fontName
        fontScale = this.fontScale
        radius = this.fontRadius
        fn = this.getFont(fontName)
        p = bdf.pixelation(fn, text)
        pw = p.width()
        sx = x + shiftWidth*pw*fontScale
        p.drawToCanvas(sx, y, this, radius, fontScale)
    def centerText(this, x, y, text):
        return this.addText(x,y,text, shiftWidth=-0.5)
    def rightJustifyText(this, x, y, text):
        return this.addText(x,y,text, shiftWidth=-1.0)
    def plot(this, shape):
        T = this.transformShape(shape)
        color = this.paintColor
        if color is None:
            raise ValueError, "canvas color not set"
        d = T.points(color)
        this.updatePixels(d)
    def updatePixels(this, d):
        # XXX possible bug: overwritten callbacks are not cancelled when no callback set.
        this.pixels.update(d)
        fc = this.foregroundCallback
        # record callback info if set.
        if fc is not None:
            cb = this.callbacks
            for point in d.keys():
                cb[point] = fc
    def plotDict(this, startx, starty, D, radius, scaleFactor):
        "plot the (x,y) key points of a dictionary as circles (for pixelized font rendering, for example)"
        C = Circle((0,0), radius)
        pts = C.points(1).keys()
        color = this.paintColor
        #pixels = this.pixels
        newpixels = {}
        for (x,y) in D.keys():
            sx = startx+scaleFactor*x
            sy = starty+scaleFactor*y
            (dx,dy) = this.convert( (sx,sy) )
            for (px,py) in pts:
                tp = (int(round(dx+px)),int(round(dy+py)))
                newpixels[tp] = color
        this.updatePixels(newpixels)
    def growFill(this, x, y, stopColorRGB=None, countLimit=FILLLIMIT):
        "fill a region to the border colored by stopColor (or to color change)"
        # KISS implementation
        # if min/max coords are not set this may loop infinitely
        # like the "paint bucket tool" in most paint programs
        fillColorIndex = this.paintColor
        stopIndex = None
        if stopColorRGB:
            if this.rcolors.has_key(stopColorRGB):
                stopIndex = this.rcolors[stopColorRGB]
            else:
                raise ValueError, "stop color has not yet been used "+repr(rgb)
        (cx,cy) = this.convert( (x,y) )
        minx = this.minx
        maxx = this.maxx
        miny = this.miny
        maxy = this.maxy
        cx = int(round(cx))
        cy = int(round(cy))
        cp = (cx,cy)
        stack = [ cp ]
        pixels = this.pixels
        insideIndex = pixels.get( cp, 0 )
        newpixels = {}
        done = {}
        count = 0
        while stack:
            count += 1
            if countLimit and countLimit<count:
                raise ValueError, "fill iteration limit exceeded (sanity check).  rerun with countLimit=None if you dare."
            p = stack[-1]
            del stack[-1]
            if done.has_key(p):
                continue
            done[p] = True
            doFill = True
            thisIndex = pixels.get( p, 0 )
            if thisIndex==stopIndex:
                #print "hit stop index", (thisIndex, stopIndex)
                doFill = False
            if stopIndex is None and thisIndex!=insideIndex:
                #print "hit outside index", (thisIndex, insideIndex, stopIndex)
                doFill = False
            (px,py) = p
            if maxx is not None and px>maxx:
                doFill = False
            if minx is not None and px<minx:
                doFill = False
            if maxy is not None and py>maxy:
                doFill = False
            if miny is not None and py<miny:
                doFill = False
            if doFill:
                #print "filling", p, (thisIndex, insideIndex, stopIndex), len(stack)
                newpixels[p] = fillColorIndex
                (px,py) = p
                for delta in (-1,1):
                    pa = (px+delta, py)
                    if not done.has_key(pa):
                        #print "addint", pa
                        stack.append(pa)
                    pb = (px, py+delta)
                    if not done.has_key(pb):
                        #print "adding", pb
                        stack.append(pb)
        this.updatePixels(newpixels)
    def dumpToPNG(this, filename):
        import KiPNG
        this.filename = filename
        if not this.pixels:
            raise ValueError, "no pixels plotted"
        transparentIndex = 0
        if this.backgroundColor is not None:
            #print "cancelling transparency"
            this.colors[0] = this.backgroundColor
            transparentIndex = None
        r = KiPNG.DictToPNG(this.pixels, filename, colorDict=this.colors,
                        transparentIndex=transparentIndex,
                        minx=this.minx, miny=this.miny, maxx=this.maxx, maxy=this.maxy)
        return r
    def getCallbackRunLengthDictionary(this):
        "dictionary of y-->[ (xstart, xend, callbackstring), ... ] for defined callbacks"
        # KISS, probably could be made faster for large images
        cb = this.callbacks
        points = cb.keys()
        allpoints = this.pixels.keys()
        #points.sort()
        xs = [x for (x,y) in allpoints]
        ys = [y for (x,y) in allpoints]
        miny = min(ys)
        maxy = max(ys)
        minx = min(xs)
        maxx = max(xs)
        #print minx, maxx, miny, maxy, maxx-minx, maxy-miny
        if this.miny is None:
            this.miny = miny
            this.maxy = maxy
            this.minx = minx
            this.maxx = maxx
        miny = this.miny
        maxy = this.maxy
        minx = this.minx
        maxx = this.maxx
        #print this.minx, this.maxx, this.miny, this.maxy, this.maxx-this.minx, this.maxy-this.miny
        bcb = this.backgroundCallback
        result = {}
        rx = range(minx, maxx+1)
        ry = range(miny, maxy+1)
        for y in ry:
            startx = minx
            lastcallback = None
            runlengths = []
            for x in rx:
                point = (x,y)
                thiscallback = cb.get(point, bcb)
                if thiscallback!=lastcallback:
                    if lastcallback:
                        # emit a run length
                        runlength = [startx-minx, x-minx, lastcallback]
                        #this.pixels[ (startx,y) ] = 1 # debug
                        #this.pixels[ (x,y) ] = 1 # debug
                        runlengths.append(runlength)
                    lastcallback = thiscallback
                    startx = x
            # emit final runlength
            if lastcallback and startx<maxx:
                runlength = [startx-minx, maxx-minx, lastcallback]
                #this.pixels[ (startx,y) ] = 1 # debug
                #this.pixels[ (maxx,y) ] = 1 # debug
                runlengths.append(runlength)
            result[y-miny] = runlengths
        #runlengthDebugPlot(result, minx, miny, maxx, maxy)
        return result
    def jsRunLengths(this):
        D = this.getCallbackRunLengthDictionary()
        ys = D.keys()
        ys.sort()
        ys.reverse()
        L = []
        for y in ys:
            runlengths = D[y]
            L.append("%s : %s" % (y, runlengths))
        result = ",\n".join(L)
        return "{\n%s\n}" % result
    def dumpJavascript(this, toFileName, imageName, functionName):
        f = file(toFileName, "w")
        #f.write(this.jsRunLengths()) # temp
        runlengths = this.jsRunLengths()
        D = {}
        D["scanLines"] = runlengths
        D["filename"] = this.filename
        D["imageName"] = repr(imageName)
        D["function"] = functionName
        if this.backgroundCallback:
            D["defaultString"] = repr(this.backgroundCallback)
        else:
            D["defaultString"] = "null"
        D["xpixels"] = this.maxx-this.minx
        D["ypixels"] = this.maxy-this.miny
        text = JSTEMPLATE % D
        f.write(text)
        f.close()
    def exampleHTML(this, htmlFileName, jsFileName, pngFileName, imageName, functionName,
                       canvasLocation="canvas.js"):
        D = {}
        D["jsFileName"] = jsFileName
        D["pngFileName"] = pngFileName
        D["imageName"] = imageName
        D["functionName"] = functionName
        D["canvasLocation"] = canvasLocation
        text = HTMLTEMPLATE % D
        f = open(htmlFileName, "w")
        f.write(text)
        f.close()

def runlengthDebugPlot(D,xmin,ymin,xmax,ymax):
    c = Canvas()
    c.setBackgroundColor(0,0,0)
    c.setColor(0,0,0xff)
    c.addRect(0,0,2,2)
    c.addRect(xmax-xmin-2,ymax-ymin-2,2,2)
    c.setColor(0, 0xff, 0)
    for y in D.keys():
        for (xstart, xend, dummy) in D[y]:
            c.addCircle(xstart,y,1)
    c.setColor(0xff, 0, 0)
    for y in D.keys():
        for (xstart, xend, dummy) in D[y]:
            c.addCircle(xend,y,1)
    c.dumpToPNG("runlengths.png")
    print "wrote runlengths.png"

HTMLTEMPLATE = """

<!--

This html example file was automatically generated by skimpyGimpy.canvas.
It will work only if the PNG image file "%(pngFileName)s", the
javascript coordinates file "%(jsFileName)s", and the javascript
utility file %(canvasLocation)s are placed in the appropriate directories.

-->

<html>
<head>
<title>test for mouse tracking for image %(pngFileName)s</title>

<!-- %(canvasLocation)s contains required utilities -->
<script src="%(canvasLocation)s"></script>

<!--
Below is a simple example callback function, required by %(jsFileName)s.
In real use you will want to customize this code.
-->
<script>
function %(functionName)s(alertString, x, y, event, image) {
	var span = document.getElementById("%(imageName)s_span");
	span.innerHTML = "%(functionName)s called with "+alertString+
            "<br>coords "+x+" "+y+
            " <br>event.type="+event.type+
            " <br>image.id="+image.id+
            " <br>offsets "+window["pageXOffset"]+" "+window["pageYOffset"];
}
</script>

</head>
<body>

<center>
<h1>Test and demo of mouse tracking for image %(pngFileName)s</h1>

<p><b>
  This automatically generated html example file demonstrates
  how to use the javascript file <code>%(jsFileName)s</code> to map mouse
  events over regions inside image <code>%(pngFileName)s</code> to javascript
  call back actions defined in the function <code>%(functionName)s.</code>
</b></p>

<!-- image placed here -->
<img src="%(pngFileName)s" id="%(imageName)s">

<!-- import the automatically generated javascript after "canvas.js" and the image declaration -->
<script src="%(jsFileName)s"></script>

<!-- function %(functionName)s writes information into span %(imageName)s_span -->
<br>
<span id="%(imageName)s_span">information about the mouse event over
   %(pngFileName)s should appear here.</span>

</center>
</body>
"""

JSTEMPLATE = """
// This javascript file was automatically generated by skimpyGimpy.canvas.
//
// To work it needs to be included in an HTML document after the declaration
// of the skimpyGimpy generated image %(filename)s which should be declared
// something like:
//   <img src="%(filename)s" id="%(imageName)s" ...>
// The HTML document must also include canvas.js (distributed with skimpyGimpy).

var scanLines = %(scanLines)s;

bindTracking(%(imageName)s, %(function)s, %(defaultString)s, %(xpixels)s, %(ypixels)s, scanLines);
"""

def jsCallBackTest(pngFileName="K.png", jsFileName="K.js", htmlFileName="K.html"):
    c = Canvas()
    c.setBackgroundColor(0,0,0)
    c.setColor(0,0,0xff)
    c.addFont("propell", "../fonts/mlmfonts/propell.bdf")
    c.setFont("propell", 7, 7)
    c.setCallBack("inside K");
    c.addText(-20,-8, "K")
    c.setCallBack("inside J");
    c.setColor(222,111,0);
    c.addText(20,20, "J")
    c.setCallBack("inside E");
    c.setColor(0,111,0);
    c.addText(-10,40, "E")
    c.setColor(155,100,80)
    c.setCallBack("left hand polygon")
    lhp = [ (0,0), (0,-60), (20,-60), (0,-40), (20,-20) ]
    c.fillPolygon( lhp )
    c.setColor(80,155,100)
    c.setCallBack("right hand polygon")
    #c.addLines(lhp)
    c.fillPolygon( [ (20,0), (20,-60), (0,-40), (20,-20), (0,0)] )
    c.setBackgroundCallback("out")
    c.dumpToPNG(pngFileName)
    imageName = "Kimage"
    functionName = "Kclick"
    c.dumpJavascript(jsFileName, imageName, functionName)
    c.exampleHTML(htmlFileName, jsFileName, pngFileName, imageName, functionName)

def polyTest(outfile="poly.png"):
    c = Canvas()
    c.setColor(0xff,77,77)
    poly = [(0,0), (10, 50), (0,100), (50,50), (100,100), (100,0)]
    poly = [ (50,0), (50,-100), (0,-100), (30,-50), (0,0) ]
    poly = [ (5,0), (5,-10), (0,-10), (3,-5), (0,0) ]
    poly = [ (0,100), (100,100), (100,90), (0,50), (100,70), (100,60), (0,50), (100,40), (100,30), (0,50), (100,0), (0,0) ]
    poly = [ (0,50), (50,0), (25,0), (25,50), (0,25), (25, 50), (50,50), (0,0) ]
    #poly = [ (0,0), (0,10), (6,10), (3,10), (10,10), (10,0) ]
    #poly = [ (0,0), (0,10), (10,10), (10,0), (3,0), (6,0), (3,0), (6,0) ]
    #cpoly = list(poly)
    #cpoly.reverse()
    #poly = poly+ [(0,0)] + cpoly
    #poly.reverse()
    poly = [ (0,0), (10,0), (0,0), (10,0), (0,0), (10,0), (10,10), (10,0), (10,10) ]
    poly = [ (0,0), (10,0), (10,5), (0,5), (10,5), (10,10), (0,10) ]
    c.fillPolygon( poly )
    #c.lineWidth = 1
    #c.setColor(77,77,77)
    #c.addLines( poly )
    c.dumpToPNG(outfile)

def fillCircleTest(outfile="fcirc.png"):
    import math
    radius = 20
    steps = 10
    delta = 8*math.pi/steps
    poly = [ ( (radius-i*delta)*math.cos(i*delta), (radius-i*delta)*math.sin(i*delta) ) for i in xrange(steps) ]
    c = Canvas()
    c.lineWidth = 1
    c.setColor(0,77,77)
    c.addLines(poly, closed=True)
    c.setColor(0xff,77,77)
    c.fillPolygon( poly )
    c.setColor(77,77,77)
    c.addLines(poly, closed=True)
    c.setColor(0,0,77)
    rr = range(-radius/2,radius/2)
    for i in rr:
        for j in rr:
            c.addRect(i*2,j*2,0,0)
    c.setColor(0,222,0)
    for i in rr:
        c.addRect(i*2,0,0,0)
        c.addRect(0,i*2,0,0)
    c.dumpToPNG(outfile)
    
def fillTest(outfile="fill.png", doStopColor=False):
    print "writing", outfile
    c = Canvas()
    c.lineWidth = 4
    c.setColor(0xff,77,77)
    c.addLine((-10,-10), (110,110))
    c.setColor(77,77,77)
    c.rotate(30)
    c.addLines( [(0,0), (0,100), (100,100), (100,0)], closed=True)
    c.setColor(77,0xff,77)
    if doStopColor:
        c.growFill(50,20,(77,77,77))
    else:
        c.growFill(50,20)
    c.dumpToPNG(outfile)
    
def fillTest0(outfile="fill0.png", doStopColor=True):
    print "writing", outfile
    c = Canvas()
    c.lineWidth = 1
    c.setColor(77,77,77)
    c.rotate(30)
    c.addLines( [(0,0), (0,5), (5,5), (5,0)], closed=True)
    c.setColor(77,0xff,77)
    if doStopColor:
        c.growFill(3,3,(77,77,77))
    else:
        c.growFill(3,3)
    c.dumpToPNG(outfile)

def test1(fn="test1.png"):
    print "writing", fn
    c = Canvas()
    c.lineCap = 20
    for (lw,closed,color) in [(12,False,(0xff,0,0)), (4,True,(0,0xff,0xff))]:
        c.lineWidth = lw
        c.setColorV(color)
        c.addLines([ (0,0), (50,50), (0,100), (50,150), (0,200), (50,250)], closed)
    c.dumpToPNG(fn)

def test0(fn="test0.png", fontdir="../fonts/"):
    print "writing", fn
    c = Canvas()
    c.setBackgroundColor(10,50,99)
    c.setWidth(10)
    c.setColor(77,88,22)
    c.addLine((0,100), (100,0))
    c.addRect(10, 10, 100, 10)
    #c.addRect(10,10, 20, 5)
    c.setColor(77,0,0)
    c.addRect(5,5,10, 100)
    c.addCircle(10,-10,40)
    c.setColor(44,99,99)
    c.translate(-1, -3)
    c.saveState()
    c.rotate(30)
    c.translate(-30,50)
    c.addRect(1,1,2,50)
    c.restoreState()
    c.addRect(5,5, 50, 13)
    c.addFont("atari", fontdir+"atari-small.bdf")
    c.setFont("atari", 2.0, 0.7)
    c.saveState()
    c.setColor(99,99,0xff)
    c.rotate(5)
    c.addText(20,0, "TEXT EXAMPLE")
    c.rotate(85)
    c.centerText(20,40, "TEXT EXAMPLE")
    c.rotate(5)
    c.rightJustifyText(20,80, "TEXT EXAMPLE")
    c.restoreState()
    c.setColor(0,99,0xff)
    c.setWidth(1)
    c.addLines([ (0,0), (50,50), (0,100), (50,150), (0,200), (50,250)])
    c.dumpToPNG(fn)

def ctest(fn="ctest.png"):
    print "writing", fn
    c = Canvas()
    c.setColor(77,88,22)
    c.addCircle( 10, 0, 5)
    c.setColor(77,88,00)
    c.addCircle( 0, 10, 5)
    c.setColor(77,00,22)
    c.addCircle( 20, 0, 5)
    c.setColor(0,88,22)
    c.addCircle( 0, 20, 5)
    c.setColor(77,0,0)
    c.addCircle( 10, 20, 5)
    c.setColor(0,0,0)
    c.addCircle( 20, 10, 5)
    c.dumpToPNG(fn)

def ctest2(fn="ctest2.png"):
    print "writing", fn
    c = Canvas()
    c.setColor(77,88,22)
    c.addCircle(0, 0, 50)
    c.setCap(0)
    c.setWidth(1)
    for i in range(30):
        c.setColor(i*5, 255-i*5, 0)
        c.addLine( (0,0), (0,50) )
        c.rotate(10)
    c.dumpToPNG(fn)

def fonttest000(filename="fonttest000.png", fontdir="../fonts/"):
    import bdf
    print "writing", filename
    fn = bdf.font()
    fn.loadFilePath(fontdir+"cursive.bdf")
    p = bdf.pixelation(fn, "100,100")
    c = Canvas()
    c.setColor(77,88,22)
    c.rotate(55)
    p.drawToCanvas(100,100,c,1.6,2)
    c.dumpToPNG(filename)

def cltest(fn="cltest.png"):
    c = Canvas()
    c.setColor(77,88,22)
    #c.addRect(-10,-10,20,20)
    c.setWidth(20)
    c.setCap(0)
    c.addLine( (-100,0), (10,0) )
    c.setColor(0, 0xff,0)
    c.addCircle(0,0,10)
    c.crop(-50,-50,50,50)
    c.dumpToPNG(fn)

def fontsTest(filename="fontsTest.png", fontdir="../fonts/"):
    print "writing", filename, "SSLLOOWWWLLLLYYYYYY"
    fontnames = [#"atari-small.bdf",
             "cursive.bdf",
             "radon-wide.bdf",
             #"mlmfonts/monoell.bdf",
             "mlmfonts/monosimple.bdf",
             #"mlmfonts/propell.bdf",
             "mlmfonts/proposimple.bdf",
             ]
    c = Canvas()
    c.radiusAdjustment = -0.2
    c.setColor(77,88,22)
    scale = 1.44
    for fn in fontnames:
        print "adding font", fn
        c.addFont(fn, fontdir+fn)
    for (rotate, fradius) in ((0,0.8), (90,0.8), (135, 0.8)):
        print "rotating", rotate
        y = 0
        radius = scale*fradius
        c.rotate(rotate)
        for fn in fontnames:
            c.setFont(fn, scale, radius)
            y-=30
            c.addText(0,scale*y, "abcdefghijklmnop01234567: "+fn)
    print "now dumping"
    c.crop(-400,-400,400,400)
    c.dumpToPNG(filename)

def allTests():
    fillCircleTest()
    polyTest()
    jsCallBackTest()
    fillTest()
    fillTest0()
    test0()
    ctest()
    ctest2()
    fonttest000()
    cltest()
    fontsTest()
    test1()
    
if __name__=="__main__":
    allTests()


        
