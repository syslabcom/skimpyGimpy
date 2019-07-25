
"helpers for manipulating wave files"

MAX16 = 32767
MIN16 = -32767
MAX8 = 255
MIN8 = 0
SAMPLESPERSECOND = 44100/2
WINDOWSIZE = 10
SUBSAMPLEFRACTION = 0.22

def wave16(frame):
    first = ord(frame[1])
    second = ord(frame[0])
    sign = 1
    if first&128:
        sign = -1
        first = first&127
    absvalue = first*256 + second
    return sign*absvalue

def toWave8ord(n, minimum, maximum):
    diff = maximum-minimum
    base = n-minimum
    f = base*256.0/diff
    f = f/2
    result = int(round(f))
    if result<0: result = 0
    if result>254: result = 254
    #print result, "from", n
    return result

def toWave16frame(n, minimum=MIN16, maximum=MAX16):
    #print "n=", n
    if n<minimum: n=minimum
    if n>maximum: n=maximum
    #print "n after", n
    theord = toWave16ord(n)
    #print "ord", theord
    negative = (theord<0)
    theord = abs(theord)
    lower = theord&255
    upper = theord&(127<<8)
    upper = upper>>8
    if negative:
        upper = upper|128
    return chr(lower)+chr(upper)

def toWave16ord(n, minimum=MIN16, maximum=MAX16):
    max16 = MAX16
    min16 = MIN16
    scale16 = max16-min16
    diff = n-minimum
    base = maximum-minimum
    ratio = diff*1.0/base
    #print "(diff,base,ratio)", (diff,base,ratio)
    fresult = ratio*scale16+min16
    result = int(fresult)
    if result>max16:
        result = max16
    if result<min16:
        result = min16
    return result

def from16to8(frame):
    w16 = wave16(frame)
    theord = toWave8ord(w16, MIN16, MAX16)
    return chr(theord)

def tone(frequency, nSamples=None,
         samplesPerSecond=SAMPLESPERSECOND, minimum=MIN16, maximum=MAX16):
    from math import sin, pi
    if nSamples is None:
        nSamples = int(samplesPerSecond)
    samplesPerSecond = float(samplesPerSecond)
    amplitude = (maximum-minimum)/2.0
    #samplesperwavelength = frequency/(2*pi)
    delta = pi*frequency/samplesPerSecond
    #print "<br>samplesPerSecond, amplitude, delta"
    #print samplesPerSecond, amplitude, delta,"<br>"
    #print delta*samplesPerSecond, 2*pi*frequency
    result = [ amplitude*sin(delta*i)
               for i in xrange(nSamples) ]
    return result

def attenuate(samples, tailFraction=0.5, downToFraction=0.3):
    samples = list(samples)
    nsamples = len(samples)
    nchange = min(int(nsamples*tailFraction)+1,nsamples)
    startIndex = nsamples-nchange
    scaleDelta = - (1.0-downToFraction)/nchange
    scaleFactor = 1.0 - scaleDelta
    for index in xrange(startIndex, nsamples):
        scaleFactor += scaleDelta
        samples[index] = samples[index]*scaleFactor
    return samples

def cattenuate(samples, tailFraction=0.5, downToFraction=0.3):
    from math import pi, cos
    samples = list(samples)
    nsamples = len(samples)
    nchange = min(int(nsamples*tailFraction)+1,nsamples)
    startIndex = nsamples-nchange
    reductionFraction = 1.0-downToFraction
    radians = 0.0
    deltaRadians = pi/nchange
    for index in xrange(startIndex, nsamples):
        radians += deltaRadians
        reduction = 0.5*cos(radians)
        scaleFactor = downToFraction + reduction*reductionFraction
        samples[index] = samples[index]*scaleFactor
    return samples


def inflectionIndices(samples, window=30):
    ls = len(samples)
    D = {0:1, ls-1:1}
    tendancy = (1,1)
    for i in xrange(window, ls-window):
        tb = 1
        ta = 1
        s = samples[i]
        if samples[i-window]<s: tb = -1
        if samples[i+window]<s: ta = -1
        t = (tb,ta)
        if t!=tendancy:
            D[i] = i
        tendancy = t
    keys = D.keys()
    keys.sort()
    return (keys, D)

