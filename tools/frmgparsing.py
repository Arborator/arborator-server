#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom import minidom
#from xml.dom.ext import PrettyPrint
import os,codecs,urllib,hashlib

sys.path.insert(0, '../lib')
from config import *

debug=True
debug=False

emptyeric="""<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<dependencies>
</dependencies>"""

def parseric(text, correction):
	if debug:print "xxxparsing:",text.encode("utf-8")
	cache= path+'cache/'
	
	md5hex = hashlib.md5(text.encode("utf-8")).hexdigest()
	analysisname= cache+text.encode("utf-8")[:10]+md5hex+'.eric.xml'
	
	if not os.path.isfile(analysisname):# if the sentence has never been analyzed:
		params={"grammar":"frmgtel","forest":"xmldep","view":"none","disambiguate":"yes", "sentence":text.encode("iso-8859-1"),"history":"<none>","hidden":"<none>","filename":"","Action":"Submit", ".cgifields":"save_history",".cgifields":"disambiguate",".cgifields":"examples"}
		params=urllib.urlencode(params)
		url="http://alpage.inria.fr/perl/parser.pl"
		try:	
			xmlcontent=urllib.urlopen(url, params).read().decode("iso-8859-1")
		except:
			print "<br><h1>no connection to",url,"</h1>"
			return 0,0
		#print params,xmlcontent.encode("utf-8")
		if xmlcontent.strip()==emptyeric: return -111,-111
		analysisfile=codecs.open(analysisname,"w","iso-8859-1")
		analysisfile.write(xmlcontent)
		analysisfile.close()
	doc = minidom.parse(analysisname)
	wordList=[]
	words={}
	links={}
	
	lastcluster={}
	goodNodeAttris=["form","lemma","cat","cluster"]
	goodEdgeAttris=["source","target","label","type"]
	
	for n in doc.getElementsByTagName("dependencies"):
		for nn in n.childNodes:
			if nn.nodeName=="node":
				id = nn.getAttribute("id")
				#print "node",id
				attris={}
				for k in nn.attributes.keys():
					if k in goodNodeAttris:
						attris[k]= nn.getAttribute(k)
						if k=="cluster":
							attris["idnum"]= int(nn.getAttribute(k).split("_")[1])
						elif k=="form": 
							if not attris[k]: attris[k]="---"
							elif attris[k]=="_NUMBER" :
								attris[k]=lastcluster["token"]
								attris["cat"]="det"
							elif attris[k]=="_LOCATION" :
								attris[k]=lastcluster["token"]
								attris["cat"]="np"
							elif attris[k]=="_ADRESSE" :
								attris[k]=lastcluster["token"]
								attris["cat"]="np"
							elif attris[k]=="_COMPANY" :
								attris[k]=lastcluster["token"]
								attris["cat"]="np"
							elif attris[k]=="_HEURE" :
								attris[k]=lastcluster["token"]
								attris["cat"]="np"
							elif attris[k].startswith("_DATE" ): # reason: _DATE_artf
								attris[k]=lastcluster["token"]
								attris["cat"]="np"
							elif attris[k].startswith("_PERSON" ): # reason: _PERSON_f
								attris[k]=lastcluster["token"]
								#print "___",attris[k]
								attris["cat"]="np"
								#attris[u"lemma"]="uuuuuuuuu"#attris[k] # TODO: why why why...
								#print "mmmmmmmmmmmmmm",k,attris[k]
							#TODO: other things to change here???
					
				words[id]=attris
				wordList+=[(attris["idnum"],id)]
			elif nn.nodeName=="edge":
				#print "edge"
				attris={}
				for k in nn.attributes.keys():
					if k in goodEdgeAttris: attris[k]= nn.getAttribute(k)
				links[nn.getAttribute("id")]=attris
			elif nn.nodeName=="cluster":
				#lastcluster["id"]=nn.getAttribute("id")
				lastcluster["token"]=nn.getAttribute("token")
				

	
	#print wordList
	#print words
	wordList.sort()
	wordList=[(i,n[1]) for i,n in enumerate(wordList)]  # n[1]: first char of eric's id code
	#print wordList
	lw = [(id,i) for i,id in wordList]
	for n,(i,id) in enumerate(wordList):
		words[id]["idnum"]=i
		words[id]["nnn"]=n # TODO: use this!!!!!
	
	for l in links:
		#print "target",words[links[l]["target"]], "source",words[links[l]["source"]],links[l]["label"]
		words[links[l]["target"]]["gov"]='"'+str(words[links[l]["source"]]["idnum"])+'":"'+links[l]["label"]+'"'
		words[links[l]["target"]]["gg"]=(words[links[l]["source"]]["idnum"],links[l]["label"])
		#words[links[l]["target"]]["gov"]=links[l]["source"]+':'+links[l]["label"]

	
	
	
	wordfeatures=[words[n] for i,n in wordList]
	indeces,ws=[],{}
	for i,n in wordList:
		indeces+=[i]
		ws[i]=words[n]
		
	####################### here:
	if correction: 
		wordfeatures=eric2rhapsodie(indeces, ws)
		sentence = " ".join([words[w[1]]["form"] for w in wordList if words[w[1]]["form"]!="---"]) #
	else:
		sentence = " ".join([words[w[1]]["form"] for w in wordList ])
	if debug:	print "sentence",sentence.encode("utf-8"),wordfeatures
	##############################
	
	return sentence,wordfeatures
	
	#print "________wordfeatures",wordfeatures
	
	


