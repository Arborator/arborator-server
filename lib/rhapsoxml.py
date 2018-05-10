#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2012 Kim Gerdes
# kim AT gerdes. fr
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of the GNU General Public License
# from http://www.gnu.org/.  For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####

from xml.dom import minidom
from collections import OrderedDict	
import argparse
import difflib, codecs, glob, os

try:from nltk import Tree
except:pass
try:from treebankfiles import rhapsodie2Sentences
except:pass


#verbose=False
#verbose=True

verbose=False

def baseXml():
	############# basics
	doc=minidom.Document()
	sampleEl=doc.createElement("sample")
	sampleEl.setAttribute("style","Rhapsodie")
	doc.appendChild(sampleEl)
	text=doc.createElement("text")
	sampleEl.appendChild(text)
	pivot=doc.createElement("words")
	pivot.setAttribute("type","pivot")
	pivot.appendChild(doc.createTextNode("pivot"))
	sampleEl.appendChild(pivot)
	tokens=doc.createElement("words")
	tokens.setAttribute("type","tokens")
	#tokens.appendChild(doc.createTextNode("ici les tokens"))
	sampleEl.appendChild(tokens)
	lexemes=doc.createElement("words")
	lexemes.setAttribute("type","lexemes")
	tagset=doc.createElement("tagset")
	tagset.setAttribute("tag","cat")
	tagset.setAttribute("name","cat")
	lexemes.appendChild(tagset)
	sampleEl.appendChild(lexemes)
	dependencies=doc.createElement("dependencies")
	dependencies.setAttribute("type","syntax")
	tagset=doc.createElement("tagset")
	tagset.setAttribute("tag","func")
	tagset.setAttribute("name","syntacticfunctions")
	dependencies.appendChild(tagset)
	sampleEl.appendChild(dependencies)
	return doc,tokens,lexemes,dependencies,text
	
	

		
def addFeat2doc(feat, doc, tokenname, lemmaname, tokens, lexemes, dependencies, exportTokenName="orthotext"): # 
	"""
	is called for each dependency tree (rectional unit)
	called from 
	- export.cgi
	- xmlSentenceAdd in database.py
	
	"""
	# TODO: get rid of this orthotext stuff and replace by: the tokenname
	toks=[]
	
	#for i in feat:
		#print feat[i][tokenname].encode("utf-8"),"___",i, feat[i],"<br>"
		
	
	dnum,fnum,tnum,lnum=0,0,0,0
	for nn in dependencies.childNodes:
		if nn.nodeName=="dependency": 
			ddnum=int(nn.getAttribute("id")[3:])
			if ddnum==0: dnum+=1
			else: dnum=ddnum
			for fu in nn.childNodes:
				if fu.nodeName=="link":fnum=int(nn.getAttribute("id")[3:])
	for nn in tokens.childNodes:
		if nn.nodeName=="word": tnum=int(nn.getAttribute("id")[3:])
	for nn in lexemes.childNodes:
		if nn.nodeName=="word": lnum=int(nn.getAttribute("id")[3:])
			
			
			
	xdep = doc.createElement("dependency")	
	dependencies.appendChild(xdep)
	xdep.setAttribute("id","dep"+str(dnum))
	
	for i in feat: toks+=[feat[i][tokenname]]
	line=" ".join(toks)
	
	xdep.appendChild(doc.createComment(line))
	lexemes.appendChild(doc.createComment(line))
	
	count=0
	############ add lexemes
	for i in feat:
		count+=1
		word = feat[i]
		word["lexid"]="lex"+str(lnum+count)
		
	count=0	
	#lastokenid=None
	tokid=""
	
	for i in feat:
		count+=1

		word = feat[i]
		#print "___",word,"<br>"
		########### making token nodes
		#if word["tokenid"]==lastokenid:
			#tnum-=1
		#else:
		xtok=doc.createElement("word")
		tokens.appendChild(xtok)
		xtok.setAttribute("text",word.get(tokenname,"!undefined!"))
		
		xtref=doc.createElement("ref")
		xtok.appendChild(xtref)
		xtref.setAttribute("idref","pivX")
		tokid="tok"+str(tnum+count)
		xtok.setAttribute("id",tokid)	
			#lastokenid=word["tokenid"]
		#print word,"<br>"
		############ making lexeme nodes
		xword=doc.createElement("word")
		lexemes.appendChild(xword)
		xword.setAttribute(exportTokenName,word.get(tokenname,"!undefined!"))
		xword.setAttribute(lemmaname,word.get(lemmaname,"!undefined!"))
		xword.setAttribute("id","lex"+str(lnum+count))		
		
		xref=doc.createElement("ref")
		xword.appendChild(xref)
		xref.setAttribute("idref",tokid)
		
		xfeatures=doc.createElement("features")
		xword.appendChild(xfeatures)
		for attr in sorted(word.keys()):
			if attr == "gov":
				for g in word.get("gov",{}):
					
					xlink = doc.createElement("link")
					xdep.appendChild(xlink)
					fnum+=1
					xlink.setAttribute("id","func"+str(fnum))
				
					
				#g = word["gov"].keys()[0]
					#if  g >= 0 : 
						#if word["gov"].keys()[0] in feat:
							#xlink.setAttribute("govid",feat[g]["lexid"])
					if g in feat:
						xlink.setAttribute("govid",feat[g]["lexid"])
					xlink.setAttribute("depid",str(word["lexid"]))
					xlink.setAttribute("func",str(word["gov"][g]))
			elif attr not in [tokenname,lemmaname,"cluster","tokenid","idnum"]:
				xfeatures.setAttribute(attr,unicode(word[attr]))
	return line
	#lnum+=count
	#tnum+=count
	


	
	
	
	
	
	####################### alignment
	
	

	

