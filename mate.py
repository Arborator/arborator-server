# -*- coding: utf-8 -*-
#!/usr/bin/python

import os,subprocess,datetime, conll, trees2train, treebankfiles, updateTrees, newconvert, getTextsForParsing, time, unicodedata, re, shutil, codecs, argparse
from database import SQL
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

def getClasses(lang="graph"):
	"""
	returns the names of the classes to be used for parsing
	mind that the parseclass used for parsing and for evaluation are different
	"""
	anna = "mate/mate_components/anna-3.3.jar"
	lemclass = "is2.lemmatizer.Lemmatizer"
	tagclass = "is2.tag.Tagger"

	if lang=="graph":
		parseclass = "is2.parser.Parser"

	elif lang=="transition":
		"""NOTE : problem probably caused by parser itself. 
		if transition-based is used for training, it adds "-tag" at the end of filename
		so transition is here just used for evaluation"""
		parseclass = "is2.transitionR6j.Parser"

	return anna, lemclass, tagclass, parseclass

def makeTrainingModels(basepath, infile,outfolder="mate/models", memory="4G", testfile="", evalfile="", lemma=None, parserType="graph"):
	"""
	training of mate
	creation of models used for parsing
	evaluation if testfile and evalfile are given
	returns names of models
	
	TODO: parserType is ignored for the time being!!!
	
	"""
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	anna,lemclass, tagclass,parseclass = getClasses("graph")
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
		if "lemtrain_" in lemma:
			lemcommand = "java -Xmx{memory} -cp {anna} {lemclass} -train {infile} -model {lemodel} {lemtest} {lemout} {evalfile}".format(memory=memory, anna=anna, lemclass=lemclass, infile=lemma, lemodel=lemodel, lemtest=lemtest, lemout=lemout, evalfile=evalfile)
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

def createNonExistingFolders(path):
	head, tail = os.path.split(path)
	if head=="":
		if tail and not os.path.exists(tail): os.makedirs(tail)
	else:
		createNonExistingFolders(head)
	if head and not os.path.exists(head): os.makedirs(head)


def parsing(infile, lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder=None, memory="4G", depparse=True, parserType="graph"):
	"""
	parsing function
	TODO: parserType is ignored
	"""
	if not outfolder:
		timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
		outfolder="mate/parses/"+timestamp+"/"
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	createNonExistingFolders(outfolder)
	outfile = outfolder+os.path.basename(infile)

	anna, lemclass, tagclass, parseclass=getClasses("graph")
	
	
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
		print "copying",outfolder+os.path.basename(infile)
		shutil.copyfile(outfolder+os.path.basename(infile), outfolder+os.path.basename(infile)+"_lem")
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
	return outfile+"_tag"


