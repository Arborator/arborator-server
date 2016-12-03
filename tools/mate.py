# -*- coding: utf-8 -*-
#!/usr/bin/python

import os,subprocess,sys,glob,datetime, random, time, unicodedata, re, shutil, codecs, argparse
sys.path.insert(0, '../lib')

import conll, trees2train, updateTrees, getTextsForParsing
#from database import SQL
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

def makeTrainingModels(basepath, lemtagin, depin, outfolder="mate/models", memory="4G", testfile="", evalfile="", lemma=None, parserType="graph"):
	"""
	training of mate
	creation of models used for parsing
	evaluation if testfile and evalfile are given
	returns names of models
	
	TODO: parserType is ignored for the time being!!!
	
	"""
	
	print "makeTrainingModels parameters:",basepath, lemtagin, depin,outfolder, memory, testfile, evalfile, lemma, parserType
	
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	anna,lemclass, tagclass,parseclass = getClasses("graph")
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
		if lemma: tagtest="-test "+testfile+"_lem"
		else: tagtest="-test "+testfile
		lemout="-out "+testfile+"_lem"
		tagout="-out "+testfile+"_tag"
	else:
		lemtest=""
		tagtest=""
		lemout=""
		tagout=""
	
	if verbose: print "\n\n========== Start of Training"
	
	lemcommand = "java -Xmx{memory} -cp {anna} {lemclass} -train {lemtagin} -model {lemodel} {lemtest} {lemout} {evalfile}".format(memory=memory, anna=anna, lemclass=lemclass, lemtagin=lemtagin, lemodel=lemodel, lemtest=lemtest, lemout=lemout, evalfile=evalfile)
	
	tagcommand = "java -Xmx{memory} -cp {anna} {tagclass} -train {lemtagin} -model {tagmodel} {tagtest} {tagout} {evalfile}".format(memory=memory, anna=anna, tagclass=tagclass,lemtagin=lemtagin, tagmodel=tagmodel, tagtest=tagtest, tagout=tagout, evalfile=evalfile)

	if evalfile=="":
		parsecommand = "java -Xmx{memory} -cp {anna} {parseclass} -train {depin} -model {parsemodel}".format(memory=memory, anna=anna, parseclass=parseclass, depin=depin, parsemodel=parsemodel)
	else:
		parsecommand="java -Xmx{memory} -cp {anna} {parseclass} -train {depin} -model {parsemodel} -test {testfile}_tag -out {testfile}_parse {evalfile}".format(memory=memory, anna=anna, parseclass=parseclass, parsemodel=parsemodel, depin=depin, testfile=testfile, evalfile=evalfile)

	if lemma:
		#if "trainlex" in lemma:
			#lemcommand = "java -Xmx{memory} -cp {anna} {lemclass} -train {infile} -model {lemodel} {lemtest} {lemout} {evalfile}".format(memory=memory, anna=anna, lemclass=lemclass, infile=lemma, lemodel=lemodel, lemtest=lemtest, lemout=lemout, evalfile=evalfile)
		if verbose: print "\n\n========== lemma training...", lemcommand
		p1 = subprocess.Popen([lemcommand],shell=True, stdout=subprocess.PIPE)
		out, err = p1.communicate()
		if verbose: print out, err
	else: lemodel=None
	if verbose: print "\n\n========== tag training...", tagcommand
	p1 = subprocess.Popen([tagcommand],shell=True, stdout=subprocess.PIPE)
	out, err = p1.communicate()
	if verbose: print out, err
	if verbose: print "\n\n========== dep training...", parsecommand
	p1 = subprocess.Popen([parsecommand],shell=True,  stdout=subprocess.PIPE)
	print  p1.stdout.read()
	if verbose: print "\n\n========== models done"
	
	return lemodel, tagmodel, parsemodel

