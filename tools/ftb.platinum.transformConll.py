#! usr/bin/python
#! coding: utf-8

import datetime, codecs, time, sys, os, glob, copy
sys.path.insert(0, '../lib')
import conll

debug=3
debug=False



def tagset(arbre):
	"""
	
	Transformation des étiquettes morphosyntaxiques

	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre
		if node["lemma"] in ["ne", "pas", "jamais", "plus"]:
                    node["tag"] = "ADN"
                    #print "apres",node["tag"]
		elif node["tag"] == "CL" and node["tag2"] == "CLS":
                    node["tag"] = "CLS"
                    #print "apres",node["tag"]
		elif node["tag"] == "CL" and node["tag2"] == "CLR":
                    node["tag"] = "CLI"
                    #print "apres", node["tag"]                    
		elif node["tag"] == "CL" and node["tag2"] == "CLO":
                    node["tag"] = "CLI"
                    #print "apres", node["tag"]
		elif node["tag"] == "V" and node["tag2"] == "V":
                    node["tag"] = "VRB"
                    #print "apres", node["tag"]
		elif node["tag"] == "V" and node["tag2"] == "VS":
                    node["tag"] = "VRB"
                    #print "apres", node["tag"]
		elif node["tag"] == "V" and node["tag2"] == "VIMP":
                    node["tag"] = "VRB"
                    #print "apres", node["tag"]
		elif node["tag"] == "V" and node["tag2"] == "VINF":
                    node["tag"] = "VNF"
                    #print "apres", node["tag"]
		elif node["tag"] == "V" and node["tag2"] == "VPP":
                    node["tag"] = "VPP"
                    #print "apres", node["tag"]
		elif node["tag"] == "V" and node["tag2"] == "VPR":
                    node["tag"] = "VPR"
                    #print "apres", node["tag"]
		elif node["tag"] == "N" and node["tag2"] == "NC":
                    node["tag"] = "NOM"
                    #print "apres", node["tag"]
		elif node["tag"] == "N" and node["tag2"] == "NPP":
                    node["tag"] = "NOM"
		elif node["tag"] == "C" and node["tag2"] == "CC":
                    node["tag"] = "COO"
                    #print "apres", node["tag"]
		elif node["tag"] == "C" and node["tag2"] == "CS":
                    node["tag"] = "CSU"
                    #print "apres", node["tag"]
		elif node["tag"] == "A" and node["tag2"] == "ADJ":
                    node["tag"] = "ADJ"
                    #print "apres", node["tag"]
		elif node["tag"] == "A" and node["tag2"] == "ADJWH":
                    node["tag"] = "PRQ"
                    #print "apres", node["tag"]
		elif node["tag"] == "ADV" and node["tag2"] == "ADV":
                    node["tag"] = "ADV"
		elif node["tag"] == "ADV" and node["tag2"] == "ADVWH":
                    node["tag"] = "PRQ"
                    #print "apres", node["tag"]
		elif node["tag"] == "PRO" and node["tag2"] == "PRO":
                    node["tag"] = "PRO"
                    #print "apres", node["tag"]
		elif node["tag"] == "PRO" and node["tag2"] == "PROREL":
                    node["tag"] = "PRQ"
                    #print "apres", node["tag"]
		elif node["tag"] == "PRO" and node["tag2"] == "PROWH":
                    node["tag"] = "PRQ"
                    #print "apres", node["tag"]
		elif node["tag"] == "D" and node["tag2"] == "DET":
                    node["tag"] = "DET"
                    #print "apres", node["tag"]
		elif node["tag"] == "D" and node["tag2"] == "DETWH":
                    node["tag"] = "PRQ"
                    #print "apres", node["tag"]
		elif node["tag"] == "P" and node["tag2"] == "P":
                    node["tag"] = "PRE"
                    #print "apres", node["tag"]
		elif node["tag"] == "P+D" and node["tag2"] == "P+D":
                    node["tag"] = "PRE"
                    #print "apres", node["tag"]
		elif node["tag"] == "P+PRO":
                    node["tag"] = "PRQ"
                    #print "apres", node["tag"]
		elif node["tag"] == "I" and node["tag2"] == "I":
                    node["tag"] = "INT"
		elif node["tag"] == "ET" and node["tag2"] == "ET":
                    node["tag"] = "X"
                    #print "apres", node["tag"]
	return arbre
    
#Modifier les liens de dépendance

def liensAux(arbre):
	"""
	transformation des liens aux_tps, aux_pass et aux_caus -> aux
	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre
		#print i, node
		if node["gov"] and node["gov"].values()[0] in ["aux_tps", "aux_pass", "aux_caus"]:
			#print node["gov"].keys()[0], "et", node["gov"].values()[0]
			node["gov"] = {node["gov"].keys()[0]:"aux"} 
	return arbre

