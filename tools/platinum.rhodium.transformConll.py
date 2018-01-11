#! usr/bin/python
#! coding: utf-8

import datetime, codecs, time, sys, os, glob, copy
sys.path.insert(0, '../lib')
import conll

debug=3
debug=False


def NNAAMMEE(tree):
	"""
	NNAAMMEE -> XXX
	"""
	for i, node in tree.iteritems():
		if node["t"]=="XXX":
			node["t"]="YYY"
			node["lemma"]="YYY"
		elif node["t"]=="NNAAMMEE":
			node["t"]="XXX"
			node["lemma"]="XXX"
	return tree


def removeTag2(tree):
	for i, node in tree.iteritems():
		del node["tag2"]
	

def emptyErrors(tree):
	for i, node in tree.iteritems():
		if node["t"]=="":
			if not node["gov"]: 
				pass
				#pprint(tree)
				#print i,node
				#print "_______________"
				
			else:
				gi,gf = node["gov"].items()[0]
				for ci,cf in node["children"].iteritems():#normalement un seul enfant
					cnode=tree[ci]
					cnode["gov"]={gi:gf}
			tree=splice(tree,i,{})
			addinfototree(tree)
			tree=emptyErrors(tree)
			break
			#print i, "removed empty node in"
			#pprint(tree)
	return tree
	
def kesk(tree):
	for i, node in tree.iteritems():
		if node["lemma"]=="est-ce":
			gi,gf = node["gov"].items()[0]
			if gi in tree and tree[gi]["lemma"]=="que": # qu'est-ce que
				govnode=tree[gi]
				#print
				#print i-1,tree[i-1]["t"],govnode
				#print i,tree[i]["t"],node
				#print i+1,tree[i+1]["t"], tree[i+1]
				#print i+2,tree[i+2]["t"], tree[i+2]
				#print "_______________"
				
				gov={}
				for ii in [i-1,i,i+1]: # for each node of qu'est-ce que
					ggnode=tree[ii]
					for ggi,ggf in ggnode["gov"].iteritems(): # collect each exterior governor
						if ggi<i-1 or i+1<ggi:
							gov[ggi]=ggf
					for ci,cf in ggnode["children"].iteritems():# change each exterior kid
						if ci<i-1 or i+1<ci:
							cnode=tree[ci]
							cnode["gov"]={gi:cf}
				if i+2 in tree and tree[i+2]["lemma"][0] in "aeiouy" and tree[i+2]["lemma"] not in ["euh","est-ce",u"est-ce que",u"est-ce-que"]:
					t=u"qu'est-ce qu'"
					#pprint(tree)
					#print i
					#if  tree[i+2]["lemma"] not in ["on","un"] : azer
				else:
					t=u"qu'est-ce que"
				tree[gi]={'lemma': u"qu'est-ce que", 'tag': u'CSU', 't':t , 'gov': gov, 'id': gi}
				tree=splice(tree,i,{})
				tree=splice(tree,i,{})
				addinfototree(tree)
				tree=kesk(tree)
				break
				#print "***"
				#pprint(tree)
			else: 
				#print
				##print i-1,tree[i-1]["t"],govnode
				#print i,tree[i]["t"],node
				#print i+1,tree[i+1]["t"], tree[i+1]
				#print i+2,tree[i+2]["t"], tree[i+2]
				#print "_______________"
				gov={}
				for ii in [i,i+1]: # for each node of est-ce que
					ggnode=tree[ii]
					for ggi,ggf in ggnode["gov"].iteritems(): # collect each exterior governor
						if ggi<i or i+1<ggi:
							gov[ggi]=ggf
					for ci,cf in ggnode["children"].iteritems():# change each exterior kid
						if ci<i or i+1<ci:
							cnode=tree[ci]
							cnode["gov"]={i:cf}
				if i+2 in tree and tree[i+2]["lemma"][0] in "aeiouy" and tree[i+2]["lemma"] not in ["euh","est-ce",u"est-ce que",u"est-ce-que"]:
					t=u"est-ce qu'"
					#pprint(tree)
					#print i
					#if  tree[i+2]["lemma"] not in ["on","un"] : qsdf
				else:
					t=u"est-ce que"
				tree[i]={'lemma': u"est-ce que", 'tag': u'CSU', 't':t , 'gov': gov, 'id': gi}
				tree=splice(tree,i+1,{})
				addinfototree(tree)
				tree=kesk(tree)
				break
	return tree


