#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2012 Kim Gerdes
# kim AT gerdes. fr
# http://arborator.ilpga.fr/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public License (the "License")
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of of version 3 of the GNU Affero General Public License
# from http://www.gnu.org/licenses/agpl-3.0.html 
# For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####

import cgi,os, shutil, config, codecs
import cgitb

cgitb.enable()
#print "Content-Type: text/html\r\n\r\nxxxxxxxx"
method = os.environ.get( 'REQUEST_METHOD' )
if method == "POST":
	form = cgi.FieldStorage()
	project=form.getvalue("project",None)
	filecontent=form.getvalue("files[]")
	thefile = form["files[]"]
	
	
	
	ns=1
	conll=None
	for li in filecontent.split("\n"):
		if not li.strip():ns+=1
		elif not conll and "\t" in li:
			n = len(li.split("\t"))
			#print n,li.encode("utf-8"),"<br>"
			if n==10:conll=10
			elif n==14:conll=14
	if not li.strip():ns-=1 # if last line empty, we counted one too much
	#if not conll:print "???",filename,"strange datatype<br>"
	thumbnail="images/conll"+str(conll)+".png"
	
	
	
	# TODO: upload XML
	if conll:
	
		foutname=os.path.join(config.configProject(project)["configuration"]["corpusfolder"]+"/conll",thefile.filename) # "upload."+
		#print foutname
		out = open(foutname, "wb")
		out.write(filecontent)
		out.close()
	
	
	filesize=os.path.getsize(foutname)
	
	

	filewithpath="corpus/conll/"+thefile.filename
	
	print "Content-Type: text/json\r\n\r\n"
	
	
	print '''{"name":"'''+thefile.filename+'''",
	"id":"'''+filewithpath+'''",
	"filetype":"'''+"conll"+str(conll)+'''",
	"size":'''+str(filesize)+''',
	"sentences":'''+str(ns)+''',
	"url":"'''+config.configProject(project)["configuration"]["url"]+filewithpath+'''",
	"thumbnail":"'''+thumbnail+'''"
	}'''
	
	
	#print '''[{"name":"'''+thefile.filename+'''",
	#"id":"'''+foutname+'''",
	#"filetype":"'''+filetype+'''",
	#"size":'''+str(filesize)+''',
	#"url":"'''+config.configProject(project)["configuration"]["url"]+foutname+'''",
	#"delete_type":"DELETE",
	#"thumbnail_url":"'''+config.configProject(project)["configuration"]["url"]+thumbnail+'''"
	#}]'''
	
	
	 #"name":"picture1.jpg",
    #"size":902604,
    #"url":"\/\/example.org\/files\/picture1.jpg",
    #"thumbnail_url":"\/\/example.org\/thumbnails\/picture1.jpg",
    #"delete_url":"\/\/example.org\/upload-handler?file=picture1.jpg",
    #"delete_type":"DELETE"
	
	#"sentences":'''+str(sentencecount)+''',
	#print form
	#print thefile
	#print thefile.filename+"*******",os.path.join(arboratorCache,thefile.filename) 
	#if isinstance(files, list):
		#print "+"
	#else: print "---"
	
	#print newsentence,analysis
	#sentenceid=0
	#treeid=0
	#newsentence="Marie dort."
	
	#try:
		#if analysis=="rhapsodie": sentenceid, treeid = xmlsqlite.text2tree(newsentence.decode("utf-8"), "guest", "parse","rhapsynt", True)
		#elif analysis=="frmg": sentenceid, treeid = xmlsqlite.text2tree(newsentence.decode("utf-8"), "guest", "parse","rhapsynt", False)
		#elif analysis=="no": sentenceid, treeid = xmlsqlite.text2tree(newsentence.decode("utf-8"), "guest", "no","rhapsynt", False)
		#print '{"sentenceid":'+str(sentenceid)+',"treeid":'+str(treeid)+'}'
	#except:
		#print '{}'
	#exo = data.getvalue("exo").strip()
	#tree = data['tree'].value
	#timestamp = mktime( date.today().timetuple() )
	#ip_address = str( environ.get( 'REMOTE_ADDR' ) )
	
	
	
	#cursor.execute( "INSERT INTO visits VALUES ( ?, ?, ? )",
		#( page, timestamp, ip_address ) )
	#db.commit()

	
	#print "******** sentenceid,userid:",sentenceid,userid
	#,tree
	#print "%s:%d:%s" % ( tree, timestamp, ip_address )
	
	#xmlsqlite.sentence2exo(sentenceid,exo=exo)
	#print "========================",treeid,"*********"
	
	#print "ok",sentenceid, treeid 
  
else:
	data = []
	print "Content-Type: text/html\r\n\r\nxxxxxxxx"