def interpolationChoices(samples, window=30, fraction=0.11):
    (ip, D) = inflectionIndices(samples, window)
    for i in xrange(len(ip)-1):
        i1 = ip[i]
        i2 = ip[i+1]
        if i2<i1:
            raise ValueError, "indices not ascending"
        diffpart = int((i2-i1)*fraction)+1
        index = i1
        while index<i2:
            index += diffpart
            index = max(i2, index)
            D[index] = 1
    keys = D.keys()
    keys.sort()
    return (keys, D)
        
def inflectionTest():
    from math import sin
    length = 80
    delta = 0.19
    window = 5
    rr = range(length)
    samples = [ int( 10*sin(x*delta) ) for x in rr ]
    print rr
    print samples
    (ii, id) = inflectionIndices(samples, window)
    print "ii", ii
    print "ip\tsamples\tr\trr"
    for i in rr:
        ind = " "
        if id.has_key(i):
            ind = "*"
        print ind, "%s\t%s" % (samples[i], i)

def sampleInterpolation(samples, window=WINDOWSIZE):
    (xs, D) = interpolationChoices(samples, window, SUBSAMPLEFRACTION)
    points = [ (x,samples[x]) for x in xs ]
    return LinearInterpolation( points, False )

def liFile(filename="li.wav"):
    insamples = samplesFromFile()
    li = sampleInterpolation(insamples)
    li = li.fit(-1.0, 1.0)
    #li = li.attenuate(0.9,0.3) # buggy?
    #li = li.stretch(0.7)
    #li = li.perturb(8, 0.01)
    li = li.overlap(li, 0.7)
    print li.extrema()
    li = li.fit(MIN8, MAX8)
    outsamples = li.toSamples()
    outsamples = [int(y) for y in outsamples]
    print "input size", len(insamples), "appx size", len(li), "out size", len(outsamples)
    return samplesToFile(filename, outsamples, sampwidth=1)

