#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,cgi,cgitb
from database import SQL

cgitb.enable()

form = cgi.FieldStorage()

project = form.getvalue('project',"").decode("utf-8")
uid = form.getvalue('uid',None)

print 'Content-type: text/html\n\n'

sql=SQL(project)
	
#print project.encode('utf-8'),"uuuuuuuuuuuuuuuuuuuuu",uid
print sql.evaluateUser(uid)
