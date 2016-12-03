#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi,sys
from os import environ
sys.path.append('modules')
from logintools import isloggedin
from lib.database import SQL

test = isloggedin("users/")
if not test:sys.exit()
admin = int(test[0]["admin"])
method = environ.get( 'REQUEST_METHOD' )

if method == "POST" and admin: #or True
	data = cgi.FieldStorage()
	
	project = data.getvalue("project",None).decode("utf-8")
	
	sid = data.getvalue("sid",None)
	nr = data.getvalue("nr",None)
	toknr = data.getvalue("toknr",None)
	connectsplit = data.getvalue("connectsplit",None)
	
	print "Content-Type: text/html\r\n\r\nconnecting trees"
	sql=SQL(project)
	if connectsplit=="connect":sql.connectRight(sid,nr)
	if connectsplit=="split":sql.splitSentence(sid,nr,toknr)
	
