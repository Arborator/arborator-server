#! usr/bin/python
#! coding: utf-8

import datetime, codecs, time, sys, os, glob, copy
sys.path.insert(0, '../lib')
import conll



		
def lireToutLex():
	"""
	fonction qui lit le lexique en mémoire
	pour des testes de consistence de la lemmatisation et de l'équitetage
	"""
	
	#allLex={}
	allLem={}
	
	for lexfile in glob.glob('../../../../Orfeo/lexique/*.sfplm'):
		
		# Lecture des fichiers .sfplm		
		
		#dic=allLex.get(lexfile[:3],{})
		
		# Ouverture d'un fichier de lexique
		with codecs.open(lexfile, "r", "utf8") as f:
			print "je lis",lexfile
			for ligne in f:
				if len(ligne) and "\t" in ligne:
					# correct errors:
					ligne=ligne.replace(u"’","'")
					ligne=ligne.replace(u"..",".")
					ligne=ligne.replace(u" -","-")
					ligne=ligne.replace(u"' ","'") # pour corriger l'entrée "qu' est -ce que" etc.
					ligne = ligne.replace("\t\t","\t")
					ligne = ligne.replace(" \t","\t")
					ligne = ligne.replace("\t ","\t")
					
					#print ligne.strip()
					cols = ligne.split("\t")
					if len(cols)==5: deco,t,cat,lem,morph = cols
					elif len(cols)==6: deco,t,cat,lem,morph,_ = cols
					else: qsdf # violent break. problem with dictionary!!!
					# specific corrections for french dictionary
					if lem[:2]=="s'":
						lem=lem[2:]
					elif lem[:3]=="se ":
						lem=lem[3:]
											
					#if deco not in ["S","P","X", "M", "MX"]:
						
						#if (not onlyLetters.match(t)):
							#if lexfile[:3]!="PCT" or len(t)>1: # virer qqs poncutation seule
					#dic[t]=lem
					allLem[lem]=allLem.get(lem,[])+[os.path.basename(lexfile)[:3]]
	for li in u"""
	du de+le PRE
	aux à+le PRE
	au à+le PRE
	j~ j~ CLS
	c~ c~ CLS
	""".strip().split("\n"):
		cols=li.strip().split()
		allLem[cols[1]] = allLem.get(cols[1],[])+[cols[2]]  
	
	
		#allLex[lexfile[:3]]=dic
		#print lexfile[:3],"a",len(allLex[lexfile[:3]]),u"entrées"
		
	#allLex["ADV"][u"-même"]=u"même"
	
	return allLem


			
def funcsearch(infolder):
	errors={}
	numerrors=0
	for infile in sorted(glob.glob(os.path.join(infolder,"*"))): # .conll
		if not os.path.isfile(infile): continue
		basename=os.path.basename(infile)
		print "reading",basename
		trees = conll.conllFile2trees(infile)
		
		for tree in trees:
			for i, node in tree.iteritems():
				
				if node["gov"].values()[0] in ["dm"] and node["tag"] not in ["INT"] :
					key= " ".join([node["t"],node["lemma"],node["tag"]])
					#print key,"!!!"
					errors[key ]=errors.get(key,0)+1
					numerrors+=1
	with codecs.open("dm.txt","w","utf-8") as outf:
		for key in sorted(errors, key=errors.get, reverse=True):
			print errors[key],key
			outf.write(str(errors[key])+" "+key+"\n")
		print "total of",numerrors,"cases"
		outf.write(" ".join(["total of",str(numerrors),"cases"]))
	



			
def search(infolder):
	allLem=lireToutLex()
	errors={}
	numerrors=0
	for infile in sorted(glob.glob(os.path.join(infolder,"*"))): # .conll
		if not os.path.isfile(infile): continue
		basename=os.path.basename(infile)
		print "reading",basename
		trees = conll.conllFile2trees(infile)
		
		for tree in trees:
			#if hasVerbalDm(tree):
			#if isNonProjective(tree):
			for i, node in tree.iteritems():
				#if (node["lemma"] in allLem and node["tag"] in allLem[node["lemma"]]) and node["tag"] not in ["NOM"] and allLem.get(node["lemma"],None):
					#pass
					##print node["t"],node["lemma"],node["tag"],"ok"
				#else:
				if node["tag"] in ["NOM"] and node["tag"] not in allLem.get(node["lemma"],[]) and allLem.get(node["lemma"],[])==[]:
					key= " ".join([node["t"],node["lemma"],node["tag"],"lexique:"," ".join(sorted(set(allLem.get(node["lemma"],["pas dans le lexique"]))))])
					#print key,"!!!"
					errors[key ]=errors.get(key,0)+1
					numerrors+=1
	with codecs.open("problems.txt","w","utf-8") as outf:
		for key in sorted(errors, key=errors.get, reverse=True):
			print errors[key],key
			outf.write(str(errors[key])+" "+key+"\n")
		print "total of",numerrors,"errors"
		outf.write(" ".join(["total of",str(numerrors),"errors"]))
	

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


def correct(tree):
	for i, node in tree.iteritems():
		if node["t"]=="aujourd' hui":
			node["t"]="aujourd'hui"
			node["lemma"]="aujourd'hui"
		if node["t"]=="quelqu' un":
			node["t"]="quelqu'un"
			node["lemma"]="quelqu'un"	
		if node["t"]==u"c' est-à-dire":
			node["t"]=u"c'est-à-dire"
			node["lemma"]=u"c'est-à-dire"	
		if node["t"]==u"c' est-à-dire que":
			node["t"]=u"c'est-à-dire que"
			node["lemma"]=u"c'est-à-dire que"	
		if node["t"]==u"n' importe quoi":
			node["t"]=u"n'importe quoi"
			node["lemma"]=u"n'importe quoi"	
		if node["lemma"]=="La":node["lemma"]="le"
		if node["lemma"]=="Le":node["lemma"]="le"
		if node["lemma"]=="Les":node["lemma"]="le"
		if node["lemma"]=="L'":node["lemma"]="le"
		if node["lemma"]=="Aujourd'hui":node["lemma"]="aujourd'hui"
		
		if node["lemma"]=="il":node["tag"]="CLS"
		if node["lemma"]=="se":node["tag"]="CLI"
		if node["lemma"]=="de+le":node["tag"]="PRE" # des et du
		
	return tree

def transform(infolder,outfolder,mixOldNew=False):
	createNonExistingFolders(outfolder)
	spaceToks={}
	#for infile in sorted(glob.glob(os.path.join(infolder,"test.conll"))):
	for infile in sorted(glob.glob(os.path.join(infolder,"*"))):
		if not os.path.isfile(infile): continue
		basename=os.path.basename(infile)
		print "reading",basename
		trees = conll.conllFile2trees(infile)
		newtrees=[]
		for tree in trees:
			if mixOldNew: newtrees+=[tree]
			newtree=copy.deepcopy(tree)
			newtree=correct(newtree)
			newtrees+=[newtree]
			
			
		conll.trees2conllFile(newtrees,os.path.join(outfolder,fixOutname(basename)))
	

def searches():			
	
	#search("../projects/Platinum/export/")
	
	#transform("../projects/Platinum/export/","../projects/Platinum/exportcorrected/")
	#search("../projects/Platinum/exportcorrected/")
	funcsearch("../projects/Platinum/exportcorrected/")

if __name__ == "__main__":
	searches()