def liensSpe(arbre):
	"""
	transformation des liens det -> spe
	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre
		if node["tag"] == "DET":
			node["gov"] = {node["gov"].keys()[0]:"spe"} 
	return arbre

def desEnTete(arbre):
	"""
	des est toujours tête comme une préposition
	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre
		if node["tag"] == "DET" and node["t"] in ["des", "du", "de", "d'"]:
			if node["gov"]:
				govid = node["gov"].keys()[0]
				govnode=arbre[govid]
				if govnode["gov"]:
					ggovid = govnode["gov"].keys()[0]
					node["gov"]={ggovid:govnode.get("gov",{}).get(ggovid,0)}
					govnode["gov"]={i:"dep"}
					
	return arbre



def liensDep(arbre):
	"""
	transformation des liens mod_rel, obj et mod -> dep
	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre
		if node["gov"] and node["gov"].values()[0] in ["mod_rel"]:
			node["gov"] = {node["gov"].keys()[0]:"dep"}
		elif node["tag"] not in ["VRB", "VNF", "VPP", "VPR"]: #lien obj lorqu'il ne dépend pas d'un verbe
			head = node["id"]
			for i, node in arbre.iteritems():
				if node["gov"] and node["gov"].values()[0] in ["obj"] and node["gov"].keys()[0] == head:
					node["gov"] = {node["gov"].keys()[0]:"dep"}
				elif node["gov"] and node["gov"].values()[0] in ["mod"] and node["gov"].keys()[0] == head:
					node["gov"] = {node["gov"].keys()[0]:"dep"}
	return arbre

def liensComp(arbre):
	"""
	transformation des liens ats, ato, a_obj, de_obj, p_obj, obj et mod ->comp
	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre #
		#print "avant",node["gov"]
		if node["gov"] and node["gov"].values()[0] in ["ats", "ato", "a_obj", "de_obj", "p_obj"]:
			node["gov"] = {node["gov"].keys()[0]:"comp"}
		elif node["tag"] in ["VRB", "VNF", "VPP", "VPR"]:#lien obj / mod lorsqu'il dépend d'un verbe
			headComp = node["id"]
			for i, node in arbre.iteritems():
				if node["gov"] and node["gov"].keys()[0] == headComp:
					if node["gov"] and node["gov"].values()[0] in ["obj"]:
						node["gov"] = {node["gov"].keys()[0]:"comp"}
						#print "Success, obj -> comp"
					elif node["gov"] and node["gov"].values()[0] in ["mod"] and node["lemma"] in [u"à", "au", "aux", "de"]:
						node["gov"] = {node["gov"].keys()[0]:"comp"}
						#print "Success, mod -> comp"
	return arbre

def liensPunct(arbre):
	"""
	Si le signe de ponctuation est final, il dépend de la racine, sinon il dépend du mot qui précède.
	"""
	for i, node in arbre.iteritems(): #pour chaque position et noeud de l'arbre
		#print "avant",node["gov"]
		if node["gov"] == {0:"root"}:
			head = node["id"] 
			for i, node in arbre.iteritems():
				if node["tag"] == "PONCT" and node["lemma"] in [u".", u"!", u"?", u";",u":"]:
					node["gov"] = {head:"ponct"}
				elif node["tag"] == "PONCT":
					node["gov"] = {i-1:"ponct"}

		#print "apres",node["gov"]
	return arbre

def liensAd(arbre):
	"""
	transformation des liens mod -> ad
	"""
	for i, node in arbre.iteritems():
		if node["tag"] in ["VRB", "VPP", "VNF", "VPR"]:#lien mod quand il dépend d'un verbe et n'est pas comp
			headVerbale = node["id"]
			for i, node in arbre.iteritems():
				if node["gov"] and node["gov"].values()[0] in ["mod"] and node["gov"].keys()[0] == headVerbale:
					Ad = node["id"]
					#print Ad, "ad"
					if headVerbale < Ad:
						node["gov"] = {node["gov"].keys()[0]:"ad"}
						#print "Success mod -> ad"
					elif node["tag"] in ["ADN", "PRQ"]:
						node["gov"] = {node["gov"].keys()[0]:"ad"}
						#print "Success Ad"
					elif Ad == headVerbale-1:
						node["gov"] = {node["gov"].keys()[0]:"ad"}
						#print "Success ad exception"
	return arbre