def eric2rhapsodie(indeces, ws):
	"""
	example
	indeces:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] 
	ws: {
	0: {'nnn': 0, u'form': u'une', u'lemma': u'un', 'idnum': 0, u'cat': u'det', 'gg': (5, u'det'), u'cluster': u'1c_0_1', 'gov': u'"5":"det"'}, 
	1: {'nnn': 1, u'form': '---', u'lemma': u'', 'idnum': 1, u'cat': u'comp', 'gg': (3, u'comp'), u'cluster': u'1c_0_0', 'gov': u'"3":"comp"'}, 
	2: {'nnn': 2, u'form': '---', u'lemma': u'', 'idnum': 2, u'cat': u'start', 'gg': (3, u'start'), u'cluster': u'1c_0_0', 'gov': u'"3":"start"'}, 
	3: {'nnn': 3, u'form': '---', u'lemma': u'', 'idnum': 3, u'cat': u'S', u'cluster': u'1c_0_0'}, 
	4: {'nnn': 4, u'form': u'petite', u'lemma': u'petit', 'idnum': 4, u'cat': u'adj', 'gg': (5, u'N'), u'cluster': u'1c_1_2', 'gov': u'"5":"N"'}, 
	5: {'nnn': 5, u'form': u'rue', u'lemma': u'rue', 'idnum': 5, u'cat': u'nc', 'gg': (1, u'N2'), u'cluster': u'1c_2_3', 'gov': u'"1":"N2"'}, 
	6: {'nnn': 6, u'form': u'qui', u'lemma': u'qui', 'idnum': 6, u'cat': u'prel', 'gg': (8, u'subject'), u'cluster': u'1c_3_4', 'gov': u'"8":"subject"'}, 
	7: {'nnn': 7, u'form': '---', u'lemma': u'', 'idnum': 7, u'cat': u'N2', 'gg': (5, u'N2'), u'cluster': u'1c_3_3', 'gov': u'"5":"N2"'}, 
	8: {'nnn': 8, u'form': u'part', u'lemma': u'partir', 'idnum': 8, u'cat': u'v', 'gg': (7, u'SRel'), u'cluster': u'1c_4_5', 'gov': u'"7":"SRel"'}, 
	9: {'nnn': 9, u'form': u'\xe0', u'lemma': u'\xe0', 'idnum': 9, u'cat': u'prep', 'gg': (8, u'preparg'), u'cluster': u'1c_5_6', 'gov': u'"8":"preparg"'},
	10: {'nnn': 10, u'form': u'droite', u'lemma': u'droite', 'idnum': 10, u'cat': u'nc', 'gg': (9, u'N2'), u'cluster': u'1c_6_7', 'gov': u'"9":"N2"'}, 
	11: {'nnn': 11, u'form': u'de', u'lemma': u'de', 'idnum': 11, u'cat': u'prep', 'gg': (12, u'PP'), u'cluster': u'1c_7_8', 'gov': u'"12":"PP"'}, 
	12: {'nnn': 12, u'form': '---', u'lemma': u'', 'idnum': 12, u'cat': u'VMod', 'gg': (8, u'vmod'), u'cluster': u'1c_7_7', 'gov': u'"8":"vmod"'}, 
	13: {'nnn': 13, u'form': u'le', u'lemma': u'le', 'idnum': 13, u'cat': u'det', 'gg': (14, u'det'), u'cluster': u'1c_8_9', 'gov': u'"14":"det"'}, 
	14: {'nnn': 14, u'form': u'cin\xe9ma', u'lemma': u'cin\xe9ma', 'idnum': 14, u'cat': u'nc', 'gg': (11, u'N2'), u'cluster': u'1c_9_10', 'gov': u'"11":"N2"'}, 
	15: {'nnn': 15, u'form': '---', u'lemma': u'', 'idnum': 15, u'cat': u'end', 'gg': (16, u'Punct'), u'cluster': u'1c_10_10', 'gov': u'"16":"Punct"'}, 
	16: {'nnn': 16, u'form': '---', u'lemma': u'', 'idnum': 16, u'cat': u'S', 'gg': (3, u'S'), u'cluster': u'1c_10_10', 'gov': u'"3":"S"'}}
	
	example
	Pierre a perdu --- --- 
	[{'nnn': 0, u'form': u'Pierre', u'lemma': u'_PERSON', 'idnum': 0, 'cat': u'np', 'gg': (2, u'subject'), u'cluster': u'1c_0_1', 'gov': u'"2":"subject"'}, {'nnn': 1, u'form': u'a', u'lemma': u'avoir', 'idnum': 1, u'cat': u'aux', 'gg': (2, u'Infl'), u'cluster': u'1c_1_2', 'gov': u'"2":"Infl"'}, {'nnn': 2, u'form': u'perdu', u'lemma': u'perdre', 'idnum': 2, u'cat': u'v', u'cluster': u'1c_2_3'}, {'nnn': 3, u'form': '---', u'lemma': u'', 'idnum': 3, u'cat': u'end', 'gg': (4, u'Punct'), u'cluster': u'1c_3_3', 'gov': u'"4":"Punct"'}, {'nnn': 4, u'form': '---', u'lemma': u'', 'idnum': 4, u'cat': u'S', 'gg': (2, u'S'), u'cluster': u'1c_3_3', 'gov': u'"2":"S"'}]

	"""
	
	
	if debug:print "<br>",indeces,"<br>",ws,"<br>","<br>"
	for i in indeces:
		w=ws[i]
		if debug: print "<br>***** before modification:",w
		w["cat"]=ericcats.get(w["cat"],w["cat"]) # correct categories
		if "gg" in w.keys(): # ggs looks like this : (2, u'subject') => index of governor, function
			#w["gg"]=(w["gg"][0],ericfuncs.get(w["gg"][1],w["gg"][1])) # correct functions
			
			# problem of auxiliaries: auxs are deps of main verb, main verb has subject
			if w["gg"][1] in ["V" ,"Infl"]: # we found an auxiliary: w 
				oldgov=w["gg"][0] # oldgov: the index of the main verb (participle or infinitive)
				#newgov=w["idnum"] # newgov: 
				#w["gg"] = (-1,"root")
				
				w["gg"] =  ws[oldgov].get("gg",(-1,"root")) # if the main verb doesn't have a governor, the aux becomes root
				ws[oldgov]["gg"]=(i,"aux")
				for j in indeces: # check all words
					ww=ws[j]
					if "gg" in ww.keys() :
						if ww["gg"][0]==oldgov : # we found a dependant of the participle
							if ww["gg"][1] in ["sub"]: # move the subject to the auxiliary	
								ww["gg"]= (i,ww["gg"][1])
						#if ww["idnum"]==oldgov:
							
			# problem of jumping over --- : pps and rels
			if w["gg"][1]in ["PP", "SRel", "prel", "N2", "audience"]: # w's gov link of this type goes to ---
				govn = ws[w["gg"][0]] # let's call the gov "govn"
				if hyph["form"]=="---":
					w["gg"]=govn["gg"] # take ---'s governor and put it on w
					if ws[w["gg"][0]]["form"]=="---":w["gg"]=(-1,"root")
			
			# problem of N2
			if w["gg"][1] in ["N2"]:
				
				#for ww in words:
				for j in indeces:
					ww=ws[j]
					if ww["idnum"]== w["gg"][0] and ww["cat"]== "prep":w["gg"]=(w["gg"][0],"obj")

				if w["cat"]in ["adj","verb","prep"]: w["gg"]=(w["gg"][0],"mod")
			
			
			w["gg"]=(w["gg"][0],ericfuncs.get(w["gg"][1],w["gg"][1])) # correct functions
				
				
		else:
			w["gg"] = (-1,"root")
		
			
	words=[ws[j] for j in indeces if ws[j]["form"]!="---"]				

	#for w in words:
	for i in indeces:
		w=ws[i]	
		if "gg" in w: 
			if w["gg"][1]in ["csu", "prep"] or (w["gg"][1]in ["obj"] and w["cat"]== "QU"):# found a bad complementizer/preposition
				govverb=w["gg"][0] # get the comp/prep's governor
				#print "!!!!!!!!!!!!"
				for j in indeces: # check all following verbs
					ww=ws[j]
					#print i,j,ww,"<br>"
					if j>i and "gg" in ww and ww["cat"]=="VB" and ww["gg"][0]==govverb: # found the first following verb with the good gov
						#print "!!!!!!!!!!!!",ww
						ww["gg"]=i,"gov" # the embedded verb gets the comp/prep as gov
						w["gg"]=govverb,"obj" # the comp/prep keeps the verb as gov and calls it "obj"
						break
			
			
			w["gov"]='"'+str(w["gg"][0])+'":"'+w["gg"][1]+'"'
		else:
			w["gg"] = (-1,"root")
	
	return words


