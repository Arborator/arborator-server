#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,cgi,cgitb,json
sys.path.append('modules')
from logintools import isloggedin
from lib import database
cgitb.enable()

form = cgi.FieldStorage()

project = form.getvalue('project',None)
treeid = form.getvalue('treeid',None)
textid = form.getvalue('textid',None)
snr = form.getvalue('snr',None)
userid = form.getvalue('userid',None)
username = form.getvalue("username","unknown")
sid = form.getvalue('sid',None)

test = isloggedin("users/")
if not test:sys.exit()
admin = test[0]["admin"]

#print "Content-Type: text/html\n" # blank line: end of headers

sql=database.SQL(project)
if treeid:
	answer = sql.statustree(int(sid),int(snr),int(treeid),int(userid),username,int(textid),int(admin))
else:
	answer = sql.statustext(int(textid),int(userid))
print "Content-Type: application/json\r\n\r\n"
print json.dumps(answer)

#print 'Content-type: text/html\n\n'
#print answer
