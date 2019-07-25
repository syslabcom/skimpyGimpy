
"""
Railroad nonterminal
"""
import Configuration
from skimpyGimpy import bdf
import Literal
import types

class Nonterminal(Literal.LiteralBase):
    # could refactor better...
    def __init__(self,
                 text,
                 canvas,
                 config=None):
        if config is None:
            config = Configuration.Configuration()
        if type(text) in types.StringTypes:
            text = [text]
        self.text = text
        self.canvas = canvas
        self.config = config
        #pr "text is", text
        (textw, texth) = self.textGeometry(text, canvas, config,
                                           config.NonterminalFontName,
                                           config.NonterminalFontScale)
        self.h = 2*config.gridDelta+texth
        self.w = textw + 4*config.gridDelta
        self.s = config.gridDelta+texth/2        
    def drawAt(self, x, y, test=False):
        # draw the linking line
        c = self.canvas
        # if testing draw a strangely colored frame of reference
        cf = self.config
        if test:
            c.setColor(*cf.TestColor)
            c.addRect(x,y, self.w, self.h)
        d = cf.gridDelta
        (start, end) = self.connectors(x,y)
        self.addLines([start, end])
        By = y+d/2
        Zy = y+self.h-d/2
        Bx = x+d
        Zx = x+self.w-d
        hZ = Zy-By
        wZ = Zx-Bx
        # interior fill
        c.setColor(*cf.NonterminalBackground)
        c.addRect(Bx, By, wZ, hZ)
        # now add the strings
        xCenter = x + self.w/2
        yText = By+hZ-d*2
        c.setFont(cf.NonterminalFontName, cf.NonterminalFontScale,
                  cf.NonterminalFontRadius)
        c.setColor(*cf.NonterminalFontColor)
        for t in self.text:
            c.centerText(xCenter, yText, t)
            yText -= 2*d

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    l = Nonterminal("test nonterminal", c)
    l2 = Nonterminal(["another", "test", "nonterminal"], c)
    l.drawAt(20, 60, test=True)
    l2.drawAt(-20, -20, test=True)
    c.dumpToPNG(outfile)
    print "test output to", outfile

if __name__=="__main__":
    test()
