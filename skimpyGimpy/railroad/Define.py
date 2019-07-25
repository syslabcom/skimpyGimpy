
import Configuration
from Nonterminal import Nonterminal
import Literal
from Sequence import Sequence

class Define(Literal.LiteralBase):
    def __init__(self, nonterm, definition, canvas, config=None, indent=50):
        if config is None:
            config = Configuration.Configuration()
        self.indent = indent
        nonterm = self.nonterm = self.interpolate(nonterm, canvas, config, Nonterminal)
        definition = self.definition = self.interpolate(definition, canvas, config, Sequence)
        self.h = self.nonterm.h + self.definition.h
        self.w = max(self.nonterm.w, self.definition.w)
    def drawAt(self, x, y, test=False):
        self.definition.drawAt(x+self.indent,y, test=test)
        self.nonterm.drawAt(x, y+self.definition.h, test=test)

def test(fontdir=".", outfile="/tmp/out.png"):
    from Choose import Choose
    from Repeat import Repeat
    from RepeatDelimited import RepeatDelimited
    from Optional import Optional
    from Choose import Choose
    from Sequence import Sequence
    from skimpyGimpy import canvas
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    nonterm = "ARGUMENTS"
    section = Nonterminal("SECTION", c)
    setid = Nonterminal("SETID", c)
    setcgi = Nonterminal("SETCGI", c)
    page = Nonterminal("PAGE", c)
    complexArg = Choose([section, setid, setcgi], c)
    complexArgs = Repeat(complexArg, c)
    definition = Optional(Choose([page, complexArgs], c), c)
    D = Define(nonterm, definition, c)
    D.drawAt(0,0)
    name = Nonterminal("name", c)
    json = Nonterminal("json", c)
    pair = Sequence([name, ":", json], c)
    pairs = Optional(RepeatDelimited(pair, ",", c), c)
    D2 = Define(["ENV", "PAIRS"], pairs, c)
    D2.drawAt(0,200)
    pageenv = Optional(["PAGE", "ENV"], c)
    pageparams = Optional(["PAGE", "PARAMS"], c)
    pagecomponents = Optional(["PAGE", "COMPONENTS"], c)
    D3 = Define("PAGE", [pageenv, pageparams, pagecomponents], c)
    D3.drawAt(0,350)
    c.dumpToPNG(outfile)
    print "output to", outfile

if __name__=="__main__":
    test()
