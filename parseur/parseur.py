#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2016 Kim Gerdes
# kim AT gerdes. fr
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
####


import codecs, glob, random, shutil, time, sys, os, argparse, psutil, subprocess
import regex as re

#import conll

verbose=False
#verbose=True



def parsing(infile, outfolder="parses/", memory=None, lemmatized=False):
	"""
	parsing function
	parserType is always graph!
	infile: an empty conll file
	
	"""
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	outfile = outfolder+os.path.basename(infile)
	if outfile.endswith(".empty.conll"): outfile=outfile[:-len(".empty.conll")]

	if not memory: memory=str(psutil.virtual_memory().available/1000000000)+"G"
	anna, lemclass, tagclass, parseclass="mate/anna-3.3.jar", "is2.lemmatizer.Lemmatizer", "is2.tag.Tagger", "is2.parser.Parser"
	
	modelFolder="models/"
	lemodel=modelFolder+"LemModel"
	tagmodel=modelFolder+"TagModel"
	parsemodel=modelFolder+"ParseModel"
	
	lemcommand="java -Xmx{memory} -cp {anna} {lemclass} -model {lemodel} -test {infile} -out {outfile}.lem.conll".format(memory=memory, anna=anna, lemclass=lemclass, infile=infile, lemodel=lemodel, outfile=outfile)
	tagcommand="java -Xmx{memory} -cp {anna} {tagclass} -model {tagmodel} -test {outfile}.lem.conll -out {outfile}.tag.conll".format(memory=memory, anna=anna, tagclass=tagclass, tagmodel=tagmodel, outfile=outfile)
	parsecommand="java -Xmx{memory} -cp {anna} {parseclass} -model {parsemodel} -test {outfile}.tag.conll -out {outfile}.parse.conll".format(memory=memory, anna=anna, parseclass=parseclass, parsemodel=parsemodel, outfile=outfile)
	
	if lemodel and lemodel[-1]!="/":
		if verbose:print "\n\n========== lemmatizing...", lemcommand
		p1 = subprocess.Popen([lemcommand],shell=True, stdout=subprocess.PIPE)
		out, err = p1.communicate()
		if verbose:
			print out, err
	else: # TODO: add this part (for non inflectional languages like Chinese and for pre-lemmatized files)
		if lemmatized:
			print "copying",outfolder+os.path.basename(infile),"as lemma file"
			shutil.copyfile(outfolder+os.path.basename(infile), outfolder+os.path.basename(infile)+".lem.conll")
		else:
			print "adding toks as lems",outfolder+os.path.basename(infile)
			trees=conll.conllFile2trees(infile)
			with codecs.open(outfolder+os.path.basename(infile)+".lem.conll","w","utf-8") as lemf:
				for tree in trees:
					lemf.write(newconvert.treeToEmptyConll14Text(tree, lemma=False)+"\n")
	if verbose:
		print "\n\n========== tagging...", tagcommand
	p1 = subprocess.Popen([tagcommand],shell=True, stdout=subprocess.PIPE)
	out, err = p1.communicate()
	if verbose: 
		print out, err
		print "\n\n========== dep analysis...", parsecommand
	p1 = subprocess.Popen([parsecommand],shell=True,  stdout=subprocess.PIPE)
	out =  p1.stdout.read()
	if verbose: 
		print out
		print "\n\n========== parsed"

	#if checkIntegrity(outfile+'_parse') == False:
		#print "*********ERROR IN FILE", outfile+"_parse", "Please Try again*********"
	return outfile+".parse.conll"


def lireDictionnaires():
	"""
	Lecture des fichiers du lexique
	"""
	droporfeo='lexiqueMultiMots/' # where we can find the lexique folder
	specialCharDic={}
	#onlyLetters=re.compile(ur'''^\w+$''',re.U+re.I)	
	for lexfile in glob.glob(droporfeo+'*.sfplm'):
		# Lecture des fichiers .sfplm
		#print "reading",lexfile
		with codecs.open(lexfile, "r", "utf8") as f:
			for ligne in f:
				if len(ligne) and "\t" in ligne:
					t,lem=ligne.strip().split("\t")
					#if (not onlyLetters.match(t[0])) or (not onlyLetters.match(t[1:-1].replace("-",""))) or not onlyLetters.match(t[-1]) :
					specialCharDic[t]=None
	if verbose: print len(specialCharDic),"special character words"
	specialCharWords = sorted(specialCharDic, key=len, reverse=True)
	return specialCharWords


	
