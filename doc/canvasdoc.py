"""
python script generator for canvas.html
"""


test = False

import sys, os
#from skimpyGimpy import canvas
#indexFilePath = "../wave/waveIndex.zip"

#if not os.path.exists(indexFilePath):
#    raise ValueError, "cannot find wave index file "+repr(indexFilePath)

if not test:
    sys.stdout = open("canvas.html", "w")

showtemplate = """
from skimpyGimpy import canvas
c = canvas.Canvas()
%(code)s
c.dumpToPNG("%(outfile)s")
"""

def qq(s):
    return s.replace("&","&amp;").replace("<", "&lt;").replace(">", "&gt;")

def show(filename0, code):
    filename = "png/"+filename0
    D = {}
    D["code"] = code
    D["outfile"] = filename
    prog = showtemplate % D
    exec(prog)
    print """
    <table border width="50%">
    <tr><th>Program</th></tr>
    <tr><td>
    """
    print "<pre>%s</pre>"%qq(prog)
    print """
    </td></tr>
    <tr><th>generated image <code>%s</code></th></tr>
    <tr><th>
    <tr><th> <img src="%s"> </th></tr>
    </table><br>
    """ % (filename, filename)


print r"""
<html>
<head>
<title>
Skimpy Gimpy PNG image canvas documentation
</title>
</head>
<body>

<table width="100%">
<td align="right">
<a href="index.html">Return to index</a>
</td>
</table>

<h3>Skimpy Gimpy PNG image canvas documentation</h3>

As a fun add on the Skimpy Gimpy package includes a <code>canvas</code>
Python
module which makes it very easy to generate certain kinds of PNG images.
Not all PNG features are implemented, but enough are available to make
the package fun and useful.  For large and complex images this package
will be slower than other methods because it is implemented in a
keep-it-simple-stupid python-only mode, but for small simpler
images it is fast enough for many uses.

<p>
As an advanced feature, the canvas includes the capability to generate
Javascript data structures which can be used to implement mouse tracking
over an image created using the canvas.  For example the following image
of the United States was generated using a canvas and integrated into
this document with the javascript data structures to present information
about the states when the mouse hovers above each state.

<script src="canvas.js"></script>

<script src="statesDemo/states.js"></script>

<script>
function onState(alertString, x, y) {
	var span = document.getElementById("myspan");
	//span.innerHTML = alertString+" "+x+" "+y;
	var newHTML = alertString;
	var stateName = alertString.toLowerCase();
	if (alertString!="out") {
	newHTML += " <br><img src=\"statesDemo/"+stateName+".png\">";
	}
	//newHTML += " "+stateName+" <br> <img src=\""+stateName+".png\">";
	var stateInfo = States[stateName];
	if (stateInfo) {
		newHTML+= "<table border>"+
			"<tr> <th>Capital</th> <td>"+stateInfo["Capital"]+"</td> </tr>"+
			"<tr> <th>StateFlower</th> <td>"+stateInfo['StateFlower']+"</td> </tr>"+
			"</table>";
	} else {
		newHTML+= "<br>(not a state)";
	}
	span.innerHTML = newHTML;
}
</script>
<br>
<center> <b>United States Mouse Tracking Example</b>
<table width="800">
<tr>
    <th width="510">
        <img src="statesDemo/AllStates.png" id="AllStates" width="500" height="300">
    </th>
    <td>
        <span id="myspan"> State information should appear here
        <br>when the mouse hovers over one of the states. </span>
    </td>
</tr>
</table>
</center>

<!-- java script scan line data structure -->
<script src="statesDemo/AllStates.js"></script>

<p>
This document walks through
some example uses of the module and its features.


<h3>Where do you get it?</h3>

<a href="http://www.sourceforge.net/projects/skimpygimpy/">Please go to the Skimpy Gimpy sourceforge
project page and click on the download link.</a>



<h3>Hello World</h3>

The following example generates a "hello world" image file and demonstrates
the use of colors and generation of text.
"""

show("HelloWorld.png", """
# set the foreground color to a light blue
c.setColor(99,99,0xff)

# set the background color to a dark green
c.setBackgroundColor(10,50,0)

# name a font "propell" and associate it with a BDF font file
c.addFont("propell", "../fonts/mlmfonts/propell.bdf")

# set the current font to "propell" with scale 2.0 and
# pixel radius 1.3
c.setFont("propell", 2.0, 1.3)

# draw some text
c.addText(0,0, "Hello PNG World")
""")

