#! usr/bin/python
#! coding: utf-8

import codecs, glob, random, shutil, time, sys, os, psutil
import regex as re

from mate import parsing
sys.path.insert(0, '../lib')

import conll

verbose=False
#verbose=True

droporfeo='/home/kim/Dropbox/Orfeo/lexique/lexiqueCorrSimp/' # where we can find the lexique folder



def lireDictionnaires(dicofolder=None):
	"""
	Lecture des fichiers du lexique
	"""
	if not dicofolder: dicofolder = droporfeo
	specialCharDic={}
	onlyLetters=re.compile(ur'''^\w+$''',re.U+re.I)

	
	for lexfile in glob.glob(dicofolder+'*.sfplm'):
		# Lecture des fichiers .sfplm
		#print "reading",lexfile
		with codecs.open(lexfile, "r", "utf8") as f:
			for ligne in f:
				if len(ligne) and "\t" in ligne:
					t,lem=ligne.strip().split("\t")
					#if t=="~": print lexfile, qsdf
					#if (not onlyLetters.match(t[0])) or (not onlyLetters.match(t[1:-1].replace("-",""))) or not onlyLetters.match(t[-1]) :
					specialCharDic[t]=None
	if "~" in specialCharDic: del specialCharDic["~"]
	print len(specialCharDic),"special character words"
	specialCharWords = sorted(specialCharDic, key=len, reverse=True)
	#print "Fin de lecture du dictionnaire"
	#for w in specialCharWords: print w
	return specialCharWords

repoint=re.compile(ur'(?<![0-9A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜÃÑÕÆÅÐÇØ])([.。]+)')
repointEnd=re.compile(ur'([.。]+)$')
reponctWithNum=re.compile(ur'(?<![0-9])(\s*[;:,!\(\)§"]+)')
rehyph=re.compile(ur'(\s*[\/\']+)') # \- pas de segmentation des traits d'union
revirer=re.compile(ur'[`]+')
redoublespace=re.compile(ur'\s+',re.U)
reparenth=re.compile(ur'\([ \w]*\)',re.U)

def preparetokenize(text):
	text=text.strip()
	text=text.replace(u"’","'")
	text=revirer.sub(r" ",text)
	text=repointEnd.sub(r" \1 ",text)
	text=repoint.sub(r" \1 ",text)
	text=reponctWithNum.sub(r" \1 ",text)
	text=rehyph.sub(r"\1 ",text)
	return text

def textToSentences(text, outname, problemout=None, keepEndSent=False, maxlength=50, writeProblemBeforeSentence=True, includeProblemSentence=False):
	"""
	creates one sentence per line file in name outname
	"""
	#writeProblemFile=False, 
	endsent=re.compile(u'(?<=(?<=\w\w\s?|\s|~))([!?.]+([  ]*»+)*)',re.U) # TODO fix for xx~.
	
	#endsent=re.compile(r"(([\?\!？](?![\?\!])|((?<!\s[A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜÃÑÕÆÅÐÇØ])\.。！……\s)|\s\|)\s*)", re.M+re.U)
	#print 777,text
	#text=preparetokenize(text).strip()
	text=text.strip()
	#print 777,text
	
	#for sent in text.split("."):
	#if keepEndSent: 	sents = endsent.sub(ur"\1\n",u"ça va ? comment ! qsdf. oh!").split("\n")
	#else: 		sents = endsent.sub(ur"\n",u"ça va ? comment ! qsdf. oh!").split("\n")
	if keepEndSent: 	sents = endsent.sub(ur"\1\n",text).split("\n")
	else: 			sents = endsent.sub(ur"\n",text).split("\n")
	
	#print endsent.sub(ur"\n",u"Si je devais parler d'un événement marquant euh, je parlerais de l'année 2010. En effet je faisais de la GRS à haut niveau, j'ai commencé à l'âge de cinq ans et euh en 2010 je faisais partie euh d'une équipe de cinq. Comment va le P.S.G. ? Et tout le reste ? pas trop mal !").split("\n")
	#qsdf
	
	sents=[s for s in sents if s.strip()]
	#print sents
	if problemout: longfile = codecs.open(problemout,"w","utf-8")
	
	with codecs.open(outname,"w","utf-8") as courtfile:
		
		for sent in sents:
			sent=preparetokenize(sent)
			sent=redoublespace.sub(" ",sent)
			sent=reparenth.sub(" ",sent).strip()
			
			sent=sent.replace("aujourd' hui","aujourd'hui")
			sent=sent.replace("quelqu' un","quelqu'un")
			
			#sent=sent.replace("parce qu","parce_qu")
			#sent=reinvers.sub(ur" \1",sent)
			
			
			if sent:
				if problemout: longfile.write(sent+"\n") # +" .\n"
				if keepEndSent: simp = sent
				else:		simp=reponct.sub(" ",sent)
				simp=redoublespace.sub(" ",simp).strip()
				if not maxlength or len(simp.split())<maxlength:
					courtfile.write(simp+"\n")
				else:
					#pass
					#courtfile.write(u"_______________phrase très longue:\n")
					print "_______________phrase très longue:"
					print simp
					#if writeProblemFile:
						#with codecs.open("sentences/"+simplename+".problem.txt","a","utf-8") as probfile:
							#probfile.write(u"_______________phrase très longue:\n"+simp+" \n")
					if includeProblemSentence:
						if writeProblemBeforeSentence:
							courtfile.write("long ! ")
						courtfile.write(simp+"\n")
						


	
