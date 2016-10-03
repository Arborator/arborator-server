#! usr/bin/python
#! coding: utf-8

import codecs, re, copy, conll, glob, os
from num2words import num2words
from pprint import pprint

debug=False

droporfeo='/home/clover/Dropbox/Orfeo/' # where we can find the lexique folder
droporfeo='/home/kim/Dropbox/Orfeo/' # where we can find the lexique folder

def lireDictionnaires(dico,forme2cat,expressions_multimots):
	"""
	Lecture des fichiers du lexique
	Le dictionnaire se présente sous la forme {forme: (type, pos, lemme)}
	"""
	#print "Lecture du dictionnaire"
	
	#l = glob.glob("/home/clover/Dropbox/Orfeo//home/clover/Dropbox/Orfeo/lexique/*sfplm")  
	#print l
	for lexfile in [
		droporfeo+'lexique/INT.sfplm', 
		droporfeo+'lexique/COO.sfplm',
		droporfeo+'lexique/CLS.sfplm',  
		droporfeo+'lexique/CLN.sfplm',
		droporfeo+'lexique/CLI.sfplm', 
		droporfeo+'lexique/ADN.sfplm',
		droporfeo+'lexique/ADV.sfplm',
		droporfeo+'lexique/PRO.sfplm', 
		droporfeo+'lexique/PRQ.sfplm', 
		droporfeo+'lexique/CSU.sfplm',
		droporfeo+'lexique/VPR.sfplm', 
		droporfeo+'lexique/VPP.sfplm',
		droporfeo+'lexique/VNF.sfplm',  
		droporfeo+'lexique/VRB.sfplm.old',
		droporfeo+'lexique/PRE.sfplm',
		droporfeo+'lexique/DET.sfplm'
	]:
		# Lecture des fichiers .sfplm
		#if ".sfplm" in lexfile and "~" not in lexfile and not lexfile.endswith("ADVJA.sfplm") and not lexfile.endswith("VRB.sfplm.old"):

			# Ouverture d'un fichier de lexique
			with codecs.open(lexfile, "r", "utf8") as f:
				for ligne in f:
					if len(ligne) and "\t" in ligne:
						ligne = ligne.replace("\t\t","\t")
						ligne = ligne.replace(" \t","\t")
						ligne = ligne.replace("\t ","\t")
						
						#print ligne.strip()
						cols = ligne.split("\t")
						if len(cols)==5: deco,t,cat,lem,morph = cols
						elif len(cols)==6: deco,t,cat,lem,morph,_ = cols
						else:
							qsdf
						if lem[:2]=="s'":
							lem=lem[2:]
						elif lem[:3]=="se ":
							lem=lem[3:]
						#if (t,cat) in dico and dico[(t,cat)]!=(deco,lem):
							#print "déjà",(t,cat)
							#print dico[(t,cat)]
							#print "nouveau:",deco,t,cat,lem,morph
						dico[(t,cat)]=(deco,lem)
						
						forme2cat[t]=forme2cat.get(t,[])+[cat]
						
						if " " in t and deco not in ["S","P","X", "M", "MX"]: # Création d'une liste des expressions multimots
								expressions_multimots+=[ligne]
	#print "Fin de lecture du dictionnaire"

dico={} # (forme,pos) -> (decomposinfo,lemme)
forme2cat={} # forme -> [cats]
expressions_multimots=[]
lireDictionnaires(dico,forme2cat,expressions_multimots)

def dicoTiretsRhapsodie():
	dico={}
	trees=conll.conll2trees("mate/fr/Rhaps.gold.conll14")
	for arbre in trees:
		for i, node in arbre.iteritems():
			if node["t"][0]=="-":
				dico[node["t"]]=dico.get(node["t"], node["tag"])
	return dico

dico_clitiques=dicoTiretsRhapsodie()

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

def corrigerNumerotation(arbre):
	indexcorrection = {0:0} # ancien indice --> nouvel indice
	problem = False
	for compteur, ind in enumerate(sorted(arbre.keys())):
		indexcorrection[ind]=compteur+1
		if compteur+1 != ind:
			problem = True
	if problem:
		arbrecorrige = {}
		for i, node in arbre.iteritems():
			print"before", node["gov"]
			node["id"]=indexcorrection[i]
			newgov={}
			for gi,f in node["gov"].iteritems():
				newgov[indexcorrection[gi]]=f
			node["gov"]=newgov
			print "after",node["gov"]
			arbrecorrige[indexcorrection[i]]=node
		return arbrecorrige
	return arbre


