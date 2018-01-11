#! usr/bin/python
#! coding: utf-8

import datetime, codecs, time, sys, os, glob, copy, re
from goldPlatinumTransformConll import splice
sys.path.insert(0, '../lib')
import conll



def lireToutLex(returnLex=False):
	"""
	fonction qui lit le lexique en mémoire
	pour des testes de consistence de la lemmatisation et de l'équitetage
	"""
	
	allLex={} # tag -> { t->[lem1, lem2, ..], ... }
	allLem={} # lem -> tag
	
	for lexfile in glob.glob('../../../../Orfeo/lexique/*.sfplm'):
		
		# Lecture des fichiers .sfplm		
		
		catt = os.path.basename(lexfile)[:3]
		print "je lis",lexfile,catt
		#print "allLex",allLex
		dic=allLex.get(catt,{})
		#print dic
		# Ouverture d'un fichier de lexique
		with codecs.open(lexfile, "r", "utf8") as f:
			
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
					
					#if t in dic:
						#print "oh",ligne
						#print t,dic[t]
						#print t,lem
					if deco not in ["S"]:	
						dic[t]=dic.get(t,[])+[(deco,lem)]
					#print t,lem
					allLem[lem]=allLem.get(lem,[])+[cat]
		allLex[catt]=dic
		#print "MWE","MWE" in allLex,catt in allLex,catt=="MWE"
		#print len(dic),"entries"
		
		
	#for li in u"""
	#du de+le PRE
	#aux à+le PRE
	#au à+le PRE
	#j~ j~ CLS
	#c~ c~ CLS
	#""".strip().split("\n"):
		#cols=li.strip().split()
		#allLem[cols[1]] = allLem.get(cols[1],[])+[cols[2]]  
	
	
		#
		#print lexfile[:3],"a",len(allLex[lexfile[:3]]),u"entrées"
		
	allLex["ADV"][u"-même"]=[("A",u"même")]
	#print "MWE","MWE" in allLex
	if returnLex: 	return allLex
	else:		return allLem


	
def lireLexiqueCorr(infile="lexiqueCorr.txt", allLex={}):
	"""
	
	"""
	instructs=["L","LS","T","R","TM","M","LM","?","TT"]

	renum=re.compile(ur"\s\d+\s")
	treebankinstr=[]
	
	with codecs.open(infile, "r", "utf8") as f:
		for line in f:
			line=line.strip()
			if line and line[0]!="#":
				print line
				instr, rest = renum.split(line)
				ins = instr.strip().split()[0]
				entries,lexcat = rest.split("lexique: ")
				try:t,l,c=entries.split()
				except:t,l,c=entries.split("\t")
				c=c.strip()
				if ins=="L":
					print "j'ajoute au dict:",t,l,c
					allLex[c][t]=allLex[c].get(t,[])+[("A",l)]
				elif ins=="LM":
					newlem=" ".join(instr.strip().split()[1:])
					print "j'ajoute au dict:",t,"newlem:",newlem,c
					allLex[c][t]=allLex[c].get(t,[])+[("A",newlem)]
				elif ins=="LS":
					print "j'ajoute au dict:",t,l,c
					allLex[c][t]=allLex[c].get(t,[])+[("A",l)]
					print "je supprime du dict:",t,l,lexcat
					try:
						del allLex[lexcat][t]
					except:
						print "----- no entry to delete",t,l,lexcat
					if len(lexcat.split())>1:qsdf
					print "trebank: tous les",t,l,lexcat,u"doivent être de cat",c 
					treebankinstr+=["\t".join(["LS trebank: tous les",t,l,lexcat,u"doivent être de cat",c ])]
				elif ins=="T":
					newcat=" ".join(instr.strip().split()[1:]).strip()
					if not newcat:	qsdf
					print "j'ajoute au dict:",t,l,"newcat:",newcat
					allLex[newcat][t]=allLex[newcat].get(t,[])+[("A",l)]
					print "trebank: tous les",t,l,c,u"doivent être de cat",newcat 
					treebankinstr+=["\t".join(["T trebank: tous les",t,l,c,u"doivent être de cat",newcat ])]
				elif ins=="TM":
					newlem=" ".join(instr.strip().split()[1:])
					print "trebank: tous les:",t,l,c,u"doivent obtenir newlem:",newlem
					treebankinstr+=["\t".join(["TM trebank: tous les:",t,l,c,"doivent obtenir newlem:",newlem ])]
				elif ins=="TT":	
					newlem,newcat=" ".join(instr.strip().split()[1:]).split()
					print "trebank: tous les:",t,"doivent obtenir newlem:",newlem,newcat
					treebankinstr+=["\t".join(["TT trebank: tous les:",t,"doivent obtenir newlem:",newlem,newcat])]
	#print "\n"*11
	with codecs.open('corrinst.txt', "w", "utf8") as f:
		f.write( "\n".join(treebankinstr) )
	
	if False: # write new lexique
	#if True: # write new lexique
		for cat in allLex:
			print "___________",cat
			with codecs.open('../../../../Orfeo/lexique/lexiqueCorr/'+cat+".sfplm", "w", "utf8") as f:
				for t in sorted(allLex[cat]):
					for deco,l in sorted(set(allLex[cat][t])):
						f.write( "\t".join([t,l,deco])+"\n" )
						#if len(sorted(set(allLex[cat][t])))>1:
							#print sorted(set(allLex[cat][t]))
					
			
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


