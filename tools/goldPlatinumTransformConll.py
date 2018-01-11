#! usr/bin/python
#! coding: utf-8

import datetime, codecs, time, sys, os, glob, copy
sys.path.insert(0, '../lib')
import conll
from searchConll import  hasEmptyNode, searches

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

def cela(tree):
	"""
	ça: lemme = ça
	"""
	for i, node in tree.iteritems():
		if node["t"]==u"ça":
			node["lemma"]=u"ça"
	return tree

def tapostrophe(tree):
	"""
	t' CLS à changer en CLI + lemme = te
	"""
	for i, node in tree.iteritems():
		if node["t"]==u"t'":
			node["lemma"]="te"
			node["tag"]="CLI"
	return tree



def sujEnSubj(tree):
	"""
	suj -> subj
	"""
	for i, node in tree.iteritems():
		for gi,gf in node["gov"].iteritems():
			if gf=="suj": tree[i]["gov"][gi]="subj"
	addinfototree(tree)
	return tree


def removeTag2(tree):
	for i, node in tree.iteritems():
		if "tag2" in node:
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
	"""
	correct segmentation horrors
	"""
	for i, node in tree.iteritems():
		if node["lemma"]=="est-ce":
			gi,gf = node["gov"].items()[0]
			if gi in tree and tree[gi]["lemma"]=="que": # qu'est-ce que
				govnode=tree[gi]
							
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
				tree[gi]={'lemma': u"qu'est-ce que", 'tag': u'PRQ', 't':t , 'gov': gov, 'id': gi}
				tree=splice(tree,i,{})
				tree=splice(tree,i,{})
				addinfototree(tree)
				tree=kesk(tree)
				break
				#print "***"
				#pprint(tree)
			else: 
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
			
		elif node["lemma"]=="qu'est-ce" and i+3 in tree:
			
			nnode = tree[i+1]
			nnnode = tree[i+2]
			if nnode["lemma"]=="ce" and  nnnode["lemma"]=="que":
				
				if tree[i+3]["lemma"][0] in "aeiouy" and tree[i+3]["lemma"] not in ["euh","est-ce",u"est-ce que",u"est-ce-que"]:
					t=u"qu'est-ce qu'"
				else:
					t=u"qu'est-ce que"
				node["t"]=t
				node["lemma"]=u"qu'est-ce que"
				node["tag"]=u"PRQ"
				tree=splice(tree,i+1,{})
				tree=splice(tree,i+1,{})
				addinfototree(tree)
				tree=kesk(tree)
				break
			
		elif node["lemma"]=="est-ce que" and i-1 in tree:
			qnode = tree[i-1]
			if qnode["lemma"]=="que":
				qnode["lemma"]="qu'est-ce que"
				if qnode["t"] in ["est-ce que", "est-ce qu'"]:
					qnode["t"]="qu'"+qnode["t"] # pour garder l'info qu' ou que
				elif i+1 in tree and tree[i+1]["lemma"][0] in "aeiouy" and tree[i+1]["lemma"] not in ["euh","est-ce",u"est-ce que",u"est-ce-que"]:
					qnode["t"]="qu'est-ce qu'"
				else:
					qnode["t"]="qu'est-ce que"
				tree=splice(tree,i,{})
				addinfototree(tree)
				#pprint(tree)
				
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

def pasgrandchose(tree):
	"""
	X -rrr-> pas grand-chose PRO
	en
	X -ad-> pas ADN lemme: pas
	X -rrr-> pas grand-chose PRO lemme:grand-chose
	
	et si on avait
	dit souvent pas grand-chose
	??
	"""
	for i, node in tree.iteritems():
		if node["lemma"]=="pas grand-chose" and node["gov"] and node["gov"].keys()[0] in tree:
			gi = node["gov"].keys()[0]
			gnode=tree[gi]
			#pprint(tree)
			#print
			node["lemma"]="grand-chose"
			node["t"]="grand-chose"
			i1= gnode.copy()
			i1.update({'child':None})
			i3=node.copy()
			i3.update({'gov': {'i1': node["gov"].values()[0]}})
			chis=i3["children"]
			tree=splice(tree,i,{})
			tree=splice(tree,gi,
			{
				'i1':i1,
				'i2':{u'tag': u'ADN', u'lemma': u'pas', u't': u'pas', 'gov': {'i1': u'ad'}},
				'i3':i3
			})
			for chi in chis:
				tree[chi]["gov"]={gi+2:tree[chi]["gov"].values()[0]}
			addinfototree(tree)
			#pprint(tree)
			#print "******"
			tree=pasgrandchose(tree)
			break
	
	return tree