print """
The first two lines of this example import the <code>canvas</code> module
and create a <code>Canvas</code> object.  The <code>Canvas</code> object
<code>c</code> encapsulates all information drawn to the image as well as
state information relating to the how to draw additional objects (such
as the current color, font, and rotation).
<p>
The last line of the example dumps the contents of the canvas
<code>c</code> to a PNG image file <code>"HelloWorld.png"</code>.
Note that the size of the image is not specified in the example.
By default the canvas will make the image size a rectangular region
just large enough to contain all the drawn pixels. (See the
<code>crop</code> method below to specify the image size.)
<p>
The lines in between the first two and the last one deal with colors
and drawing text.

<h3>Colors</h3>

Before any draw operation a canvas should have a foreground "paint color"
defined using
<pre>
c.setColor(R,G,B) # R,G,B in range 0..255
</pre>
which defines the red, green, and blue intensities for the current
drawing color.
<p>
A canvas may also have exactly one optional background color
specified by
<pre>
c.setBackgroundColor(R,G,B)
</pre>
which specifies the red, green, and blue intensities for the pixels
in the image which is not explicitly drawn on.  If the background color
is left out the background of the image will be <b>transparent</b>;
so, for example, if the image is
in a web page it will show whatever is behind it on the page, as
demonstrated in the following example.
"""

show("TransparentWorld.png", """
# set the foreground color to a light blue
c.setColor(99,99,0xff)

# NO BACKGROUND COLOR (TRANSPARENT)

# name a font "propell" and associate it with a BDF font file
c.addFont("propell", "../fonts/mlmfonts/propell.bdf")

# set the current font to "propell" with scale 2.0 and
# pixel radius 1.3
c.setFont("propell", 2.0, 1.3)

# draw some text
c.addText(0,0, "Hello Transparent PNG World")
""")

print """
<h3>Circles and Coordinates</h3>

The following example draws a number of circles
onto a PNG image using the method
<pre>
c.addCircle(centerX, centerY, radius)
</pre>
which draws a circle of radius <code>radius</code> centered at
<code>(centerX, centerY)</code> using the current foreground color.
The example also demonstrates canvas coordinates
and painting over objects.
"""

show("Coords.png", """
# set up the font as cursive, scale 1.0
c.addFont("cursive", "../fonts/cursive.bdf")
c.setFont("cursive", 1.0)
# set the background color to pale yellow
c.setBackgroundColor(255,255,100)

# put circles and a label at (0,0)
c.setColor(255,0,0)
c.addCircle(0,0, 30) # big blue circle
c.setColor(0,255,0)
c.addCircle(0,0, 15) # medium green circle
c.setColor(0,0,255)
c.addCircle(0,0,2) # small blue circle
c.setColor(0,0,0)
c.addText(0,0, "(0,0)") # black text

# put circles and a label at (50,50)
c.setColor(255,0,0)
c.addCircle(50,50, 30) # big blue circle
c.setColor(0,255,0)
c.addCircle(50,50, 15) # medium green circle
c.setColor(0,0,255)
c.addCircle(50,50,2) # small blue circle
c.setColor(0,0,0)
c.addText(50,50, "(50,50)") # black text

# put circles and a label at (-50,-50)
c.setColor(255,0,0)
c.addCircle(-50,-50, 30) # big blue circle
c.setColor(0,255,0)
c.addCircle(-50,-50, 15) # medium green circle
c.setColor(0,0,255)
c.addCircle(-50,-50,2) # small blue circle
c.setColor(0,0,0)
c.addText(-50,-50, "(-50,-50)") # black text

# put circles and a label at (50,-50)
c.setColor(255,0,0)
c.addCircle(50,-50, 30) # big blue circle
c.setColor(0,255,0)
c.addCircle(50,-50, 15) # medium green circle
c.setColor(0,0,255)
c.addCircle(50,-50,2) # small blue circle
c.setColor(0,0,0)
c.addText(50,-50, "(50,-50)") # black text
""")

