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

import re, os, codecs, sys
#import config, xmlsqlite, traceback

sys.path.insert(0, '../lib')
from conll import conllFile2trees, update, trees2conllFile

debug=True
debug=False

lettre=re.compile("\w",re.U)


def tree2nodedic(tree, correctiondic={}):
	""" 
	takes the conll string (or malt) representation of a single tree and creates a dictionary for it
	correctiondic of the form {"tag":"cat"} (old to new) corrects feature names
	"""
	
	treedic={}
	bonnr=0
	for line in tree.split('\n'):
		#print "$$$$",line
		line=line.strip()
		if line:
			cells = line.split('\t')
			nrCells = len(cells)
			if nrCells > 10 and cells[3]!="":
				# il faut séparer les cas avec 11 cellules des cas avec 21, car on a les "&".
				codeetexte,_, nr, t, lemma, tag, morph,_,_,_,_,g0,f0 =  cells[:13]
				if nrCells > 20:
					codeetexte,_, nr, t, lemma, tag, morph,_,_,_,_,g0,f0,g1,f1,g2,f2,g3,f3,g4,f4 =  cells[:21]
				if debug:print cells[:20]
				nr=int(nr)
				if tag[:2]=="I_":
					if lettre.search(t[0]) and lettre.search(derniert[0]):treedic[bonnr]["t"]+=" "
					#if nr-bonnr>1:treedic[bonnr]["t"]+=" "
					treedic[bonnr]["t"]+=t
				else:
					bonnr=nr
					
					features={'id':nr,'t': t,'lemma': lemma, 'tag': tag,  'gov':{}, 'morph':morph}
					if g0:	features["gov"][int(g0)]=f0
					else:
						if g3:	
							try:
								features["gov"][int(g3)]=f3
							except:
								print "problem int"
								out=codecs.open("problem.txt","a","utf-8")
								out.write("\t".join(cells[:21])+"\n")
								out.close()
								features["gov"][int(g3.split(",")[0])]=f3
						else:
							if g1:	features["gov"][int(g1)]=f1
							
							else:
								
								
								print "problem"
								out=codecs.open("problem.txt","a","utf-8")
								out.write("\t".join(cells[:21])+"\n")
								out.close()
							
					#if features['gov']== {23: u'sub'} and features['t']=='qui' and codeetexte=='M0023 ':	
						##raw_input("iii")
						#print "kkkkkkkkkkkkkkk"
						#print tree
					treedic[int(nr)]=features
				derniert=t
				
	#print nodedic
	return treedic
		
	
def specialconllFile2trees(path, correctiondic={}):
	"""
	important function!
	
	called from enterConll and uploadConll in treebankfiles.cgi
	
	"""
	f=codecs.open(path,"r","utf-8")
	tree=""
	trees=[]
	for li in f:
		li=li.strip()
		if li:
			elements = li.split("\t")
			#print li
			if elements[0]=="TextID": continue
			if len(elements)>1: nr = elements[1]
			else: nr = ""
			
			if nr: 	tree+=li+"\n"
			else: # emptyline, sentence is finished copy.deepcopy(nodedic)
				treedic=tree2nodedic(tree,correctiondic)
				trees+=[treedic]
				#del nd
				tree=""
	f.close()
	if tree.strip(): # last tree may not be followed by empty line
		treedic=tree2nodedic(tree,correctiondic)
		trees+=[treedic]
	return trees


	
def completeInformation(tree):
	for id in sorted(tree):
		node=tree[id]
		
		if node["gov"]!={}:
			tgov=node["gov"].keys()[0]
			if tgov!=0:
				tfonc=node["gov"][tgov]
				if debug:print node
				tree[tgov]['kid']=tree[tgov].get('kid',{})
				tree[tgov]['kid'][id]=tfonc
	return tree
	
	

def passcomp(tree):
	#print tree
	for id in sorted(tree):
		node=tree[id]
		if 'past_participle' in node.get('morph',""):
			tgov=node["gov"].keys()[0]
			tfonc=node["gov"][tgov]
			if tfonc=="pred" and tree[tgov]["tag"]=="V":
				
				
				node['gov']=tree[tgov]['gov']
				#print "kkk",tree[tgov]
				for i,f in tree[tgov]['kid'].iteritems():
					if f!="pred":
						tree[i]['gov']={id:f}
						#print "---",tree[i]
				tree[tgov]['gov']={id:'aux'}
				print "____",node
				
	return tree


def simpleConll(inputfilename):
	"""
	fonction qui lit rhapsodie tok
	et choisit la fonction unique par token
	resort un format conll standard
	"""
	trees=conllFile2trees(inputfilename)
	#1/0
	with codecs.open(inputfilename+'.simpl', 'w','utf-8') as f: 
		for treedic in trees: 
			#print "\n"
			
			#for id in sorted(treedic):
				#node=treedic[id]
				#print "____",id, node
			#print "ooo"
			treedic=completeInformation(treedic)
			ntreedic=passcomp(treedic)
			
			
			# treedic ressemble à {1: {'lemma': u'bonjour', 'gov': {0: u'root'}, 'tag': u'B_I', 'id': 1, 't': u'bonjour'}, 3: {'lemma': u'Eric', 'gov': {0: u'root'}, 'tag': u'B_N', 'id': 3, 't': u'Eric'}}
			for tokid in sorted(treedic):
				
				tdic=treedic[tokid]
				#print tokid,tdic
				if tdic["gov"]!={}:
					tgov=tdic["gov"].keys()[0]
					tfonc=tdic["gov"][tgov]
				else: tgov,tfonc="",""
				f.write("\t".join([str(tdic["id"]),tdic["t"],tdic["lemma"],tdic["tag"][2:],"","",str(tgov),tfonc])+"\n")
			f.write("\n")
			


def passcompUp(infilename, outfilename):
	trees=conllFile2trees(infilename)
	print "read trees"
	with codecs.open(outfilename,"w","utf-8")  as outfile:
		for tree in trees: 
			tree=completeInformation(tree)
			tree=passcomp(tree)
			for i,tokenid in enumerate(sorted(tree)):
				node=tree[tokenid]
				gov = node.get("gov",{}).items()
				govid,func= gov[0]
				outfile.write("\t".join([str(tokenid),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n")
				
			outfile.write("\n")

def makeConllUfromNaijaFile(infilename):
	trees=[]
	tree={}
	with codecs.open(infilename,"r","utf-8") as infile:
		for line in infile:
		#print "$$$$",line
			line=line.strip()
			if line and line[0]!="#":
				cells = line.split('\t')
				nrCells = len(cells)
				if nrCells != 10 :
					print line
					continue
				nr,t,x,tag=cells[:4]
				nr = int(nr)
				newf={'id':nr,'t': t,'tag': tag}
				x=x.strip()	
				if "=" in x:
					mf=dict([(av.split("=")[0],av.split("=")[-1]) for av in x.split("|")])
					newf=update({"features":mf},newf)
					
				elif x!=".":
					newf=update({"lemma":x},newf)
				if nr==1:
					trees+=[tree.copy()]
					tree={}
				tree[nr]=update(tree.get(nr,{}),newf)
	print len(trees),"trees"
	trees2conllFile(trees,os.path.basename(infilename).split(".")[0]+".conllu",columns="u")
	
if __name__ == "__main__":
	
	#simpleConll("Rhap-M2006-Aligned_data.tok")
	#simpleConll("Rhapsodie.tok")
	#passcompUp("Rhapsodie.conll","Rhapsodie.passcomp.conll")
	makeConllUfromNaijaFile("../corpus/annotatedCorpora.csv")
	
	
	
