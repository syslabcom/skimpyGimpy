
"""parse state boundary information"""

filename = "st99_d00.dat"

fipsfilename = "st99_d00a.dat"

class stateBoundary:
    def __init__(this):
        this.identity = None
        this.d = {}
        this.pairs = None
        this.name = None
        this.fips = None
        this.fipsNum = None
    def setName(this, name, fips):
        this.name = name
        this.fips = fips
        this.fipsNum = int(fips, 10)
    def parse(this, f):
        "return False on end of file"
        d = this.d
        done = False
        while not done:
            line = f.readline()
            if not line:
                return False
            else:
                split = line.split()
                if split[0].upper() == "END":
                    done = True
                else:
                    floats = list(map(float, split))
                    latlon = floats[-2:]
                    lat = -1
                    if len(latlon)>1:
                        (lat, lon) = latlon
                    # ignore if latitude is positive
                    if lat>0:
                        print("WARNING: IGNORING LATITUDE", (this.identity, split))
                        this.d = {}
                        return True
                    count = len(d)
                    d[count] = latlon
                    if len(floats)==3:
                        this.identity = int(floats[0])
        return True
    def prepare(this):
        d = this.d
        r = list(range(len(d)))
        pairs = list(r)
        print(this.identity, len(d), d[0], d[1], d[2], d[3])
        minlat = maxlat = d[0][0]
        minlon = maxlon = d[0][1]
        for i in r:
            pair = d[i]
            (lat,lon) = pair
            minlat = min(minlat, lat)
            maxlat = max(maxlat, lat)
            minlon = min(minlon, lon)
            maxlon = max(maxlon, lon)
            pairs[i] = pair
        this.minlat = minlat
        this.maxlat = maxlat
        this.minlon = minlon
        this.maxlon = maxlon
        this.pairs = pairs
    def preplot(this, pixelMax=200):
        minlat = this.minlat
        minlon = this.minlon
        maxlat = this.maxlat
        maxlon = this.maxlon
        dlon = maxlon-minlon
        dlat = maxlat-minlat
        dmax = max(dlon, dlat)
        scaleFactor = pixelMax*1.0/dmax
        this.replot(scaleFactor)
    def replot(this, scaleFactor):
        indexToPoints = {}
        pointsToIndex = {}
        for (lat,lon) in this.pairs:
            slat = int(lat*scaleFactor)
            slon = int(lon*scaleFactor)
            slatlon = (slat, slon)
            if not (slatlon in pointsToIndex):
                index = len(pointsToIndex)
                pointsToIndex[slatlon] = index
                indexToPoints[index] = slatlon
                #print index, slatlon
        r = list(range(len(pointsToIndex)))
        plotpoints = list(r)
        for i in r:
            plotpoints[i] = indexToPoints[i]
        this.plotpoints = plotpoints
    def plotLines(this, canvas):
        points = this.plotpoints
        if len(points)>1:
            canvas.fillPolygon(this.plotpoints[1:])
        elif points:
            #print "WARNING: SINGLE POINT", this.identity, points
            (x,y) = points[0]
            canvas.addCircle( x, y, 1)
        else:
            print("NO POINTS?", this.identity, points)
    def label(this, canvas, stringLabel=None):
        points = this.plotpoints
        if len(points)>0:
            (x,y) = points[0]
            if stringLabel is None:
                stringLabel = this.name
            if stringLabel is None:
                stringLabel = str(this.identity)
            canvas.centerText(x,y, stringLabel)

def extrema(points):
    xs = [x for (x,y) in points]
    ys = [y for (x,y) in points]
    return [ min(xs), max(xs), min(ys), max(ys) ]

def maxExtent(points):
    (xm, xM, ym, yM) = extrema(points)
    return max( xM-xm, yM-ym )
            
def dumpBordersToPNG(borders, name, colorV):  
    from skimpyGimpy import canvas
    filename = name.lower()+".png"
    allcoords = []
    for border in borders:
        allcoords.extend(border.pairs)
    mE = maxExtent(allcoords)
    scaleFactor = 100.0/mE
    print(filename, scaleFactor)
    c = canvas.Canvas()
    c.setColorV(colorV)
    for border in borders:
        border.replot(scaleFactor)
        border.plotLines(c)
    c.dumpToPNG(filename)

def setNames(borderDictionary):
    fipsDict = {}
    f = open(fipsfilename)
    done = False
    count = 0
    while not done:
        # skip to blank line
        linestrip = ""
        while not linestrip and not done:
            line = f.readline()
            if not line:
                done = True
            linestrip = line.strip()
        if not done:
            identity = int(linestrip)
            fips = f.readline().strip().replace('"', '')
            name = f.readline().strip().replace('"', '')
            border = borderDictionary.get(identity)
            dummy1 = f.readline()
            dummy2 = f.readline()
            if border:
                border.setName(name, fips)
                print("setting", identity, name, fips)
                fipsnum = border.fipsNum
                fipsL = fipsDict.get(fipsnum, [])
                fipsL.append(border)
                fipsDict[fipsnum] = fipsL
                count += 1
    print("set", count, "names")
    return fipsDict

def test1():
    f = open(filename)
    state = stateBoundary()
    state.parse(f)
    print("got", len(state.d), "points")
    state.prepare()
    print("dimensions", (state.minlat, state.maxlat), (state.minlon, state.maxlon), (state.maxlat-state.minlat,
                                                                                     state.maxlon-state.minlon))
    state.preplot()
    print("plot points", len(state.plotpoints))
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.setColor(255,0,0)
    c.setCap(0)
    c.setWidth(1)
    state.plotLines(c)
    c.dumpToPNG("alaska.png")

def getStates():
    idDict = {}
    done = False
    f = open(filename)
    while not done:
        state = stateBoundary()
        test = state.parse(f)
        if not state.d or state.identity is None:
            if not test:
                done = True
        else:
            state.prepare()
            idDict[state.identity] = state
            print(state.identity, "parsed")
    fipsDict = setNames(idDict)
    return (idDict, fipsDict)

def plotStates(outfile="AllStates.png", jsFile="AllStates.js", scaleFactor=5.0):
    import random
    from skimpyGimpy import canvas
    (idDict, fipsDict) = getStates()
    c = canvas.Canvas()
    c.setBackgroundCallback("out")
    c.setCap(0)
    c.setWidth(1)
    c.addFont("propell", "/skimpyGimpy_1_2/fonts/mlmfonts/propell.bdf")
    c.setFont("propell", 1)
    colors = [ ( int(random.uniform(0,128)), int(random.uniform(128,255)), int(random.uniform(0,255) )) for
               x in range(100)]
    colors2 = [ ( int(random.uniform(128,256)), int(random.uniform(0,128)), int(random.uniform(0,128) )) for
               x in range(40)]
    count = 0
    for fipsNum in list(fipsDict.keys()):
        borders = fipsDict[fipsNum]
        border0 = borders[0]
        colorV = random.choice(colors)
        c.setColorV( colorV )
        name = border0.name
        print("plotting", fipsNum, name, colorV)
        c.setCallBack(border0.name)
        for border in borders:
            border.replot(scaleFactor)
            border.plotLines(c)
        #c.setColorV(random.choice(colors2))
        #state.label(c)
        count += 1
        dumpBordersToPNG(borders, name, colorV)
    c.dumpToPNG(outfile)
    c.dumpJavascript(jsFile, imageName="AllStates", functionName="onState")

if __name__=="__main__":
    plotStates()