def rendezvous(tree):
	#z=False
	for i, node in tree.iteritems():
		if node["lemma"]=="rendez-vous" and i+1 in tree and tree[i+1]["t"]=="-vous":
			node["t"]="rendez-vous"
			tree=splice(tree,i+1,{})
			addinfototree(tree)
			#pprint(tree)
			#print "******"
			tree=rendezvous(tree)
			#z=True
			break
	#if z:
		#print "mmmmm"
		#pprint(tree)
		#print "nnnnnnnnnnnnn"
	return tree
		
def cls(tree):
	for i, node in tree.iteritems():
		if node["tag"]=="CLS":
			gi,gf = node["gov"].items()[0]
			if gi in tree and tree[gi]["tag"]!="VRB" and gf not in ["para","disflink"]: # CLS whose governor is not a verb
				govnode=tree[gi]
				
				#pprint(tree)
				#print "******",i
			
			
	return tree


def desEnTete(tree):
	"""
	des est toujours tête comme une préposition
	"""
	for i, node in tree.iteritems():
		if node["tag"] == "DET" and node["t"] in ["des", "du", "de", "d'"]:
			if node["gov"]:
				govid = node["gov"].keys()[0]
				if govid in tree:
					govnode=tree[govid]
					if govnode["gov"]:
						ggovid = govnode["gov"].keys()[0]
						node["gov"]={ggovid:govnode.get("gov",{}).get(ggovid,0)}
						govnode["gov"]={i:"dep"}
		node["tag"] == "PRE"			
	return tree


#V disfl-> des à -->  comp
#V disfl->  "du", "de", "d'" --> comp
#V disfl-> 

def auxEnTete(tree):
	"""
	aux est la tête
	"""
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["aux"] and node["gov"].keys()[0]>i: # found a node that is a dependent aux
			#print "found a node that is a dependent aux",i,node
			gi = node["gov"].keys()[0]
			gnode=tree[gi]
			if gnode["gov"] and gnode["gov"].values()[0] in ["aux"] and gnode["gov"].keys()[0]>gi: # found a double aux
				#print "found a double aux",gi,node
				ggi = gnode["gov"].keys()[0]
				ggnode=tree[ggi]
				for ci,cf in ggnode["children"].iteritems():
					if cf in ["suj","periph","insert","mark"]: # toutes ces fonctions montent sur 
						cnode=tree[ci]
						cnode["gov"]={i:cf}
					elif cf=="dm" and ci<i: # dm seulement quand ils sont à gauche de l'auxiliaire
						cnode=tree[ci]	
						cnode["gov"]={i:"dm"}
					elif cf=="ad":
						cnode=tree[ci]
						if cnode["t"] in ["ne","n'"]:
							cnode["gov"]={i:cf}
				node["gov"]=ggnode["gov"].copy() 
				gnode["gov"]={i:"aux"}
				ggnode["gov"]={gi:"aux"}
			else: # only simple aux
				for ci,cf in gnode["children"].iteritems():
					if cf in ["suj","periph","insert","mark"]: # toutes ces fonctions montent sur 
						cnode=tree[ci]
						cnode["gov"]={i:cf}
					elif cf=="dm" and ci<i: # dm seulement quand ils sont à gauche de l'auxiliaire
						cnode=tree[ci]	
						cnode["gov"]={i:"dm"}
					elif cf=="ad":
						cnode=tree[ci]
						if cnode["t"] in ["ne","n'"]:
							cnode["gov"]={i:cf}
				node["gov"]=gnode["gov"].copy()
				gnode["gov"]={i:"aux"}
			
			addinfototree(tree)
	return  tree		
			#pprint(tree)
			
from searchConll import  hasEmptyNode
			
