
import entity

class Attribute(entity.Entity):
    def drawContainer(self):
        entity.Entity.drawContainer(self, self.cfg.backgroundColor)
        c = self.canvas
        cfg = self.cfg
        d = cfg.delta
        (x,y) = self.p
        w = self.gw*d
        h = self.gh*d
        c.setColor(*cfg.attributeColor)
        xR = x+w-h/2
        xL = x+h/2
        yM = y+h/2
        rectwidth = xR-xL
        if rectwidth>0:
            c.addRect(xL, y, xR-xL, h)
            c.addCircle(xL, yM, h/2)
        c.addCircle(xR, yM, h/2)

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    #c.setFont("propell", 1.0)
    #c.setColor(55,55,55)
    #c.centerText(0,0,"hi there!")
    l = Attribute("test literal", c, 120, 160)
    l2 = Attribute(["another", "test", "literal"], c, -120, -120)
    l.draw()
    l2.draw()
    c.dumpToPNG(outfile)
    print "test output to", outfile

if __name__=="__main__":
    test()