class LinearInterpolation:
    def __init__(this, breakpoints, sort=True):
        if sort:
            breakpoints = list(breakpoints)
            breakpoints.sort()
        this.points = breakpoints
    def __len__(this):
        return len(this.points)
    def __repr__(this):
        return "LinearInterpolation(%s)" % this.points
    def __call__(this, x):
        ys = this.yValues([x])
        return ys[0]
    def definedRange(this):
        xstart = this.points[0][0]
        xstop = this.points[-1][0]
        return (xstart, xstop)
    def toSamples(this):
        (xstart, xstop) = this.definedRange()
        return this.yValues(xrange(int(xstart)+1, int(xstop)))
    def extrema(this):
        ys = [y for (x,y) in this.points]
        return (min(ys), max(ys))
    def perturb(this, xradius, yradius):
        from random import uniform
        points = [ (x+uniform(-xradius,xradius), y+uniform(-yradius,yradius)) for (x,y) in this.points ]
        return LinearInterpolation(points, False)
    def stretch(this, xfactor=2.0):
        points = [ (x*xfactor, y) for (x,y) in this.points ]
        return LinearInterpolation(points, False)
    def fit(this, miny, maxy):
        points = this.points
        ys = [ y for (x,y) in points ]
        ymax = max(ys)
        ymin = min(ys)
        diffy = maxy-miny
        ydiff = ymax-ymin
        points = [ (x, miny+diffy*(y-ymin)/ydiff) for (x,y) in points ]
        return LinearInterpolation(points, False)
    def scale(this, yfactor=2.0):
        points = [ (x, y*yfactor) for (x,y) in this.points ]
        return LinearInterpolation(points, False)
    def shift(this, deltax):
        points = [ (x+deltax, y) for (x,y) in this.points ]
        return LinearInterpolation(points, False)
    def attenuate(this, tailFraction=0.3, downToFraction=0.1):
        (xstart, xstop) = this.definedRange()
        xdiff = (xstop-xstart)*1.0
        attstart = xstop - xdiff*tailFraction
        points = list(this.points)
        for i in xrange(len(points)):
            (x,y) = points[i]
            if x>attstart:
                reductionfraction = (xstop-x)/xdiff
                y = y * (1.0-reductionfraction)
                points[i] = (x,y)
        return LinearInterpolation(points, False)
    def overlap(this, other, overlapFraction):
        (thisstart, thisstop) = this.definedRange()
        (otherstart, otherstop) = other.definedRange()
        thisdiff = thisstop-thisstart
        otherdiff = otherstop-otherstart
        diff = min(thisdiff, otherdiff)
        samplesToOverlap = diff*overlapFraction
        othershift = thisstop - samplesToOverlap - otherstart
        otherShifted = other.shift(othershift)
        (shiftstart, shiftend) = otherShifted.definedRange()
        outerpoints = {}
        innerxs = {}
        for p in this.points:
            (x,y) = p
            if x<shiftstart:
                outerpoints[p]=1
            else:
                innerxs[x] = 1
        for p in otherShifted.points:
            (x,y) = p
            if x>thisstop:
                outerpoints[p]=1
            else:
                innerxs[x] = 1
        xs = innerxs.keys()
        xs.sort()
        thisys = this.yValues(xs)
        shiftys = otherShifted.yValues(xs)
        innerpoints = [ (x, y1+y2) for (x,y1,y2) in zip(xs, thisys, shiftys) ]
        points = innerpoints + outerpoints.keys()
        points.sort()
        return LinearInterpolation(points, False)
    def sum(this, other):
        "not mathematically correct, just a hack"
        allxD = {}
        for (x,y) in this.points:
            allxD[x] = 1
        for (x,y) in other.points:
            allxD[x] = 1
        allx = allxD.keys()
        allx.sort()
        myys = this.yValues(allx)
        oys = other.yValues(allx)
        sumpoints = [ (x, y1+y2) for (x, y1, y2) in zip(allx, myys, oys) ]
        return LinearInterpolation(sumpoints, False)
    def yValues(this, xValues, epsilon=0.0001):
        "return mappings for sorted xValues, return 0s where not in range" # xxxx ?
        from bisect import bisect
        (xstart, xstop) = this.definedRange()
        points = this.points
        result = list(xValues)
        pindex = None
        lr = len(result)
        for i in xrange(lr):
            xi = xValues[i]
            if xi>=xstart and xi<=xstop:
                if pindex is None:
                    pindex = bisect( points, (xi,0) )
                    if pindex>=len(points): pindex = lr-1
                while points[pindex][0]+epsilon<xi:
                    pindex+=1
                p0 = points[pindex-1]
                (x0,y0) = p0
                diff = float(xi-x0)
                if abs(diff)<epsilon:
                    result[i] = y0
                else:
                    p1 = points[pindex]
                    (x1,y1) = p1
                    f = diff/(x1-x0)
                    yi = y0 + f*(y1-y0)
                    result[i] = yi
            else:
                result[i] = 0
        return result

def overlap(samples1, samples2, fraction=0.2):
    "overlap samples1 with samples2, modify samples1 in place"
    if not samples1:
        return samples2
    if not samples2:
        return samples1
    lens1 = len(samples1)
    lens2 = len(samples2)
    minlen = min(lens1, lens2)
    nchange = int(fraction*minlen)
    s1start = lens1-nchange
    #result = list(samples1)
    result = samples1
    for i in xrange(nchange):
        s1i = s1start+i
        result[s1i] = samples1[s1i] + samples2[i]
    result = result + samples2[nchange:]
    return result

def randomDeletes(samples, atleast=0.01, atmost=0.02):
    from random import uniform
    deletes = {}
    slen = len(samples)
    ndeletes = int(uniform(atleast, atmost)*slen)
    for i in xrange(ndeletes):
        choice = int(uniform(1,slen-1))
        deletes[choice] = choice
    outlen = slen-len(deletes)
    result = range(outlen)
    sindex = 0
    for i in result:
        while deletes.has_key(sindex):
            sindex+=1
        result[i] = samples[sindex]
        sindex+=1
    return result

def delFile(filename="del.wav"):
    samples = samplesFromFile()
    samples = randomDeletes(samples)
    #print samplesToDivs(samples, 300)
    return samplesToFile(filename, samples, sampwidth=1)
    