def removePuncsFromConllfile(conllfile):
	"""
	transforms the roots (0) to empty (-1)
	"""
	with codecs.open(conllfile,"r","utf-8") as f:
		conlltext=f.read()
		conlltext=conlltext.replace("0	_	punc","-1	_	punc")
	with codecs.open(conllfile,"w","utf-8") as f:
		f.write(conlltext)

	

def emptyFromSentence(sentencefile, remultimatch=None,outfolder="."):
	"""
	sentencefile with one sentence per line --> conll14.empty.conll
	if remultimatch not empty, it is used for tokenization
	"""
	newname=os.path.basename(sentencefile)
	if newname.endswith(".txt"): newname=newname[:-len(".txt")]
	newname+=".empty.conll"
	outname=os.path.join(outfolder,newname)
	with codecs.open(sentencefile,"r","utf-8") as f, codecs.open(outname,"w","utf-8") as g:
		for li in f:
			if remultimatch: 	toks = tokenize(li,remultimatch)
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
	text=reponct.sub(r" \1 ",text).replace(" '","'") # spaces around punctuation, but not before hyphen (french specific!)
	text=renogroupponct.sub(r" \1 ",text).replace(" ~","~") # spaces around no group punctuation
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
	


def tokenize(line, remultimatch):
	"""
	tokenization of line
	uses remultimatch = compiled list of words ordered by size (bigger first)
	returns list of tokens
	"""
	
	# prepare line:
	line=line.replace(u"’","'")
	respaces=re.compile(ur'\s+')
	line=respaces.sub(r" ",line)
	
	# go!
	toks=[]
	for chunk, done in numurltokenize(line,returnMatchInfo=True):
		if done:
			toks+=[chunk]
		else:
			laststart=0
			for m in remultimatch.finditer(chunk):
				toks += simpletokenize(chunk[laststart:m.start()]) + [m.group(0).strip()] # strip is needed for cases like "etc. !"
				laststart=m.end()
			toks+=simpletokenize(chunk[laststart:])
	
	return toks
	

def parseSentenceFile(sentencefile, remultimatch, outfolder=None, memory=None, removePunct=True):
	"""
	main function
	sentencefile: file with one sentence per line
	remultimatch: compiled re to match multiwords
	"""
	if not memory: memory=str(psutil.virtual_memory().available/1000000000)+"G"
	if not outfolder: outfolder="parses/"
	
	print "preparing",sentencefile,"..."
	emptyConll = emptyFromSentence(sentencefile, remultimatch=remultimatch, outfolder=outfolder)
	print "parsing",sentencefile,"..."
	parsedfile=parsing(emptyConll, outfolder=outfolder, memory=memory)
	print "cleaning",parsedfile,"..."
	if removePunct: removePuncsFromConllfile(parsedfile)


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='wrapper of tokenizer and mate parser with French syntactic models')
	parser.add_argument('-s','--sentence', help='sentence between quotes', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-f','--sentencesFile', help='file containing one sentence per line', type=lambda s: unicode(s, 'utf8'), required=False)
	args = vars(parser.parse_args())
	
	ti=time.time()
	
	specialCharWords=lireDictionnaires()
	# prepare multiword matching:
	multimatch = ur"(( |\b)"+    ur"( |\b)|( |\b)".join([re.escape(mm) for mm in specialCharWords])   +ur"( |\b))"
	remultimatch=re.compile(multimatch,re.U+re.I)
	
	if args.get("sentencesFile",None):
		parseSentenceFile(args.get("sentencesFile",None),remultimatch=remultimatch)
	if args.get("sentence",None):
		with codecs.open("parses/singleSentence.txt","w","utf-8") as singleSentenceFile:
			singleSentenceFile.write(args.get("sentence",None)+"\n")
			parseSentenceFile("parses/singleSentence.txt",remultimatch=remultimatch)
		with codecs.open("parses/singleSentence.parse.conll","r","utf-8") as singleSentenceParse:
			print singleSentenceParse.read()
	
	if verbose: print "it took",time.time()-ti,"seconds"