print """
Please note the following features of the canvas demonstrated above
<ul>
<li> The canvas uses standard cartesian (x-right, y-up) coordinates.
<li> Coordinates may be negative.
<li> If you draw an object over another object the part of the older
object that is drawn on will be obscured.  For example if we reverse the
order of the drawn circles, only the big red one would remain visible.
</ul>

<h3>Fonts and text</h3>

The method
<pre>
c.addFont(fontName, BDFFontFilePath)
</pre>
names a font for internal use and associates the name with an external
BDF format font file (such as any of the fonts provided in the Skimpy
distribution).
<p>
Once a font has been named it may be set as the current font for the
canvas using the method
<pre>
c.setFont(fontName, fontScale=1.0, radius=None)
</pre>
The <code>fontScale</code> if given adjusts the size of the
font and the font radius if given adjusts the pixel radius.
BDF format fonts are defined as arrays of pixels, and the
canvas represents those pixels using circles.  If the radius
is not given the canvas attempts to choose a radius that will
fill in the glyphs without making them bleed together.
<p>
The methods
<pre>
c.addText(x,y, text)
c.centerText(x,y, text)
c.rightJustifyText(x,y, text)
</pre>
Draws text on the canvas using the current foreground color
and the current font options, left justified, centered, or
right justified respectively with respect to the <code>(x,y)</code>
location.
<p>
The following example exercises various font options.
"""

show("Fonts.png", """
# name some fonts
c.addFont("propell", "../fonts/mlmfonts/propell.bdf")
c.addFont("cursive", "../fonts/cursive.bdf")
# set colors
c.setBackgroundColor(255,255,100)
c.setColor(255,0,0)
# draw some cursive
c.setFont("cursive")
c.addText(0,200, "cursive")
c.centerText(0,180, "centered")
c.rightJustifyText(0,160, "right justified")
c.setFont("cursive", 2.5)
c.addText(0,140, "larger")
# draw some propell
c.setColor(0,255,0)
c.setFont("propell")
c.addText(0,100, "propell")
c.centerText(0,80, "centered")
c.rightJustifyText(0,60, "right justified")
c.setFont("propell", 2.5)
c.addText(0,40, "larger")
""")

print """
Note that the <code>y</code> coordinate for drawing text always
refers to the "base line" for the text.

<h3>Rectangles, rotations, translations</h3>

The method
<pre>
c.addRect(llx, lly, width, height)
</pre>
draws a rectangle using the current forground color starting
at lower left corner <code>(llx,lly)</code> and extend for
width <code>width</code> and height <code>height</code>.
The following example draws a green rectangle over a red one.
"""

show("Rects.png", """
c.setBackgroundColor(255,255,100)
c.setColor(255,0,0) 
c.addRect(0,0,150,5) # horizontal red rect
c.setColor(0,255,0)
c.addRect(20,-30, 10,160) # vertical green rect

# add some helpful labels
c.addFont("cursive", "../fonts/cursive.bdf")
c.setFont("cursive")
c.setColor(0,0,0)
c.addText(150,5,"(0,0) 150x5")
c.rightJustifyText(20,130,"(20,-30) 10x160")
""")

print """
It is often very convenient to "shift" or "rotate"
the coordinate system when rendering graphics.  To support
such coordinate transformation the canvas provides the
following methods
<pre>
c.translate(dx, dy)
c.rotateRadians(radians)
rotate(degrees)
</pre>
The following example generates two sets of rectangles like the
previous example, one unrotated, and one rotated by 135 degrees.
"""


show("RotRects.png", """
c.setBackgroundColor(255,255,100)
c.addFont("propell", "../fonts/mlmfonts/propell.bdf")
c.setFont("propell", 1.0)

# UNROTATED
c.setColor(255,0,0) 
c.addRect(0,0,150,5) # horizontal red rect
c.setColor(0,255,0)
c.addRect(20,-30, 10,160) # vertical green rect
c.setColor(0,0,0)
c.addText(0,0,"(0,0)")

# ROTATE THE COORDINATE SYSTEM
c.rotate(135)

c.setColor(255,0,0) 
c.addRect(0,0,150,5) # horizontal red rect
c.setColor(0,255,0)
c.addRect(20,-30, 10,160) # vertical green rect
c.setColor(0,0,0)
c.addText(0,0,"(0,0) rotated")
""")

print """
Similarly the following example draws two pairs of rectangles,
one translated to the alternate coordinate system with origin
at (-50,50).
"""

show("ShiftRects.png", """
c.setBackgroundColor(255,255,100)
c.addFont("propell", "../fonts/mlmfonts/propell.bdf")
c.setFont("propell", 1.0)

# UNSHIFTED
c.setColor(255,0,0) 
c.addRect(0,0,150,5) # horizontal red rect
c.setColor(0,255,0)
c.addRect(20,-30, 10,160) # vertical green rect
c.setColor(0,0,0)
c.addText(0,0,"(0,0) shifted")

# SHIFT THE COORDINATE SYSTEM
c.translate(-50,50)

c.setColor(255,0,0) 
c.addRect(0,0,150,5) # horizontal red rect
c.setColor(0,255,0)
c.addRect(20,-30, 10,160) # vertical green rect
c.setColor(0,0,0)
c.addText(0,0,"(0,0)")
""")