def brandNewXml():
	############# basics
	doc=minidom.Document()
	sampleEl=doc.createElement("sample")
	sampleEl.setAttribute("style","Rhapsodie")
	doc.appendChild(sampleEl)
	
	return doc
	
	
def addinfototree(tree,deletePara=True):
	rootindeces=[]
		
		
	for i,node in tree.items(): # getting some basic additional features: children and govcats
		tree[i]["children"]=tree[i].get("children",[])
		tree[i]["govcats"]={}
		
		if "junc" in node["gov"].values() and len(node["gov"].values())>1:
			for j,func in node["gov"].items():
				#if deletePara and func.startswith("para"):
					#del node["gov"][j]
				if func!="junc":
					del node["gov"][j]
		
		for j,func in node["gov"].items():
			#print func,func.endswith("_inherited")
			if func.endswith("_inherited"):
				# if the node has other govs than the inherited, ignore the inherited link
				if [dep for g,dep in node["gov"].iteritems() if not dep.endswith("_inherited")]:
					continue
			if func=="attention":
				# if the node has other govs than the attention, ignore the attention link
				if [dep for g,dep in node["gov"].iteritems() if dep!="attention"]:
					continue
			if j in tree: # in tree: has governor
				tree[j]["children"]=tree[j].get("children",[])+[i]
				tree[i]["govcats"][tree[j]["cat"]]=tree[i]["govcats"].get(tree[j]["cat"],[])+[ (j,func) ]
			else: # not in tree: roots
				if [dep for g,dep in node["gov"].iteritems() if not dep.endswith("_inherited") and g!=j and dep!="attention"]:
					continue # we have other governors than the root node and inherited govs
				rootindeces+=[i]
	return rootindeces

def makeConstNode(i,node,constDic, rootindeces,tree):
	if node["cat"] in constDic:
		
		if node["cat"]=="V":
			if node.get("mode","")=="infinitive":
				ntree=Tree("(VP (V "+node["orthotext"]+"))")
			elif "V" in node["govcats"]:
				j,func=node["govcats"]["V"][0]
				if func.startswith("para"): # copy governor's const
					gov=tree[j]
					if "const" not in gov:
						makeConstNode(j,gov,constDic, rootindeces,tree)	
					if unicode(gov["const"])[1]=="V": # governor's const is VP
						ntree=Tree("(VP (V "+node["orthotext"]+"))")
					else:	# governor's const is S
						ntree=Tree("(S (V "+node["orthotext"]+"))")
				else: # verb depends on verb
					ntree=Tree("(VP (V "+node["orthotext"]+"))")			
			else:
				ntree=Tree("(S (V "+node["orthotext"]+"))")
		else:
			ntree=constDic[node["cat"]].copy(True)
			ntree.insert(0,Tree("("+node["cat"]+" "+node["orthotext"]+")"))
	else:
		if node["children"] or i in rootindeces or node["cat"] in node["govcats"]:
			ntree=Tree("("+node["cat"]+"P ("+node["cat"]+" "+node["orthotext"]+"))")
		else:
			ntree=Tree("("+node["cat"]+" "+node["orthotext"]+")")
			
	ntree.depindex=i
	ntree.function=unicode(node["gov"].items()[0][1])
	
	node["const"]=ntree
	for t in list(ntree.subtrees(lambda t: t.height() == 2)):
		t.depindex=i
		t.lexid=node["lexid"]
	