def corrigerArbreCompos(arbre): # Décomposition des mots composés
	for i, node in arbre.iteritems():
		tok = node["t"]
		if node["tag"] != "NUM":
			#print (tok,node["tag"])
			if re.match("jusqu'.+",tok):
				tok = tok.replace("'", "' ")
			corrtype= dico.get( (node["t"],node["tag"]),"P")[0] # P comme pas trouvé
			if corrtype in ["S","P","X", "M", "MX"] and " " in tok:
				if corrtype in ["M", "X"]:
					nomFonc='MORPH'
				else:
					nomFonc="DEP"
				lem=node["lemma"]
				tag=node["tag"]
				arbIns = {}
				toksplit=tok.split()
				for ii,mot in enumerate(toksplit):
					if tok in ["de la", "de l'"]:
						nlem=dico.get((mot,forme2cat.get(mot,"?")[0]), "???")[1]
						ntag=forme2cat.get(mot,"?")[0]
						nnode={"lemma": nlem, "t":mot, 'id':'i1', 'tag':ntag, 'gov':{'i0':"SPE"}}
						node["gov"]={node["gov"].keys()[0]: "DEP"}
						#print node
					else:
						if mot !='A':
							nlem=dico.get((mot.lower(),forme2cat.get(mot.lower(),"?")[0]), "???")[1]
							ntag=forme2cat.get(mot.lower(),"?")[0]
						else:
							nlem=mot
							ntag='NOM'
						if ntag=='?' and nlem=='?':
							ntag=node['tag']
							nlem=mot.lower()
						nnode={"lemma": nlem, "t":mot, 'id':'i1', 'tag':ntag, 'gov':{'i0':nomFonc}}
					if ii==0:
						nnode['child']=None
					arbIns['i1']=nnode
				nouvelarb = splice(arbre,i,arbIns)
				nouvelarb=corrigerNumerotationSplice(nouvelarb)
				nouvelarb = corrigerArbreCompos(nouvelarb)
				return nouvelarb
	return arbre

def retoken(arbre):
	nouvelarb = copy.deepcopy(arbre)
	for i, node in arbre.iteritems():
		if node["gov"] == {}:
			node["gov"]={0:"!attention"}
		if (node["t"] == "est" and i+3 < len(arbre)) and (" ".join([arbre[x]["t"] for x in range(i,i+3)]) in ["est -ce que", "est -ce qu'"]):
			#print arbre
			#print i
			nouvelarb[i]["t"] = "est-ce "+arbre[i+2]["t"]
			nouvelarb[i]["gov"]={0:"root"}
			nouvelarb[i]["lemma"]= "est-ce que"
			nouvelarb[i]["tag"]= "CSU"
			nouvelarb = splice(nouvelarb, i+1, {})
			nouvelarb = splice(nouvelarb, i+1, {})
			#print nouvelarb
	if nouvelarb == {}:
		print arbre
	return nouvelarb

def corrigerNumerotationSplice(arbre, listeId=[]):
	if listeId:	newgovid=min(listeId)
	index={}
	node2tag={}
	for node in arbre.keys():
		index[arbre[node]["id"]]=node
		node2tag[arbre[node]["tag"]]=node2tag.get(arbre[node]["tag"], [])+[node]
	for i, node in arbre.iteritems():
		if node["gov"]=={}:
			if node["govtags"] == {}:
						node["gov"]={0:'ROOT'}
			else:
				govtag=node["govtags"].keys()[0]
				newgov= dict(node["govtags"].values()[0])
				if newgov.keys()[0] in listeId:
					#print newgov
					node["gov"]={newgovid:newgov.values()[0]}
					#print node["gov"]
				elif newgov.keys()[0] in index.keys():
					node["gov"]={index[newgov.keys()[0]]:newgov.values()[0]}
					if node["gov"].keys()[0] == i:
						node["gov"]={i-1:newgov.values()[0]}
				else:
					if govtag in node2tag.keys():
						for x in node2tag[govtag]:
							if newgov.keys()[0]-x <=2:
								node["gov"]={x:newgov.values()[0]}
					else:
						node['gov']={0:'root'}
	return arbre

def addinfototree(tree,deletePara=True):
	rootindeces=[]

	for i,node in tree.items(): # getting some basic additional features: children and govtags
		tree[i]["children"]=tree[i].get("children",[])
		tree[i]["govtags"]={}
		
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
				tree[i]["govtags"][tree[j]["tag"]]=tree[i]["govtags"].get(tree[j]["tag"],[])+[ (j,func) ]
			else: # not in tree: roots
				if [dep for g,dep in node["gov"].iteritems() if not dep.endswith("_inherited") and g!=j and dep!="attention"]:
					continue # we have other governors than the root node and inherited govs
				rootindeces+=[i]
	return rootindeces