def cestadire(tree):
	"""
	c' + est-à-dire : un seul token COO
	"""
	for i, node in tree.iteritems():
		if node["t"]=="c'" and i+1 in tree and (tree[i+1]["t"]==u"est-à-dire" or tree[i+1]["t"]==u"est à dire"):
			for ci,cf in tree[i+1]["children"].iteritems():
				tree[ci]["gov"]={i:cf}
			node["t"]=u"c'est-à-dire"
			node["lemma"]=u"c'est-à-dire"
			node["tag"]=u"COO"
			tree=splice(tree,i+1,{})
			addinfototree(tree)
			tree=cestadire(tree)
			break
		if node["t"]==u"est-à-dire":
			node["tag"]="COO"
	return tree

		
def prons(tree):
	"""
	je|tu|il|ils|on -> CLS
	elle|elles|nous|vous ce qui sont suj -> CLS
	si "ce" a un dep VRB alors ce -> PRO
	si un cls est dep d'une préposition -> PRO
	tous les CLI dep autre que "y" doivent être comp
	"""
	for i, node in tree.iteritems():
		if node["lemma"] in "je tu il ils on".split():
			node["tag"]="CLS"
		if node["lemma"] in "elle elles nous vous ce".split() and "subj" in node["gov"].values():
			node["tag"]="CLS"
		if node["lemma"] == "ce" and "VRB" in [tree[ci]["tag"] for ci in node["children"]]:
			node["tag"]="PRO"
		if node["tag"] == "CLS" and "dep" in node["gov"].values() and "PRE" in node["govtags"]:
			node["tag"]="PRO"
			addinfototree(tree)
		if node["tag"] == "CLI" and "dep" in node["gov"].values() and node["t"]!="y":
			node["gov"]={node["gov"].keys()[0]:"comp"}
			addinfototree(tree)
	return tree	

def disflink(tree):

	"""
	si une PRE est disflink et n'a pas de dépendant,
	disflink -> ad si le gouv est un VRB|VNF|VPP
	disflink -> dep sinon (sauf si le gouv est dm ou mark)
	on peut éventuellement faire la même règle pour les DET
	
	tout disflink entre entre prep et nom est en fait une dép
	"""
	for i, node in tree.iteritems():
		if node["tag"]in ["PRE","DET"] and "disflink" in node["gov"].values():
			if "VRB" in node["govtags"] or "VNF" in node["govtags"] or "VPP" in node["govtags"]:
				node["gov"]={node["gov"].keys()[0]:"ad"}
			else:
				node["gov"]={node["gov"].keys()[0]:"dep"}
		elif node["tag"]in ["NOM"] and "disflink" in node["gov"].values() and "PRE" in node["govtags"]:
			node["gov"]={node["gov"].keys()[0]:"dep"}
	return tree

