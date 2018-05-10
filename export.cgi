#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2017 Kim Gerdes
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

# this is the export script called from the editor or the viewer for exporting _individual_ trees

from sys      import exit
from xml.dom import minidom
import sys,cgi,cgitb,json
from lib import conll, rhapsoxml
cgitb.enable()


def jswords2nodedic(treefromjson):
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

def json2tree(jsonsource):
	
	treefromjson=json.loads(jsonsource)
	nodedic={}
	tree = conll.Tree()
	for i in treefromjson["tree"]:
		nodedic[int(i)]={}
		for k in treefromjson["tree"][i]:
			if k=="features":
				for a in treefromjson["tree"][i][k]:
					nodedic[int(i)][a]=treefromjson["tree"][i][k][a]
			else:
				nodedic[int(i)][k]=treefromjson["tree"][i][k]
	tree.sentencefeatures=treefromjson["sentencefeatures"]
	conll.update(tree, nodedic)
	return tree


def exportxml(nodedic):
	print 'Content-type: text/xml;charset=utf-8\n'
	alltext="\n"
	doc,tokens,lexemes, dependencies, text = rhapsoxml.baseXml()
	te=rhapsoxml.addFeat2doc(nodedic,doc,"t","lemma",tokens,lexemes, dependencies)
	text.appendChild(doc.createTextNode(te))
	xmltext= doc.toprettyxml(indent="     ",encoding="utf-8")
	print xmltext
	
	
if __name__ == "__main__":
	form = cgi.FieldStorage()
	jsonsource = form.getvalue('source',None)
	exptype = form.getvalue('type',None)
	if exptype=="conll":
		print 'Content-type: text/plain;charset=utf-8\n\n'
		#print str(json2tree(jsonsource))
		print json2tree(jsonsource).conllu().encode("utf-8")
	elif exptype=="xml":
		nodedic=jswords2nodedic(json.loads(jsonsource))
		exportxml(nodedic)
	else:
		print 'Content-type: text/plain;charset=utf-8\n\nNo data was sent!'
	