def parsing(infile, lemodel="LemModel", tagmodel="TagModel", parsemodel="ParseModel", outfolder="parses", memory="4G", depparse=True, parserType="graph", lemmatized=False):
	"""
	parsing function
	TODO: parserType is ignored
	"""
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	outfile = outfolder+os.path.basename(infile)

	anna, lemclass, tagclass, parseclass=getClasses("graph")
	
	
	lemcommand="java -Xmx{memory} -cp {anna} {lemclass} -model {lemodel} -test {infile} -out {outfile}_lem".format(memory=memory, anna=anna, lemclass=lemclass, infile=infile, lemodel=lemodel, outfile=outfile)
	tagcommand="java -Xmx{memory} -cp {anna} {tagclass} -model {tagmodel} -test {outfile}_lem -out {outfile}_tag".format(memory=memory, anna=anna, tagclass=tagclass, tagmodel=tagmodel, outfile=outfile)

	parsecommand="java -Xmx{memory} -cp {anna} {parseclass} -model {parsemodel} -test {outfile}_tag -out {outfile}_parse".format(memory=memory, anna=anna, parseclass=parseclass, parsemodel=parsemodel, outfile=outfile)
	
	if lemodel and lemodel[-1]!="/":
		if verbose:print "\n\n========== lemmatizing...", lemcommand
		p1 = subprocess.Popen([lemcommand],shell=True, stdout=subprocess.PIPE)
		out, err = p1.communicate()
		if verbose:
			print out, err
	else:
		if lemmatized:
			print "copying",outfolder+os.path.basename(infile),"as lemma file"
			shutil.copyfile(outfolder+os.path.basename(infile), outfolder+os.path.basename(infile)+"_lem")
		else:
			print "adding toks as lems",outfolder+os.path.basename(infile)
			trees=conll.conllFile2trees(infile)
			with codecs.open(outfolder+os.path.basename(infile)+"_lem","w","utf-8") as lemf:
				for tree in trees:
					lemf.write(newconvert.treeToEmptyConll14Text(tree, lemma=False)+"\n")
	if verbose:
		print "\n\n========== tagging...", tagcommand
	p1 = subprocess.Popen([tagcommand],shell=True, stdout=subprocess.PIPE)
	out, err = p1.communicate()
	if verbose: print out, err
	if depparse:
			if verbose: print "\n\n========== dep analysis...", parsecommand
			p1 = subprocess.Popen([parsecommand],shell=True,  stdout=subprocess.PIPE)
			print  p1.stdout.read()
			if verbose: print "\n\n========== parsed"

	if checkIntegrity(outfile+'_parse') == False:
		print "*********ERROR IN FILE", outfile+"_parse", "Please Try again*********"
	return outfile+"_parse"


