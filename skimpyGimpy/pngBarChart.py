
"KISS bar chart example class for PNG"

class BarChart:
    axisColor = (0xff, 0, 0)
    labelColor = (0, 0xff, 0)
    barColor = (0, 0, 0xff)
    fontPath = "../fonts/mlmfonts/monosimple.bdf"
    barWidth = 20
    barSeparation = 10
    barMaxHeight = 200
    fontScale = 1.0
    fontRadius = None
    fontMargin = 10
    axisWidth = 1
    tickFormat = "%4.2f"
    tickShift = 5
    lowerLeft = (-100,-100)
    upperRight = (300, 300)
    def __init__(this, labelsAndData, axisDelta):
        this.labelsAndData = labelsAndData
        this.axisDelta = axisDelta
    def drawTo(this, filename, jsfilename=None, htmlfilename=None,
               canvasLocation="canvas.js"):
        from canvas import Canvas
        c = Canvas()  
        #c.setBackgroundColor(0,0,0)
        #c.setBackgroundCallback("out")
        #c.setCallBack("not on data")
        ((xm,ym), (xM, yM)) = (this.lowerLeft, this.upperRight)
        c.crop(xm,ym,xM,yM)
        c.addFont("f", this.fontPath)
        c.setFont("f", this.fontScale, this.fontRadius)
        # draw labels
        c.saveState()
        c.rotate(-90)
        c.setColorV(this.labelColor)
        y = this.barSeparation
        maxdata = 0
        for (label, data) in this.labelsAndData:
            #c.setCallBack("%s: %s" % (data, label))
            c.addText(this.fontMargin,y, label)
            maxdata = max(data, maxdata)
            y = y+this.barSeparation+this.barWidth
        # draw bars
        c.setColorV(this.barColor)
        y = this.barSeparation
        for (label, data) in this.labelsAndData:
            c.setCallBack("%s: %s" % (label, data))
            barlength = (data*this.barMaxHeight)/maxdata
            c.addRect(-barlength,y,barlength,this.barWidth)
            y = y+this.barSeparation+this.barWidth
        c.restoreState()
        # draw axis
        c.setColorV(this.axisColor)
        c.addLine( (0,0), (0,this.barMaxHeight) )
        c.addLine( (0,0), (this.barSeparation+len(this.labelsAndData)*(this.barSeparation+this.barWidth), 0))
        mark = this.axisDelta
        while mark<maxdata:
            c.setColorV(this.axisColor)
            y = (mark*this.barMaxHeight)/maxdata
            c.addRect(-this.fontMargin, y,
                this.fontMargin, this.axisWidth)
            c.setColorV(this.labelColor)
            c.rightJustifyText(-this.fontMargin, y-this.tickShift, this.tickFormat%mark)
            mark += this.axisDelta
        # write the file
        c.dumpToPNG(filename)
        if jsfilename:
            c.dumpJavascript(jsfilename, "chart", "mouseChart")
            if htmlfilename:
                c.exampleHTML(htmlfilename, jsfilename, filename,
                              "chart", "mouseChart",
                              canvasLocation=canvasLocation)

def test(name="bars", verbose=False, canvasLocation="canvas.js"):
    fn = name+".png"
    js = name+".js"
    html = name+".html"
    if verbose:
        print "writing", fn, js, html
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
    axisDelta = 10
    b = BarChart(labelsAndData, axisDelta)
    b.drawTo(fn, js, html,
             canvasLocation=canvasLocation)

if __name__=="__main__":
    test(verbose=True)