def walk(lowfrequency, highfrequency, nSamples=None,
         samplesPerSecond=SAMPLESPERSECOND, minimum=MIN16, maximum=MAX16,
         maxFrequencyChangePerSample=300.0):
    from math import sin, pi
    from random import uniform
    if nSamples is None:
        nSamples = int(samplesPerSecond)
    samplesPerSecond = float(samplesPerSecond)
    amplitude = (maximum-minimum)/2.0
    result = r = range(nSamples)
    x = 0.0
    f = uniform(lowfrequency, highfrequency)
    for i in r:
        f += uniform(-maxFrequencyChangePerSample, maxFrequencyChangePerSample)
        if f<lowfrequency:
            f = lowfrequency+maxFrequencyChangePerSample
        if f>highfrequency:
            f = highfrequency-maxFrequencyChangePerSample
        delta = pi*f/samplesPerSecond
        x += delta
        result[i] = amplitude*sin(x)
    return result

def mix(primarySamples, primaryWeight, otherSamples, otherWeights):
    nsamples = len(primarySamples)
    result = fit(primarySamples, -primaryWeight, primaryWeight)
    for (samples, weight) in zip(otherSamples, otherWeights):
        extra = fit(samples, -weight, weight)
        le = len(extra)
        for i in xrange(nsamples):
            result[i] += extra[i%le]
    return result

def mixFile(filename="mix.wav"):
    foreground = samplesFromFile()
    background = walk(-880, 880, 44000)
    samples = foreground
    samples = mix(foreground, 100, [background], [25])
    samples = fit(samples, 0,254)
    print samplesToDivs(samples, 300)
    return samplesToFile(filename, samples, sampwidth=1)

def walkFile(filename="walk.wav", low=-990, high=880):
    samples = walk(low, high, 44100*3, maxFrequencyChangePerSample=100)
    samples = fit(samples, MIN16, MAX16)
    #print samplesToDivs(samples, 300)
    return samplesToFile(filename, samples)

def toneFile(filename="A.wav", frequency=440):
    samples = tone(frequency)
    last = samples[0]
    ntransitions = 0
##    for x in samples:
##        if x<0 and last>=0:
##            ntransitions += 1
##        last = x
    #print "ntransitions", ntransitions
    #print map(int, samples[:1000])
    #print samplesToDivs(samples, 300)
    return samplesToFile(filename, samples)

def attenuateFile(filename="att.wav", f=440):
    samples = tone(f, 44000)
    samples = cattenuate(samples, 0.7, 0)
    samples = samples+[0]*44000
    samples = samples*8
    return samplesToFile(filename, samples)

def tone2File(filename="twotone.wav", f1=440, f2=330):
    s1 = tone(f1, 10)
    s2 = tone(f2, 10)
    s1 = attenuate(s1, 0.7, 0)
    s2 = attenuate(s2, 1.0, 0)
    samples = overlap(s1, s2)
    print samples
    return samplesToFile(filename, samples)

def samplesFromFile(filename="wave/underscore.wav"):
    import wave
    f = wave.open(filename)
    nframes = f.getnframes()
    sampwidth = f.getsampwidth()
    if sampwidth not in (1,2):
        raise ValueError, "can't work with sampwidth %s" % sampwidth
    frames = [None]*nframes
    for i in range(nframes):
        frames[i] = f.readframes(1)
    if sampwidth==1:
        samples = map(ord, frames)
    else:
        samples = map(wave16, frames)
    #print samples[:3000]
    mins = min(samples)
    maxs = max(samples)
    #print len(samples), mins, maxs
    mid = (mins+maxs)/2
    ntransitions = 0
    #for x in samples:
    #    if x<mid and last>=mid:
    #        ntransitions += 1
    #    last = x
    #print "ntransitions", ntransitions, "<br>"
    #print samplesToDivs(samples, 300)
    return samples

def fit(samples, minimum, maximum):
    smin = min(samples)
    smax = max(samples)
    stretch = (maximum-minimum)*1.0/(smax-smin)
    return [ (s-smin)*stretch + minimum for s in samples ]

def fit16(samples):
    result = fit(samples, MIN16, MAX16)
    return map(int, result)

def fit8(samples):
    result = fit(samples, MIN8, MAX8)
    return map(int, result)

def samplesToFile(filename, samples, sampwidth=2):
    f = file(filename, "w")
    #f = wave.open(filename, "w")
    #samplesToFileObject(f, samples, sampwidth)
    f.write(samplesToString(samples, sampwidth))
    f.close()