def liensPeriph(arbre):
	"""
	transformation des liens mod -> periph
	"""
	for i, node in arbre.iteritems():
		if node["tag"] in ["VRB", "VPP", "VNF", "VPR"]:
			headMod = node["id"]
			for i, node in arbre.iteritems():
				if node["tag"] not in ["ADN","PRQ"]:
					headPeriph = node["id"]
					if node["gov"] and node["gov"].values()[0] in ["mod"] and node["gov"].keys()[0] == headMod and headPeriph < headMod:
						node["gov"] = {node["gov"].keys()[0]:"periph"}
						#print "Success mod -> periph"
	return arbre

def liensPara(arbre):
	"""
	Transformation des liens coord + changement de dépendant -> lien para
	"""
	headPara = ""
	endPara = ""
	for i, node in arbre.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["coord"]:
			headPara = node["gov"].keys()[0]
		#	endMark = node["id"]
		elif node["gov"] and node["gov"].values()[0] in ["dep_coord"]:
			endPara = node["id"]
			if headPara < endPara:
				node["gov"] = {headPara:"para"}
	return arbre


def liensMark(arbre):
	"""
	Transformation des liens dep_coord + inversion tête-dépendant -> lien mark
	"""
	headMark = ""
	endMark = ""
	for i, node in arbre.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["para"]:
			headMark = node["id"]
			#print node["t"]
			for i, node in arbre.iteritems():
				if node["gov"] and node["gov"].values()[0] in ["coord"]:
					endMark = node["id"]
					if headMark > endMark:
						node["gov"] = {headMark:"mark"}
		elif node["gov"] and node["gov"].values()[0] in ["dep_coord"]:
			headMark = node["id"]
			for i, node in arbre.iteritems():
				if node["tag"] == "COO" and node["gov"] and node["gov"].values()[0] in ["root"]:
					endMark = node["id"]
					if headMark > endMark:
						node["gov"] = {headMark:"mark"}
						for i, node in arbre.iteritems():
							if node["gov"] and node["gov"].values()[0] in ["dep_coord"]:
								node["gov"] = {0:"root"}
				elif node["tag"] == "ADV":
					node["gov"] = {node["gov"].keys()[0]:"dep"}
	return arbre



#def NNAAMMEE(tree):
	#"""
	#NNAAMMEE -> XXX
	#"""
	#for i, node in tree.iteritems():
		#if node["t"]=="XXX":
			#node["t"]="YYY"
			#node["lemma"]="YYY"
		#elif node["t"]=="NNAAMMEE":
			#node["t"]="XXX"
			#node["lemma"]="XXX"
	#return tree


#def removeTag2(tree):
	#for i, node in tree.iteritems():
		#del node["tag2"]
	

#def emptyErrors(tree):
	#for i, node in tree.iteritems():
		#if node["t"]=="":
			#if not node["gov"]: 
				#pprint(tree)
				#print i,node
				#print "_______________"
				
			#else:
				#gi,gf = node["gov"].items()[0]
				#for ci,cf in node["children"].iteritems():#normalement un seul enfant
					#cnode=tree[ci]
					#cnode["gov"]={gi:gf}
			#tree=splice(tree,i,{})
			#addinfototree(tree)
			#tree=emptyErrors(tree)
			#break
			##print i, "removed empty node in"
			##pprint(tree)
	#return tree
	
