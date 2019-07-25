"""
Railroad repeat
"""

from . import Configuration
from skimpyGimpy import bdf
from . import Literal

class Optional(Literal.LiteralBase):
    def __init__(self, thing, canvas, config=None):
        if config is None:
            config = Configuration.Configuration()
        thing = self.thing = self.interpolate(thing, canvas, config)
        self.canvas = canvas
        self.config = config
        # compute geometry
        d = config.gridDelta        
        self.w = thing.w + 4 * d
        self.h = thing.h + 2 * d
        self.s = thing.s + 2 * d
    def drawAt(self, x, y, test=False):
        c = self.canvas
        # if testing draw a strangely colored frame of reference
        cf = self.config
        if test:
            c.setColor(*cf.TestColor)
            c.addRect(x,y, self.w, self.h)
        # draw the thing
        d = cf.gridDelta
        middlex = self.w/2 + x
        thing = self.thing
        thingx = middlex-thing.w/2
        thing.drawAt( thingx, y )
        connect = thing.connectors(thingx, y)
        (thingleft, thingright) = connect
        (myleft, myright) = self.connectors(x,y)
        c.setColor(*cf.LinkColor)
        c.setWidth(cf.LinkWidth)
        # link in the thing
        c.addLines([myleft, thingleft])
        c.addLines([thingright, myright])
        # add the repeat loop
        above = thing.h + y + d
        (leftx, lefty) = myleft
        (rightx, righty) = myright
        c.addLines([ (leftx+d, lefty),
                     (leftx+2*d, lefty+d),
                     (leftx+2*d, above-d),
                     (leftx+3*d, above),
                     (rightx-3*d, above),
                     (rightx-2*d, above-d),
                     (rightx-2*d, lefty+d),
                     (rightx-d, lefty) ]
                   )
        # arrow heads
        #c.addLines([ (rightx-d, righty+d), myright, (rightx-d, righty-d) ] )
        self.arrowRight(rightx, righty)
        middlex = (leftx+rightx)/2
        #c.addLines([ (middlex-d, above+d), (middlex, above), (middlex-d, above-d) ] )
        self.arrowRight(middlex, above)

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    l = Literal.Literal(["test","literal"], c)
    r = Optional(l, c)
    r.drawAt(100, -100)
    c.dumpToPNG(outfile)
    print("test output to", outfile)
    
if __name__=="__main__":
    test()
