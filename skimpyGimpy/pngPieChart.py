"""
Object encapsulating a PNG pie chart.
"""

import math

RSHADES = [0,64,122]
NRSHADES = len(RSHADES)
SHADES = range(0,256,64)
NSHADES = len(SHADES)

class PieChart:
    colors = [ (RSHADES[ i%NRSHADES],
                SHADES[ (i*3/2+2) % NSHADES],
                SHADES[ (i*5/4+3) % NSHADES])
               for i in range(25) ]
    fontPath = "../fonts/mlmfonts/monosimple.bdf"
    fontScale = 1.0
    fontRadius = None
    fontMargin = 10
    labelColor = (255,0,0)
    labelInside = True
    labelMargin = 10
    def __init__(this, labelsAndData, radius):
        #print this.colors
        #print SHADES
        this.labelsAndData = labelsAndData
        this.radius = radius
    def drawOn(this, canvas):
        totalData = 0
        for (label, data) in this.labelsAndData:
            totalData += data
        radians = 0
        i = 0
        canvas.saveState()
        for (label, data) in this.labelsAndData:
            canvas.setCallBack("%s: %s" % (label, data))
            i += 1
            dataratio = data*1.0/totalData
            angle = 2*math.pi*dataratio
            endradians = radians + angle
            wedge = wedgePoints(radians, endradians, this.radius)
            color = this.colors[i % len(this.colors) ]
            canvas.setColorV(color)
            canvas.fillPolygon(wedge)
            radians = endradians
        canvas.restoreState()
        # do labels
        radians = 0
        canvas.addFont("f", this.fontPath)
        canvas.setFont("f", this.fontScale, this.fontRadius)
        if this.labelColor:
            canvas.setColorV(this.labelColor)
            for (label, data) in this.labelsAndData:
                dataratio = data*1.0/totalData
                angle = 2*math.pi*dataratio
                endradians = radians + angle
                midradians = radians + angle/2.0
                edgex = this.radius * math.cos(midradians)
                canvas.saveState()
                if edgex>=0: # or True:
                    canvas.rotateRadians(midradians)
                    if this.labelInside:
                        canvas.rightJustifyText(this.radius-this.labelMargin, 0, label)
                    else:
                        canvas.addText(this.radius + this.labelMargin, 0, label)
                else:
                    # don't show upside down labels
                    reverseRotation = midradians-math.pi
                    canvas.rotateRadians(reverseRotation)
                    if this.labelInside:
                        canvas.addText(-this.radius + this.labelMargin, 0, label)
                    else:
                        canvas.rightJustifyText(-this.radius-this.labelMargin, 0, label)
                canvas.restoreState()
                radians = endradians
        return canvas
    def drawTo(this, filename, jsfilename=None, htmlfilename=None,
               canvasLocation="canvas.js"):
        from canvas import Canvas
        c = Canvas()
        this.drawOn(c)
        c.dumpToPNG(filename)
        if jsfilename:
            c.dumpJavascript(jsfilename, "pieChart", "mouseChart")
            if htmlfilename:
                c.exampleHTML(htmlfilename, jsfilename, filename,
                              "pieChart", "mouseChart",
                              canvasLocation=canvasLocation)

def wedgePoints(startRadians, endRadians, radius, delta=math.pi/180):
    result = [ (0,0) ]
    if (endRadians<startRadians):
        raise ValueError, "end must be larger than start %s %s" % (
            endRadians,startRadians)
    nangles = int( (endRadians-startRadians)/delta)+2
    for i in range(nangles):
        angle = startRadians + (i-1)*delta
        x = math.cos(angle)*radius
        y = math.sin(angle)*radius
        result.append( (x,y) )
    return result

def test(name="pieChart", canvasLocation="canvas.js"):
    labelsAndData = [
        ("december", 30),
        ("january", 50),
        ("february", 40),
        ("march", 15),
        ("april", 64),
        ("may", 4),
        ("june", 49),
        ("july", 37),
        ]
    p = PieChart(labelsAndData, 200)
    p.drawTo(name+".png", name+".js", name+".html",
             canvasLocation=canvasLocation)

if __name__=="__main__":
    test()