def recomposerMultimots(arbre, expressions_multimots):
	nouvelarbre=copy.deepcopy(arbre)
	correspondance=False
	for ligne in expressions_multimots:
		motCompose = ligne.split("\t")
		token=motCompose[1]
		token = token.replace("-"," -")
		termesMotCompose = token.split()
		#print termesMotCompose
		length = len(termesMotCompose)
		for i, node in nouvelarbre.iteritems():
			if i+(length-1)<=len(nouvelarbre):
				if node["t"] == termesMotCompose[0]:
					index=i
					if " ".join([nouvelarbre[i+x]["t"] for x in range(length)]) == token:
						#try:
						node["t"]=token.replace(" -", "-")
						node["lemma"]=motCompose[3]
						node["tag"]=motCompose[2]
						#print node["gov"], i
						if node["gov"].keys()[0] >i:
							for c in range(length):
								#print "  ", arbre[i+c]["gov"].keys()[0], i+c
								if arbre[i+c]["gov"].keys()[0] not in [x for x in range(i, i+c+1)]:
									node["gov"]=arbre[i+c]["gov"]
									#print "    ", node["gov"]
						listeId=[]
						for x in range(1,length):
							listeId += [i+x]
						#print listeId
						for indice in listeId:
							#print indice # On supprime les children des termes s'il sont dans l'expression
							if node["gov"].keys() not in listeId: # S'il y a des children
								nouvelarbre=splice(nouvelarbre, i+1, {})
							#print i, x, " ".join([node["t"] for i, node in nouvelarbre.iteritems()])
						copielisteId=listeId+[i]
						nouvelarbre=corrigerNumerotationSplice(nouvelarbre, copielisteId)
						listeId=[]
						
						nouvelarbre=recomposerMultimots(nouvelarbre, expressions_multimots)
						
	return nouvelarbre



def digits(arbre, digitsandnumbers):
	for i, node in arbre.iteritems():
		for number in digitsandnumbers:
			if number == node["t"] or number+"~" == node["t"]:
				node["lemma"] = node["t"]
				node["tag"]= "NUM"
				node["tag2"]="NUM"
	return arbre

def corrigerSegmentationClitiques(arbre, dico_clitiques):
	nouvelarb=copy.deepcopy(arbre)
	#print "before", len(arbre)
	for clitique in dico_clitiques.keys():
		for i, node in arbre.iteritems():
			if clitique in node["t"] and "#" not in node["t"]:
				#print "\n\n****",clitique
				arbIns={}
				nnode={"lemma": clitique[1:], "t":clitique, 'id':'i'+str(i+1), 'tag':dico_clitiques[clitique], 'gov':{'i1':"dep"}}
				verbe={"lemma": node["lemma"][:-len(clitique)], "t":node["t"][:-len(clitique)], 'id':'i1', 'tag':node["tag"], 'gov':node["gov"]}
				arbIns={ 'i1':verbe,'i2':nnode}
				#print arbIns
				nouvelarb = splice(nouvelarb,i,arbIns)
				nouvelarb=corrigerNumerotationSplice(nouvelarb)
				nouvelarb = corrigerArbreCompos(nouvelarb)
				#print arbre
				#print 
				#print nouvelarb
				#print "___"
				#qsdf
				"""
				probleme avec dernier arbre composé de jeanne mallet (A DEBUG)
				"""
	return nouvelarb

def nombresComposes(arbre):
	for i,node in arbre.iteritems():
		if re.match(ur"[0-9]+$", node["t"]):
			#print node["t"], i
			if node["t"]== u"000":
				node["t"]="1000"
			node["t"]= num2words(int(node["t"]), lang='fr')
			#print node["t"]
			arbre = nombresComposes(arbre)
	return arbre

def corrigerInaudibles(arbre):
	for i, node in arbre.iteritems():
		if node["t"].endswith("-~"):
			#print node["t"]
			node["t"]=node["t"][:-2]+"~"
			node["lemma"]= node["t"]
		elif node["t"].endswith("-"):
			#print node["t"]
			node["t"]=node["t"][:-1]+"~"
			node["lemma"]= node["t"]
	return arbre

def corrigerClitiques(arbre):
	for i, node in arbre.iteritems():
		if node["t"] in ["nous","vous"]:
			if node["gov"].values()[0] == "suj":
				node["tag"]= "CLS"
			elif node["gov"].values()[0] == "comp":
				node["tag"] = "CLI"
			else:
				node["tag"]="PRO"
		elif node["t"] == "elle":
			if node["gov"].values()[0] == "suj":
				node["tag"] = "CLS"
			else:
				node["tag"]="PRO"
		elif node["t"] == "il":
			if node["gov"].values()[0] == "comp":
				node["tag"] = "CLI"
			else:
				node["tag"]="PRO"
		if re.match(ur"[A-Z]", node["t"]) and not re.match(ur"[A-Z]", node["lemma"]):
			node["lemma"]=node["t"]
		if node["t"] == "NNAAMMEE":
			node["lemma"]= "_"
	return arbre

