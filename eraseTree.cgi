#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,cgi,cgitb
sys.path.append('modules')
from logintools import isloggedin
from lib import database
cgitb.enable()

form = cgi.FieldStorage()

project = form.getvalue('project',None).decode("utf-8")
treeid = form.getvalue('treeid',None)
sentencenr = form.getvalue('sentencenr',None)
username = form.getvalue('username',None).decode("utf-8")

test = isloggedin("users/")
if not test:sys.exit()
admin = test[0]["admin"]
if not admin:sys.exit()

#print "Content-Type: text/html\n" # blank line: end of headers

sql=database.SQL(project)


print 'Content-type: text/html\n\n'
print sql.eraseTree(treeid,sentencenr,username,admin).encode("utf-8")