def phraseStructure(xmlfile, doc=None):
	
	
	if verbose:print "making phrase structure"
	
	if not doc:	doc=brandNewXml()
	sample=doc.getElementsByTagName("sample")[0]
	phraseStrus=doc.createElement("constrees")
	phraseStrus.setAttribute("type","phraseStructure")
	sample.appendChild(phraseStrus)
	
	
	constDic={"V":Tree("(S)"),"N":Tree("(NP)"),"I":Tree("(IP)"),"Adj":Tree("(AP)"),"Pre":Tree("(PP)"),"CS":Tree("(CP)") ,"Pro":Tree("(NP)")   }
	#left in automatic mode: D "Adv":Tree("(AdvP)"), "Cl":Tree("(NP)"),
	sentences, fs = rhapsodie2Sentences(xmlfile)
	
	phrasestructurecounter=0
	#print sentences[0]
	
	allConstTrees=[]
	#print len(sentences)		
	for treeindex,tree in enumerate(sentences): # [:33] [19:20]
		
		
		if verbose:
			print "_____________",treeindex

		
		rootindeces=addinfototree(tree)
		
		
		
		
		
		for i,node in tree.items(): # creating the actual phrase structure
			#if node.get("mode",""): print "mode",node.get("mode","")
			#print i, node
			
			makeConstNode(i,node,constDic,rootindeces,tree)
			

			
				
			#print "____",unicode(ntree)
	
		alreadyconst=[]
		for i,node in tree.items(): # putting the const trees for each node together
			children=sorted(node["children"])

			for j,chi in enumerate(children):
				
				if chi in alreadyconst:
					continue
				
				if chi<i:
					node["const"].insert(j,tree[chi]["const"])
					alreadyconst+=[chi]
				elif chi>i: # necessary to kick out autochildren
					node["const"].insert(len(node["const"]),tree[chi]["const"])
					alreadyconst+=[chi]
			#print "===",unicode(node["const"])
				
	
		#for i,n in tree.items():
			#print i,n["orthotext"],n
			
		nodesshown=[]	
		for i in rootindeces: # output
			if i in nodesshown:continue
			ctree=tree[i]["const"]
			allConstTrees+=[ctree]
			
			#for t in ctree.subtrees(lambda t: t.height() == 2):
				#print unicode(t)
			
			nodesshown += [t.depindex for t in list(ctree.subtrees(lambda t: t.height() == 2))]
			
			#for pro in ctree.productions():
				#print pro
			
			phraseStru=doc.createElement("constree")
			phraseStru.setAttribute("id","phrasestruct"+str(phrasestructurecounter))
			phraseStru.appendChild(doc.createComment(" ".join(list(ctree.leaves()))))
			phraseStrus.appendChild(phraseStru)
			
			root=doc.createElement("const")
			root.setAttribute("ctype","phrase")
			root.setAttribute("cat",unicode(ctree.node))			
			root.setAttribute("func","root")
			phraseStru.appendChild(root)
			
			for child in ctree:
				traverse(child,doc,root)
			#print "vvv",doc.toprettyxml()
			#ctree.draw()
			phrasestructurecounter+=1

			#print 
			print "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",treeindex,i
			
			if (treeindex,i)>=(118,0):
				if ctree.height()>3:
					
					print "drawn"
					print "height",ctree.height()
					ctree.draw()

		#print doc.toprettyxml()
	return allConstTrees		
			
def traverse(t,doc, lastconst, plexid=None):
	#print unicode(doc.toprettyxml())[:333],"uuu",plexid
	try:
		t.node
	except AttributeError:
		#print unicode(t)
		
		const=doc.createElement("const")
		const.setAttribute("ctype","lexeme")
		#const.setAttribute("cat","lexeme")
		#const.setAttribute("shape","empty")
		#const.setAttribute("localreg","empty")
		#const.setAttribute("function","?")
		const.setAttribute("func","head")
		const.setAttribute("idref",plexid)
		lastconst.appendChild(const)
	else:
		# Now we know that t.node is defined
		#print '(', unicode(t.node),t.function
		const=doc.createElement("const")
		const.setAttribute("ctype","phrase")
		const.setAttribute("cat",unicode(t.node))
		const.setAttribute("shape","empty")
		const.setAttribute("localreg","empty")
		
		try: const.setAttribute("func",t.function)
		except: const.setAttribute("func","head")		
		
		lastconst.appendChild(const)
		try: 	plexid=t.lexid
		except: 	plexid=None
		if verbose : print "lexid",unicode(t),plexid
		for child in t:
			traverse(child,doc,const,plexid)
		#print ')',	
	
	

def joinRead(xmlfilename):
	data=open(xmlfilename,"r").read()
	#print data[:100]
	lines=[li.strip() for li in data.split('\n')]
	data=(lines[0]+'\n<!DOCTYPE word [<!ATTLIST word id ID #IMPLIED>]>\n'+"\n".join(lines[1:])).replace("\n","")
	#print data,1/0
	#doc = minidom.parseString('<!DOCTYPE word [<!ATTLIST word id ID #IMPLIED>]>'+data)
	#doc = minidom.parseString('<!DOCTYPE div [<!ATTLIST div id ID #IMPLIED>]><div><div id="foo">FOO word</div><div id="bar">BAR word</div></div>')
	#print data[:100]
	doc = minidom.parseString(data)
	#doc=minidom.parse(xmlfilename)
	pivs, tokens, lexemes, deps, nodedics = OrderedDict(),OrderedDict(),OrderedDict(),OrderedDict(),OrderedDict()
	wtypedic={"pivot":pivs,"tokens":tokens,"lexemes":lexemes}
	dtypedic={"syntax":deps}
	
	# all dictionaries look like this: u'lex565': (<DOM Element: word at 0xb617e2cc>, 566)
	for wordgroup in doc.getElementsByTagName("words"):# looking at all the wordgroups
		currentdic = wtypedic.get(wordgroup.getAttribute("type"),None) # if they are mentioned in the wtypedic, read them in
		if currentdic=={}:
			#order=0
			for w in wordgroup.getElementsByTagName("word"):
				#order+=1
				currentdic[w.getAttribute("id")]=w
				#print type(w),w.toprettyxml(indent="     ")
	# each of the pivs, tokens, lexemes, ... sends: lexid ==> the xmldoc node 
	return {"pivs":pivs, "tokens":tokens, "lexemes":lexemes},doc,[l.getAttribute("orthotext") for lexid,l in lexemes.items()],[lexid for lexid,l in lexemes.items()]

	