def removePuncsFromConllfile(conllfile):
	with codecs.open(conllfile,"r","utf-8") as f:
		conlltext=f.read()
		conlltext=conlltext.replace("0	_	punc","-1	_	punc")
	with codecs.open(conllfile,"w","utf-8") as f:
		f.write(conlltext)

def degradeConllfile(conllfile, removeFuncs=["para"], removeDeps=0.4):
	trees=conll.conllFile2trees(conllfile)
	nbgovs=0
	for arbre in trees:
		for i, node in arbre.iteritems():
			if "gov" in node and node["gov"].keys()[0]!=-1 and node["gov"].values()[0] not in removeFuncs: 
				nbgovs+=1
	print int(nbgovs*removeDeps)
	tobeRemoved=sorted(random.sample(range(nbgovs),int(nbgovs*removeDeps)))
	print "nbgovs:", nbgovs, "tobeRemoved:", tobeRemoved
	nbgovs=0
	for arbre in trees:
		for i, node in arbre.iteritems():
			if "gov" in node and node["gov"].keys()[0]!=-1:
				if node["gov"].values()[0] in removeFuncs: 
					node["gov"]={}
				else:
					nbgovs+=1
					if nbgovs in tobeRemoved:
						node["gov"]={}
	newname=conllfile
	if conllfile.endswith(".conll"): newname=conllfile[:-len(".conll")]
	shutil.move(conllfile, newname+".orig")
	conll.trees2conllFile(trees, newname+".deg", columns=10)
	
	
	

def emptyFromSentence(sentencefile, specialCharWords=[],outfolder="."):
	"""
	file with one sentence per line --> conll14
	if specialCharWords not empty, it is used for tokenization
	"""
	outname=os.path.join(outfolder,os.path.basename(sentencefile)+".conll")
	print "emptyFromSentence:",sentencefile, outfolder, outname
	with codecs.open(sentencefile,"r","utf-8") as f, codecs.open(outname,"w","utf-8") as g:
		for li in f:
			if specialCharWords: 	toks = tokenize(li,specialCharWords)
			else:			toks = simpletokenize(li)
			for num,tok in enumerate( toks ):
				g.write("\t".join([str(num+1), tok ]+["_"]*12)+'\n')
			g.write("\n")

	return outname


def simpletokenize(text, returnMatchInfo=False):
	"""
	simple punctuation and space based tokenization
	
	specific for french (apostrophes are glued to the precedent word: d' un
	in english we'd need: do n't Mike 's
	"""
	if verbose: print "_____before simpletokenize",text
	reponct=re.compile(ur'''(\s*[.;:,!?\(\)§"'«»]+)''',re.U+re.M) # prepare for default punctuation matching. removed - \d from list
	renogroupponct=re.compile(ur'''(\s*[;:,«»\(\)"])''', re.U+re.M) # signs that have to be alone - they cannot be grouped
	
	
	
	## do the remaining simple token-based splitting
	toks=[]
	#for text,done in ntoks:
		#if done:
			#nntoks+=[(text,done)]
		#else:
	text=reponct.sub(r" \1 ",text).replace(" '","'") # spaces around punctuation, but not before hyphen (french specific!)
	text=renogroupponct.sub(r" \1 ",text).replace(" ~","~") # spaces around no group punctuation

	#nntoks += [(t,1) for t in text.split()] #
	if verbose: print "____after simpletokenize",text
	return text.split()
	
	
