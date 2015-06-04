#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi,os, shutil
#from datetime import date
#from time     import mktime, time
#from sqlite3   import connect
#from os       import environ, path
#from sys      import exit
from config import *
#import xmlsqlite

#db = connect( "trees.sqlite" )
#cursor = db.cursor()
#cursor.execute('''create table  IF NOT EXISTS sentences
#(sentence text)''')



method = os.environ.get( 'REQUEST_METHOD' )
if method == "POST": # or True:
	form = cgi.FieldStorage()
	#thefile = form.getvalue("file[]")
	filecontent=form.getvalue("files[]")
	thefile = form["file[]"]
   
	
	foutname=os.path.join(arboratorCache,thefile.filename) # "upload."+
	##fout = file (foutname, 'wb')
	sentencecount=0
	filetype=None
	out = open(foutname, "wb")
	while 1:
		data = thefile.file.read(4096)
		if not data:
			break
		out.write(data)
		for line in data.split("\n"):
			if not filetype:
				if "\t" in line and len(line.split("\t"))==14:
					filetype="conll14"
		        if not line.strip(): sentencecount+=1
		
	out.close()
	filesize=os.path.getsize(foutname)
	
	thumbnail="images/nanovakyartha.png"

	if filetype=="conll14":
		if foutname.endswith(".conll14"): appendix=""
		else: appendix="."+str(sentencecount)+".conll14"
		shutil.move(foutname, "corpus/conll/"+thefile.filename+appendix)
		thumbnail="images/conll14.png"
	

	filewithpath="corpus/conll/"+thefile.filename+appendix
	
	#print 1/0
	#if not data.has_key( 'tree' ): exit( 1 )
	#print 1/0
	#tree = data.getlist("tree")
	#sentenceid = data.getvalue("sentenceid")

	#newsentence = form.getvalue("newsentence",None)
	#analysis = form.getvalue("analysis",None)
	print "Content-Type: text/json\r\n\r\n"
	#print '''[{"name":"desktop.ini","size":77,"url":"\/tvakyartha\/ramsch\/fileupload\/example\/files\/desktop.ini","thumbnail":null},{"name":"filezilla-connect-transfert.png","size":82775,"url":"\/tvakyartha\/ramsch\/fileupload\/example\/files\/filezilla-connect-transfert.png","thumbnail":"\/tvakyartha\/ramsch\/fileupload\/example\/thumbnails\/filezilla-connect-transfert.png"}]
	#'''
	#print unicode(thefile.filename)
	#print '{"name":"picture.jpg","type":"image/jpeg","size":"123456789"}'
	
	print '''{"name":"'''+thefile.filename+'''",
	"id":"'''+filewithpath+'''",
	"filetype":"'''+filetype+'''",
	"size":'''+str(filesize)+''',
	"sentences":'''+str(sentencecount)+''',
	"url":"'''+url+filewithpath+'''",
	"thumbnail":"'''+thumbnail+'''"
	}'''

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