def align(old, new, olddoc,newdoc, olid, newlexid, oldlex,newlex, newtokens, tokcounter,oldidtoktoidpiv):
	
	#if oldlex!=newlex:
	#print newlexid,olid,"=========== aligning",oldlex,"==>",newlex
	
	
	
	
	#print new["lexemes"][newlexid].toprettyxml()
	
	oldxlex=old["lexemes"][olid] # xml node
	oldtokid=oldxlex.getElementsByTagName("ref")[0].getAttribute("idref") # id
	#print oldtokid
	oldxtok=old["tokens"][oldtokid] # xml node

	#xpivrefs=oldxtok.getElementsByTagName("ref") # list of xml nodes: pivot references in old token
	pivrefs=oldidtoktoidpiv.get(oldtokid,[]) # list of xml nodes: pivot references in old token
	#print "uu",oldxtok.toprettyxml()
	#for xpr in xpivrefs:
		#print xpr.toprettyxml()
	#print "oldxtok",oldxtok.toprettyxml()
	
	
	#print oldlexes[o1:o2][i],newlex
	#print "oldlexids",oldlexids[o1:o2][i]
	#print "newlexid",newlexid
	#print oldxlex.getAttribute("start"),oldxlex.getAttribute("end")
	#print type(new["lexemes"][newlexids[n1:n2][i]]),1/0
	new["lexemes"][newlexid].setAttribute("start",oldxlex.getAttribute("start")) # copy start/end attributes
	new["lexemes"][newlexid].setAttribute("end",oldxlex.getAttribute("end"))
	
	
	#print "--"
	
	#print new["lexemes"][newlexids[n1:n2][i]].toprettyxml(indent="     ")
	#1/0
	tokstr=[]
	
	for j,tok in enumerate(newlex.split()): # for each token (separated by space)
		
		#create good and new toks:
		xtok=newdoc.createElement("word") # create new token element
		xtok.setAttribute("id","tok"+str(tokcounter))
		#if len(xpivrefs)>j: # if there is a ref to the pivots (some nodes have no pivot (esperluette))
		if len(pivrefs)>j: # if there is a ref to the pivots (some nodes have no pivot (esperluette))
		
			#xtok.setAttribute("start",olddoc.getElementById(xpivrefs[j].getAttribute("idref")).getAttribute("xmin"))
			xtok.setAttribute("start",olddoc.getElementById(pivrefs[j]).getAttribute("xmin"))
			xtok.setAttribute("end",olddoc.getElementById(pivrefs[j]).getAttribute("xmax"))
			#xtok.setAttribute("orthotext",oldxtok.getAttribute("orthotext")) # problem: sometimes not separated: eg "pas du tout"
			xtok.setAttribute("orthotext",tok)
			tokstr+=[tok]
			#print "oooo",xpivrefs[j].getAttribute("idref"),olddoc.getElementById(xpivrefs[j].getAttribute("idref"))
			xref=newdoc.createElement("ref") # create a ref child node
			xref.setAttribute("idref",pivrefs[j]) # copy the ref to the pivot
			xtok.appendChild(xref) # hang them in
			
			#oldxtok.removeChild(xpivrefs[j])
		newtokens.appendChild(xtok)
		#print "xtok",xtok.toprettyxml()
		
		xref=newdoc.createElement("ref") # create a ref child node
		xref.setAttribute("idref","tok"+str(tokcounter)) # put the ref to the new token
		new["lexemes"][newlexid].appendChild(xref) # hang them in
		new["lexemes"][newlexid].getElementsByTagName("features")[0].setAttribute("token"," ".join(tokstr))
		tokcounter+=1
	oldidtoktoidpiv[oldtokid]=pivrefs[len(newlex.split()):] # fucking difficult: kick out the already used pivots...
	#print new["lexemes"][newlexid].toprettyxml()
	#if oldlex==u"est-à-dire":1/0
	return tokcounter

	