#def kesk(tree):
	#for i, node in tree.iteritems():
		#if node["lemma"]=="est-ce":
			#gi,gf = node["gov"].items()[0]
			#if gi in tree and tree[gi]["lemma"]=="que": # qu'est-ce que
				#govnode=tree[gi]
				##print
				##print i-1,tree[i-1]["t"],govnode
				##print i,tree[i]["t"],node
				##print i+1,tree[i+1]["t"], tree[i+1]
				##print i+2,tree[i+2]["t"], tree[i+2]
				##print "_______________"
				
				#gov={}
				#for ii in [i-1,i,i+1]: # for each node of qu'est-ce que
					#ggnode=tree[ii]
					#for ggi,ggf in ggnode["gov"].iteritems(): # collect each exterior governor
						#if ggi<i-1 or i+1<ggi:
							#gov[ggi]=ggf
					#for ci,cf in ggnode["children"].iteritems():# change each exterior kid
						#if ci<i-1 or i+1<ci:
							#cnode=tree[ci]
							#cnode["gov"]={gi:cf}
				#if i+2 in tree and tree[i+2]["lemma"][0] in "aeiouy" and tree[i+2]["lemma"] not in ["euh","est-ce",u"est-ce que",u"est-ce-que"]:
					#t=u"qu'est-ce qu'"
					##pprint(tree)
					##print i
					##if  tree[i+2]["lemma"] not in ["on","un"] : azer
				#else:
					#t=u"qu'est-ce que"
				#tree[gi]={'lemma': u"qu'est-ce que", 'tag': u'CSU', 't':t , 'gov': gov, 'id': gi}
				#tree=splice(tree,i,{})
				#tree=splice(tree,i,{})
				#addinfototree(tree)
				#tree=kesk(tree)
				#break
				##print "***"
				##pprint(tree)
			#else: 
				##print
				###print i-1,tree[i-1]["t"],govnode
				##print i,tree[i]["t"],node
				##print i+1,tree[i+1]["t"], tree[i+1]
				##print i+2,tree[i+2]["t"], tree[i+2]
				##print "_______________"
				#gov={}
				#for ii in [i,i+1]: # for each node of est-ce que
					#ggnode=tree[ii]
					#for ggi,ggf in ggnode["gov"].iteritems(): # collect each exterior governor
						#if ggi<i or i+1<ggi:
							#gov[ggi]=ggf
					#for ci,cf in ggnode["children"].iteritems():# change each exterior kid
						#if ci<i or i+1<ci:
							#cnode=tree[ci]
							#cnode["gov"]={i:cf}
				#if i+2 in tree and tree[i+2]["lemma"][0] in "aeiouy" and tree[i+2]["lemma"] not in ["euh","est-ce",u"est-ce que",u"est-ce-que"]:
					#t=u"est-ce qu'"
					##pprint(tree)
					##print i
					##if  tree[i+2]["lemma"] not in ["on","un"] : qsdf
				#else:
					#t=u"est-ce que"
				#tree[i]={'lemma': u"est-ce que", 'tag': u'CSU', 't':t , 'gov': gov, 'id': gi}
				#tree=splice(tree,i+1,{})
				#addinfototree(tree)
				#tree=kesk(tree)
				#break
	#return tree


#def rendezvous(tree):
	##z=False
	#for i, node in tree.iteritems():
		#if node["lemma"]=="rendez-vous" and i+1 in tree and tree[i+1]["t"]=="-vous":
			#node["t"]="rendez-vous"
			#tree=splice(tree,i+1,{})
			#addinfototree(tree)
			#pprint(tree)
			#print "******"
			#tree=rendezvous(tree)
			##z=True
			#break
	##if z:
		##print "mmmmm"
		##pprint(tree)
		##print "nnnnnnnnnnnnn"
	#return tree
		
#def cls(tree):
	#for i, node in tree.iteritems():
		#if node["tag"]=="CLS":
			#gi,gf = node["gov"].items()[0]
			#if gi in tree and tree[gi]["tag"]!="VRB" and gf not in ["para","disflink"]: # CLS whose governor is not a verb
				#govnode=tree[gi]
				
				#pprint(tree)
				#print "******",i
			
			
	#return tree


#def desEnTete(tree):
	#"""
	#des est toujours tête comme une préposition
	#"""
	#for i, node in tree.iteritems():
		#if node["tag"] == "DET" and node["t"] in ["des", "du", "de", "d'"]:
			#if node["gov"]:
				#govid = node["gov"].keys()[0]
				#if govid in tree:
					#govnode=tree[govid]
					#if govnode["gov"]:
						#ggovid = govnode["gov"].keys()[0]
						#node["gov"]={ggovid:govnode.get("gov",{}).get(ggovid,0)}
						#govnode["gov"]={i:"dep"}
		#node["tag"] == "PRE"			
	#return tree


##V disfl-> des à -->  comp
##V disfl->  "du", "de", "d'" --> comp
##V disfl-> 

