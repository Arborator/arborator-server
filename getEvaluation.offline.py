#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,cgi,cgitb,codecs
from database import SQL

#cgitb.enable()
#project = form.getvalue('project',"").decode("utf-8")
project="depexo"
#form = cgi.FieldStorage()
#uid = form.getvalue('uid',None)
uid = 1 # admin
#print 'Content-type: text/html\n\n'

sql=SQL(project)
	
#print project.encode('utf-8'),"uuuuuuuuuuuuuuuuuuuuu",uid

tid=4

uids=[uid for uid, in sql.uidForText(tid)]
print uids
with codecs.open(project+str(tid)+".results.html","w","utf-8") as out:
	for i,uid in enumerate(uids):
		print "__________________",uid,i,float(i)/len(uids)*100,"%"
		out.write(sql.evaluateUser(uid, tid, consolidateLine=True)+"\n")