def correctfeatures(e, lexidtonode):
	features = e.getElementsByTagName("features")[0]
	try: node = lexidtonode[features.getAttribute("lexid")]
	except: return # happens for crazy nodes like lex191 that don't appear in any tree
	cat = features.getAttribute("cat")
	orthotext = e.getAttribute("orthotext")
	token = features.getAttribute("token") # the crazy token feature
	
	lemma = e.getAttribute("lemma")
	#ajouter mode="indicative" et tense="present" pour tous les V qui n'ont pas de trait mode instancié
	if cat=="V" and not features.hasAttribute("mode"):
		features.setAttribute("mode","indicative")
		features.setAttribute("tense","present")
		
	#faire mode="infinitive" pour tous les V dont la forme se termine par er, ir, oir
	if cat=="V" and orthotext[-2:]=="er" or orthotext[-2:]=="ir" or orthotext[-3:]=="oir" or orthotext==u"répondre" or orthotext=="dire" or orthotext=="reprendre" or orthotext=="prendre" or orthotext=="conduire" :	
		features.setAttribute("mode","infinitive")
	
	#faire mode="infinitive" pour tous les V dont le lemme et la forme sont identique et se termine par re
	if cat=="V" and lemma==orthotext and lemma[-2:]=="re":
		features.setAttribute("mode","infinitive")
	
	#changer mode= "gerundive" en mode="present_participle"
	if cat=="V" and features.getAttribute("mode")=="gerundive":
		features.setAttribute("mode","present_participle")
	
	#print e.toprettyxml()
	
	# faire mode="past_participle" et supprimer le trait tense pour tous les V qui dépendent d'un lemme="avoir" ou lemme="être" par une relation pred
	# kim: changé en : si verbe et dépend d'un verbe par pred
	if cat=="V" and "V" in node["govcats"] and "pred" in node["gov"].values():
		if features.hasAttribute("tense") : features.removeAttribute("tense")
		features.setAttribute("mode","present_participle")
	
	#faire mode="past_participle" et supprimer le trait tense pour tous les V dont la forme se termine par é, i, u, ée, és, ées (on fait pas ie, ies, is parce que ca peut étre d'autres formes)
	if cat=="V" and (orthotext[-1:]==u"é" or orthotext[-1:]==u"i" or orthotext[-1:]==u"u" or orthotext[-2:]==u"ée" or orthotext[-2:]==u"és" or orthotext[-3:]==u"ées"):
		if features.hasAttribute("tense") : features.removeAttribute("tense")
		features.setAttribute("mode","past_participle")
	
	#faire mode="present_participle" et supprimer le trait tense pour tous les V dont la forme se termine par ant
	if cat=="V" and (orthotext[-3:]==u"ant"):
		if features.hasAttribute("tense") : features.removeAttribute("tense")
		features.setAttribute("mode","present_participle")
	
	
	#2) il y a aussi qq lemmes à changer
	#faire lemme="ça" quand forme="ça"
	if orthotext==u"ça":
		e.setAttribute("lemma",u"ça")
		
	#et faire forme="n'" quand token="n'" (IMPORTANT)
	if orthotext==u"ça":
		e.setAttribute("lemma",u"ça")
	
	
	#faire forme="qu' " quand token="qu' "
	if token=="qu' " or token=="qu'":
		e.setAttribute("orthotext","qu' ")
	
	
	
	if cat=="V" and features.getAttribute("mode")=="conditional":
		features.setAttribute("mode","indicative")
		features.setAttribute("tense","conditional")
	
	#Pour les V il faudrait le faire une fois maintenant et une fois que tout aura été corrigé (avant l'export) ????
	

	#3) supprimer les traits qui servent à rien :
	dumbfeatures="""
	token
	que
	aux
	aux_req
	attention
	attentionFeature
	Vadj
	countable
	def
	dem
	det
	poss
	numberposs
	index
	wh
	control
	extraction
	neg
	sat
	enum
	hum
	nb
	sat
	time
	inv
	width
	features
	pcas
	real
	position""".strip().split()
	for df in dumbfeatures:
		if features.hasAttribute(df) : features.removeAttribute(df)
		
	#si cat≠V supprimer trait mode
	if cat!="V" :
		if features.hasAttribute("mode") : features.removeAttribute("mode")
	#pour les V
	else:
		#si mode≠past_particple|present_participle supprimer trait gender
		if features.getAttribute("mode")!="past_particple":
			if features.hasAttribute("gender") : features.removeAttribute("gender")
		#si mode≠ indicative supprimer trait tense, person
		if features.getAttribute("mode")!="indicative":
			if features.hasAttribute("tense") : features.removeAttribute("tense")
			if features.hasAttribute("person") : features.removeAttribute("person")
		#si mode= infinitive supprimer trait numberposs
		if features.getAttribute("mode")=="infinitive":
			if features.hasAttribute("numberposs") : features.removeAttribute("numberposs")
	

	if cat=="CS" or cat=="I":
		if features.hasAttribute("gender") : features.removeAttribute("gender")
		if features.hasAttribute("number") : features.removeAttribute("number")
		if features.hasAttribute("person") : features.removeAttribute("person")
		if features.hasAttribute("tense") : features.removeAttribute("tense")
	if cat!="V":
		if features.hasAttribute("tense") : features.removeAttribute("tense")
		
	
	if lemma and lemma[0]=="-": lemma=lemma[1:]
	
	if cat=="Adj" and not features.hasAttribute("gender"): features.setAttribute("gender","masc/fem")




	
	