#def auxEnTete(tree):
	#"""
	#aux est la tête
	#"""
	#for i, node in tree.iteritems():
		#if node["gov"] and node["gov"].values()[0] in ["aux"] and node["gov"].keys()[0]>i: # found a node that is a dependent aux
			##print "found a node that is a dependent aux",i,node
			#gi = node["gov"].keys()[0]
			#gnode=tree[gi]
			#if gnode["gov"] and gnode["gov"].values()[0] in ["aux"] and gnode["gov"].keys()[0]>gi: # found a double aux
				##print "found a double aux",gi,node
				#ggi = gnode["gov"].keys()[0]
				#ggnode=tree[ggi]
				#for ci,cf in ggnode["children"].iteritems():
					#if cf in ["suj","periph","insert","mark"]: # toutes ces fonctions montent sur 
						#cnode=tree[ci]
						#cnode["gov"]={i:cf}
					#elif cf=="dm" and ci<i: # dm seulement quand ils sont à gauche de l'auxiliaire
						#cnode=tree[ci]	
						#cnode["gov"]={i:"dm"}
					#elif cf=="ad":
						#cnode=tree[ci]
						#if cnode["t"] in ["ne","n'"]:
							#cnode["gov"]={i:cf}
				#node["gov"]=ggnode["gov"].copy() 
				#gnode["gov"]={i:"aux"}
				#ggnode["gov"]={gi:"aux"}
			#else: # only simple aux
				#for ci,cf in gnode["children"].iteritems():
					#if cf in ["suj","periph","insert","mark"]: # toutes ces fonctions montent sur 
						#cnode=tree[ci]
						#cnode["gov"]={i:cf}
					#elif cf=="dm" and ci<i: # dm seulement quand ils sont à gauche de l'auxiliaire
						#cnode=tree[ci]	
						#cnode["gov"]={i:"dm"}
					#elif cf=="ad":
						#cnode=tree[ci]
						#if cnode["t"] in ["ne","n'"]:
							#cnode["gov"]={i:cf}
				#node["gov"]=gnode["gov"].copy()
				#gnode["gov"]={i:"aux"}
			
			#addinfototree(tree)
	#return  tree		
			##pprint(tree)
			
#from searchConll import  hasEmptyNode
			
def goldplatinum(tree):
	removeTag2(tree)
	addinfototree(tree)
	tree=auxEnTete(tree)
	tree=desEnTete(tree)
	tree=NNAAMMEE(tree)

	tree=emptyErrors(tree)
	
	tree=kesk(tree)
	tree=rendezvous(tree)
	tree=cls(tree)
	return tree

def ftbplatinum(tree):
	
	addinfototree(tree)
	
	tree=tagset(tree)
	tree=auxEnTete(tree)
	tree=desEnTete(tree)
	tree=NNAAMMEE(tree)

	tree=emptyErrors(tree)
	
	tree=kesk(tree)
	tree=rendezvous(tree)
	tree=cls(tree)
	return tree





def pprint(tree):
	for i in tree:
		print i, tree[i]["t"],tree[i]
	print


