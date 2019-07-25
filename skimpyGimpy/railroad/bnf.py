"""
Generate a PNG railroad diagram from a BNF rule.
   target ::= rule
   rule in  xxx | yyy , [ xxx ] , xxx* , xxx+ , "literal" , nonterminal
"""

from .Choose import Choose
from .Repeat import Repeat
from .RepeatDelimited import RepeatDelimited
from .Optional import Optional
from .Sequence import Sequence
from skimpyGimpy import canvas
from .Nonterminal import Nonterminal
from .Literal import Literal
from .Define import Define

directoryname = "diagrams"
fontdir = "."
import string

punct = "|[]()+*"

def getc(fontdir=fontdir):
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    #c.addFont("propell", fontdir+"/5x7.bdf")
    return c

def dump(diagram, filename, c):
    diagram.drawAt(0,0)
    filepath = filename #directory+"/"+filename+".png"
    c.dumpToPNG(filepath)
    ##pr "wrote", filepath

def bnfDiagram(rule, filename):
    "store a bnf diagram representing the rule to the given filename"
    c = getc()
    [target, body] = rule.split("::=")
    target = target.strip()
    body = body.strip()
    (definition, cursor) = alternatives([], 0, body, c)
    if cursor<len(body):
        raise ValueError("not all of body consumed "+repr(body[cursor:]))
    diagram = Define(target, definition, c)
    dump(diagram, filename, c)

def alternatives(accumulator, cursor, text, c):
    (sq, cursor1) = sequence([], cursor, text, c)
    #pr "alternative", repr(text[cursor:])
    accumulator1 = accumulator+[sq]
    ltext = len(text)
    if cursor1<=cursor:
        raise ValueError("cursor not advancing")
    if text[cursor1:cursor1+1]=="|":
        #pr "alternative advancing at", repr(text[cursor1:])
        cursor1+=1
        while cursor1<ltext and text[cursor1] in string.whitespace:
            cursor1+=1
        # recursive case
        return alternatives(accumulator1, cursor1, text, c)
    if not accumulator1:
        raise ValueError("don't know what to do with empty rule body in alternative "+repr((cursor, text[cursor:])))
    if len(accumulator1)==1:
        return (accumulator1[0], cursor1)
    return (Choose(accumulator1, c), cursor1)

def sequence(accumulator, cursor, text, c):
    #pr "sequence at", repr(text[cursor:])
    (paren, cursor1) = parenthesized(cursor, text, c)
    if cursor1<=cursor:
        raise ValueError("cursor not advancing")
    accumulator1 = accumulator + [paren]
    if len(text)>cursor1 and not text[cursor1] in "|)]":
        #pr "sequence advancing at", repr(text[cursor1:])
        # parse another entry in sequence
        return sequence(accumulator1, cursor1, text, c)
    else:
        # end of sequence
        if not accumulator1:
            raise ValueError("don't know what to do with empty rule body in sequence "+repr((cursor, text[cursor:])))
        if len(accumulator1)==1:
            # trivial seq
            return (accumulator1[0], cursor1)
        else:
            return (Sequence(accumulator1, c), cursor1)
        
def parenthesized(cursor, text, c):
    start = cursor
    ltext = len(text)
    firstchar = text[cursor:cursor+1]
    if firstchar in string.whitespace:
        raise ValueError("cursor should not be positioned at whitespace")
    # parse an item
    if firstchar=="(":
        # (parenthesized)
        #pr "parsing parenthesized", repr(text[cursor:])
        (result,cursor) = alternatives([], cursor+1, text, c)
        if text[cursor:cursor+1]!=")":
            raise "mismatched parentheses "+repr((cursor, text[cursor:]))
        cursor+=1
    elif firstchar=="[":
        #pr "parsing bracketed", repr(text[cursor:])
        # [optional]
        (alt, cursor) = alternatives([], cursor+1, text, c)
        if text[cursor:cursor+1]!="]":
            raise "mismatched brackets "+repr((cursor, text[cursor:]))
        result = Optional(alt, c)
        cursor += 1
    else:
        # not parenthesized... (base case)
        #pr "parsing basic element", repr(text[cursor:])
        (result, cursor) = termOrNonTerm(cursor, text, c)
    # skip ws
    while cursor<ltext and text[cursor] in string.whitespace:
        cursor+=1
    # look for */+
    ch = text[cursor:cursor+1]
    if ch=="*":
        #pr "repeat* found", repr(text[cursor:])
        result = Optional(Repeat(result, c), c)
        cursor += 1
    elif ch=="+":
        #pr "repeat+ found", repr(text[cursor:])        
        result = Repeat(result, c)
        cursor += 1
    # skip ws
    while cursor<ltext and text[cursor] in string.whitespace:
        cursor+=1
    #pr "parsed paren component", repr(text[start:cursor])
    return (result, cursor)

def termOrNonTerm(cursor, text, c):
    start = cursor
    firstchar = text[cursor]
    if firstchar in string.whitespace:
        raise ValueError("cursor should not be positioned at white space")
    if firstchar in punct:
        raise ValueError("cursor should not be positioned at punctuation")
    if firstchar=='"':
        # parse a terminal
        cursor += 1
        namestart = nameend = cursor
        while text[cursor]!='"':
            cursor+=1
            nameend = cursor
        name = text[namestart:nameend]
        result = Literal(name, c)
        cursor+=1
        #pr "found literal", repr(text[start:cursor])
    else:
        # parse a nonterm
        namestart = nameend = cursor
        ch = text[cursor]
        while ch not in punct and ch not in string.whitespace:
            cursor+=1
            nameend = cursor
            ch = text[cursor]
        name = text[namestart:nameend]
        result = Nonterminal(name, c)
        #pr "found nonterm", repr(text[start:cursor])
    ltext = len(text)
    while cursor<ltext and text[cursor] in string.whitespace:
        cursor+=1
    return (result, cursor)

def dotest(rule, filename):
    print("storing", rule)
    bnfDiagram(rule, filename)
    print("stored to", filename)

def test():
    dotest(' literal ::= "the literal" ', "/tmp/literal.png")
    dotest(' nonterm ::= TheNonTerm  | "the literal" ', "/tmp/nonterm.png")
    dotest(' alt ::= "<<" TheNonTerm  | "the literal" ">>" ', "/tmp/seq.png")
    dotest(' alt ::= "<<" (TheNonTerm  | "the literal") ">>" ', "/tmp/paren.png")
    dotest(' alt ::= "<<" (TheNonTerm  | "the literal")* ">>" ', "/tmp/star.png")
    dotest(' alt ::= "<<" (TheNonTerm  | "the literal")+ ">>" ', "/tmp/more.png")
    dotest(' alt ::= "<<" [TheNonTerm  | "the literal"] ">>" ', "/tmp/opt.png")

if __name__=="__main__":
    test()
