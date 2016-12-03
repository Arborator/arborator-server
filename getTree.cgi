#!/usr/bin/python
# -*- coding: utf-8 -*-

#import cgi

import sys,cgi,cgitb, os
cgitb.enable()
form = cgi.FieldStorage()
userdir = 'users/'
thisfile = os.environ.get('SCRIPT_NAME',".")
action = form.getvalue("action",None)
sys.path.append('modules')
from logintools import login
from logintools import isloggedin

action, userconfig = login(form, userdir, thisfile, action)
adminLevel = int(userconfig["admin"])

project = form.getvalue('project',"").decode("utf-8")

treeid = form.getvalue('treeid',None)
compare = form.getvalue('compare',None)

filename = form.getvalue('filename',"").decode("utf-8")

nr = int(form.getvalue('nr',1))
filetype = form.getvalue('filetype',None)

print 'Content-type: application/json\n\n'

#if project=="quickie":
	#if filetype == "conll14" or filetype == "conll10" or filetype == "conll4":
		#from lib.conll import conll2jsonTree
		#conll2jsonTree(filename,nr)
#else:
from lib.database import SQL
sql=SQL(project)

if compare:
	treeids={}
	for k in form.keys():
		if k.startswith("treeids"):
			treeids[int(k.split("[")[-1][:-1])]=form.getvalue(k)
	sql.compare(treeids)
else:
	sql.tree2json(treeid=treeid, adminLevel=adminLevel)