def numurltokenize(text, returnMatchInfo=False):
	"""
	number and url tokenization
	
	"""
	reurl=re.compile(ur'''(https?://|\w+@)?[\w\d\%\.]*\w\w\.\w\w[\w\d~/\%\#]*(\?[\w\d~/\%\#]+)*''', re.U+re.M+re.I)
	resignswithnumbers=re.compile(ur'''(?<![0-9A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜÃÑÕÆÅÐÇØ])\d+[\d,.\s]+''', re.U+re.M)
	
	if verbose: print "before numurltokenize",text
	
	# do the url recognition
	toks=[] # couples : (tok, todo=0, done=1)
	laststart=0
	for m in reurl.finditer(text):
		#print 'reurl:%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
		toks += [(text[laststart:m.start()],0), (m.group(0).strip(),1)] #
		#print toks
		laststart=m.end()
	toks += [(text[laststart:],0)] #
	#print toks
	
	# do the number recognition
	ntoks=[]
	for text,done in toks:
		if done:
			ntoks+=[(text,done)]
		else:
			laststart=0
			for m in resignswithnumbers.finditer(text):
				#print 'resignswithnumbers:%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
				ntoks += [(text[laststart:m.start()],0), (m.group(0).strip(),1)] #
				#print toks
				laststart=m.end()
			ntoks += [(text[laststart:],0)] #
	if verbose: print "after numurltokenize",ntoks
	
	if returnMatchInfo: 	return ntoks
	else:			return [t for t,done in ntoks]
	


def tokenize(line, specialCharWords):
	"""
	tokenization of line
	uses specialCharWords = list of words ordered by size (bigger first)
	returns list of tokens
	"""
	
	# prepare line:
	line=line.replace(u"’","'")
	respaces=re.compile(ur'\s+')
	line=respaces.sub(r" ",line)
	
	#print u"à part entière" in specialCharWords
	
	# prepare multiword matching:
	multimatch = ur"(( |\b)"+    ur"( |\b)|( |\b)".join([re.escape(mm) for mm in specialCharWords])   +ur"( |\b))"
	#multimatch = ur"(\b"+    ur"\b|\b".join([re.escape(mm) for mm in specialCharWords])   +ur"\b)"
	remultimatch=re.compile(multimatch,re.U+re.I)
	# go!
	toks=[]
	for chunk, done in numurltokenize(line,returnMatchInfo=True):
		#print "tokenize chunk",chunk, done
		if done:
			toks+=[chunk]
		else:
			laststart=0
			for m in remultimatch.finditer(chunk):
				#print 'remultimatch:%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
				#print "ppp",laststart,m.start()
				toks += simpletokenize(chunk[laststart:m.start()]) + [m.group(0).strip()] # strip is needed for cases like "etc. !"
				#print toks
				laststart=m.end()
			toks+=simpletokenize(chunk[laststart:])
	
	if verbose: print "after tokenize",toks
	return toks
	
			