print """
Furthermore multiple rotations and translations can be
combined as demonstrated below.

<h3>Saving and restoring the canvas state</h3>

At any time the method
<pre>
c.saveState()
</pre>
method will store the state of the canvas (such as its current font
and coordinate transformation) to make it easy to restore the state
later on using
<pre>
c.restoreState()
</pre>
For example the following example saves and restores the state
in order to return to the default coordinate transform after a rotation
and a translation.
"""

show("State.png", """
c.setBackgroundColor(255,255,100)
c.addFont("cursive", "../fonts/cursive.bdf")
c.addFont("propell", "../fonts/mlmfonts/propell.bdf")
c.setFont("cursive", 1.0, 1.2)
c.setColor(0,255,255) 

# SAVE THE STATE
c.saveState()

# CHANGE THE CANVAS STATE
c.translate(-50,50)
c.rotate(135)
c.setFont("propell")

# DRAW IN CHANGED STATE
c.setColor(255,0,0) 
c.addRect(0,0,150,5) # horizontal red rect
c.setColor(0,255,0)
c.addRect(20,-30, 10,160) # vertical blue rect
c.setColor(0,0,0)
c.addText(0,0,"(0,0)")

# RESTORE STATE
c.restoreState()

# DRAW IN RESTORED STATE
c.addRect(0,0,150,5) # horizontal cyan rect
c.setColor(255,0,255)
c.addRect(20,-30, 10,160) # vertical magenta rect
c.setColor(0,0,0)
c.addText(0,0,"(0,0)")
""")

print """

<h3>Filling Polygons</h3>

The canvas method
<pre>
c.fillPolygon(pointSequence)
</pre>
Fills a closed polygonal region bounded by the line segments between successive vertices of the point
sequence with the current color.
"""

show("fillPoly.png", """
c.setBackgroundColor(255,255,100)
c.setColor(0,0,255)
pointSequence = [ (0,0), (50,50), (75,0), (100,25), (50,-50)]
c.fillPolygon(pointSequence)
""")

print """

<h3>Drawing lines</h3>

The canvas method
<pre>
c.addLine((x1,y2), (x2,y2))
</pre>
draws a line segment starting at <code>(x1,y1)</code>
and ending at <code>(x2,y2)</code> using the current foreground
color, line cap, and line width.  The methods
<pre>
c.setCap(capLength)
c.setWidth(lineWidth)
</pre>
The line cap specifies a distance to overshoot the end of a line
segment.  The following example demonstrates these methods by
drawing a thin blue line on a thick red line.

"""


show("Line.png", """
c.setBackgroundColor(255,255,100)

# thick red line with no cap
c.setColor(255,0,0)
c.setCap(0)
c.setWidth(20)
c.addLine( (0,0), (100,100) )

# thin blue line with cap=10
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
c.addLine( (0,0), (100,100) )
""")

print """
The canvas object also has the method
<pre>
c.addLines(points)
c.addLines(points, closed=True)
</pre>
which draws a polyline if <code>closed</code>
is not specified or a polygon if <code>closed=True</code>
built from the <code>points</code> sequence.  For example
the following draws a blue triangle over a red
zigzag.
"""

show("Lines.png", """
c.setBackgroundColor(255,255,100)

# thick red line with no cap
c.setColor(255,0,0)
c.setCap(4)
c.setWidth(9)
zigzag = [ (0,25), (25,50), (50,25), (75,50), (100,25) ]
c.addLines( zigzag )

# thin blue line with cap=10
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
triangle = [ (0,0), (50,50), (100,0) ]
c.addLines( triangle, closed=True )
""")

print """

<h3>Filling regions</h3>

The method
<pre>
c.growFill(x,y, stopColorRGB=None)
</pre>
Fills a region in an image, much like the "paint bucket" tool
often fills a region in image creation tools like Microsoft Paint.
If the <code>stopColorRGB</code> is not specified the fill will start
at the <code>(x,y)</code> position provided and grow until the first
change in color in the image, as demonstrated in the following example
which fills the lower part of the triangle up to the zigzag.

"""


