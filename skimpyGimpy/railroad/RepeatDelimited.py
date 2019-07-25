import Configuration
from skimpyGimpy import bdf
import Literal

class RepeatDelimited(Literal.LiteralBase):
    def __init__(self,
                 thing,
                 delimiter,
                 canvas,
                 config=None):
        if config is None:
            config = Configuration.Configuration()
        thing = self.thing = self.interpolate(thing, canvas, config)
        delimiter = self.delimiter = self.interpolate(delimiter, canvas, config)
        self.canvas = canvas
        self.config = config
        # compute geometry
        d = config.gridDelta        
        self.w = max(thing.w, delimiter.w)+6*d
        self.h = thing.h+delimiter.h
        self.s = thing.s
    def drawAt(self, x, y, test=False):
        c = self.canvas
        cf = self.config
        d = cf.gridDelta
        middlex = self.w/2+x
        thingx = middlex-self.thing.w/2
        thingy = y+self.delimiter.h
        delimiterx = middlex-self.delimiter.w/2
        delimitery = y
        self.thing.drawAt(thingx, thingy, test=test)
        self.delimiter.drawAt(delimiterx, delimitery, test=test)
        (myleft, myright) = self.connectors(x,y)
        (thingleft, thingright) = self.thing.connectors(thingx, thingy)
        (delimiterleft, delimiterright) = self.delimiter.connectors(delimiterx, delimitery)
        c.setColor(*cf.LinkColor)
        c.setWidth(cf.LinkWidth)
        # link in the thing
        c.addLines([myleft, thingleft])
        c.addLines([thingright, myright])
        (leftx, lefty) = myleft
        (rightx, righty) = myright
        self.loopRight( (leftx+d*2, lefty), delimiterleft)
        self.loopLeft( (rightx-d*2, righty), delimiterright)
        self.arrowRight( *thingleft )
        self.arrowLeft( *delimiterright )

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    l = Literal.Literal(["test","literal"], c)
    d = Literal.Literal("???", c)
    r = RepeatDelimited(l, d, c)
    r.drawAt(100, -100)
    c.dumpToPNG(outfile)
    print "test output to", outfile
    
if __name__=="__main__":
    test()

        