def samplesToString(samples, sampwidth=2):
    import cStringIO, wave
    f0 = cStringIO.StringIO()
    f = wave.open(f0, "wb")
    samplesToFileObject(f, samples, sampwidth)
    result = f0.getvalue()
    f.close()
    return result

def samplesToFileObject(f, samples, sampwidth=2):
    nchannels = 1
    #sampwidth = 2
    framerate = SAMPLESPERSECOND
    nframes = 0
    comptype = None
    compname = None
    #f = wave.open(filename, "w")
    #params = (nchannels, sampwidth, framerate, nframes, comptype, compname)
    #f.setparams(params)
    f.setnchannels(nchannels)
    f.setsampwidth(sampwidth)
    f.setframerate(framerate)
    if sampwidth==2:
        outframes = map(toWave16frame, samples)
    elif sampwidth==1:
        outframes = map(chr, map(int, map(round, samples)))
    framestring = "".join(outframes)
    #print samples[:100]
    #print repr(framestring[:100])
    f.writeframes(framestring)

def samplesToDivs(samples, maxWidth):
    widths = fit(samples, 0, maxWidth)
    format = '<div style="height:1px;width:%spx;background-color:red;border:0;overflow:hidden"></div>'
    L = [ format%int(max(1,s)) for s in widths ]
    s = ["nsamples=%s max=%s min=%s<br>" % (len(samples), int(max(samples)), int(min(samples)))]
    #return "\n".join(L)
    count = 0
    while L:
        s.append("%s<br>" % count)
        chunk = L[:500]
        L = L[500:]
        count+=500
        schunk = "\n".join(chunk)
        s.append(schunk)
        if count>2000: break
    return "\n".join(s)

class LettersIndex:
    def __init__(this):
        this.lettersToPath = {}
        this.lettersToAppx = {}
    def dumpZip(this, zipFileName):
        "dump compressed representation of this"
        import marshal, zlib
        outfile = file(zipFileName, "wb")
        # force load all files...
        for x in this.keys():
            test = this.getAppx(x)
        D = {}
        appx = this.lettersToAppx
        for letter in appx.keys():
            li = appx[letter]
            D[letter] = li.points
        rp = marshal.dumps(D)
        rpz = zlib.compress(rp)
        outfile.write(rpz)
        outfile.close()
    def loadZip(this, zipFileName):
        "load compressed representation of this (all at once)"
        # XXX could be made lazy using zipfile...
        import marshal, zlib
        infile = file(zipFileName, "rb")
        rpz = infile.read()
        rp = zlib.decompress(rpz)
        D = marshal.loads(rp)
        for (letter, points) in D.items():
            this.lettersToAppx[letter] = LinearInterpolation(points)
    def addLetter(this, letter, sequence):
        this.lettersToAppx[letter] = sampleInterpolation(sequence)
    def addLetterFile(this, letter, filename):
        this.lettersToPath[letter] = filename
    def getAppx(this, letter):
        ls = this.lettersToAppx
        if ls.has_key(letter):
            return ls[letter]
        lp = this.lettersToPath
        if lp.has_key(letter):
            path = lp[letter]
            samples = samplesFromFile(filename=path)
            this.addLetter(letter, samples)
            return this.lettersToAppx[letter]
        raise ValueError, "no mapping found for "+repr(letter)
    def keys(this):
        d = {}
        d.update(this.lettersToAppx)
        d.update(this.lettersToPath)
        return d.keys()
    def clean(this, s):
        s = s.lower()
        r = []
        d = {}
        d.update(this.lettersToAppx)
        d.update(this.lettersToPath)
        for c in s:
            if d.has_key(c):
                r.append(c)
        result = "".join(r)
        if not result: result = " "
        return result

def testIndex():
    result = LettersIndex()
    #result.addLetterFile("a", "test.wav")
    result.addLetterFile("b", "guitar_a.wav")
    #result.dumpZip("test.zip")
    #result.loadZip("test.zip")
    a = tone(220)
    b = tone(261.63)
    c = tone(329.63)
    d = tone(392)
    e = tone(220*2)
    f = tone(554.37)
    g = tone(1174.66)
    h = tone(392*2)
    result.addLetter("a", a+d)
    #result.addLetter("b", b+a)
    result.addLetter("c", c+g)
    result.addLetter("d", d+e)
    result.addLetter("e", e+c)
    result.addLetter("f", f+h)
    result.addLetter("g", g+b)
    result.addLetter("h", h+f)
    return result