def detailedEvaluation(parserType="graph", memory="4G", testfile="", evalfile="", path="mate/evaluation", evaluationPercent=10):
	"""
	takes a mate-parsed file (testfile) and compares it to a gold file (evalfile)
	writes detailed evaluation in timestamped logfile
	returns name of logfile
	"""
	f=open(path+"evaluation_"+str(evaluationPercent)+"."+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')+"transition_based_anna.3.3.txt", "w")

	anna,lemclass, tagclass,parseclass = getClasses("transition")
	
	evalcommand="java -Xmx4G -cp {anna} {parseclass} -eval {evalfile} -out {testfile}".format(anna=anna, parseclass=parseclass, evalfile=evalfile, testfile=testfile)

	if verbose: print "evaluation\n", evalcommand
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
def treeToConll14Text(tree):
	outtext=""
	for i in sorted(tree.keys()):
		node = tree[i]
		gov = node.get("gov",{}).items()
		govid = -1
		func = "_"
		
		if gov:
			for govid,func in gov:
				if govid!=-1:
					outtext+="\t".join([str(i),node.get("t","_"), node.get("lemma",""), node.get("lemma",""), node.get("tag","_"), node.get("tag","_"), "_","_", str(govid), str(govid),func,func,"_","_"])+"\n"
		else:
			outtext+="\t".join([str(i),node.get("t","_"), node.get("lemma",""), node.get("lemma",""), node.get("tag","_"), node.get("tag","_"), "_","_", str(govid), str(govid),func,func,"_","_"])+"\n"
	return outtext

def treeToEmptyConll14Text(tree, lemma=True):
	outtext=""
	for i in sorted(tree.keys()):
		node = tree[i]
		lem="_"
		if not lemma: lem=node.get("t","_")
		outtext+="\t".join([str(i),node.get("t","_"), node.get("t","_"), lem]+["_"]*10)+"\n"
	return outtext

def makeTrainTestSets(infolder,pattern="*conll",train="train",test="test",empty="emptytest",testsize=10, lemma=True):
	"""
	chooses testsize % for test file, rest for train file
	"""
	tottec,tottrc,toks=0,0,0
	traintrees=[]
	with codecs.open(os.path.join(infolder, test),"w","utf-8") as testf, codecs.open(os.path.join(infolder, empty),"w","utf-8") as emptyf, codecs.open(os.path.join(infolder, train),"w","utf-8") as trainf:
		for infilename in glob.glob(os.path.join(infolder, pattern)):
			print "newconvert: looking at",infilename
			
			tec,trc=0,0
			allsentences=conll.conllFile2trees(infilename)
			print len(allsentences),"sentences"
			testselection=random.sample(range(len(allsentences)),len(allsentences)*testsize/100)
			
			for i,s in enumerate(allsentences):
				toks+=len(s)
				if i in testselection:
					testf.write(treeToConll14Text(s)+"\n")
					emptyf.write(treeToEmptyConll14Text(s,lemma)+"\n")
					tec+=1
				else:
					traintrees+=[s]
					trainf.write(treeToConll14Text(s)+"\n")
					trc+=1
						
			print "testing with",tec,"sentences. training with",trc,"sentences"
			tottec+=tec
			tottrc+=trc
			if not lemma: shutil.copyfile(os.path.join(infolder, empty), os.path.join(infolder, empty)+"_lem")
	print "tottec,tottrc,toks=",tottec,tottrc,toks
	return traintrees

			
def splitForTraining(infilename="Rhapsodie.micro_simple.conll.oldnum"):
	"""
	+ splitting for parsing
	"""
	count=0
	with codecs.open("bonne.Rhapsodie1000","w","utf-8") as outfile, codecs.open("bonne.Rhapsodie600","w","utf-8") as testfile, codecs.open("bonne.Rhapsodie600empty","w","utf-8") as emptyfile:
		
		for tree in conllFile2trees(infilename):
			count+=1
			treecorrdic={0:0}
			for i,tokenid in enumerate(sorted(tree)):
				treecorrdic[tokenid]=i+1
			print treecorrdic
			for i,tokenid in enumerate(sorted(tree)):
				node=tree[tokenid]
				gov = node.get("gov",{}).items()
				govid,func= gov[0]
				#govid
				print "____",i+1,tokenid,node,govid,func,treecorrdic,treecorrdic[tokenid],treecorrdic[govid]
				
				if count<=1000:
					outfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(treecorrdic[govid]),str(treecorrdic[govid]),func,func,"_","_"])+"\n")
				else:
				
					testfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(treecorrdic[govid]),str(treecorrdic[govid]),func,func,"_","_"])+"\n")
					emptyfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), "_", "_", "_", "_", "_", "_", "_","_","_","_","_","_"])+"\n")
			if count<=1000:outfile.write("\n")
			else:
				testfile.write("\n")
				emptyfile.write("\n")