def joinRhapsodies(goodfilename,oldfilename,newcombinedname):
	from treebankfiles import rhapsodie2Sentences
	if verbose: 
		print "reading the files"
		print "oldfilename",oldfilename
		print "goodfilename",goodfilename
	old,olddoc,oldlexes,oldlexids=joinRead(oldfilename) # contains time
	dumbolddoc = minidom.parse(oldfilename) # only for markup
	
	new,newdoc,newlexes,newlexids=joinRead(goodfilename)# good for deps!
	if verbose: print "finished reading the files"
	lexidtonode={}
	sentences, fs = rhapsodie2Sentences(goodfilename)
	for s in sentences:
		rootindeces=addinfototree(s)
		for i,node in s.items():
			lexidtonode[node["lexid"]]=node	
	
	#for i in sorted(lexidtonode): print i,lexidtonode[i]
	brandnewdoc=brandNewXml()
	newtokens=brandnewdoc.createElement("words")
	newtokens.setAttribute("type","tokens")
	
	
	newoldlexid,oldnewlexid={},{}
	s = difflib.SequenceMatcher(None, newlexes, oldlexes)
	
	tokcounter=0
	
	
	for e in new["lexemes"].values():
		for refchild in e.getElementsByTagName('ref'): # old refs out
			e.removeChild(refchild)
		correctfeatures(e,lexidtonode)
	
	oldidtoktoidpiv={}
	for oid,oxtok in old["tokens"].items():
		
		for xr in oxtok.getElementsByTagName("ref"):
			oldidtoktoidpiv[oid]=oldidtoktoidpiv.get(oid,[])+[xr.getAttribute("idref")]
			
	#print oldidtoktoidpiv
	
	
	for info,n1,n2,o1,o2 in s.get_opcodes():
		if verbose:print "\n_____________",info,"_________________ new:",n1,n2,"old:",o1,o2
		if info=="equal":
			
			for i,olid in enumerate(oldlexids[o1:o2]):
				newlexid=newlexids[n1:n2][i] #id
				newlex=newlexes[n1:n2][i] # str
				oldlex=oldlexes[o1:o2][i]
				
				newoldlexid[newlexid]=olid # put in dico
				oldnewlexid[olid]=newlexid # put in dico
				
				tokcounter=align(old, new, olddoc,newdoc, olid, newlexid, oldlex,newlex, newtokens, tokcounter, oldidtoktoidpiv)
				
				
		elif info=="replace" or info=="insert" or info=="delete":
			
			totn=float(len(" ".join(newlexes[n1:n2]))) # complete length of the new lexemes
			toto=float(len(" ".join(oldlexes[o1:o2]))) # complete length of the old lexemes
			
			#print "matching",toto,totn
			if verbose: print "newlexes",", ".join(newlexes[n1:n2])
			#print newlexids[n1:n2]
			if verbose: print "oldlexes",", ".join(oldlexes[o1:o2])
			#print oldlexids[o1:o2]
			
			lastlen=0
			nperc=[] # contains the fractions of each lexemes (0 < x < 1=
			for t in newlexes[n1:n2]:
				nperc+=[(len(t)+lastlen)/totn]
				lastlen+=len(t)+1
			lastlen=0
			operc=[] # contains the fractions of each lexemes (0 < x < 1=
			for t in oldlexes[o1:o2]:
				operc+=[(len(t)+lastlen)/toto]
				lastlen+=len(t)+1
			
			#print "nperc",nperc
			#print "operc",operc
			coperc=operc[:] # copy of operc
			#print 
			#print [len(t)/toto for t in newlexes[n1:n2]]
			#print [len(t)/totn for t in oldlexes[o1:o2]]
			aligndic={} # hashtable that sends the corresponding fractions of new lexemes to the old ones
			lasto=None
			for i,p in enumerate(nperc):
				#print "p",p
				while operc and operc[0]<=p:
					#print "operc[0]<=p",operc[0],p
					lasto=operc.pop(0)
					aligndic[p]=aligndic.get(p,[])+[lasto]
					#print aligndic
				
				if operc:
					#print "operc[0]>p",operc[0],p,lasto
					
					#print abs(operc[0]-p),abs(operc[0]-nperc[i+1])
					if abs(operc[0]-p)<abs(operc[0]-nperc[i+1]):
						#print "next one still better comes to me!"
						lasto=operc.pop(0)
						aligndic[p]=aligndic.get(p,[])+[lasto]
					
					#print lasto,abs(lasto-p),abs(operc[0]-p)
					if lasto in aligndic.get(p,[]): continue # case i just found smaller ones to aligndic to
					#print "got to aligndic up to the next one"
					aligndic[p]=aligndic.get(p,[])+[operc[0]]
					#elif abs(lasto-p)<abs(operc[0]-p):
						#print "got to aligndic down to the last one"
						#aligndic[p]=aligndic.get(p,[])+[lasto]
					
			if verbose:print aligndic
			for p,opli in sorted(aligndic.items()):
				for op in opli:
					
					
					
					olid=oldlexids[o1:o2][coperc.index(op)]
					newlex=newlexes[n1:n2][nperc.index(p)]
					oldlex=oldlexes[o1:o2][coperc.index(op)]
					newlexid=newlexids[n1:n2][nperc.index(p)] #id
					
					newoldlexid[newlexid]=olid # put in dico
					oldnewlexid[olid]=newlexid # put in dico
					#print "aligning",newlex,oldlex
					tokcounter=align(old, new, olddoc,newdoc, olid, newlexid, oldlex,newlex, newtokens, tokcounter, oldidtoktoidpiv)
					
				
			
		else: 
			print info,n1,n2,o1,o2
			1/0
			
				
		#print "_______________"
		
		
	if verbose:print "_________________________"
	
	
	
	for c in olddoc.getElementsByTagName("const"):
		if c.getAttribute("ctype")=="lexeme":
			#print c.getAttribute("idref")
			if c.getAttribute("idref") in oldnewlexid:
				
				c.setAttribute( "idref", oldnewlexid[c.getAttribute("idref")] )
			else:
				c.parentNode.removeChild(c)
	
	
	
	
	
	#sample=brandnewdoc.getElementsByTagName("sample")[0]
	#for e in  sample.getElementsByTagName("words"):
		#print e.getAttribute("type")
	#print brandnewdoc.getElementsByTagName("words")
	#print
	sample=brandnewdoc.getElementsByTagName("sample")[0] # the principal node
	
	
	
	
	for e in newdoc.getElementsByTagName("words"):# looking at all the wordgroups
		if e.getAttribute("type")=="lexemes":
			nxlexemes = e
			break
	for e in newdoc.getElementsByTagName("dependencies"):# looking at all the wordgroups
		if e.getAttribute("type")=="syntax":
			nxdependencies = e
			break		
	for e in olddoc.getElementsByTagName("words"):# looking at all the wordgroups
		if e.getAttribute("type")=="pivot":
			nxpivot = e
			break
	for e in olddoc.getElementsByTagName("constrees"):# looking at all the wordgroups
		if e.getAttribute("type")=="pile_tree":
			nxpiles = e
		#if e.getAttribute("type")=="topology_tree":
		################################################### !!!!!!!!!!!!!!!!!!!!!!!
		if e.getAttribute("type")=="macrosyntax_tree":
			nxtopos = e
					
	bxlexemes = brandnewdoc.importNode(nxlexemes,  True)
	bnxdependencies = brandnewdoc.importNode(nxdependencies,  True)
	
	#markup = (olddoc.getElementsByTagName("markup_text")[0]).firstChild.data.split
	xtext=brandnewdoc.importNode(dumbolddoc.getElementsByTagName("markup_text")[0],True)
	
	# putting it all together:
	sample.appendChild(xtext)
	sample.appendChild(nxpivot)
	sample.appendChild(newtokens)
	sample.appendChild(bxlexemes)
	sample.appendChild(bnxdependencies)
	sample.appendChild(nxpiles)
	sample.appendChild(nxtopos)
	
	#allCats,allFuncs,catdeps,depcats=freqs(goodfilename,allCats,allFuncs,catdeps,depcats)
	#1/0
	allConstTrees=phraseStructure(goodfilename, brandnewdoc)
	#print sample.toprettyxml()
	
	xmlrhaps=codecs.open(newcombinedname, "w","utf-8")
	#text.appendChild(doc.createTextNode(alltext))
	#PrettyPrint(doc,xmlrhaps)
	texte= brandnewdoc.toprettyxml() #indent="     "
	xmlrhaps.write(texte)
	
	xmlrhaps.close()
	return allConstTrees
	
	