def splice(sentencedic,nodenum,intdic,copiedfeatures=['t','token','lemma','cat','tag','beg','end']):
		"""
		integrates the intdic into sentencedic at position nodenum
		an empty intdic kicks out the node in a proper manner (other dependencies are still ok)

		format of intdic:
			indices start with 'i', for example 'i2'
			last node that carries 'child' feature will receive the children of the former nodenum node
			last node that has governor i0 will receive the governors of the former nodenum node
			if no node has a 'i0' governor, the first node will receive the governors
			WATCH OUT: the ix will be ordered. so i10 will be before i9!!!
			example pour est-ce, remplacé par ce sous-arbre :
			{
				'i1':{ u'person': u'3', u'number': u'sg', u'cat': u'V', u'lemma': u'\xeatre', u'token': u'est', u'tense': u'present', u'mode': u'indicative', 'gov': {'i0':'root'}, u't': u'A', 'child':None},
				'i2':{u'cat': u'Cl', u'lemma': u'c', u'token': u'-ce', u't': u'B', 'gov': {'i1': u'sub'}}
			}

		gives back new sentencedic

		"""
		intgov,intchi=None,None
		if debug>2: 
			print "================== integrating"
			for i in sorted(intdic):
				print i,intdic[i]
			print "into ((((((((((((("
			for i in sorted(sentencedic):
				print i,sentencedic[i].get("t","-"),sentencedic[i]
			print "))))))))))))))) at ",nodenum
		#try:
		l = [0]+sorted(sentencedic)[:nodenum-1]+sorted(intdic)+sorted(sentencedic)[nodenum:]
		if debug>2: print "lllll",l


		for i in sorted(intdic):

			sentencedic[i]=sentencedic[nodenum].copy() # l'ancien noeud qui va être virer est copier pour chaque ix
			for at in copiedfeatures:
				if at in intdic[i]:
					sentencedic[i][at]=intdic[i][at]
			sentencedic[i]['gov']=intdic[i].get('gov',{})

			if 'i0' in intdic[i].get('gov',{}).keys(): # found the gov: the one that has a root link
				sentencedic[i]['gov']=sentencedic[nodenum]['gov']
				intgov=i
			if "child" in intdic[i]: # found the child bearer
				intchi = i
				del intdic[i]['child']
		if not intgov:# if no governor is indicated, i guess it's the first word
			intgov="i1"
			if intgov in sentencedic: sentencedic[intgov]['gov']=sentencedic[nodenum]['gov']
		if not intchi: intchi=intgov

		# correct wrong gov links
		for i in sorted(sentencedic):
			if nodenum in sentencedic[i]['gov'].keys():
				sentencedic[i]['gov'][intchi]=sentencedic[i]['gov'][nodenum]
				del sentencedic[i]['gov'][nodenum]

		# bring all in a new list with new indeces based on l
		newsentencedic={}
		for newi,oldi in enumerate(l):
			if newi:# not 0
				newsentencedic[newi]=sentencedic[oldi]
				govdic={}
				for govi,dep in sentencedic[oldi]['gov'].iteritems():
					if govi>=0 and govi in l: govdic[l.index(govi)]=dep
				newsentencedic[newi]['gov']=govdic
				newsentencedic[newi]['id']=newi
				#print type(newsentencedic)


		if debug>2:
			print "result:((((((((((((("
			for i in sorted(newsentencedic):
				print i,newsentencedic[i].get("t",""),newsentencedic[i]
			print ")))))))))))))))"

		return newsentencedic


def addinfototree(tree, reset=True):
	"""
	add to each node:
	children: dico: childi -> func 
	govtags: dico: tag of governor --> [(govi,func), ...]
	"""
	if reset:
		for i,node in tree.items():
			tree[i]["children"]={}
			tree[i]["govtags"]={}
	
	
	rootindeces=[]

	for i,node in tree.items(): # getting some basic additional features: children and govtags
		tree[i]["children"]=tree[i].get("children",{})
		tree[i]["govtags"]={}
		
		for j,func in node["gov"].items():
			if j in tree: # in tree: has governor j
				tree[j]["children"]=tree[j].get("children",{})
				tree[j]["children"][i]=func
				tree[i]["govtags"][tree[j]["tag"]]=tree[i]["govtags"].get(tree[j]["tag"],[])+[ (j,func) ]
			else: # not in tree: roots
				rootindeces+=[i]
	return rootindeces

def fixOutname(name):
	if name.startswith("validated."): 
		name=name.split(".")[1]
		#name=name[len("validated."):]
	if name.endswith("lastHuman.conll"): name=name[:-len(".lastHuman.conll")]
	if name.endswith(".conll"): name=name[:-len(".conll")]
	return name

def createNonExistingFolders(path):
	head, tail = os.path.split(path)
	if head=="":
		if tail and not os.path.exists(tail): os.makedirs(tail)
	else:
		createNonExistingFolders(head)
	if head and not os.path.exists(head): os.makedirs(head)

def transform(infolder,outfolder,mixOldNew=True):
	createNonExistingFolders(outfolder)
	#for infile in sorted(glob.glob(os.path.join(infolder,"test.conll"))):
	for infile in sorted(glob.glob(os.path.join(infolder,"*.conll"))):
		basename=os.path.basename(infile)
		print "reading",basename
		trees = conll.conllFile2trees(infile)
		newtrees=[]
		for tree in trees:
			if mixOldNew: newtrees+=[tree]
			newtree=copy.deepcopy(tree)
			newtree=platinum(newtree)
			newtrees+=[newtree]
		conll.trees2conllFile(newtrees,os.path.join(outfolder,fixOutname(basename)))
		
			
transform("projects/OrfeoGold2016/export/","projects/OrfeoGold2016/platinum/",mixOldNew=False)		 