class Mixer:
    minOverlapPercent = 20
    maxOverlapPercent = 30
    maxStretchPercent = 10
    attenuateLimit = 0.3
    def __init__(this, word, index):
        this.word = word
        this.index = index
        this.mix = None
    def cleanMix(this):
        from random import uniform
        index = this.index
        minStretch = 1.0 - this.maxStretchPercent*0.01
        maxStretch = 1.0 + this.maxStretchPercent*0.01
        minOverlap = 0.01*this.minOverlapPercent
        maxOverlap = 0.01*this.maxOverlapPercent
        all = None
        for c in this.word:
            appx = index.getAppx(c)
            appx = appx.fit(-1.0, 1.0)
            appx = appx.stretch(uniform(minStretch,maxStretch))
            overlap = uniform(minOverlap, maxOverlap)
            attenuation = min(overlap*2, 1.0)
            appx = appx.attenuate(attenuation, this.attenuateLimit)
            if all is None:
                all = appx
            else:
                all = all.overlap(appx, overlap)
        #all = all.fit(MIN8, MAX8)
        #all = all.perturb(8, 0.01)
        outsamples = all.toSamples()
        #outsamples = [int(y) for y in outsamples]
        this.mix = outsamples
        return outsamples
##    def overMix(this):
##        from random import shuffle, uniform
##        index = this.index
##        choices = list(this.index.keys())
##        shuffle(choices)
##        novermix = int(round(uniform(this.minOverMix, this.maxOverMix)))
##        mixSequences = []
##        mixWeights = []
##        for i in range(novermix):
##            letter = choices[i]
##            s = index.getSamples(letter)
##            ls = len(s)
##            cut1 = int(uniform(0,ls/2))
##            cut2 = int(uniform(ls/2+1, ls))
##            if cut1>cut2: cut2 = cut1+1
##            s = s[cut1:cut2]
##            mixSequences.append(s)
##            mixWeights.append( uniform(this.OverMixMinWeight, this.OverMixMaxWeight) )
##        samples = mix(this.mix, this.primaryWeight, mixSequences, mixWeights)
##        this.mix = samples
##        return samples
##    def whistle(this):
##        import random
##        nsamples = int(random.uniform(44100, 88111))
##        tune = walk(-this.maxWhistle, this.maxWhistle, nsamples)
##        samples = mix(this.mix, this.primaryWeight, [tune], [this.whistleWeight])
##        this.mix = samples
##        return samples
##    def deleteSome(this):
##        this.mix = randomDeletes(this.mix, this.minDeletePercent*0.01, this.maxDeletePercent*0.01)
    def writeToFile(this, filename, sampwidth=1):
        samples = this.mix
        if sampwidth==1:
            samples = fit(samples, MIN8, MAX8)
        elif sampwidth==2:
            samples = fit(samples, MIN16, MAX16)
        return samplesToFile(filename, samples, sampwidth=sampwidth)
    def doProcess(this):
        this.cleanMix()
        #this.whistle()
        #this.deleteSome()
        #this.overMix()
    def doFile(this, filename, sampwidth=1):
        this.doProcess()
        this.writeToFile(filename, sampwidth)

def testMix():
    index = testIndex()
    mixer = Mixer("abbabcdefghb", index)
    mixer.doFile("mixer.wav")