def vrb(tree):
	"""
	dit|dites|fait|faites|écrit avec un suj -> VRB
	dites|faites qui est root -> VRB
	"""
	for i, node in tree.iteritems():
		if node["t"] in u"dit dites fait faites écrit".split() and "subj" in node["children"].values():
			node["tag"]="VRB"
		if node["t"] in "dites faites".split() and 0 in node["gov"]:
			node["tag"]="VRB"
		
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
		if node["gov"] and node["gov"].values()[0] in ["aux"] and node["gov"].keys()[0]>i: # found an aux
			#print "found a node that is a dependent aux",i,node
			gi = node["gov"].keys()[0]
			gnode=tree[gi]
			if gnode["gov"] and gnode["gov"].values()[0] in ["aux"] and gnode["gov"].keys()[0]>gi: # found a double aux
				#print "found a double aux",gi,node
				ggi = gnode["gov"].keys()[0]
				ggnode=tree[ggi]
				for ci,cf in ggnode["children"].iteritems():
					if cf in ["subj","periph","insert","mark"]: # toutes ces fonctions montent sur 
						cnode=tree[ci]
						cnode["gov"]={i:cf}
					elif cf=="dm" and ci<i: # dm seulement quand ils sont à gauche de l'auxiliaire
						cnode=tree[ci]	
						cnode["gov"]={i:cf}
					elif cf=="ad":
						cnode=tree[ci]
						if cnode["t"] in ["ne","n'"]:
							cnode["gov"]={i:cf}
				node["gov"]=ggnode["gov"].copy() 
				gnode["gov"]={i:"aux"}
				ggnode["gov"]={gi:"aux"}
			else: # only simple aux
				#print node
				for ci,cf in gnode["children"].iteritems(): # look at all the siblings of the aux
					if cf in ["subj","periph","insert","mark"]: # toutes ces fonctions montent sur l'auxiliaire
						cnode=tree[ci]
						cnode["gov"]={i:cf}
					elif cf=="dm" and ci<i: # dm seulement quand ils sont à gauche de l'auxiliaire
						cnode=tree[ci]	
						cnode["gov"]={i:cf}
					elif cf=="ad":
						cnode=tree[ci]
						if cnode["t"] in ["ne","n'"]:
							cnode["gov"]={i:cf}
				node["gov"]=gnode["gov"].copy()
				gnode["gov"]={i:"aux"}
				#print node
				#pprint(tree)
				#qsdf
			addinfototree(tree)
	return  tree		
			#pprint(tree)
			

def auxpara(tree):
	"""
	#si X-para-> Y et X-aux-> Z, alors Y-aux-> Z
	"""
	for i, node in tree.iteritems():
		if "para" in node["children"].values() and "aux" in node["children"].values():
			yparai=[ci for ci in node["children"] if node["children"][ci]=="para"][0]
			zauxi =[ci for ci in node["children"] if node["children"][ci]=="aux" ][0]
			tree[zauxi]["gov"]={yparai:"aux"}
			addinfototree(tree)
			#pprint(tree)
			#qsdf
	return  tree	

def adperiph(tree):
	"""
	1) si X <-ad|comp- Y et il y a un Z suj tel que X < Z < Y, alors X <-periph- Y
	"""
	for i, node in tree.iteritems():
		if ("ad" in node["children"].values() or "comp" in node["children"].values()) and "suj" in node["children"].values():
			zsubji =[ci for ci in node["children"] if node["children"][ci]=="suj" ][0]
			for xadci in [ci for ci in node["children"] if node["children"][ci] in ["ad","comp"]]:
				if xadci<zsubji<i:
					tree[xadci]["gov"]={i:"periph"}
					addinfototree(tree)
	return  tree	

def montperiph(tree):
	"""
	2) (à appliquer ensuite) si X <-periph- Y et W-aux-> Y, alors  X <-periph- Y	
	"""
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["periph"]:
			ygi = node["gov"].keys()[0]
			ygnode=tree[ygi]
			if ygnode["gov"] and ygnode["gov"].values()[0] in ["aux"]:
				wggi=ygnode["gov"].keys()[0]
				node["gov"]={wggi:"periph"}
				addinfototree(tree)
	return  tree

def rootperiph(tree):
	"""
	beaucoup de periph qui se balladent
	si un periph a 0 comme gouv, lui attribuer le nœud root comme gouv

	"""
	for i, node in tree.iteritems():
		if node["gov"] and 0 in node["gov"] and  node["gov"][0] == "periph":
			for j, rnode in tree.iteritems():
				if rnode["gov"] and 0 in rnode["gov"] and  rnode["gov"][0] == "root":
					node["gov"]={j:"periph"}
					break 
				
	return  tree	


