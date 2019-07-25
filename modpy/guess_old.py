#!c:/python24/python.exe -u

"""
This demo page implements a simple CAPTCHA visual "challenge/response"
intended to verify that the agent interacting with a web form is a human
and not a computer program.
"""

#import cgitb; cgitb.enable()

import sys
sys.path.append(r"/home/awatters/webapps/mod_python/htdocs/skimpyGimpy")
import skimpyGimpy, cgi

#data = cgi.FieldStorage()

#raise "test error"

#print "content-type: text/html"
#print

textsample = """
Despite their great species diversity all rodents share common
features Rodents have a single pair of incisors in each jaw
and the incisors grow continually throughout life The incisors
have thick enamel layers on the front but not on the back this
causes them to retain their chisel shape as they are worn down
Behind the incisors is a large gap in the tooth rows or diastema
there are no canines and typically only a few molars at the rear
of the jaws Rodents gnaw with their incisors by pushing the lower
jaw forward and chew with the molars by pulling the lower jaw backwards
In conjunction with these chewing patterns rodents have large
and complex jaw musculature with modifications to the skull
and jaws to accommodate it Like some other mammal taxa but
unlike rabbits and other lagomorphs male rodents have a baculum
penis bone Most rodents are herbivorous but some are
omnivorous and others prey on insects Rodents show a wide
range of lifestyles ranging from burrowing forms such as
gophers and mole rats to tree-dwelling squirrels and   
gliding flying squirrels from aquatic capybaras and muskrats to
desert specialists such as kangaroo rats and jerboas and from solitary
organisms such as porcupines to highly social organisms living in extensive
colonies such as prairie dogs left and naked mole rats

Rodents cost billions of dollars in lost crops each year
and some are carriers of human diseases such as bubonic plague
typhus and Hanta fever However various rodent species are economically
important as sources of food or fur in many parts of the world and others
are used extensively in biomedical research
"""

words = [x.lower() for x in textsample.split()]

htmlTemplate = """
<html>
<head>
<title>Example skimpy gimpy challenge page</title>
</head>
<body>
<h1>Example skimpy gimpy challenge page</h1>
%(doc)s
<hr>
<b>%(message)s</b>
<hr>
%(skimpy)s
<hr>
<br>
<a href="../waveguess.py/go?index=%(index)s">
Hear this word spelled.
</a>
<form action="go">
What is the word? 
<input name="word"> <input type="submit" value="guess">
<input type="hidden" name="index" value="%(index)s">
</form>
<br>
<a href="/index.html">return to index</a>
</body>
</html>
"""
def go(req, index=None, word=None):
	import random
	newindex = int(random.uniform(0, 1000))%len(words)
	D = {}
	D["index"] = newindex
	newword = words[newindex]
	g = skimpyGimpy.gimpyString(newword)
	g.color = "green"
	g.scale = 1.1
	D["skimpy"] = g.formatAll()
	message = "guess the word!"
	if word is not None:
		oldindex = int(index.strip())
		guess = word.strip().lower()
		real = words[oldindex]
		if guess == real:
			message = "Right! the word was %s! Please guess again." % repr(real)
		else:
			message = "No, the word was %s, not %s!  Try this word:" % (repr(real), repr(guess))
	D["message"] = message
	D["doc"] = __doc__
	return htmlTemplate % D

if __name__=="__main__":
	go(None, "50", "goof")


