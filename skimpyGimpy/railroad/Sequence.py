from . import Literal
from . import Configuration

class Sequence(Literal.LiteralBase):
    def __init__(self,
                 members,
                 canvas,
                 config=None):
        if config is None:
            config = Configuration.Configuration()
        members = self.members = [self.interpolate(m, canvas, config) for m in members]
        self.canvas = canvas
        self.config = config
        # compute geometry
        d = config.gridDelta
        nm = len(self.members)
        self.w = sum( [m.w for m in members] )
        self.h = max( [m.h for m in members] )
        self.s = max( [m.s for m in members] )
    def drawAt(self, x, y, test=False):
        h = self.h
        s = self.s
        mx = x
        connectors = []
        for m in self.members:
            my = y+h-s-m.h+m.s
            m.drawAt(mx, my, test=test)
            connectors.append(m.connectors(mx, my))
            mx += m.w

def test(fontdir=".", outfile="/tmp/out.png"):
    from .Choose import Choose
    from .Repeat import Repeat
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    l = Literal.Literal(["test", "literal"], c)
    l2 = Literal.Literal(["another", "test", "literal"], c)
    ch = Choose([l, l2], c)
    l3 = Repeat(Literal.Literal("nothing", c), c)
    ch2 = Sequence([ch, l3, l2], c)
    ch2.drawAt(20,100)
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test()