def idioticdepnumbers(infile,outfile):
	print infile,outfile
	inf=codecs.open(infile, "r","utf-8")
	outf=codecs.open(outfile, "w","utf-8")
	depcount=0
	for line in inf:
		if '<dependency id="dep' in line:
			#print "ooooooooooooo",line
			line=line.replace("dep0","dep"+str(depcount))
			line=line.replace("dep1","dep"+str(depcount))
			depcount+=1
		outf.write(line)
	inf.close()
	outf.close()




def freqs(xmlfile,freqsdics):
	from treebankfiles import rhapsodie2Sentences
	print "freqs"
	
	doc=brandNewXml()
	sample=doc.getElementsByTagName("sample")[0]
	phraseStrus=doc.createElement("constrees")
	phraseStrus.setAttribute("type","phraseStructure")
	sample.appendChild(phraseStrus)
	
	sentences, fs = rhapsodie2Sentences(xmlfile)
	
	filecode=xmlfile.split("Rhap")[1].split("Synt")[0][1:-1]
	
	
	
	
	for treeindex,tree in enumerate(sentences):
		#rootindeces=addinfototree(tree, False)
		
		
		
		for i,node in tree.items():
			
			freqsdics[0][node["cat"]]=freqsdics[0].get(node["cat"],[])+[(filecode,treeindex)]
			for f in node["gov"].values():
				freqsdics[1][f]=freqsdics[1].get(f,[])+[(filecode,treeindex)]
			for gi,f in node["gov"].iteritems():
				if gi:
					freqsdics[2][ "-".join([tree[gi]["cat"],f ]) ]=freqsdics[2].get( "-".join([tree[gi]["cat"],f ]), [])+[(filecode,treeindex)]
					freqsdics[4][ "-".join([tree[gi]["cat"],f, node["cat"]]) ]=freqsdics[4].get( "-".join([tree[gi]["cat"],f , node["cat"]]), [])+[(filecode,treeindex)]
				freqsdics[3][ "-".join([f,node["cat"]]) ]=freqsdics[3].get( "-".join([f,node["cat"]]) , [])+[(filecode,treeindex)]
				
	return freqsdics

