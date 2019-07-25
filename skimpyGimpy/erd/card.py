
"cardinality marks"

MINS = [0, 1]
MAXS = [1, "many"]

class Cardinality:
    def __init__(self, minimum, maximum, upx, upy, rightx, righty, delta, canvas):
        if minimum not in MINS:
            raise ValueError("bad min "+repr((minimum, MINS)))
        if maximum not in MAXS:
            raise ValueError("bad max "+repr((maximum, MAXS)))
        assert abs(upx*rightx + upy*righty)<0.01, "ups and rights must be orthogonal"
        (self.minimum, self.maximum, self.upx, self.upy, self.rightx, self.righty, self.delta) = (
            minimum, maximum, upx, upy, rightx, righty, delta)
        self.canvas = canvas
    def addLines(self, lines):
        self.canvas.addLines(lines)
        lines = lines[:]
        lines.reverse()
        self.canvas.addLines(lines)
    def drawAt(self, x, y, test=False):
        (minimum, maximum, upx, upy, rightx, righty, delta) = (
            self.minimum, self.maximum, self.upx, self.upy, self.rightx, self.righty, self.delta)
        c = self.canvas
        if test:
            c.addLines( [ (x,y), (x+upx*delta, y+upy*delta),
                          (x+upx*2*delta+rightx*delta, y+upy*2*delta+righty*delta) ] )
            c.addLines( [ (x-2*delta*rightx, y-2*delta*righty),
                          (x+2*delta*rightx, y+2*delta*righty) ] )
        # draw min icon above
        xmin = x + upx*delta
        ymin = y + upy*delta
        if minimum==0:
            # circle radius delta/2
            c.addCircle(xmin, ymin, 3*delta/8)
        elif minimum==1:
            # line segment
            startx = xmin+rightx*delta/4
            starty = ymin+righty*delta/4
            endx = xmin-rightx*delta/4
            endy = ymin-righty*delta/4
            self.addLines( [ (startx, starty), (endx, endy) ] )
        else:
            raise ValueError("unreachable code "+repr(minimum))
        # draw max icon below
        xmax = x + upx*delta/2
        ymax = y + upy*delta/2
        if maximum==1:
            # line segment
            startx = xmax+rightx*delta/4
            starty = ymax+righty*delta/4
            endx = xmax-rightx*delta/4
            endy = ymax-righty*delta/4
            self.addLines( [ (startx, starty), (endx, endy) ] )
        elif maximum=="many":
            # hat
            startx = x+rightx*delta/2
            starty = y+righty*delta/2
            midx = x+upx*delta/2
            midy = y+upy*delta/2
            endx = x-rightx*delta/2
            endy = y-righty*delta/2
            self.addLines( [ (startx, starty), (midx, midy), (endx, endy) ] )
        else:
            raise ValueError("unreachable code")

def test(outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.setColor(0,0,0)
    (upx, upy) = (0,1)
    (rightx, righty) = (1,0)
    delta = 8
    x=0
    y=0
    for orientation in range(4):
        x = 0
        for minimum in MINS:
            for maximum in MAXS:
                card = Cardinality(minimum, maximum, upx, upy, rightx, righty, delta, c)
                card.drawAt(x,y, True)
                x += 5*delta
        # rotate
        (upy, upx, rightx, righty) = (righty, -rightx, upx, upy)
        y += 5*delta
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test()

    
    
