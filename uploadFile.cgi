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

import cgi, os, shutil, config, codecs, re, sys
import cgitb
print "Content-Type: application/json\n"
cgitb.enable()
#print "Content-Type: text/html\r\n\r\nxxxxxxxx"
method = os.environ.get( 'REQUEST_METHOD' )
if method == "POST":
	form = cgi.FieldStorage()
	project=form.getvalue("project",None).decode("utf-8")
	filetype=form.getvalue("type",None)
	analyze=form.getvalue("analyze",None)
	filecontent=form.getvalue("files[]")
	thefile = form["files[]"].filename.decode("utf-8")
	
	
	if filetype=="conll":
		ns=1
		conll=None
		for li in filecontent.split("\n"):
			if not li.strip():ns+=1
			elif not conll and "\t" in li:
				n = len(li.split("\t"))
				#print n,li.encode("utf-8"),"<br>"
				if n==4:conll=4
				if n==10:conll=10
				elif n==13:conll=10 # orfeo file format: conll10 + begin, end, speaker
				elif n==14:conll=14
		if not li.strip():ns-=1 # if last line empty, we counted one too much
		#if not conll:print "???",filename,"strange datatype<br>"
		
		
		
		
		# TODO: upload XML
		if conll:
		
			foutname=os.path.join(config.configProject(project)["configuration"]["corpusfolder"]+"/conll",thefile) # 
			out = open(foutname, "wb")
			out.write(filecontent)
			out.close()
		else:
			print "Content-Type: text/html\r\n\r\nProblem analyzing the CoNLL file. Are you sure the file {fn} is in CoNLL format?".format(fn=thefile)
			sys.exit()
	elif filetype=="standard":
		conll=10
		foutname=os.path.join(config.configProject(project)["configuration"]["corpusfolder"]+"/conll",thefile+".conll10") # 
		out = codecs.open(foutname, "w","utf-8")
		ns=0
		if analyze=='english':
	
			from pattern.en import parse
			
			reslash=re.compile("\/",re.U+re.I+re.M)
			reslashinv=re.compile("&slash;",re.U+re.I+re.M)
			reponct=re.compile(ur"((</span>)? (<span class='\w+'>)|(</span>) (<span class='\w+'>)?| )(?P<punct>[.,;()])",re.U+re.I+re.M)
			
			filecontent = reslash.sub("&slash;",filecontent)
			
			pc = parse(filecontent, tokenize=True, tags=True, chunks=True, relations=True, lemmata=True, light=False)
			
			
			
			for li in pc.split("\n"):
				#print li
				li=li.strip()
				if li:
					for nb,t in enumerate(li.split()):
						w,cat,ch,vp,php,l = t.split("/")
						out.write("\t".join([str(nb+1), reslashinv.sub("/",w), reslashinv.sub("/",l), cat, "_", "_","_", "_", "_", "_"])+"\n")
						
					out.write("\n")
					ns+=1						
						
		elif analyze=='chinese':
			from parse import zhparse
			temp=open("corpus/zh.utf-8","wb")
			temp.write(filecontent)
			temp.close()
			nb=1
			nix=True # avoiding multiple empty lines
			for (cat,w) in zhparse("corpus/zh.utf-8"):
				if w:
					out.write("\t".join([str(nb), w, w, cat, "_", "_","_", "_", "_", "_"])+"\n")
					nb+=1
					nix=False
				else:
					if not nix:
						out.write("\n")
						ns+=1	
					nb=1
					nix=True
			
		
		elif analyze=='no':
			renl=re.compile("\n+",re.U+re.M)
			rew=re.compile("(\W+)",re.U+re.M)
			for line in renl.split(filecontent.strip()):
				nb=0
				for t in rew.split(line.strip()):
					t=t.strip()
					if t:
						nb+=1
						out.write("\t".join([str(nb), t, t, "_", "_", "_","_", "_", "_", "_"])+"\n")
						
			
				out.write("\n")
			
			
		#markuptext = reponct.sub(r"\g<punct>",reslashinv.sub("/",markuptext))
	else: # filetype=sentline
			conll=10
			foutname=os.path.join(config.configProject(project)["configuration"]["corpusfolder"]+"/conll",thefile+".conll10").encode("utf-8") # 
			ns=0
			out = codecs.open(foutname, "w","utf-8")
			
			if analyze=='chinese':
				from parse import zhparse
				temp=open("corpus/zh.utf-8","wb")
				temp.write(filecontent)
				temp.close()
				nb=1
				nix=True # avoiding multiple empty lines
				for (cat,w) in zhparse("corpus/zh.utf-8"):
					if w:
						out.write("\t".join([str(nb), w, w, cat, "_", "_","_", "_", "_", "_"])+"\n")
						nb+=1
						nix=False
					else:
						if not nix:
							out.write("\n")
							ns+=1	
						nb=1
						nix=True
			else:
				nl=re.compile(ur"\s*\r?\n+\r?\s*",re.U+re.M+re.I)
				#wsplit=re.compile(ur"(\W+)",re.U+re.M+re.I) # to be used for untokenized text
				wsplit=re.compile(ur"\s+",re.U+re.M+re.I)
				space=re.compile(ur"^\s*$",re.U+re.M+re.I)
				for li in nl.split(filecontent.decode("utf-8")):
					#out.write("___"+repr(wsplit.split(li))+"___\n")
					
					nb=1
					for t in wsplit.split(li.strip()):
						t=t.strip()
						if space.match(t):continue
						out.write("\t".join([str(nb), t, t, "?", "_", "_","_", "_", "_", "_"])+"\n")
						nb+=1
					out.write("\n")	
						
			out.close()	
		#print "Content-Type: text/json\r\n\r\n{}"
		#sys.exit(1)
	
	filesize=os.path.getsize(foutname)

	filewithpath="corpus/conll/"+thefile
	thumbnail="images/conll"+str(conll)+".png"
	
	#print "Content-Type: application/json\r\n\r\n"
	#print "Content-Type: text/plain\n\n"
	#print "Content-Type: application/json\n\n"
	#print thefile.encode("utf-8")
	print (''' {"files":[{"name":"'''+thefile+'''",	
	"id":"'''+filewithpath+'''",
	"filetype":"'''+"conll"+str(conll)+'''",
	"size":'''+str(filesize)+''',
	"sentences":'''+str(ns)+''',
	"url":"'''+config.configProject(project)["configuration"]["url"]+filewithpath+'''",
	"thumbnail":"'''+thumbnail+'''"
	}]}''').encode("utf-8")
	
	
  
else:
	print "Content-Type: text/html\r\n\r\nxxxxxxxx"