def trainingEvaluationParsing(project=u"OrfeoGold2016", parserType="graph", whoseTrees="validator", evaluationPercent=10, additionnalLexicon=None, resultAnnotator="mate", getFromFolder=False, parseDB=False, memory="40G"):
	"""
	if additionnalLexicon is given, it is joined to the training file for lemmatization and tagging.
	change memory here!
	todo :
		- add function to choose parser type (lang=)
		- creer mate.log pour progression (fin = "Ready.")
	"""
	mateLogs("Begin")
	ti = time.time()
	
	if getFromFolder: parseDB=False # TODO: correct this so that all options are available
	parserType=(parserType or "graph")
	whoseTrees=whoseTrees or "validator"
	evaluationPercent=evaluationPercent or 10
	resultAnnotator=resultAnnotator or "mate"
	
	try:os.chmod("mate/parse.log", 0666) # just in case...
	except:pass
	
	timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')


	#####
	#defining project and creation of saves directories
	#####
	
	basepath= createDailyPath("./mate/", project)
	if parseDB:
		backupbase=backupOldDatabase(project,basepath)
		mateLogs("A copy of the database has been stored in {backupbase}. Getting validated trees...".format(backupbase=backupbase) )
	traindir=createDirectory(basepath+"training")
	modeldir=createDirectory(basepath+"models")
	logdir=createDirectory(basepath+"logs")
	parsedir=createDirectory(basepath+"parses")


	#####
	#getting gold trees for training
	#####
	
	if getFromFolder: # getFromFolder contains folder name containing only conll files
		goldtrees=[]
		for infile in glob.glob(os.path.join(getFromFolder, '*')):
			gtrees=conll.conllFile2trees(infile)
			for tree in gtrees:
				for i in tree:
					for gi in tree[i]["gov"]:
						if not 0<=gi<=len(tree):
							print infile
							print tree
							print "has a problematic governor:",gi
							sys.exit()
			goldtrees+=gtrees
	else:
		goldtrees = trees2train.getValidatedTrees(project, basepath, whoseTrees)
	mateLogs( u"{nrtrees} validated trees extracted".format(nrtrees=len(goldtrees)) ) 
		
	lemma = None
	if goldtrees: # see whether the first token of the first tree has a lemma. if lemma==None: we'll skip lemmatization
		lemma=goldtrees[0][sorted(goldtrees[0])[0]].get("lemma",None) # just trying to get the first lemma value
		if lemma=="_": lemma=None
		print "found lemma in first tree:",lemma
		#TODO: do something here: double tokens as lemmas for chinese, see function makeTrainTestSets
	else:
		print "no trees from:",getFromFolder
		sys.exit()
	print "goldtrees:",len(goldtrees)
	
	#####
	#creating trainingfiles
	#####
	
	alldeptraining=traindir+"alldeptraining.conll"
	conll.trees2conllFile(goldtrees, alldeptraining, columns=14)
	traintrees=makeTrainTestSets(traindir,pattern=os.path.basename(alldeptraining),train="partialdeptrain.conll",test="test.conll",empty="emptytest.conll",testsize=int(evaluationPercent), lemma=lemma)
	print "traintrees:",len(traintrees)
	if additionnalLexicon:
		lexicontrees = conll.conllFile2trees(additionnalLexicon)
		print "lexicontrees:",len(lexicontrees)
		alllemtagtrain=traindir+"alllemtagtrain.conll"
		conll.trees2conllFile(goldtrees+lexicontrees, alllemtagtrain, columns=14)
		partiallemtagtrain=traindir+"partiallemtagtrain.conll"
		conll.trees2conllFile(traintrees+lexicontrees, partiallemtagtrain, columns=14)
	else:
		alllemtagtrain=alldeptraining
		partiallemtagtrain=traindir+"partialdeptrain.conll"
	
	#creating files used for evaluation
	#if isinstance(evaluationPercent, str): evaluationPercent = int(evaluationPercent)
	mateLogs("trainfiles created")
	if verbose:
		print "just testing whether i can load them..."
		conll.conllFile2trees(traindir+"partialdeptrain.conll")
		conll.conllFile2trees(traindir+"emptytest.conll")
		conll.conllFile2trees(traindir+"test.conll")
	
	
	mateLogs("training of partial tree file for evaluation... ====")
	lemodelpartial, tagmodelpartial, parsemodelpartial=makeTrainingModels(basepath, lemtagin=partiallemtagtrain, depin=traindir+"partialdeptrain.conll",outfolder=modeldir, memory=memory, testfile=traindir+"emptytest.conll", evalfile=traindir+"test.conll", lemma=lemma, parserType=parserType)
	mateLogs("evaluation...")
	#evaluation
	evaluFileName = detailedEvaluation(parserType=parserType, memory=memory, testfile=traindir+"emptytest.conll_parse", evalfile=traindir+"test.conll", path=logdir, evaluationPercent=evaluationPercent)
	
	evalu=unicode(evaluFileName)+"\n"
	with codecs.open(evaluFileName,"r","utf-8") as f:
		evalu+=f.read()
	
	#full training
	mateLogs("training of full tree file for parsing... ====")
	lemodel, tagmodel, parsemodel=makeTrainingModels(basepath, lemtagin=alllemtagtrain, depin=alldeptraining,outfolder=modeldir, memory=memory,lemma=lemma, parserType=parserType)
	#getting texts to parse
	mateLogs("training and evaluation complete. Starting the parse...\n\n{evalu}".format(evalu=evalu))
	#filenames=getTextsForParsing.main(project, parsedir)
	if parseDB:
		filenames=getTextsForParsing.extractConllFiles(project, parsedir)
		#parsing
		for infile in filenames:
			#mateLogs("Training and evaluation complete. Starting the parse of {infile}\n\n{evalu}".format(infile=infile, evalu=evalu))
			mateLogs("Training and evaluation complete. Starting the parse of {}\n\n".format(infile))
			parsedfile=parsing(infile, lemodel=lemodel, tagmodel=tagmodel, parsemodel=parsemodel, outfolder=parsedir, parserType=parserType, memory=memory)
			#update on base
			newname=os.path.basename(parsedfile)
			updateTrees.updateParseResult(project, parsedir, filepattern=newname, annotatorName=resultAnnotator, removeToGetDB="_parse")

	
	
	# make it easy for everyone to erase all this stuff:
	for root, dirs, files in os.walk(basepath):
		for momo in dirs:
			try:	os.chmod(os.path.join(root, momo), 0777)
			except:	pass
		for momo in files:
			try:	os.chmod(os.path.join(root, momo), 0666)
			except:	pass
	
	totaltime=(time.time()-ti)/60
	mateLogs("Ready. It took {totaltime} minutes for the whole process\n\n{evalu}".format(totaltime=round(totaltime,1), evalu=evalu) )