show("fill1.png", """
c.setBackgroundColor(255,255,100)

# thick red zigzag
c.setColor(255,0,0)
c.setCap(4)
c.setWidth(9)
zigzag = [ (0,25), (25,50), (50,25), (75,50), (100,25) ]
c.addLines( zigzag )

# blue triangle
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
triangle = [ (0,0), (50,50), (100,0) ]
c.addLines( triangle, closed=True )
c.setColor(0,255,255)

# fill to any color change
c.growFill(20,10)
""")

print """
If the <code>stopColorRGB</code> is specified the fill will proceed until
a pixel with the given <code>stopColorRGB</code> is encountered.  For example
the following fill stops only at the triangle, painting over the part
of the zigzag that is inside the triangle.
"""

show("fill2.png", """
c.setBackgroundColor(255,255,100)

# thick red line with no cap
c.setColor(255,0,0)
c.setCap(4)
c.setWidth(9)
zigzag = [ (0,25), (25,50), (50,25), (75,50), (100,25) ]
c.addLines( zigzag )

# blue triangle
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
triangle = [ (0,0), (50,50), (100,0) ]
c.addLines( triangle, closed=True )
c.setColor(0,255,255)

# fill to blue
c.growFill(20,10, stopColorRGB=(0,0,255))
""")

print """

<h3>Specifying the view region (cropping)</h3>

By default the canvas generates a rectangular image just
large enough to include all drawn pixels.  If you desire
an image size different from that you may specify the size
using the method
<pre>
c.crop(minx, miny, maxx, maxy):
</pre>
which forces the image to range between x values <code>minx..maxx</code>
and y values <code>miny..maxy</code>.
<p>
For example the following shows the previous image on a larger
background.
"""

show("crop1.png", """
c.setBackgroundColor(255,255,100)

# thick red zigzag
c.setColor(255,0,0)
c.setCap(4)
c.setWidth(9)
zigzag = [ (0,25), (25,50), (50,25), (75,50), (100,25) ]
c.addLines( zigzag )

# blue triangle
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
triangle = [ (0,0), (50,50), (100,0) ]
c.addLines( triangle, closed=True )
c.setColor(0,255,255)

# fill to blue
c.growFill(20,10, stopColorRGB=(0,0,255))
c.crop(-20,-20, 120,70)
""")

print """
The following shows only the right side of the previous image
with a transparent background.
"""

show("crop2.png", """
# thick red zigzag
c.setColor(255,0,0)
c.setCap(4)
c.setWidth(9)
zigzag = [ (0,25), (25,50), (50,25), (75,50), (100,25) ]
c.addLines( zigzag )

# blue triangle
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
triangle = [ (0,0), (50,50), (100,0) ]
c.addLines( triangle, closed=True )
c.setColor(0,255,255)

# fill to blue
c.growFill(20,10, stopColorRGB=(0,0,255))
c.crop(50,-20, 120,70)
""")

print """
<h3>Javascript mouse tracking</h3>

The canvas object encapsulates a number of methods
to support the implementation of Javascript mouse event
callbacks for images embedded in web pages.  To help
implement Javascript mouse event callbacks the canvas method
provides the following: the ability to generate the <b>image</b>,
the ability to generate a <b>Javascript data structure</b> associated
with the image, and a collection of
<b>utility routines</b> <code>canvas.js</code>.  The HTML which
embeds the image must: name the image, include the <code>canvas.js</code>
utility routines, include the generated data structure, and define
a callback function to receive the mouse events.
<p>
The canvas object distinguishes different regions of the image
using string call back identifiers.  Strings are associated
with drawn pixels in much the same way as color are associated
with drawn pixels using the following methods.
The method
<pre>
c.setCallBack(callBackString)
</pre>
specifies a string to deliver to the mouse tracking call back
function any pixel drawn afterwards.  The method
<pre>
c.resetCallBack()
</pre>
Specifies that subsequently drawn pixels should not
be associate with an explicit callback string.  Finally, the method
<pre>
c.setBackgroundCallback(callBackString)
</pre>
specifies a string to deliver to the mouse tracking call back
function for any pixel with no explicitly defined callback string.
<p>
Once the image drawing is complete, generate the Javascript data
structure to support mouse callbacks using the canvas method
<pre>
c.dumpJavascript(toFileName, imageName, functionName)
</pre>
where <code>toFileName</code> provides the path for the Javascript file to
store the data structure, <code>imageName</code> provides the HTML
identifier used to locate the image in the HTML file, and
<code>functionName</code> names the Javascript function to handle
the mouse events.
<p>
The example shown below generates an image with associated
callback strings and also prints and HTML fragment which
embeds the image and the appropriate Javascript references
inside an HTML file.
"""

