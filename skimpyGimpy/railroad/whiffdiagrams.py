"Generate WHIFF template configurations railroad diagrams"

import os
from .Choose import Choose
from .Repeat import Repeat
from .RepeatDelimited import RepeatDelimited
from .Optional import Optional
from .Sequence import Sequence
from skimpyGimpy import canvas
from .Nonterminal import Nonterminal
from .Literal import Literal
from .Define import Define

directory = "/tmp/diagrams"
fontdir = "."

def getc():
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    #c.addFont("propell", fontdir+"/5x7.bdf")
    return c

def pp():
    c = getc()
    param = Nonterminal("PARAMETER", c)
    cgidefault = Nonterminal(["CGI", "DEFAULT"], c)
    definition = Repeat(Choose([param, cgidefault], c), c)
    diagram = Define(["PAGE", "PARAMETERS"], definition, c)
    dump(diagram, "PageParameters", c)

def dump(diagram, filename, c):
    diagram.drawAt(0,0)
    filepath = directory+"/"+filename+".png"
    c.dumpToPNG(filepath)
    print("wrote", filepath)

def param(tag="parameter", nameStr="name"):
    c = getc()
    fullbody = Sequence(["}}", Nonterminal("PAGE", c), "{{/%s}}"%tag], c)
    body = Choose([fullbody, "/}}"], c)
    name = Nonterminal(nameStr, c)
    definition = Sequence(["{{%s"%tag, name, body], c)
    ntname = tag.upper().split("-")
    diagram = Define(ntname, definition, c)
    dump(diagram, tag, c)

def cgidefault():
    c = getc()
    name = Nonterminal("name", c)
    page = Nonterminal("PAGE", c)
    definition = Sequence(["{{cgi-default", name, "}}",
                           page, "{{/cgi-default}}"], c)
    diagram = Define (["CGI", "DEFAULT"], definition, c)
    dump(diagram, "CgiDefaults", c)
    
def getenv(tag="get-env"):
    return param(tag, ["INDEXED", "NAME"])

def indexedName():
    c = getc()
    name = Nonterminal("name", c)
    json = Nonterminal("json", c)
    optIndex = Optional(Repeat(["[", json, "]"], c), c)
    diagram = Define(["INDEXED", "NAME"], [name, optIndex], c)
    dump(diagram, "indexedName", c)
    
def getid():
    return getenv("get-id")
    
def ident(tag="id"):
    c = getc()
    name = Nonterminal("name", c)
    definition = Sequence(["{{%s"%tag, name, "/}}"], c)
    ntname = tag.upper().split("-")
    diagram = Define(ntname, definition, c)
    dump(diagram, tag, c)
    
def getcgi(tag="get-cgi"):
    return ident(tag)
    
def text():
    c = getc()
    definition = Nonterminal(["character sequence", "not containing",
                              "either }} or {{"],c)
    diagram = Define("text", definition, c)
    dump(diagram, "text", c)
    
def url():
    c = getc()
    definition = Nonterminal(["Standard HTTP", "Uniform Resource",
                              "Locator"],c)
    diagram = Define("url", definition, c)
    dump(diagram, "url", c)

def name():
    c = getc()
    definition = Nonterminal(["alpha-numeric name", "which may contain",
                              "dot '.' or underscore '_'"],c)
    diagram = Define("name", definition, c)
    dump(diagram, "name", c)

def json():
    c = getc()
    definition = Nonterminal(["Javascript Serialized", "Object Notation",
                              "encoded data structure"],c)
    diagram = Define("json", definition, c)
    dump(diagram, "json", c)

def comment():
    c = getc()
    stuff = Nonterminal(["character sequence", "not containing }}"],c)
    definition = Sequence(["{{comment", stuff, "/}}"], c)
    diagram = Define("comment", definition, c)
    dump(diagram, "comment", c)

def useSection():
    c = getc()
    name = Nonterminal("name", c)
    env = Nonterminal(["ENV", "PAIRS"], c)
    optenv = Optional(env, c)
    args = Nonterminal("ARGS", c)
    argsseq = Sequence(["}}", args, ["{{/use-","section}}"]], c)
    optargs = Choose([argsseq, "/}}"], c)
    definition = Sequence([["{{use-","section"], name, optenv, optargs], c)
    diagram = Define(["USE", "SECTION"], definition, c)
    dump(diagram, "useSection", c)