def affcomp(tree):
	"""
	tout aff devient comp

	"""
	for i, node in tree.iteritems():
		if node["gov"]:
			for govi, func in node["gov"].iteritems():
				if func=="aff":
					node["gov"][govi]="comp"				
				
	return  tree	

def csuperiph(tree):
	"""
	autre pb avec les periph : si X est un periph qui dépend d'un CSU, X doit dépendre du VRB dépendant de la CSU
	ct faux !
	meilleure version
	si Y est CSU et Y-periph-> X et Y n'est pas root, alors X <-periph- Z <-dep - Y
	"""
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["periph"] and "CSU" in node["govtags"]:
			csui,f=node["govtags"]["CSU"][0]
			csunode=tree[csui]
			if "root" not in csunode["gov"].values():
				cis=[ci for ci in csunode["children"] if tree[ci]["tag"][0]=="V"]
				if cis:
					vi=cis[0]
					node["gov"]={vi:"periph"}
					addinfototree(tree)
					#pprint( tree)
				
				
	return  tree	


		
		

def pprint(tree):
	for i in tree:
		print i, tree[i]["t"],tree[i]
	print
	
def corrigerNumerotation(arbre):
	indexcorrection = {0:0} # ancien indice --> nouvel indice
	problem = False
	for compteur, ind in enumerate(sorted(arbre.keys())):
		indexcorrection[ind]=compteur+1
		if compteur+1 != ind:
			problem = True
	if problem:
		print indexcorrection
		pprint(arbre)
		arbrecorrige = {}
		for i, node in arbre.iteritems():
			node["id"]=indexcorrection[i]
			newgov={}
			for gi,f in node["gov"].iteritems():
				newgov[indexcorrection[gi]]=f
			node["gov"]=newgov
			arbrecorrige[indexcorrection[i]]=node
		return arbrecorrige
	else:
		return arbre

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

			sentencedic[i]=sentencedic[nodenum].copy() # l'ancien noeud qui va être viré et copié pour chaque ix
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
	tree=corrigerNumerotation(tree)
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


def platinum(tree):
	removeTag2(tree)
	addinfototree(tree)
	#pprint (tree)
	
	tree=NNAAMMEE(tree)
	tree=cela(tree)
	tree=tapostrophe(tree)
	tree=sujEnSubj(tree)
	
	

	tree=emptyErrors(tree)
	if hasEmptyNode(tree): # testing whether all empty nodes have been removed
		print tree
		qsdf
	tree=kesk(tree)
	tree=rendezvous(tree)
	tree=pasgrandchose(tree)
	
	tree=auxEnTete(tree)
	tree=auxpara(tree)
	#print "after aux:"
	#pprint (tree)
	tree=desEnTete(tree)
	tree=adperiph(tree)
	#print "before aux:"
	#pprint (tree)
	tree=montperiph(tree)
	#print "after montperiph:"
	#pprint (tree)
	tree=rootperiph(tree)
	#pprint (tree)
	tree=csuperiph(tree)
	
	
	tree=prons(tree)
	tree=disflink(tree)
	tree=vrb(tree)
	tree=cestadire(tree)
	tree=kesk(tree)
	tree=affcomp(tree)
	
	#pprint (tree)
	
	return tree


def directDatabaseChangeForForgottenCorrection():
	from database import SQL
	sql=SQL("Platinum")
	db,cursor=sql.open()
	cursor.execute('update links set function="comp" where function="aff";')
	db.commit()	
	db.close()
	print "changed"



def transform(infolder,outfolder,mixOldNew=True):
	createNonExistingFolders(outfolder)
	spaceToks={}
	#for infile in sorted(glob.glob(os.path.join(infolder,"test.conll"))):
	for infile in sorted(glob.glob(os.path.join(infolder,"*.conll"))):
		if not os.path.isfile(infile): continue
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
	
	
		
if __name__ == "__main__":

	transform("../projects/OrfeoGold2016/export/","../projects/OrfeoGold2016/platinum/",mixOldNew=False)		 
	#searches()
	#directDatabaseChangeForForgottenCorrection()