def getIndex():
    result = LettersIndex()
    result.addLetterFile("a", "wave/a.wav")
    result.addLetterFile("b", "wave/b.wav")
    result.addLetterFile("c", "wave/c.wav")
    result.addLetterFile("d", "wave/d.wav")
    result.addLetterFile("e", "wave/e.wav")
    result.addLetterFile("f", "wave/f.wav")
    result.addLetterFile("g", "wave/g.wav")
    result.addLetterFile("h", "wave/h.wav")
    result.addLetterFile("i", "wave/i.wav")
    result.addLetterFile("j", "wave/j.wav")
    result.addLetterFile("k", "wave/k.wav")
    result.addLetterFile("l", "wave/l.wav")
    result.addLetterFile("m", "wave/m.wav")
    result.addLetterFile("n", "wave/n.wav")
    result.addLetterFile("o", "wave/o.wav")
    result.addLetterFile("p", "wave/p.wav")
    result.addLetterFile("q", "wave/q.wav")
    result.addLetterFile("r", "wave/r.wav")
    result.addLetterFile("s", "wave/s.wav")
    result.addLetterFile("t", "wave/t.wav")
    result.addLetterFile("u", "wave/u.wav")
    result.addLetterFile("v", "wave/v.wav")
    result.addLetterFile("w", "wave/w.wav")
    result.addLetterFile("x", "wave/x.wav")
    result.addLetterFile("y", "wave/y.wav")
    result.addLetterFile("z", "wave/z.wav")
    result.addLetterFile("0", "wave/0.wav")
    result.addLetterFile("1", "wave/1.wav")
    result.addLetterFile("2", "wave/2.wav")
    result.addLetterFile("3", "wave/3.wav")
    result.addLetterFile("4", "wave/4.wav")
    result.addLetterFile("5", "wave/5.wav")
    result.addLetterFile("6", "wave/6.wav")
    result.addLetterFile("7", "wave/7.wav")
    result.addLetterFile("8", "wave/8.wav")
    result.addLetterFile("9", "wave/9.wav")
    result.addLetterFile("-", "wave/hyphen.wav")
    result.addLetterFile("_", "wave/underscore.wav")
    result.addLetterFile(".", "wave/dot.wav")
    result.addLetterFile("@", "wave/atsign.wav")
    result.addLetterFile(" ", "wave/space.wav")
    result.addLetterFile("/", "wave/slash.wav")
    result.addLetterFile(":", "wave/colon.wav")
    return result

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

def WaveAudioSpelling(s, indexfilepath):
    index = LettersIndex()
    index.loadZip(indexfilepath)
    s = index.clean(s)
    m = Mixer(s, index)
    m.doProcess()
    samples = m.doProcess()
    samples = fit(m.mix, MIN8, MAX8)
    audio = samplesToString(samples, sampwidth=1)
    return audio

usage = """
waveTools.py generates a wave audio file which speaks
an audio representation for an encoded string.  It has
two command line options:

waveTools.py --filename file.wav encodeString
  to write wave file "file.wave" as encoded String

waveTools.py --stdout encodeString
  to write wave file encoding string to standard output

also add '--indexfile path/waveIndex.zip' to identify
a compiled wave index file to use.
"""

def main():
    import sys, os
    parms = sys.argv[1:]
    wif = "waveIndex.zip"
    indexFile = None
    compiled = True # set true to use zip file
    if os.path.exists(wif):
        indexFile = wif
    try:
        wif = getparm(parms, "--indexfile")
        if wif:
            indexFile = wif
        filename = getparm(parms, "--filename")
        stdout = getparm(parms, "--stdout", getValue=False)
        if len(parms)<1:
            raise ValueError, "please provide string to encode"
        if len(parms)>1:
            raise ValueError, "unknown parameters "+repr(parms)
        instring = parms[0]
        if not filename and not stdout:
            raise "must specify --filename or --stdout option"
        if filename and stdout:
            raise "--filename and --stdout parameters cannot be used at the same time"
    except:
        print usage
        raise
    else:
        if not compiled: indexFile = None
        if indexFile:
            if filename:
                print "using index file path", repr(indexFile)
            index = LettersIndex()
            index.loadZip(indexFile)
        else:
            index = getIndex()
        instring = instring.lower()
        #instring = index.clean(instring)
        m = Mixer(instring, index)
        if filename:
            m.doFile(filename)
        elif stdout:
            m.doProcess()
            samples = fit(m.mix, MIN8, MAX8)
            sys.stdout.write(samplesToString(samples, sampwidth=1))

if __name__=="__main__":
    main()
    #liFile()
    #inflectionTest()
    #from profile import run
    #run("main()")
    #testMix()
    #tone2File()
    #attenuateFile()
    #delFile()
    #mixFile()
    #walkFile()
    #toneFile()
    #samplesFromFile()
    
    
    

    
