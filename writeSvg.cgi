#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi,sys,codecs
from os import environ
sys.path.append('modules')
from logintools import isloggedin

test = isloggedin("users/")
if not test:sys.exit()
admin = int(test[0]["admin"])

method = environ.get( 'REQUEST_METHOD' )
if method == "POST" : #or True
	data = cgi.FieldStorage()
	
	project = data.getvalue("project",None).decode("utf-8")
	#project = data.getlist("project")
	svg = data.getvalue("svg",None)
	treeid = data.getvalue("treeid",None)
	
	if treeid:
		svgfile=codecs.open("svg/"+project+"."+treeid,"w","utf-8")
		svgfile.write(svg)
		svgfile.close()
	
	
