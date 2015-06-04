#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi,sys
from os       import environ
import database,json
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
	tree = data.getvalue("tree",None)
	
	if tree:
		snode=json.loads(tree)
		
		sentenceid = int(data.getvalue("sentenceid",0))
		sentencenr = int(data.getvalue("sentencenr",0))
		userid = int(data.getvalue("userid",0))
		username = data.getvalue("username","unknown")
		todo = data.getvalue("todo",-1)
		validator = int(data.getvalue("validator",0))
		addEmptyUser = data.getvalue("addEmptyUser",None)
		tokensChanged = eval(data.getvalue("tokensChanged","[]"))
		validvalid = eval(data.getvalue("validvalid","[]"))
		
		#print "Content-Type: application/json\r\n\r\n"
		#print sentenceid
		
		sql=database.SQL(project)
		#open("logger.txt","w").write("save.cgi "+ str([username,sentenceid,userid,snode,tokensChanged])+"\n")
		treeid, newtree, sent =sql.saveTree(sentenceid,userid,snode,tokensChanged)
		#open("logger.txt","a").write("_____ return to save.cgi "+ str([treeid, newtree, sent])+"\n")
		treelinks, firsttreeid, sentenceinfo = sql.links2AllTrees(sentenceid,sentencenr,username,admin,todo=todo, validator=validator,addEmptyUser=addEmptyUser,validvalid=validvalid)
		
		print "Content-Type: application/json\r\n\r\n"
		#print sentenceid
		if newtree:
			#print newtree
			newtree.update({"treeid":treeid, "treelinks":treelinks, "firsttreeid":firsttreeid, "sentence":sent})
			print json.dumps(newtree, sort_keys=True)
		else: print json.dumps({"treeid":treeid, "treelinks":treelinks, "firsttreeid":firsttreeid})
