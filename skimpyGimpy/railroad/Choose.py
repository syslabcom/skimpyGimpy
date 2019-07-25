
"""
Railroad nonterminal
"""
from . import Configuration
from skimpyGimpy import bdf
from . import Literal

def near(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return abs(x1-x2)+abs(y1-y2)<0.5

class Choose(Literal.LiteralBase):
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
        maxwidth = max( [x.w for x in members] )
        d = config.gridDelta
        self.w = maxwidth + 6 * d
        first = members[0]
        self.s = first.s
        totalheight = sum([x.h for x in members] )
        self.h = totalheight
    def drawAt(self, x, y, test=False):
        c = self.canvas
        # if testing draw a strangely colored frame of reference
        cf = self.config
        if test:
            c.setColor(*cf.TestColor)
            c.addRect(x,y, self.w, self.h)
        members = self.members[:]
        firstmember = self.members[0]
        othermembers = self.members[1:]
        # draw the members from last to first
        members.reverse()
        d = cf.gridDelta
        middlex = self.w/2 + x
        membery = y
        connectors = []
        for m in members:
            memberx = middlex-m.w/2
            m.drawAt(memberx, membery, test=test)
            connectors.insert(0, m.connectors(memberx, membery))
            membery += m.h
        # link in the first member with straight lines
        firstconnector = connectors[0]
        (fleft, fright) = firstconnector
        linky = y+self.h-self.s
        startLine = (x, linky)
        endLine = (x+self.w, linky)
        self.addLines( [startLine, fleft] )
        self.addLines( [fright, endLine] )
        # link in other members with jagged lines
        otherconnectors = connectors[1:]
        for (member, connector) in zip(othermembers, otherconnectors):
            (fleft, fright) = connector
            (leftX, leftY) = fleft
            p0 = (x+d, linky)
            p1 = (x+d*2, linky-d)
            p2 = (x+d*2, leftY+d)
            p3 = (x+d*3, leftY)
            #pr "addLines", [startLine, p0, p1, p2, p3, fleft]
            # work around a bug in skimpyGimpy.canvas which doesn't allow dup'd points
            segs = [startLine, p0, p1, p2, p3]
            if not near(p3, fleft):
                segs.append(fleft)
            self.addLines(segs)
            # mirror image
            (rightX, rightY) = fright
            p0 = (x+self.w-d, linky)
            p1 = (x+self.w-d*2, linky-d)
            p2 = (x+self.w-d*2, rightY+d)
            p3 = (x+self.w-d*3, rightY)
            #c.addLines([endLine, p0, p1, p2, p3, fright])
            segs = [p3, p2, p1, p0, endLine]
            if not near(p3,fright):
                segs.insert(0, fright)
            #self.addLines([fright, p3, p2, p1, p0, endLine])
            self.addLines(segs)
        # put a little arrowheads too...
        endX = endLine[0]
        #self.addLines( [ (endX-d, linky+d), endLine, (endX-d, linky-d) ] )
        self.arrowRight(endX, linky)
        startX = x+d
        #self.addLines( [ (startX-d, linky+d), (startX, linky), (startX-d, linky-d) ] )
        self.arrowRight(startX, linky)

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.setColor(55,55,95)
    c.addFont("propell", fontdir+"/propell.bdf")
    l = Literal.Literal("test literal", c)
    l2 = Literal.Literal(["another", "test literal"], c)
    ch = Choose([l, l2], c)
    l3 = Literal.Literal("nothing", c)
    ch2 = Choose([ch, l3, l2], c)
    ch2.drawAt(120,190)
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test()
