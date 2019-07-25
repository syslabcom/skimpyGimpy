
from . import entity

class Relationship(entity.Entity):
    def drawContainer(self):
        entity.Entity.drawContainer(self, self.cfg.backgroundColor)
        c = self.canvas
        cfg = self.cfg
        d = cfg.delta
        (x,y) = self.p
        w = self.gw*d
        h = self.gh*d
        c.setColor(*cfg.relationshipColor)
        xR = x+w
        yU = y+h
        yM = y+h/2
        xl = x+2*d
        xr = xR-2*d
        if True or xl>xr:
            xl = xr = x+w/2
        points = [ (x, yM), (xl, yU), (xr, yU), (xR, yM), (xr, y), (xl, y) ]
        c.fillPolygon(points)

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    #c.setFont("propell", 1.0)
    #c.setColor(55,55,55)
    #c.centerText(0,0,"hi there!")
    l = Relationship("test literal", c, 120, 160)
    l2 = Relationship(["another", "test", "literal"], c, -120, -120)
    l.draw()
    l2.draw()
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test()

