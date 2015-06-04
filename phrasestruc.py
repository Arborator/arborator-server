#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2014 Kim Gerdes
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
import argparse
import difflib, codecs, glob, os, re
import conll
from nltk import Tree


verbose=False

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
				ntree=Tree("(VP (V "+node["t"]+"))")
			elif "V" in node["govcats"]:
				j,func=node["govcats"]["V"][0]
				if func.startswith("para"): # copy governor's const
					gov=tree[j]
					if "const" not in gov:
						makeConstNode(j,gov,constDic, rootindeces,tree)	
					if unicode(gov["const"])[1]=="V": # governor's const is VP
						ntree=Tree("(VP (V "+node["t"]+"))")
					else:	# governor's const is S
						ntree=Tree("(S (V "+node["t"]+"))")
				else: # verb depends on verb
					ntree=Tree("(VP (V "+node["t"]+"))")			
			else:
				ntree=Tree("(S (V "+node["t"]+"))")
		else:
			ntree=constDic[node["cat"]].copy(True)
			ntree.insert(0,Tree("("+node["cat"]+" "+node["t"]+")"))
	else:
		if node["children"] or i in rootindeces or node["cat"] in node["govcats"]:
			ntree=Tree("("+node["cat"]+"P ("+node["cat"]+" "+node["t"]+"))")
		else:
			ntree=Tree("("+node["cat"]+" "+node["t"]+")")
			
	ntree.depindex=i
	ntree.function=unicode(node["gov"].items()[0][1])
	#ntree.t=node["t"]
	
	node["const"]=ntree
	for t in list(ntree.subtrees(lambda t: t.height() == 2)):
		t.depindex=i
		#t.lexid=node["lexid"]
		t.lexid=node["id"]
		t.t=node["t"]	
	

def makePhraseStructure(trees):
	constDic={"V":Tree("(S)"),"N":Tree("(NP)"),"I":Tree("(IP)"),"Adj":Tree("(AP)"),"Pre":Tree("(PP)"),"CS":Tree("(CP)") ,"Pro":Tree("(NP)")   }
	#left in automatic mode: D "Adv":Tree("(AdvP)"), "Cl":Tree("(NP)"),
	#sentences, fs = rhapsodie2Sentences(xmlfile)
	doc=brandNewXml()
	phraseStrus=doc.createElement("constrees")
	phraseStrus.setAttribute("type","phraseStructure")
	sample=doc.getElementsByTagName("sample")[0]
	sample.appendChild(phraseStrus)
	
	
	phrasestructurecounter=0
	#print sentences[0]
	
	allConstTrees=[]
	#print len(sentences)		
	for treeindex,tree in enumerate(trees): # [:33] [19:20]
		
		if verbose:
			print "_____________",treeindex
			print tree

		rootindeces=addinfototree(tree)
		
		for i,node in tree.items(): # creating the actual phrase structure
			makeConstNode(i,node,constDic,rootindeces,tree)
			
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
				
		nodesshown=[]	
		for i in rootindeces: # output
			if i in nodesshown:continue
			ctree=tree[i]["const"]
			allConstTrees+=[ctree]
			
			nodesshown += [t.depindex for t in list(ctree.subtrees(lambda t: t.height() == 2))]
			
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
			
			phrasestructurecounter+=1

	return allConstTrees, doc		
			
def traverse(t,doc, lastconst, plexid=None):
	
	try:
		t.node
	except AttributeError:
		#print unicode(t)
		pass
		#const=doc.createElement("const")
		#const.setAttribute("ctype","lexeme")
		##const.setAttribute("cat","lexeme")
		##const.setAttribute("shape","empty")
		##const.setAttribute("localreg","empty")
		##const.setAttribute("function","?")
		#const.setAttribute("func","head")
		##const.setAttribute("idref",str(plexid))
		##const.setAttribute("token",str(plexid))
		#lastconst.appendChild(const)
	else:
		# Now we know that t.node is defined
		#print '(', unicode(t.node),t.function
		const=doc.createElement("const")
		const.setAttribute("ctype","phrase")
		const.setAttribute("cat",unicode(t.node))
		try:const.setAttribute("t",unicode(t.t))
		except:pass
		#const.setAttribute("shape","empty")
		#const.setAttribute("localreg","empty")
		
		try: const.setAttribute("func",t.function)
		except: const.setAttribute("func","head")		
		
		lastconst.appendChild(const)
		try: 		plexid=t.lexid
		except: 	plexid=None
		if verbose : print "lexid",unicode(t),plexid
		for child in t:
			traverse(child,doc,const,plexid)




