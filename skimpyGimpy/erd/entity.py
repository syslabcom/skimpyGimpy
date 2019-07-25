
import config
import math
import types
import card
from skimpyGimpy import bdf

def sign(a,b):
    if a>b:
        return 1
    elif a<b:
        return -1
    else:
        return 0

def orthogonals(p1, p2):
    (p1x,p1y) = p1
    (p2x,p2y) = p2
    dx = sign(p1x, p2x)
    dy = sign(p1y, p2y)
    assert dx*dy==0, "p1--p2 must be parallel to x or y axis"
    up = (dx, dy)
    right = (dy, dx)
    return (up, right)

class Entity:
    def __init__(self, name, canvas, x, y, underline=False, minwidth=None, cfg=None):
        if type(name) in types.StringTypes:
            name = [name]
        self.name = name
        self.underline = underline
        self.canvas = canvas
        self.p = (x,y)
        self.minwidth = minwidth
        if cfg is None:
            cfg = config.Configuration()
        self.cfg = cfg
        (self.gw, self.gh) = self.textGeometry()
    def draw(self, test=False):
        self.drawContainer()
        self.drawText()
        if test:
            self.testAnnotation()
    def testAnnotation(self):
        cfg = self.cfg
        d = cfg.delta
        c = self.canvas
        c.setColor(0,0,0)
        B = self.barriers()
        for p in B.keys():
            (x,y) = p
            c.addRect(x-1, y-1, 2, 2)
        D = self.destinationMap()
        #minimum = 1
        minimum = 0
        maximum = "many"
        #maximum = 1
        #for (p1, p2) in D.items():
        #    (x,y) = p2
        #    ((upx, upy), (rightx, righty)) = orthogonals(p1, p2)
        #    #c.addLines([p1, p2])
        #    cardinality = card.Cardinality(minimum, maximum, upx, upy, rightx, righty, d, c)
        #    cardinality.drawAt(x,y)
    def drawContainer(self, color=None):
        c = self.canvas
        cfg = self.cfg
        d = cfg.delta
        (x,y) = self.p
        w = self.gw*d
        h = self.gh*d
        if color is None:
            color = cfg.entityColor
        c.setColor(*color)
        c.addRect(x, y, w, h)
    def drawText(self):
        c = self.canvas
        cfg = self.cfg
        d = cfg.delta
        (x,y) = self.p
        w = self.gw*d
        h = self.gh*d
        nameList = list(self.name)
        nameList.reverse()
        nname = len(nameList)
        hname = cfg.fontHeight*nname
        vslack = h-hname
        tx = x + w/2
        ty = y + vslack/2
        c.setFont(cfg.fontName, 1.0, 0.2)
        c.setColor(*cfg.textColor)
        for t in nameList:
            c.centerText(tx, ty, t)
            if self.underline:
                c.addLines([(x+d/2, ty-4), (x+w-d/4, ty-4)])
            ty += cfg.fontHeight
    def destinationMap(self):
        result = {}
        (x,y) = self.p
        gw = self.gw
        gh = self.gh
        cfg = self.cfg
        d = cfg.delta
        for gx in range(1, gw):
            result[ (gx*d + x, y-d) ] = (gx*d + x, y)
            result[ (gx*d + x, y+gh*d+d) ] = (gx*d + x, y+gh*d)
        for gy in range(1, gh):
            result[ (x-d, gy*d + y) ] = (x, gy*d + y)
            result[ (x+gw*d+d, gy*d + y) ] = (x+gw*d, gy*d+y)
        return result
    def barriers(self):
        result = {}
        (x,y) = self.p
        gw = self.gw
        gh = self.gh
        cfg = self.cfg
        d = cfg.delta
        # xxxx probably only need the border, not interior...
        for gx in xrange(gw+1):
            for gy in xrange(gh+1):
                result[ (x+gx*d, y+gy*d) ] = True
        return result
    def textGeometry(self):
        "geometry in grid coordinates"
        c = self.canvas
        cfg = self.cfg
        w = 0
        d = cfg.delta
        fontname = cfg.fontName
        font = c.getFont(fontname)
        fontscale = 1.0
        textList = self.name
        for text in textList:
            pixels = bdf.pixelation(font, text)
            basicwidth = pixels.width()
            textwidth = basicwidth * fontscale
            if textwidth>w:
                w = textwidth
        minwidth = self.minwidth
        if minwidth and w<minwidth:
            w = minwidth
        h = len(textList)*cfg.fontHeight
        gh = int(math.ceil(float(h)/float(d)))
        if gh<4:
            gh = 4
        gw = int(math.ceil(float(w)/float(d)))
        # width never less than height
        gw = max(gw, gh)
        return (gw, gh)

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    c.addFont("propell", fontdir+"/atari-small.bdf")
    #c.setFont("propell", 1.0)
    #c.setColor(55,55,55)
    #c.centerText(0,0,"hi there!")
    l = Entity("test literal", c, 120, 160)
    l2 = Entity(["another", "test", "literal"], c, -120, -120)
    l.draw()
    l2.draw()
    c.dumpToPNG(outfile)
    print "test output to", outfile

if __name__=="__main__":
    test()