def page():
    c = getc()
    env = Optional(Nonterminal(["PAGE", "ENVIRONMENT"], c), c)
    params = Optional(Nonterminal(["PAGE", "PARAMETERS"], c), c)
    comp = Optional(Nonterminal(["PAGE", "COMPONENTS"], c), c)
    definition = Sequence([env, params, comp], c)
    diagram = Define("PAGE", definition, c)
    dump(diagram, "page", c)

def pageEnv():
    c = getc()
    env = Nonterminal(["ENV", "PAIRS"], c)
    diagram = Define(["PAGE", "ENVIRONMENT"], ["{{env", env, "/}}"],c)
    dump(diagram, "pageEnv", c)
    
def useUrl():
    c = getc()
    url = Nonterminal("url", c)
    env = Nonterminal(["ENV", "PAIRS"], c)
    optenv = Optional(env, c)
    args = Nonterminal("ARGS", c)
    argsseq = Sequence(["}}", args, ["{{/use-","url}}"]], c)
    optargs = Choose([argsseq, "/}}"], c)
    definition = Sequence([["{{use-","url"], '"', url, '"', optenv, optargs], c)
    diagram = Define(["USE", "URL"], definition, c)
    dump(diagram, "useUrl", c)

def envPairs():
    c = getc()
    name = Nonterminal("name", c)
    json = Nonterminal("json", c)
    pair = Sequence([name, ":", json], c)
    rept = RepeatDelimited(pair, ",", c)
    opt = Optional(rept, c)
    diagram = Define(["ENV", "PAIRS"], opt, c)
    dump(diagram, "envPairs", c)

def setId(tag="set-id"):
    c = getc()
    name = Nonterminal("name", c)
    page = Nonterminal("PAGE", c)
    nttag = tag.upper().split("-")
    diagram = Define(nttag, ["{{%s"%tag, name, "}}", page, "{{/%s}}"%tag], c)
    dump(diagram, tag, c)

def section():
    setId("section")

def pageComponents():
    c = getc()
    options = "GET-CGI ID GET-ENV USE-SECTION USE-URL GET-ID TEXT"
    optL = options.split()
    optLL = [x.split("-") for x in optL]
    optNT = [Nonterminal(x,c) for x in optLL]
    choice = Repeat(Choose(optNT, c), c)
    diagram = Define(["PAGE", "COMPONENTS"], choice, c)
    dump(diagram, "pageComponents", c)

def args():
    c = getc()
    options = "SECTION SET-ID SET-CGI BIND-URL BIND-SECTION"
    optL = options.split()
    optLL = [x.split("-") for x in optL]
    optNT = [Nonterminal(x,c) for x in optLL]
    choice = Repeat(Choose(optNT, c), c)
    orpage = Choose([Nonterminal("PAGE", c), choice], c)
    diagram = Define("ARGS", orpage, c)
    dump(diagram, "args", c)
    
def setCgi():
    setId("set-cgi")    

def bindSection():
    c = getc()
    name = Nonterminal("name", c)
    sectionname = Nonterminal(["section","name"], c)
    diagram = Define(["BIND", "URL"], ["{{bind-section", name,
                                       sectionname, "/}}"], c)
    dump(diagram, "bindSection", c)
    
def bindUrl():
    c = getc()
    name = Nonterminal("name", c)
    url = Nonterminal("url", c)
    diagram = Define(["BIND", "URL"], ["{{bind-section", name, '"',
                                       url, '"', "/}}"], c)
    dump(diagram, "bindUrl", c)

if __name__=="__main__":
    if not os.path.exists(directory):
        print("creating directory", directory)
        os.mkdir(directory)
    pp()
    param()
    cgidefault()
    getenv()
    ident()
    getid()
    getcgi()
    text()
    useSection()
    useUrl()
    comment()
    page()
    pageEnv()
    envPairs()
    section()
    setId()
    setCgi()
    indexedName()
    pageComponents()
    args()
    name()
    json()
    url()
    bindUrl()
    bindSection()
    