def correct(tree,corrinst=[]):
	for i, node in tree.iteritems():
		t,l,ca=node["t"],node["lemma"],node["tag"]
		if t=="aujourd' hui":
			node["t"]="aujourd'hui"
			node["lemma"]="aujourd'hui"
		if t=="quelqu' un":
			node["t"]="quelqu'un"
			node["lemma"]="quelqu'un"	
		if t==u"c' est-à-dire":
			node["t"]=u"c'est-à-dire"
			node["lemma"]=u"c'est-à-dire"	
		if t==u"c' est-à-dire que":
			node["t"]=u"c'est-à-dire que"
			node["lemma"]=u"c'est-à-dire que"	
		if t==u"n' importe quoi":
			node["t"]=u"n'importe quoi"
			node["lemma"]=u"n'importe quoi"	
		if l=="La":node["lemma"]="le"
		if l=="Le":node["lemma"]="le"
		if l=="Les":node["lemma"]="le"
		if l=="L'":node["lemma"]="le"
		if l=="Aujourd'hui":node["lemma"]="aujourd'hui"
		
		if l=="il":node["tag"]="CLS"
		if l=="se":node["tag"]="CLI"
		
		for ty,a,b,c,d in corrinst:
			if ty=="TLS" and t==a and l==b and c==ca:
				print t,l,ca,"correcting",ty,a,b,c,d,"into",d
				node["tag"]=d
			elif ty=="TM" and t==a and l==b and c==ca:
				print t,l,ca,"correcting",ty,a,b,c,d,"into",d
				node["lemma"]=d
			elif ty=="TT" and t==a:
				if l!=b or c!=ca:
					print t,l,ca,"correcting",ty,a,b,c,d,"into",b,c
					node["lemma"]=b
					node["tag"]=c
				
		if l=="accord" and i-1 in tree and tree[i-1]["lemma"]=="de": # TODO: repair! doesn't redirect dependents of d'accord!!!
			#print node
			tree[i-1]["t"]=tree[i-1]["t"][0]+u"'accord"
			tree[i-1]["lemma"]=u"d'accord"	
			tree[i-1]["tag"]=u"INT"
			tree=splice(tree,i,{})
			tree=correct(tree)
			return tree
		
	return tree

def compil(infile):
	instr=[]
	with codecs.open(infile, "r", "utf8") as f:
		for li in f:
			col=li.strip().split("\t")
			
			if li.split()[0] in ["T","LS"]:
				instr+=[("TLS",col[1],col[2],col[3],col[5])]
			elif li.split()[0] in ["TM"]:
				instr+=[("TM",col[1],col[2],col[3],col[5])]
			elif li.split()[0] in ["TT"]:
				instr+=[("TT",col[1],col[3],col[4],"_")]
	return instr

def transform(infolder,outfolder,mixOldNew=False):
	createNonExistingFolders(outfolder)
	
	corrinst=compil('corrinst.txt')
	print len(corrinst),"rules"
	for infile in sorted(glob.glob(os.path.join(infolder,"*"))):
		if not os.path.isfile(infile): continue
		basename=os.path.basename(infile)
		print "reading",basename
		trees = conll.conllFile2trees(infile)
		newtrees=[]
		for tree in trees:
			if mixOldNew: newtrees+=[tree]
			newtree=copy.deepcopy(tree)
			newtree=correct(newtree,corrinst)
			newtrees+=[newtree]
			
			
		conll.trees2conllFile(newtrees,os.path.join(outfolder,fixOutname(basename)))
	

def searches():			
	
	#search("../projects/Platinum/export/")
	
	transform("../projects/Platinum/export/","../projects/Platinum/exportcorrected/")
	#search("../projects/Platinum/exportcorrected/")
	#funcsearch("../projects/Platinum/exportcorrected/")

if __name__ == "__main__":
	searches()
	#lireLexiqueCorr(allLex=lireToutLex(returnLex=True))
	#