def pasteBracketing(trees,ctrees,conllinfilename, out):

	reword=re.compile(" ([^\(\)]+)(?=\))",re.U+re.M+re.DOTALL)
	reonlylett=re.compile("[\w\'\-\&\~]+",re.U+re.M+re.DOTALL)
	respace=re.compile("\s+",re.U+re.M+re.DOTALL)
	rebrack=re.compile("\s*(\)+)\s*",re.U+re.M+re.DOTALL)
	
		
	#################### making the phrase structure parts
	sentences=[]	
	for ctree in ctrees: 
		c = respace.sub(" ",ctree.pprint())
		#.replace("\n"," ")
		#out.write(c+"\n\n")
		
		#for match in reword.finditer(ctree.pprint()):
			#print match.group(1)
			
		sentence=[]
		starter=""
		for seg in reword.split(c): 
			#print "___",seg
			if reonlylett.match(seg):
				#print seg, "onlylett"
				sentence+=[ [starter,seg,""] ]
			else:
				if rebrack.search(seg):
					#print "sentence[-1]",sentence[-1]
					sentence[-1][-1]+=rebrack.search(seg).group(1)
					seg=rebrack.sub("",seg)
				starter=seg
			#print sentence
		sentences+=[sentence]
		#print
	#print sentences
	
	#################### tucking the phrase structure parts to the token as the "ba" (before after) featuer
	for tree in  trees:
		#print tree
		for i in sorted(tree): # for each word
			t = unicode(tree[i]["t"]).strip()
			#print "\n________",i,t
			ii=0
			starti=0
			while True:
				if ii>=10:
					#len(sentences):
					#print "error!!!!!!!!!!!!!!!",[t]
					#for s in sentences[:10]:
						#print s
					starti+=1
					ii=0
					#print "starti",starti
					if starti>=99:
						1/0
				#print "ooo",sentences[ii][0][1]
				if starti<len(sentences[ii]) and sentences[ii][starti][1]==t:
					#print "found it",ii,sentences[ii][starti]
					tree[i]["ba"]=sentences[ii].pop(starti)
					if sentences[ii]==[]:
						#print "popped"
						sentences.pop(ii)
					#print tree[i]
					break
				ii+=1
			
			
			#print tree[i]
			#print tree[i]["const"].pprint()
			#print "\n"
		#print "\n\n\n"

	#################### add to file
	
	#lines=[]
	treenr=0
	lastemptylinenr=-1
	after=""
	with codecs.open(conllinfilename,"r","utf-8") as f:
		lines=[f.readline()[:-1]+"\tPhrase Struc"]
		#print lines
		for li in f:
			li=li[:-1]
			print li
			
			mili=li.strip()
			if len(mili)>5:
				parts = mili.split("\t")
				if len(parts) in [3,5]:#,5
					if len(parts) ==3: lastemptylinenr=len(lines)
				else: # normal line
					tokid=int(parts[2])
					print "tokid",tokid,trees[treenr-1][tokid]["t"]
					print "treenr",treenr
					print trees[treenr-1]
					ba = trees[treenr-1][tokid]["ba"]
					#print "ba",ba
					if ba[1].strip() != trees[treenr-1][tokid]["t"].strip():
						1/0
					#print "adding b to",lines[lastemptylinenr]
					if len(lines[lastemptylinenr].split("\t"))==15:
						lines[lastemptylinenr]+="\t"
					lines[lastemptylinenr]+=ba[0]
					after = ba[2]
					
			else: 
				print "___________________________newtree",lastemptylinenr,len(lines)
				if lastemptylinenr<len(lines)-1:
					treenr+=1
					li+="\t"+after+" "
				lastemptylinenr=len(lines)
				#print "adding",after," to this line"
				#print len(li.split("\t"))
				
			lines+=[li]
				
	#with codecs.open(out,"w","utf-8") as g:
	for li in lines:
		if li and li[-1]==" ":li=li[:-1]
		out.write(li+"\n")

	





startlatex="""\documentclass[pdftex,10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{fullpage}
\usepackage{qtree}
\pagestyle{empty}
\\begin{document}
"""
endlatex="""\\end{document}
\\end"""

def conll2phrasestructure(conllinfilename, phrasestructureoutname, args):
	beginning=""
	rhaps=False
	with codecs.open(conllinfilename,"r","utf-8") as f: beginning = f.read(50)
	if beginning.startswith("Text ID	Tree ID	Token ID"): rhaps=True
	trees=conll.conll2trees(conllinfilename, {"tag":"cat"}, rhaps=rhaps)
	ctrees,xmldoc=makePhraseStructure(trees)
	out=codecs.open(phrasestructureoutname,"w","utf-8")
	if args.bracketing:
		for ctree in ctrees: out.write(ctree.pprint()+"\n\n")
	elif args.pasteBracketing:
		pasteBracketing(trees,ctrees,conllinfilename, out)
	elif args.latex:
		out.write(startlatex)
		for ctree in ctrees: out.write(ctree.pprint_latex_qtree()+"\n\n")
		out.write(endlatex)
	else:
		out.write(xmldoc.toprettyxml())
	out.close()
	if args.graphs:
		for ctree in ctrees:
			ctree.draw()
	
	

	
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='make phrase structure file.')
	parser.add_argument('infile', type=str,  help='the CoNLL file with 10 columns')
	parser.add_argument('outfile', type=str,  help='The XML file that will be written, containing the combination and correction of the two other files')
	parser.add_argument('--verbose', '-v', action='count')
	
	parser.add_argument('--xml', '-x', action='store_true', help='Save as Rhapsodie XML, containing the features (default)')
	parser.add_argument('--bracketing', '-b', action='store_true', help='Save as simple bracketing')
	parser.add_argument('--pasteBracketing', '-p', action='store_true', help='Paste the bracketing at the next column of a Rhapsodie CoNLL file')
	parser.add_argument('--latex', '-l', action='store_true', help='A latex qtree representation of these trees')
	
	
	parser.add_argument('--graphs', '-g', action='store_true', help='Show all created phrase structure trees graphically')
	
	args=parser.parse_args()
	verbose=args.verbose
	conll2phrasestructure(args.infile, args.outfile, args)		
				
				