
"dump xsdb data as javascript dictionary of dictionaries"

query = """
<query>
<consult href="stateAll.xsdb">
</consult>
</query>
"""

from xsdbXMLpy import interp
q = interp.Query(query)
print "var States = {"
inside1 = False
for D in q.dictionaries():
	#print D
	if inside1:
		print ","
	else:
		pass
	inside2 = False
	name = D["State"]
	print repr(name), ": {"
	keys = D.keys()
	keys.sort()
	for k in keys:
		if inside2:
			print ","
		else:
			print
		print "    ",repr(k),":",repr(D[k]),
		inside2 = True
	print "}",
	inside1 = True
print "} // end of States dictionary"

