#! usr/bin/python
#! coding: utf-8

import datetime, codecs, time, sys, os, glob
sys.path.insert(0, '../lib')
import conll

def hasVerbalDm(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["dm"] and node["tag"]=="VRB":
			return True
	return False

def hasVRBPeriph(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["periph"] and node["tag"]=="VRB":
			return True
	return False

def hasVerbalPeriph(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["periph"] and node["tag"][0]=="V":
			return True
	return False

def hasAux(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["aux"]:
			return True
	return False

def hasMorph(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["morph"]:
			return True
	return False

def estce(tree):
	for i, node in tree.iteritems():
		if "est-ce" in node["t"]:
			return True
	return False

def lalala(tree):
	for i, node in tree.iteritems():
		if u"-là" in node["t"]:
			return True
	return False

def hasNoGov(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].keys()[0] in [-1]:
			return True
	return False

def disflink(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].values()[0] in ["disflink"]:
			return True
	return False

def hasEmptyNode(tree):
	for i, node in tree.iteritems():
		if node["t"]=="":
			return True
	return False

def isNonProjective(tree):
	for i, node in tree.iteritems():
		if node["gov"] and node["gov"].keys()[0] in tree and node["tag"] not in ["PRQ", "CLI"]:
			j=node["gov"].keys()[0]
			for ii, nnode in tree.iteritems(): # look again at each node
				if i<ii<j: # between
					for jj in nnode["gov"]:
						if jj<i or jj>j:
							if jj==0 or (ii in tree and tree[ii]["tag"] not in ["PRQ", "CLI"]):
								return True
				else:
					for jj in nnode["gov"]:
						if i<jj<j: 
							if jj==0 or (ii in tree and tree[ii]["tag"] not in ["PRQ", "CLI"]):
								return True
	return False

def cls(tree):
	for i, node in tree.iteritems():
		if node["tag"]=="CLS":
			gi,gf = node["gov"].items()[0]
			if gi in tree and tree[gi]["tag"] not in ["VRB"] and gf not in ["para","disflink"]: # CLS whose governor is not a verb
				return True
				#govnode=tree[gi]
				
				#pprint(tree)
				#print "******",i
			
			
	return False

	

def lemmaContains(tree, char="-"):
	
	lemmacorrection=dict( [(a.split(":")[0],a.split(":")[1]) for a in u"""
c' est-à-dire que:c'est-à-dire que
est-ce-que:est-ce que
quelques-un:quelques-uns
Ax-~~:Ax~
festiv-été:Festiv-été
t-il:il
ouvre-moi:ouvrir
trouve-moi:trouver
rappelle-moi:rappeler
débrouille-toi:débrouiller
met-il:mettre
es-tu:être
doit-on:devoir
moment-là:moment
gars-là:gars
jour-là:jour
bruit-là:bruit
mois-là:mois
festival-là:festival
côté-là:côté
jeunes-là:jeunes
niveau-là:niveau
celui-là:celui
lui-même:lui
sapeurs-pompier:sapeur-pompier
proposition-là:proposition
petit-à-petit:petit à petit
groupe-là:groupe
titre-là:titre
stylo-là:stylo
pays-là:pays
sens-là:sens
faut-il:falloir
passe-moi:passer
appelez-le:appeler

""".strip().split("\n")])
	print lemmacorrection
	
	
	motstraits=u"""
anti-littérature
pré-fait
six-dix
arrière-plan
anti-concertation
contre-littérature
arrière-grand-mère
Reuilly-Diderot
Saint-Germain
grands-parents
outre-mer
qu'est-ce que
est-ce que
vice-versa
peut-être
sous-terrain
tout-à-fait
entre-temps
au-dehors
rouge-gorge
c'est-à-dire
au-delà
essuie-glace
là-haut
petit-ami
Alsace-Lorraine
Hauts-de-Seine
rond-point
centre-ville
Notre-Dame
Sainte-Claire
Grand-Bigard
Ghlin-Baudour
Point-rouge
Mbuji-Mayi
ex-gouverneur
là-bas
là-dedans
dix-neuvième
dix-septième
dix-huitième
vingt-et-unième
rendez-vous
baby-sitter
quand-même
après-midi
grand-parent
Pointe-à-Pitre
Saint-Trop
Villeneuve-Loubet
Bruxelles-ville
Arts-Loi
enseignant-chercheur
mathématicien-écrivain
pâtissier-boulanger
Jean-François
Jean-Baptiste
Jean-Louis
Jean-Paul
Jean-Christophe
week-end
lunch-packet
Saint-Sauveur
Proche-Orient
grand-chose
là-dessus
au-dessus
là-haut-dessus
top-model
Saint-Jean
Saint-Jean-de-Maurienne
c'est-à-dire que
anti-viral
JT-dernière
Festiv-été
sous-marin
septante-sept
mille-neuf-cent-nonant
mitterando-mitterandien
savoir-vivre
sapeur-pompier
tout-petit
vis-à-vis de
médico-social
belle-mère
mi-temps
micro-processeur
contre-attaque
fois-ci
celui-ci
celle-ci
moi-même
ceux-là
vis-à-vis
Nord-Africains
Royaume-Uni
Grande-Bretagne
États-Unis d'Amérique
quelques-uns
vu-t-une
	""".strip().split("\n")
	for i, node in tree.iteritems():
		if char in node["lemma"]:
			if 1<node["lemma"].find(char)<len(node["lemma"]):
				if node["lemma"] not in motstraits and node["lemma"] not in lemmacorrection:
					if node["tag"] != "NUM":
						#print i,node["lemma"].find(char)
						return True
					
			
			
def search(infolder,fun):
	goodtrees=[]
	print "doing", fun.__name__
	#try: os.mkdir(outdir)	
	#except OSError: pass
	for infile in sorted(glob.glob(os.path.join(infolder,"*"))): # .conll
		if not os.path.isfile(infile): continue
		basename=os.path.basename(infile)
		print "reading",basename
		trees = conll.conllFile2trees(infile)
		
		for tree in trees:
			#if hasVerbalDm(tree):
			#if isNonProjective(tree):
			if fun(tree):
				goodtrees+=[tree]
	print "found",len(goodtrees)
	if goodtrees:
		conll.trees2conllFile(goodtrees,fun.__name__+".conll")

def searches():			
	#search("projects/OrfeoGold2016/platinum/", hasVerbalDm)		
	#search("projects/OrfeoGold2016/platinum/", isNonProjective)
	#search("projects/OrfeoGold2016/platinum/", hasEmptyNode)
	#search("projects/OrfeoGold2016/platinum/", cls)
	#search("projects/OrfeoGold2016/platinum/", hasAux)
	#search("projects/OrfeoGold2016/platinum/", estce)
	#search("projects/OrfeoGold2016/platinum/", lalala)
	#search("projects/OrfeoGold2016/platinum/", hasNoGov)
	#search("projects/OrfeoGold2016/platinum/", disflink)
	#search("projects/OrfeoGold2016/platinum/", hasVRBPeriph)
	#search("projects/OrfeoGold2016/platinum/", hasVerbalPeriph)
	#search("projects/OrfeoGold2016/platinum/", hasMorph)
	#search("../projects/Platinum/exportcool/", lemmaContains)
	search("../projects/Platinum/export/", lemmaContains)

if __name__ == "__main__":
	searches()