def freqsout(freqsdics,freqtypes):
	
	files=[codecs.open(fn+".csv","w","utf-8") for fn in freqtypes]
	
		
	for i,dic in enumerate(freqsdics):
			for l,c in sorted([ (len(freqsdics[i][cc]),cc) for cc in freqsdics[i]]): # , reverse=True
				#print c,l,",".join()
				files[i].write("\t".join((c,str(l)))+"\n")
				files[i].write(", ".join([fil+":"+str(nb) for fil, nb in freqsdics[i][c]])+"\n")
				
	print "frequencies written to"," ".join(freqtypes)	
	

def conll2phrase(conllinfilename, phrasestructureoutname):
	pass

	
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Combine Rhapsodie XML files.')
	parser.add_argument('oldfile', type=str,  help='The XML file before manual correction in the Arborator, containing the correct pivots and constituent trees')
	parser.add_argument('goodfile', type=str,  help='The XML file exported from the Arborator, containing the correct lexemes and dependencies')
	parser.add_argument('outfile', type=str,  help='The XML file that will be written, containing the combination and correction of the two other files')
	parser.add_argument('--verbose', '-v', action='count')
	parser.add_argument('--conll2phrase', '-c', action='store_true')
	parser.add_argument('--idiot', '-i', action='store_true')
	parser.add_argument('--graphs', '-g', action='store_true', help='Show all created phrase structure trees graphically')
	parser.add_argument('--freqs', '-f', action='store_true', help='Create statistics over the syntactic analyses ')
	parser.add_argument('--dir', '-d', action='store_true', help='use whole folders instead of files')
	
	args=parser.parse_args()
	verbose=args.verbose
	
	freqtypes=["allCats","allFuncs","catdeps","depcats","catdepcats"]
	
	freqsdics=[{} for t in freqtypes]
	
	if args.conll2phrase:
		print args
	elif args.idiot:
		idioticdepnumbers(args.oldfile,args.goodfile)
	else:
		if args.dir:
			for oldfile in glob.glob(os.path.join(args.oldfile, '*.*')):
				print "************************************************************* handling",os.path.basename(oldfile)[5:10]
				#Rhap-M0002-Synt.xml
				goodfile=os.path.join(args.goodfile, "Rhap."+os.path.basename(oldfile)[5:10]+".Synt.xml.most.recent.trees.rhaps.xml")
				outfile=os.path.join(args.outfile, os.path.basename(oldfile)[5:10]+".cool.xml")
				#print oldfile,goodfile,outfile
				allConstTrees=joinRhapsodies(goodfile,oldfile,outfile)
				idioticdepnumbers(outfile,os.path.join(args.outfile, os.path.basename(oldfile)[5:10]+".absolutely.cool.xml"))
				print "result written to",outfile
				if args.freqs:
					freqsdics=freqs(goodfile, freqsdics)
					
						
					
					
				if args.graphs:
					for i,tree in enumerate(allConstTrees):
						
						if i<95:continue
						print i
						tree.draw()
		else:	# single file	
			
			if args.freqs:
				freqsdics=freqs(args.goodfile,freqsdics)
			allConstTrees=joinRhapsodies(args.goodfile,args.oldfile,args.outfile)
			print "result written to",args.outfile
			
			if args.graphs:
				for i,tree in enumerate(allConstTrees):
					
					#if i<95:continue
					print i
					tree.draw()
				
	if args.freqs:			
		freqsout( freqsdics,freqtypes )			
				
				