def parseSentenceFile(sentencefile, modelfolder="mate/platinum.2016-10-20_01:34/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="4G", removePunct=False, specialCharWords=[], degrade=False):
	"""
	removed parsertype from options!
	"""
	print "\n\nparseSentenceFile",sentencefile
	emptyConll = emptyFromSentence(sentencefile, specialCharWords=specialCharWords, outfolder=outfolder)
	print "made empty",emptyConll
	parsedfile=parsing(emptyConll, lemodel=modelfolder+lemodel, tagmodel=modelfolder+tagmodel, parsemodel=modelfolder+parsemodel, outfolder=outfolder, memory=memory)
	print parsedfile
	if removePunct: removePuncsFromConllfile(parsedfile)
	if degrade: degradeConllfile(parsedfile)
	return parsedfile

def textToParseAll(simpletxtfile):
	
	#if not os.path.dirname(os.path.abspath(sys.argv[0])).endswith("tools"): # problem when importing from uploadFile via parSentences
		#os.chdir(os.path.dirname(os.path.abspath(sys.argv[0]))+"/tools")
		#print 444,os.path.dirname(os.path.abspath(sys.argv[0]))+"/tools"
		#print "now i'm at os.getcwd()",os.getcwd()
	
	#specialCharWords=lireDictionnaires(os.path.join(os.path.dirname(__file__),"fr/lexiqueCorrSimp/"))
	specialCharWords={}
	memory = str(psutil.virtual_memory().total/(1000000000)-1)+"G"
	textToSentences(codecs.open(simpletxtfile,'r','utf-8').read(),simpletxtfile+".sents" , maxlength=0, keepEndSent=True)
	
	parsedfile = parseSentenceFile(os.path.abspath(simpletxtfile+".sents"), 
		modelfolder=os.path.abspath(os.path.join(os.path.dirname(__file__),"mate/platinum.2016-11-29_00:22/models"))+"/", 
		lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", 
		outfolder=os.path.join(os.path.dirname(__file__),"parses"), memory=memory, removePunct=False, specialCharWords=specialCharWords, degrade=False)
	return parsedfile

if __name__ == "__main__":
	ti=time.time()
	specialCharWords=lireDictionnaires()
	#sent=u"D'abord, dit-il, c'est elle-même qui « regarde» aujourd'hui le long-métrage « §218 etc.  », long de 2,3m !!! Et c'est « avec » le gars-même qui l'a vue sur Http://liberation.fr?!?! Allons-y pour voir l'âge de/des Œuvre(s)... J'irais pour 100 000€ pour lui envoyer un mèl à part entière au qsdf@sqfd3sqdf.com"
	#toks= simpletokenize(sent)
	#print toks
	#print " ".join( toks )
	#toks = tokenize(sent,specialCharWords=lireDictionnaires()) 
	#print toks
	#print "__".join( toks )
	#print re.sub(ur"\s+","",sent)==re.sub(ur"\s+","","".join(toks))
	#print re.sub(ur"\s+","",sent)
	#print re.sub(ur"\s+","","".join(toks))
	
	#emptyFromSentence("2a.txt",specialCharWords=lireDictionnaires())
	
	#parseSentenceFile("2a.txt", modelfolder="mate/platinum.2016-11-14_02:05/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="7G", removePunct=True, specialCharWords=specialCharWords, degrade=True)
	#parseSentenceFile("2b.txt", modelfolder="mate/platinum.2016-11-14_02:05/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="7G", removePunct=True, specialCharWords=specialCharWords, degrade=True)
	#parseSentenceFile("2c.txt", modelfolder="mate/platinum.2016-11-14_02:05/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="7G", removePunct=True, specialCharWords=specialCharWords, degrade=True)
	
	#degradeConllfile("/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/2a.conll")
	#degradeConllfile("/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/2b.conll")
	#degradeConllfile("/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/2c.conll")
	#degradeConllfile("/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/1a.conll")
	#degradeConllfile("/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/1b.conll")
	#degradeConllfile("/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/1c.conll")
	#degradeConllfile("2b.txt.conll_parse")
	#degradeConllfile("2c.txt.conll_parse")
	
	
	#parseSentenceFile("exo1sents.a")
	#parseSentenceFile("exo1sents.b")
	#parseSentenceFile("exo1sents.c")
	#parseSentenceFile("cantonese_sample_for_dict.txt", modelfolder="mate/hkud.2016-11-02_04:04/models/", lemodel="", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="4G", removePunct=False, useTokDic=False)
	#parseSentenceFile("cantonese_sample_for_dict.txt", modelfolder="mate/hkud.2016-11-02_11:03/models/", lemodel="", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="4G", removePunct=False, useTokDic=False)
	#parseSentenceFile("cantonese_sample_for_dict.txt.fakeMand", modelfolder="mate/hkud.2016-11-02_11:03/models/", lemodel="", tagmodel="TagModel", parsemodel="ParseModel", outfolder=".", memory="4G", removePunct=False, useTokDic=False)
	for sentfile in glob.glob("sentences/*"):
		if ".problem." in sentfile: continue
	
		#print 
		#qsdf
	
		#parseSentenceFile(sentfile, modelfolder="mate/platinum.2016-11-29_00:22/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder="parses", memory="47G", removePunct=True, specialCharWords=specialCharWords, degrade=False)
		memory = str(psutil.virtual_memory().total/(1000000000)-1)+"G"
		parseSentenceFile(os.path.abspath(sentfile), 
			modelfolder=os.path.abspath(os.path.join(os.path.dirname(__file__),"mate/platinum.2016-11-29_00:22/models"))+"/", 
			lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", 
			outfolder=os.path.abspath(os.path.join(os.path.dirname(__file__),"parses")), memory=memory, removePunct=True, specialCharWords=specialCharWords, degrade=False)
		

	#parseSentenceFile("../corpus/upload.fr.txt", modelfolder="mate/platinum.2017-03-26_03:10/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder="parses", memory="47G", removePunct=False, specialCharWords=specialCharWords, degrade=False)
	
	#textToParseAll("/home/kim/gromoteur/export-bitcoin/www.numerama.com---tech---306898-une-etude-remet-en-cause-la-suprematie-du-bitcoin-sur-les-autres-crypto-monnaies.html.txt")
	
	
	print "it took",time.time()-ti,"seconds"