def retokeniser(nomdufichier, path="",addtoout=""):
	if not path: path,_= os.path.split(nomdufichier) # take the same path as the nomdufichier
	if path:
		if path[-1]!="/": path=path+"/"		
	trees = conll.conll2trees(nomdufichier) # on lit le fichier
	print "le fichier",nomdufichier,"a",len(trees),"arbres"
	#newtrees, alltrees=[], []
	newtrees=[]
	digitsandnumbers=codecs.open(droporfeo+"lexique/gg", "r", "utf-8").read().split('\n')
	for i, arbre in enumerate(trees): # on boucle sur les arbres
		#alltrees+=[copy.deepcopy(arbre)]
		#oldtree=copy.deepcopy(arbre)
		racines = addinfototree(arbre)
		oldtree=copy.deepcopy(arbre)
		arbre = corrigerNumerotation(arbre)
		arbre = nombresComposes(arbre)
		arbre = digits(arbre, digitsandnumbers)
		arbre=corrigerArbreCompos(arbre) # Décomposition des expressions multimots
		#for i, node in arbre.items(): # Reconfiguration des enfants
			#if node["gov"] == {}:
			#print "crap"

		arbre=recomposerMultimots(arbre, expressions_multimots)
		arbre=corrigerNumerotationSplice(arbre)

		arbre=corrigerSegmentationClitiques(arbre, dico_clitiques)
		arbre=corrigerInaudibles(arbre)
		arbre=corrigerClitiques(arbre)
		arbre= retoken(arbre)
		#if arbre!=oldtree:
			#print i
			#for ii in arbre:
				#if arbre[ii]!=oldtree.get(ii,None):
					#print ii,arbre[ii]['t'],arbre[ii],oldtree.get(ii,None)
		newtrees.append(arbre)
	newname=path+os.path.basename(nomdufichier+addtoout)
	conll.trees2conll10(newtrees, newname, columns=10)
	return newname

def segmentationChiffres(arbre):
	for i,node in arbre.iteritems():
		if node["tag"] == "NUM" and " " in node["t"]:
			toksplit=node["t"].split()
			for ii,mot in enumerate(toksplit):
				nlem=mot
				ntag="NUM"
				nnode={"lemma": nlem, "t":mot, 'id':'i1', 'tag':ntag, 'gov':{'i0':nomFonc}}
				if ii==0:
					nnode['child']=None
				arbIns['i1']=nnode
				nouvelarb = splice(arbre,i,arbIns)
				nouvelarb=corrigerNumerotationSplice(nouvelarb)
				nouvelarb = corrigerArbreCompos(nouvelarb)
				return nouvelarb
	return arbre

def retokenizeTree(arbre):
	for i,node in arbre.iteritems():
		if "gov" not in arbre[i]:
			arbre[i]["gov"]={0:"!attention"}

	racines = addinfototree(arbre)
	#print racines
	arbre = corrigerNumerotation(arbre)
	arbre = nombresComposes(arbre)
	arbre = digits(arbre, digitsandnumbers)
	arbre=corrigerArbreCompos(arbre) # Décomposition des expressions multimots
	#for i, node in arbre.items(): # Reconfiguration des enfants
		#if node["gov"] == {}:
		#print "crap"

	arbre=recomposerMultimots(arbre, expressions_multimots)
	arbre=corrigerNumerotationSplice(arbre)

	arbre=corrigerSegmentationClitiques(arbre, dico_clitiques)
	arbre=corrigerInaudibles(arbre)
	arbre=corrigerClitiques(arbre)
	arbre= retoken(arbre)

	for i,node in arbre.iteritems():
		del node["govtags"]
		del node["children"]

	return arbre

if __name__ == "__main__":
	path="mate/parses/"
	try:
		os.mkdir(path)
	except OSError:
		pass
	retokeniser("./mate/test_200816.conll", path)
	#retokeniser("./mate/parses/test/test.conll", path)
	"""for infile in glob.glob("mate/parses/originals/*.orfeo"):
					print infile
					retokeniser(infile, path)
					kjbk"""
	#conll.trees2conll10(alltrees, "mate/parses/Tscha_cha_reu_ass_08.trs.lif.w+p.orfeo"+".conll10")