JAVASCRIPT_EXAMPLE = '''
from skimpyGimpy import canvas
c = canvas.Canvas()

c.setBackgroundCallback("MOUSE OVER BACKGROUND")
c.setBackgroundColor(255,255,100)

# thick red zigzag (with callback)
c.setCallBack("MOUSE OVER ZIGZAG")
c.setColor(255,0,0)
c.setCap(4)
c.setWidth(9)
zigzag = [ (0,25), (25,50), (50,25), (75,50), (100,25) ]
c.addLines( zigzag )

# blue triangle (no callback for border)
c.resetCallBack()
c.setColor(0,0,255)
c.setCap(10)
c.setWidth(2)
triangle = [ (0,0), (50,50), (100,0) ]
c.addLines( triangle, closed=True )
c.setColor(0,255,255)

# fill to blue (with callback)
c.setCallBack("MOUSE INSIDE TRIANGLE")
c.growFill(20,10, stopColorRGB=(0,0,255))
c.crop(-20,-20, 120,70)

# store the png
c.dumpToPNG("png/mouse.png")

# store the Javascript
c.dumpJavascript("png/mouse.js", "mouseExample", "mouseExampleCallback")

# print out the html fragment using the generated image and javascript
# for mouse tracking.
HTML_FRAGMENT = """

<!-- the image using the id "mouseExample" -->
<img src="png/mouse.png" id="mouseExample">

<!-- a div for displaying callback information -->
<div id="mouseExampleDiv">
Mouse callback information will display here.
</div>

<!-- the Javascript callback "mouseExampleCallback" -->
<script>
function mouseExampleCallback(alertString, x, y, event, image) {
        // display event information in the mouseExampleDiv
	var span = document.getElementById("mouseExampleDiv");
	span.innerHTML = "mouseChart called with "+alertString+
            "<br>coords "+x+" "+y+
            " <br>event.type="+event.type+
            " <br>image.id="+image.id;
}
</script>

<!-- the Javascript utility functions -->
<script src="canvas.js"></script>

<!-- the generated data structures -->
<script src="png/mouse.js"></script>

"""
print HTML_FRAGMENT
'''
print """
<pre>%s</pre>
""" % qq(JAVASCRIPT_EXAMPLE)

print """
Below the HTML code generated by the example is embedded in the present
document.  <em>Drag the mouse over the image to see the mouse events
reported below the image (on supported browsers, with Javascript enabled).</em>
<center>
"""
exec(JAVASCRIPT_EXAMPLE)
print "</center>"

print """
Note that the generated data structures make reference to the callback function
and the image object and therefore must <em>follow</em> the definition of both
the image and the callback function.
<p>
The callback function should have the following signature
<pre>
function mouseExampleCallback(alertString, x, y, event, image)
</pre>
where <code>alertString</code> provides the string associated for the
region under the mouse, <code>(x,y)</code> provide the coordinates for
the pixel in the image under the mouse, <code>event</code> is the
Javascript event object, and <code>image</code> is the HTML/DOM image
object.
"""

print """
<h3>Bar Chart Example</h3>

As an extended demonstration of how to use the canvas
capabilities SkimpyGimpy ships with two experimental
modules <code>pngBarChart</code>
and <code>pngPieChart</code> which generates charts.
Please look at the source of this module for more information.
An example bar chart.
<br>
<center> <img src="barchart.png"> </center>
"""
from skimpyGimpy import pngBarChart
pngBarChart.test("barchart.png")

print """

</body>
</html>
"""

print """
<h3>Entity Relationship Model Example</h3>

The <code>skimpyGimpy.erd</code> package demonstrates the
use of the <code>canvas</code> to create entity relationship
database design diagrams such as the following
<br>
<center> <img src="erdiagram.png"> </center>
<br>
Please see the source files for this package for more
information.
"""

print """
<h3>Railroad Diagrams</h3>

The <code>skimpyGimpy.railroad</code> package demonstrates the
use of the <code>canvas</code> to create railroad diagrams representing
the syntax of computer languages
such as the following
<br>
<center> <img src="rrdiagram.png"> </center>
<br>
Please see the source files for this package for more
information.
"""

