# -*- coding: utf-8 -*-
#!/usr/bin/python

import os,subprocess,sys,glob,datetime, conll, trees2train, treebankfiles, updateTrees, newconvert, getTextsForParsing, time, unicodedata, re, shutil, codecs
from database 	import SQL
#import retokenisation

verbose=True

def checkIntegrity(infile):
	"""
	checks size of file
	if empty returns False
	else returns True
	"""
	b = os.path.getsize(infile)
	if b > 0:
		return True
	else:
		return False

def backupOldDatabase(project, outpath):
	oldpath = "projects/"+project
	newpath=outpath+project+"_"+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
	command="cp -ar "+oldpath+" "+newpath
	p1 = subprocess.Popen([command],shell=True, stdout=subprocess.PIPE)
	out, err = p1.communicate()
	return newpath

def slugify(value):
	"""
	Normalizes string, converts to lowercase, removes non-alpha characters,
	and converts spaces to hyphens.
	"""
	
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
	return re.sub('[-\s]+', '-', value)

def createDailyPath(path, project):
	"""
	creates timestamped directory
	takes path as argument
	returns timestamped path
	"""
	if path[-1]!="/": path=path+"/"
	newpath=path+slugify(project)+"."+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')+"/"
	try:
		os.mkdir(newpath)
	except OSError:
		pass
	return newpath

def createDirectory(path):
	if path[-1]!="/": path=path+"/"
	try:
		os.mkdir(path)
	except OSError:
		pass
	return path

def getClasses(lang="parse"):
	"""
	returns the names of the classes to be used for parsing
	mind that the parseclass used for parsing and for evaluation are different
	"""
	anna = "mate/mate_components/anna-3.3.jar"
	lemclass = "is2.lemmatizer.Lemmatizer"
	tagclass = "is2.tag.Tagger"

	if lang=="parse":
		parseclass = "is2.parser.Parser"

	elif lang=="eval":
		"""NOTE : problem probably caused by parser itself. 
		if transition-based is used for training, it adds "-tag" at the end of filename
		so transition is here just used for evaluation"""
		parseclass = "is2.transitionR6j.Parser"

	return anna, lemclass, tagclass, parseclass

def makeTrainingModels(infile,outfolder="mate/models", memory="4G", testfile="", evalfile="", lemma=None):
	"""
	training of mate
	creation of models used for parsing
	evaluation if testfile and evalfile are given
	returns names of models
	"""
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	anna,lemclass, tagclass,parseclass = getClasses("parse")
	infile=unicode(infile)
	if evalfile=="":
		lemodel=outfolder+"LemModel"
		tagmodel=outfolder+"TagModel"
		parsemodel=outfolder+"ParseModel"
	else:
		lemodel=outfolder+"LemModelEval"
		tagmodel=outfolder+"TagModelEval"
		parsemodel=outfolder+"ParseModelEval"
		evalfile="-eval "+evalfile
	
	if testfile:
		lemtest="-test "+testfile
		tagtest="-test "+testfile+"_lem"
		lemout="-out "+testfile+"_lem"
		tagout="-out "+testfile+"_tag"
		
	else:
		lemtest=""
		tagtest=""
		lemout=""
		tagout=""
	
	if verbose: print "\n\n========== Start of Training"
	
	lemcommand = "java -Xmx{memory} -cp {anna} {lemclass} -train {infile} -model {lemodel} {lemtest} {lemout} {evalfile}".format(memory=memory, anna=anna, lemclass=lemclass, infile=infile, lemodel=lemodel, lemtest=lemtest, lemout=lemout, evalfile=evalfile)
	
	tagcommand = "java -Xmx{memory} -cp {anna} {tagclass} -train {infile} -model {tagmodel} {tagtest} {tagout} {evalfile}".format(memory=memory, anna=anna, tagclass=tagclass,infile=infile, tagmodel=tagmodel, tagtest=tagtest, tagout=tagout, evalfile=evalfile)

	if evalfile=="":
		parsecommand = "java -Xmx{memory} -cp {anna} {parseclass} -train {infile} -model {parsemodel}".format(memory=memory, anna=anna, parseclass=parseclass, infile=infile, parsemodel=parsemodel)
	else:
		parsecommand="java -Xmx{memory} -cp {anna} {parseclass} -train {infile} -model {parsemodel} -test {testfile}_tag -out {testfile}_parse {evalfile}".format(memory=memory, anna=anna, parseclass=parseclass, parsemodel=parsemodel, infile=infile, testfile=testfile, evalfile=evalfile)

	if lemma:
		if verbose: print "\n\n========== lemmatizing...", lemcommand
		p1 = subprocess.Popen([lemcommand],shell=True, stdout=subprocess.PIPE)
		out, err = p1.communicate()
		if verbose: print out, err
	else: lemodel=None
	if verbose: print "\n\n========== tagging...", tagcommand
	p1 = subprocess.Popen([tagcommand],shell=True, stdout=subprocess.PIPE)
	out, err = p1.communicate()
	if verbose: print out, err
	if verbose: print "\n\n========== dep analysis...", parsecommand
	p1 = subprocess.Popen([parsecommand],shell=True,  stdout=subprocess.PIPE)
	print  p1.stdout.read()
	if verbose: print "\n\n========== parsed"

	return lemodel, tagmodel, parsemodel

