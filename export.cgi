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


#import cgi
#from xml.dom.ext import PrettyPrint
#from datetime import date
#from time     import mktime, time
#from sqlite3   import connect
#from os       import environ
from sys      import exit
from xml.dom import minidom

#import traceback,
import sys,cgi,cgitb,json
#import treebankfiles

import rhapsoxml

cgitb.enable()

# this is the export script called from the editor or the viewer for exporting _individual_ trees
# as well as for the direct transformation of dirty trees into conll (used for the quick editor) (if trees are sent)
	
def jswords2nodedic(words):
	nodedic={}
	for i in words:
		nodedic[int(i)]={}
		for k in words[i]:
			if k=="features":
				for a in words[i][k]:
					nodedic[int(i)][a]=words[i][k][a]
			else:
				nodedic[int(i)][k]=words[i][k]
	return nodedic

	
	
def exportxml(nodedic):
	
	print 'Content-type: text/xml\n'
	alltext="\n"
	doc,tokens,lexemes, dependencies, text = rhapsoxml.baseXml()
	
	te=rhapsoxml.addFeat2doc(nodedic,doc,"t","lemma",tokens,lexemes, dependencies)
	
	#for i in nodedic: te+= "\n"+str( i)+ str( nodedic[i])+"\n"
	
	
	text.appendChild(doc.createTextNode(te))
	xmltext= doc.toprettyxml(indent="     ",encoding="utf-8")
	print xmltext
	

def printconll(nodedic,cat):
	
	for i in sorted(nodedic.keys()):
		node = nodedic[i]
		gov = node.get("gov",{}).items()
		govid = -1
		func = "_"
		if gov:
			for govid,func in gov: # must be treated differently: idiosyncratic conll format: double line for double governors!
				if govid!=-1:
					print ("\t".join([str(i),node.get("t","_"), node.get("lemma",""), node.get(cat,"_"), node.get("tag2","_"),"_", str(govid),func,"_","_"])).encode("utf-8")
		else:
			print ("\t".join([str(i),node.get("t","_"),node.get("lemma",""),node.get(cat,"_"),node.get("tag2","_"),"_",str(govid),func,"_","_"])).encode("utf-8")
		##                        nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells
	

	

def consolidateconll(trees, filename, exptype):
	from conll import conll2trees
	from json import loads
	trees=loads(trees)
	#print "iiiiiiiiiiiiiii",conll2trees(filename)
	for i,tree in enumerate(conll2trees(filename)):
		#print "******",i,tree
		if str(i) in trees:
			nodedic={}
			for nr in trees[str(i)]:
				nodedic[int(nr)]=trees[str(i)][nr]
				if "features" in trees[str(i)][nr]:
					for a,v in trees[str(i)][nr]["features"].iteritems():
						nodedic[int(nr)][a]=v
						
					
			#print 'uuuuuuuu',nodedic
			#print "\n\n\n"
			printconll(nodedic,"tag")
		else:
			#print 'rrrrrrr'
			printconll(tree,"tag")
		print 
	
	
if __name__ == "__main__":
	#print 'Content-type: text/plain\n\nxxxxxxxxxxxxxxxxxxxx'
	form = cgi.FieldStorage()
	
	exptype = form.getvalue('type',None)
	tree = form.getvalue('source',None)
	trees = form.getvalue('trees',None)
	filename = form.getvalue('filename',None)
	cat = form.getvalue('cat',None)
	#print tree
	#print "uuuuuuuuu",filename
	
	#print nodedic
	
	if trees and filename:
		print 'Content-type: text/plain;charset=utf-8\n\n'
		consolidateconll(trees, filename, exptype)
	elif exptype=="conll":
		nodedic=jswords2nodedic(json.loads(tree))
		print 'Content-type: text/plain;charset=utf-8\n\n\n\n'
		printconll(nodedic,cat)
	elif exptype=="xml":
		nodedic=jswords2nodedic(json.loads(tree))
		exportxml(nodedic)
	else:
		print 'Content-type: text/plain;charset=utf-8\n\nxxxxxxxxxxxxxxxxxxxx'
	

