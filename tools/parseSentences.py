#! usr/bin/python
#! coding: utf-8

import codecs, glob, random, shutil, time, sys, os
import regex as re

from mate import parsing
sys.path.insert(0, '../lib')

import conll

debug=False

droporfeo='/home/kim/Dropbox/Orfeo/lexique/lexiqueCorrSimp/' # where we can find the lexique folder



def lireDictionnaires():
	"""
	Lecture des fichiers du lexique
	"""
	
	specialCharDic={}
	onlyLetters=re.compile(ur'''^\w+$''',re.U+re.I)

	
	for lexfile in glob.glob(droporfeo+'*.sfplm'):
		# Lecture des fichiers .sfplm
		#print "reading",lexfile
		with codecs.open(lexfile, "r", "utf8") as f:
			for ligne in f:
				if len(ligne) and "\t" in ligne:
					t,lem=ligne.strip().split("\t")
					#if (not onlyLetters.match(t[0])) or (not onlyLetters.match(t[1:-1].replace("-",""))) or not onlyLetters.match(t[-1]) :
					specialCharDic[t]=None
						
	print len(specialCharDic),"special character words"
	specialCharWords = sorted(specialCharDic, key=len, reverse=True)
	#print "Fin de lecture du dictionnaire"
	#for w in specialCharWords: print w
	return specialCharWords



	
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
	
	reponct=re.compile(ur'''(\s*[.;:,!?\(\)§"'«»\d]+)''',re.U+re.M) # prepare for default punctuation matching. removed - from list
	renogroupponct=re.compile(ur'''(\s*[;:,«»\(\)"])''', re.U+re.M) # signs that have to be alone - they cannot be grouped
	
	
	
	## do the remaining simple token-based splitting
	toks=[]
	#for text,done in ntoks:
		#if done:
			#nntoks+=[(text,done)]
		#else:
	text=reponct.sub(r" \1 ",text).replace(" '","'") # spaces around punctuation, but not before hyphen (french specific!)
	text=renogroupponct.sub(r" \1 ",text) # spaces around no group punctuation
	#nntoks += [(t,1) for t in text.split()] #
	#print "nntoks",nntoks
	return text.split()
	
	
def numurltokenize(text, returnMatchInfo=False):
	"""
	number and url tokenization
	
	"""
	reurl=re.compile(ur'''(https?://|\w+@)?[\w\d\%\.]*\w\w\.\w\w[\w\d~/\%\#]*(\?[\w\d~/\%\#]+)*''', re.U+re.M+re.I)
	resignswithnumbers=re.compile(ur'''\d+[\d,.\s]+''', re.U+re.M)
	
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
	#print ntoks
	
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
		#print chunk, done
		if done:
			toks+=[chunk]
		else:
			laststart=0
			for m in remultimatch.finditer(chunk):
				#print 'remultimatch:%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
				toks += simpletokenize(chunk[laststart:m.start()]) + [m.group(0).strip()] # strip is needed for cases like "etc. !"
				#print toks
				laststart=m.end()
			toks+=simpletokenize(chunk[laststart:])
	
	#print toks
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
	for sentfile in glob.glob("sentences2/*"):
		parseSentenceFile(sentfile, modelfolder="mate/platinum.2016-11-29_00:22/models/", lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder="parses", memory="47G", removePunct=True, specialCharWords=specialCharWords, degrade=False)

	
	print "it took",time.time()-ti,"seconds"