def parsing(infile, lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder="parses", memory="40G", depparse=True):
	"""
	parsing function
	"""
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	outfile = outfolder+os.path.basename(infile)

	anna, lemclass, tagclass, parseclass=getClasses("parse")
	
	
	lemcommand="java -Xmx{memory} -cp {anna} {lemclass} -model {lemodel} -test {infile} -out {outfile}_lem".format(memory=memory, anna=anna, lemclass=lemclass, infile=infile, lemodel=lemodel, outfile=outfile)
	tagcommand="java -Xmx{memory} -cp {anna} {tagclass} -model {tagmodel} -test {outfile}_lem -out {outfile}_tag".format(memory=memory, anna=anna, tagclass=tagclass, tagmodel=tagmodel, outfile=outfile)

	parsecommand="java -Xmx{memory} -cp {anna} {parseclass} -model {parsemodel} -test {outfile}_tag -out {outfile}_parse".format(memory=memory, anna=anna, parseclass=parseclass, parsemodel=parsemodel, outfile=outfile)
	
	if lemodel:
		if verbose:print "\n\n========== lemmatizing...", lemcommand
		p1 = subprocess.Popen([lemcommand],shell=True, stdout=subprocess.PIPE)
		out, err = p1.communicate()
		if verbose:
			print out, err
	else:
		shutil.copyfile(infile, infile+"_lem")
	if verbose:
		print "\n\n========== tagging..."
	p1 = subprocess.Popen([tagcommand],shell=True, stdout=subprocess.PIPE)
	out, err = p1.communicate()
	if verbose: print out, err
	if depparse:
			if verbose: print "\n\n========== dep analysis..."
			p1 = subprocess.Popen([parsecommand],shell=True,  stdout=subprocess.PIPE)
			print  p1.stdout.read()
			if verbose: print "\n\n========== parsed"

	if checkIntegrity(outfile+'_parse') == False:
		print "*********ERROR IN FILE", outfile+"_parse", "Please Try again*********"
	return outfile+"_parse"