if __name__ == "__main__":
	""" 
	example usage:
	python mate.py Platinum --getFromFolder projects/Platinum/export/
	python mate.py Platinum -f projects/Platinum/punc/
	python mate.py Platinum -a mate/VRB.conll14 -f projects/Platinum/punc/
	python mate.py Platinum -a mate/fr/lex.conll14 -f projects/Platinum/punc/
	python mate.py Platinum -f ../projects/Platinum/punc/
	python mate.py Platinum -f ../projects/Platinum/exportcool/
	python mate.py Platinum -f ../projects/Platinum/exportcorrected/
	
	python mate.py HKUD -f mate/testEvalMate/training/HongKongTVMandarin.UD_ZH%.conll14
	python mate.py HKUD -f mate/testEvalMate/training/alltrees/

	
	"""	
	parser = argparse.ArgumentParser(description='Trains Mate, evaluates, and parses the complete project')
	parser.add_argument('project', type=lambda s: unicode(s, 'utf8'), help='project name')
	parser.add_argument('-t','--parserType', help='parser type: graph or transition', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-w','--whoseTrees', help='take validated trees from: all or validator', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-e','--evaluationPercent', help='percentage of trees taken for evaluation', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-a','--additionnalLexicon', help='name of additional lexicon', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-r','--resultAnnotator', help='username to be used for the newly parsed trees', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-f','--getFromFolder', help='name of folder containing the gold conlls', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-testRun', help="don't actually parse", action='store_true')
	args = vars(parser.parse_args())
	
	#trainingEvaluationParsing(project=u"OrfeoGold2016")
	if args.get("testRun",None):
		mateLogs("Ready. It took {totaltime} seconds for the whole process".format(totaltime=1) )
		print "ok so far", args["testRun"]
	else:
		#print 'args.get("whoseTrees","validator")',args.get("whoseTrees","validator")
		trainingEvaluationParsing(project=args["project"], parserType=args.get("parserType","graph"), whoseTrees=args.get("whoseTrees","validator"), evaluationPercent=int(args.get("evaluationPercent",None) or 10), additionnalLexicon=args.get("additionnalLexicon",None), resultAnnotator=args.get("resultAnnotator","mate"), getFromFolder=args.get("getFromFolder",None))
		
	
	