def detailedEvaluation(parserType="graph", memory="4G", testfile="", evalfile="", path="mate/evaluation", evaluationPercent=10):
	"""
	takes a mate-parsed file (testfile) and compares it to a gold file (evalfile)
	writes detailed evaluation in timestamped logfile
	returns name of logfile
	"""
	f=open(path+"evaluation_"+str(evaluationPercent)+"."+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')+"transition_based_anna.3.3.txt", "w")

	anna,lemclass, tagclass,parseclass = getClasses("transition")
	
	evalcommand="java -Xmx4G -cp {anna} {parseclass} -eval {evalfile} -out {testfile}".format(anna=anna, parseclass=parseclass, evalfile=evalfile, testfile=testfile)

	if verbose: print "evaluation."
	p1 = subprocess.Popen([evalcommand],shell=True,  stdout=subprocess.PIPE)
	f.write(p1.stdout.read())
	#print p1.stdout.read()
	return f.name


def mateLogs(text, mode="w"):
	with codecs.open("./mate/parse.log", mode, "utf-8") as f:
		f.write(text)
	if verbose:
		print "\n\n==========",text


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
			un sous dossier avec les différents fichiers d'entrainement
"""

def trainingEvaluationParsing(project=u"OrfeoGold2016", parserType="graph", whoseTrees="validator", evaluationPercent=10, additionnalLexicon=None, resultAnnotator="mate"):
	"""
	todo :
		- add function to choose parser type (lang=)
		- creer mate.log pour progression (fin = "Ready.")
	TODO: additionnalLexicon working???
	"""
	
	parserType=(parserType or "graph")
	whoseTrees=whoseTrees or "validator"
	evaluationPercent=evaluationPercent or 10
	resultAnnotator=resultAnnotator or "mate"
	
	try:os.chmod("mate/parse.log", 0666) # just in case...
	except:pass
	mateLogs("Begin")
	ti = time.time()
	#print "Begin"
	timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
	#defining project and creation of saves directories
	
	basepath= createDailyPath("./mate/", project)
	backupbase=backupOldDatabase(project,basepath)
	
	mateLogs("A copy of the database has been stored in {backupbase}. Getting validated trees...".format(backupbase=backupbase) )
	#creation of dirs
	traindir=createDirectory(basepath+"training")
	modeldir=createDirectory(basepath+"models")
	logdir=createDirectory(basepath+"logs")
	parsedir=createDirectory(basepath+"parses")
	
	######
	#getting gold trees for training
	trees = trees2train.getValidatedTrees(project, basepath, whoseTrees)
	lemma = None
	if trees: # see whether the first token of the first tree has a lemma. if lemma==None: we'll skip lemmatization
		lemma=trees[0][sorted(trees[0])[0]].get("lemma",None) # just trying to get the first lemma value
		if lemma=="_": lemma=None
	mateLogs( u"{nrtrees} validated trees extracted".format(nrtrees=len(trees)) ) 
	#####
	#creating trainingfile
	fulltrainfile=traindir+"trainingset_"+timestamp
	conll.trees2conll10(trees, fulltrainfile, colons=14)
	if additionnalLexicon:
		lemma = traindir+"lemtrain_"+os.path.basename(fulltrainfile)
		lemtrees= conll.conll2trees(additionnalLexicon)
		conll.trees2conll10(lemtrees+trees, lemma, colons=14)
	mateLogs("trainfile created")
	#creating files used for evaluation
	if isinstance(evaluationPercent, str): evaluationPercent = int(evaluationPercent)
	newconvert.makeTrainTestSets(traindir,pattern=os.path.basename(fulltrainfile),train="train",test="test",empty="emptytest",testsize=evaluationPercent, lemma=lemma)

	if verbose:
		print "just testing whether i can load them..."
		conll.conll2trees(traindir+"train")
		conll.conll2trees(traindir+"emptytest")
		conll.conll2trees(traindir+"test")
		
	mateLogs("training of partial tree file for evaluation...")
	
	lemodelpartial, tagmodelpartial, parsemodelpartial=makeTrainingModels(basepath, traindir+"train",outfolder=modeldir, memory="4G", testfile=traindir+"emptytest", evalfile=traindir+"test", lemma=lemma, parserType=parserType)
	mateLogs("evaluation...")
	#evaluation
	evaluFileName = detailedEvaluation(parserType=parserType, memory="4G", testfile=traindir+"test", evalfile=traindir+"emptytest_parse", path=logdir, evaluationPercent=evaluationPercent)
	
	
	evalu=unicode(evaluFileName)+"\n"
	with codecs.open(evaluFileName,"r","utf-8") as f:
		evalu+=f.read()
	
	#full training
	mateLogs("training of full tree file for parsing...")
	lemodel, tagmodel, parsemodel=makeTrainingModels(basepath, fulltrainfile,outfolder=modeldir, memory="4G",lemma=lemma, parserType=parserType)
	#getting texts to parse
	mateLogs("training and evaluation complete. Starting the parse...\n\n{evalu}".format(evalu=evalu))
	#filenames=getTextsForParsing.main(project, parsedir)
	filenames=getTextsForParsing.extractConllFiles(project, parsedir)
	#parsing
	for infile in filenames:
		mateLogs("Training and evaluation complete. Starting the parse of {infile}\n\n{evalu}".format(infile=infile, evalu=evalu))
		parsedfile=parsing(infile, lemodel=lemodel, tagmodel=tagmodel, parsemodel=parsemodel, outfolder=parsedir, parserType=parserType)
		#update on base
		newname=os.path.basename(parsedfile)
		updateTrees.updateParseResult(project, parsedir, filepattern=newname, annotatorName=resultAnnotator, removeToGetDB="_parse")

	totaltime=(time.time()-ti)/60
	
	# make it easy for everyone to erase all this stuff:
	for root, dirs, files in os.walk(basepath):
		for momo in dirs:
			try:	os.chmod(os.path.join(root, momo), 0777)
			except:	pass
		for momo in files:
			try:	os.chmod(os.path.join(root, momo), 0666)
			except:	pass
	
	mateLogs("Ready. It took {totaltime} minutes for the whole process\n\n{evalu}".format(totaltime=round(totaltime,1), evalu=evalu) )


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Trains Mate, evaluates, and parses the complete project')
	parser.add_argument('project', type=lambda s: unicode(s, 'utf8'), help='project name')
	parser.add_argument('-t','--parserType', help='parser type: graph or transition', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-w','--whoseTrees', help='take validated trees from: all or validator', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-e','--evaluationPercent', help='percentage of trees taken for evaluation', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-a','--additionnalLexicon', help='name of additional lexicon', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-r','--resultAnnotator', help='username to be used for the newly parsed trees', type=lambda s: unicode(s, 'utf8'), required=False)
	
	parser.add_argument('-i','--infile', help='file to be parsed', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-lm','--lemmodel', help='lemmatizing model', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-tm','--tagmodel', help='tagging model', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-pm','--parsemodel', help='parsing model', type=lambda s: unicode(s, 'utf8'), required=False)

	
	parser.add_argument('-testRun', help="don't actually parse", action='store_true')
	args = vars(parser.parse_args())
	
	#trainingEvaluationParsing(project=u"OrfeoGold2016")
	if args.get("testRun",None):
		mateLogs("Ready. It took {totaltime} seconds for the whole process".format(totaltime=1) )
		print "ok so far", args["testRun"]
	elif args.get("infile",None):
		
		parsing(infile, lemodel=args.get("lemmodel",None), tagmodel=args.get("tagmodel",None), parsemodel=args.get("parsemodel",None))
		
		
	else:
		#print 'args.get("whoseTrees","validator")',args.get("whoseTrees","validator")
		trainingEvaluationParsing(project=args["project"], parserType=args.get("parserType","graph"), whoseTrees=args.get("whoseTrees","validator"), evaluationPercent=int(args.get("evaluationPercent",None) or 10), additionnalLexicon=args.get("additionnalLexicon",None), resultAnnotator=args.get("resultAnnotator","mate"))
	