def platinum(tree):
	removeTag2(tree)
	addinfototree(tree)
	tree=auxEnTete(tree)
	tree=desEnTete(tree)
	tree=NNAAMMEE(tree)

	tree=emptyErrors(tree)
	if hasEmptyNode(tree):
		print tree
		qsdf
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

	
def correcttree2nodedic(tree,catname="cat"):
		""" 
		takes the conll string representation of a single tree and creates a dictionary for it
		here special format: spacelemmas
		"""
	
		nodedic={}
		for line in tree.split('\n'):
			line=line.strip()
			
			#print "___",line
			if line:
				cells = line.split('\t')
				nrCells = len(cells)
				if nrCells in [6,7]:
					if nrCells == 6:
						nr, t, lemma, tag, head, rel = cells
						#nr,head = int(nr), int(head)
						if int(head)>=0:nodedic['i'+nr]={'id':'i'+nr,"t": t,'lemma': lemma, catname: tag, 'gov':{'i'+head: rel} }
						else:nodedic['i'+nr]={'id':'i'+nr,"t": t,'lemma': lemma, catname: tag, 'gov':{} }
					elif nrCells == 7:
						nr, t, lemma, tag, head, rel, child = cells
						
						#nr,head = int(nr), int(head)
						#if lemma2!="_": lemma=lemma2 # TODO: find out what the difference between these colons is!!!!!!
						if int(head)>=0:nodedic['i'+nr]={'id':'i'+nr,"t": t,'lemma': lemma, catname: tag, 'gov':{'i'+head: rel} }
						else:nodedic['i'+nr]={'id':'i'+nr,"t": t,'lemma': lemma, catname: tag, 'gov':{} }
						
						
						if child.strip()=="-":
							nodedic['i'+nr]["child"]=True
						else:
							print child,cells,"--- strange line:"
							print line
				else:
					print "strange line"
					print line
					print "in:"
					print tree
			
					
		return nodedic
	
	
def correctionDics(correctionfilename):
	
	if debug: print "reading the correction file",correctionfilename
	corrf=codecs.open(correctionfilename,"r","utf-8")
			
	corrlist=[]
	#currtoken=None
	currdic={}
	currconlltree=""
	
	for line in corrf:
		line=line.split("#")[0] # comments
		#if (line.strip()+" ")[0]!="#":
		if line.strip():
			#if "#" in line: 
			if currdic: # second or further line of a block
				if line.startswith("<-"):
					corrlist+=[(currdic,-1)]
					currconlltree=""
					currdic={}
				elif line.startswith("->"):
					#gluedic[currtoken]=1
					corrlist+=[(currdic,1)]
					currconlltree=""
					currdic={}
				else:
					currconlltree+=line
			else: # first line of a block
				trucs=line.split("\t")
				if len(trucs)>3:
					_,currtoken,currlemma,currcat=trucs[:4] # [0].strip()
					currdic={}
					for (a,v) in [("t",currtoken),("lemma",currlemma),("cat",currcat)]:
						v=v.strip()
						if v: currdic[a]=v
					
				else:
					print "strange line:",line
					currconlltree=""
					currdic={}	
		else: # empty line
			if currconlltree.strip():
				corrlist+=[(currdic,correcttree2nodedic(currconlltree))]
				#corrdic[currtoken]=correcttree2nodedic(currconlltree)			
			
			currconlltree=""
			currdic={}		
	if debug:
		for matchdic,insdic in corrlist:
			print matchdic
			if isinstance(insdic, int):
				print insdic
			else:
			
				for i in sorted(insdic):
					print i,insdic[i]
			print "_______________"
	
			
	return corrlist
	


def findSpaces(spaceDic, tree, spc=" '-"):
	for i,node in tree.items():
		for s in spc:
			if s in node["t"] or s in node["lemma"]:
				spaceDic[node["lemma"]]=spaceDic.get(node["lemma"],0)+1


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
	spaceToks={}
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
			
			findSpaces(spaceToks,tree)
			
		conll.trees2conllFile(newtrees,os.path.join(outfolder,fixOutname(basename)))
	
	
	#corrdic = correctionDics("corrConll.txt")
	#for c in corrdic:
		#print c
	#qsdf
	for i,tok in enumerate(sorted(spaceToks)):
		print i,tok,spaceToks[tok]
		
		
	
transform("projects/OrfeoGold2016/export/","projects/OrfeoGold2016/platinum/",mixOldNew=False)		 
