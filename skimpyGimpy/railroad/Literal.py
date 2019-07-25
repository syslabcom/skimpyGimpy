
"""
Railroad literal
"""

from . import Configuration
from skimpyGimpy import bdf
import types

class LiteralBase:
    def connectors(self, x, y):
        middley = y + self.h - self.s
        return [ (x, middley), (x+self.w, middley) ]
    def addLines(self, points):
        c = self.canvas
        cf = self.config
        c.setColor(*cf.LinkColor)
        d = cf.gridDelta
        c.setWidth(cf.LinkWidth)
        pts = points[:]
        #pr "adding lines", pts
        c.addLines(pts)
        pts.reverse()
        #pr "adding reverse lines", pts
        c.addLines(pts)
    def arrowRight(self, x, y, deltax=-1):
        cf = self.config
        d = cf.gridDelta/2
        xdx = x+deltax*d
        self.addLines( [ (xdx, y+d), (x,y), (xdx, y-d) ] )
    def arrowLeft(self, x, y):
        return self.arrowRight(x,y,1)
    def loopRight(self, startp, endp, deltax=-1):
        cf = self.config
        d = cf.gridDelta
        (startx, starty) = startp
        (endx, endy) = endp
        deltay = 1
        if starty>endy:
            deltay = -1
        nextx = startx + deltax*d
        nexty = starty + deltay*d
        penty = endy - deltay*d
        self.addLines( [ endp,
                      (startx, endy),
                      (nextx, penty),
                      (nextx, nexty),
                      startp ] )
    def loopLeft(self, startp, endp):
        return self.loopRight(startp, endp, 1)
    def textGeometry(self, textList, canvas, config, fontname, fontscale):
        w = 0
        d = config.gridDelta
        font = canvas.getFont(fontname)
        for text in textList:
            pixels = bdf.pixelation(font, text)
            basicwidth = pixels.width()
            textwidth = basicwidth * fontscale
            if textwidth>w:
                w = textwidth
        h = 2*len(textList) * d
        return (w, h)
    def interpolate(self, thing, canvas, config, interpolator=None):
        if interpolator is None:
            interpolator = Literal
        if not isinstance(thing, LiteralBase):
            return interpolator(thing, canvas, config)
        return thing

class Literal(LiteralBase):
    def __init__(self,
                 text,
                 canvas,
                 config=None):
        if config is None:
            config = Configuration.Configuration()
        if type(text) in (str,):
            text = [text]
        self.text = text
        self.canvas = canvas
        self.config = config
        (textw, texth) = self.textGeometry(text, canvas, config,
                                           config.LiteralFontName, config.LiteralFontScale)
        self.h = 2*config.gridDelta+texth
        self.w = textw + 4*config.gridDelta
        self.s = config.gridDelta+texth/2
    def drawAt(self, x, y, test=False):
        cf = self.config
        d = cf.gridDelta
        c = self.canvas
        # if testing draw a strangely colored frame of reference
        if test:
            c.setColor(*cf.TestColor)
            c.addRect(x,y, self.w, self.h)
        # connector line
        (start, end) = self.connectors(x,y)
        self.addLines([start, end])
        By = y+d/2
        Ly = y+3*d/2
        Hy = y+self.h-3*d/2
        Zy = y+self.h-d/2
        Bx = x+d
        Lx = x+2*d
        Hx = x+self.w-2*d
        Zx = x+self.w-d
        hR = Hy-Ly
        wR = Hx-Lx
        hZ = Zy-By
        wZ = Zx-Bx
        radius = d
        # rounded corners
        c.setColor(*cf.LiteralBackground)
        for xx in (Lx, Hx):
            for yy in (Ly, Hy):
                c.addCircle(xx,yy,radius)
        # interior fill
        c.addRect(Lx, By, wR, hZ)
        c.addRect(Bx, Ly, wZ, hR)
        # now add the strings
        xCenter = (Lx+Hx)/2
        yText = Hy-d
        c.setFont(cf.LiteralFontName, cf.LiteralFontScale, cf.LiteralFontRadius)
        c.setColor(*cf.LiteralFontColor)
        for t in self.text:
            c.centerText(xCenter, yText, t)
            yText -= 2*d

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    #c.setFont("propell", 1.0)
    #c.setColor(55,55,55)
    #c.centerText(0,0,"hi there!")
    l = Literal("test literal", c)
    l2 = Literal(["another", "test", "literal"], c)
    l.drawAt(120, 160, test=True)
    l2.drawAt(-120, -120, test=True)
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test()
