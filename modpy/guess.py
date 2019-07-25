

"""
This mod python module implements a simple CAPTCHA visual "challenge/response"
intended to verify that the agent interacting with a web form is a human
and not a computer program.
"""

import sys
p = "/home/awatters/webapps/mod_python/htdocs/skimpyGimpy"
if p not in sys.path:
	sys.path.insert(0,p)

from skimpyGimpy import skimpyAPI
import skimpyModPyConfig

# sample words

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


# page template

htmlTemplate = """
<html>
<head>
<title>Example skimpy gimpy challenge page</title>
</head>
<body>
<center>

<h1>Example skimpy gimpy challenge page</h1>

<table width="60%(pct)s">
<tr><td>
This mod python program implements a simple CAPTCHA visual "challenge/response"
intended to verify that the agent interacting with a web form is a human
and not a computer program using the <a href="http://skimpygimpy.sourceforge.net">skimpyGimpy</a>
CAPTCHA generators.
</td></tr>
</table>
<br><br>

<b>%(message)s</b>
<br>
preformatted text version:
<br>
%(skimpy)s
<br>
image version: <img src="%(png)s">
<br>
wave audio version: <a href="go?wave=%(index)s">click for audio</a>
<br><br>
<form action="go">
What is the word?
<input name="wordIn"> <input type="submit" value="guess">
<input type="hidden" name="indexIn" value="%(index)s">
</form>
<br>

<table width="60%(pct)s">
<tr><td>
Note that this simple minded demo is not "secure" in the sense that it is subject
to "replay attacks" -- if you repeat a URL that succeeded it will succeed again.
For true CAPTCHA security you need to store the CAPTCHA match string in a temporary
opaque session object that the client cannot access in any way.  The hiding of the
CAPTCHA string is beyond the scope of this module and left to the user/programmer's
creativity.
</td></tr>
</table>
</body>
</html>
"""

# driver function
def go(req=None, wordIn=None, indexIn=None, wave=None, **others):
    import random
    # return a wave file redirect only if "wave" is requested
    if wave is not None:
            oldindex = int(wave)
            word = words[oldindex]
            return skimpyModPyConfig.makeWaveAndRedirect(word)
    # choose a random index and word at that index.
    index = int(random.uniform(0, 1000))%len(words)
    D = {}
    D["pct"] = "%"
    D["index"] = index
    word = words[index]
    # create text, PNG, and Wave representations for the word
    color = "ff0000"
    prescale = 1
    pngscale = 2.2
    speckle = 0.1
    D["skimpy"] = skimpyAPI.Pre(word, speckle=speckle, scale=prescale, color=color).data()
    (fpath, hpath) = skimpyModPyConfig.getPNGPaths()
    skimpyAPI.Png(word, speckle=speckle, scale=pngscale, color=color).data(fpath)
    D["png"] = hpath
    message = "guess the word!"
    # if the user submitted a guess see if the guess was the correct word.
    if wordIn is not None:
            oldindex = int(indexIn)
            guess = wordIn.strip().lower()
            # find the actual word presented
            real = words[oldindex]
            if guess == real:
                    message = "Right! the word was %s! Please guess again." % repr(real)
            else:
                    message = "No, the word was %s, not %s!  Try this word:" % (repr(real), repr(guess))
    # generate html output
    D["message"] = message
    return htmlTemplate % D

if __name__=="__main__":
    go()
    