def detailedEvaluation(lang="eval", memory="4G", testfile="", evalfile="", path="mate/evaluation"):
	"""
	takes a mate-parsed file (testfile) and compares it to a gold file (evalfile)
	writes detailed evaluation in timestamped logfile
	returns name of logfile
	"""
	f=open(path+"evaluation_"+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')+"_transition_based_anna.3.3.txt", "w")

	anna,lemclass, tagclass,parseclass = getClasses("parse")
	
	evalcommand="java -Xmx4G -cp {anna} {parseclass} -eval {evalfile} -out {testfile}".format(anna=anna, parseclass=parseclass, evalfile=evalfile, testfile=testfile)

	if verbose: print "evaluation."
	p1 = subprocess.Popen([evalcommand],shell=True,  stdout=subprocess.PIPE)
	f.write(p1.stdout.read())
	#print p1.stdout.read()
	return f.name

"""
STEPS
	1. copier BDD dans dossier sauvegardesOrfeo
	2. extraire arbres validés (trees2train.getnewtrees())
	3. entrainer mate
		3a. sur 90% pour evaluation
		3b. sur 100% pour modèle
	3. extraire textes Orfeo + conll.makeEmpty
	4. parser textes Orfeo
	5. remettre en ligne sous user = parser

Ne pas oublier :
	fichiers logs
	revoir arborescence projet
		un dossier horodaté (Jour+heure)
			Un sous dossier avec les modèles (full/partiel)
			un sous dossier avec les arbres parsés
			un sous dossier avec les différents ficthiers d'entrainement
"""

def doIt(project=u"OrfeoGold2016"):
	ti = time.time()
	print "Begin"
	timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
	#defining project and creation of saves directories
	
	basepath= createDailyPath("./mate/", project)
	print "Everything will be stored in", basepath
	backupbase=backupOldDatabase(project,basepath)
	print "A copy of the database has been stored in:", backupbase

	#creation of dirs
	traindir=createDirectory(basepath+"training")
	modeldir=createDirectory(basepath+"models")
	logdir=createDirectory(basepath+"logs")
	parsedir=createDirectory(basepath+"parses")
	
	######
	#getting gold trees for training
	trees = trees2train.getValidatedTrees(project, basepath)
	lemma = None
	if trees: # see whether the first token of the first tree has a lemma. if lemma==None: we'll skip lemmatization
		lemma=trees[0][sorted(trees[0])[0]].get("lemma",None) # just trying to get the first lemma value
		if lemma=="_": lemma=None
	
	#####
	#creating trainingfile
	fulltrainfile=traindir+"trainingset_"+timestamp
	conll.trees2conll10(trees, fulltrainfile, colons=14)
	#creating files used for evaluation
	newconvert.makeTrainTestSets(traindir,pattern=os.path.basename(fulltrainfile),train="train",test="test",empty="emptytest",testsize=10, lemma=lemma)

	print "just testing whether i can load them..."
	conll.conll2trees(traindir+"train")
	conll.conll2trees(traindir+"emptytest")
	conll.conll2trees(traindir+"test")
	
	print "\n\n========== newmate training of partial tree file for evaluation"
	
	lemodelpartial, tagmodelpartial, parsemodelpartial=makeTrainingModels(traindir+"train",outfolder=modeldir, memory="40G", testfile=traindir+"emptytest", evalfile=traindir+"test", lemma=lemma)
	print "\n\n========== newmate evaluation"
	#evaluation
	detailedEvaluation(lang="eval", memory="40G", testfile=traindir+"test", evalfile=traindir+"emptytest_parse", path=logdir)
	#full training
	print "\n\n========== newmate training of full tree file for parsing"
	lemodel, tagmodel, parsemodel=makeTrainingModels(fulltrainfile,outfolder=modeldir, memory="40G",lemma=lemma)

	#getting texts to parse
	
	#filenames=getTextsForParsing.main(project, parsedir)
	#TO REMOVE, DEBUG ONLY !
	filenames=getTextsForParsing.getEmptyConlls(project, parsedir, lemma)
	#parsing
	for infile in filenames:
		print "\n\n\========== parsing", infile
		parsedfile=parsing(infile, lemodel=lemodel, tagmodel=tagmodel, parsemodel=parsemodel, outfolder=parsedir)
		#update on base
		newname=os.path.basename(parsedfile)
		updateTrees.updateParseResult(project, parsedir, filepattern=newname)
	totaltime=(time.time()-ti)/60
	print "Over. It took", totaltime, "for whole process."



if __name__ == "__main__":
	
	#doIt(project=u"OrfeoGold2016")
	#doIt(project=u"HongKongTVMandarin")
	time.sleep(1) 
	with codecs.open("mate/parse.log","w","utf-8") as log:
		log.write(u"Ready! Now i could be done")
	print "ooooooooo"
	#traindir="mate/2016-08-20_14:07/training/"
	#modeldir="mate/2016-08-20_14:07/models/"
	#lemodelpartial, tagmodelpartial, parsemodelpartial=makeTrainingModels(traindir+"train",outfolder=modeldir, memory="40G", testfile=traindir+"emptytest", evalfile=traindir+"test")



