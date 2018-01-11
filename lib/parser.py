# -*- coding: utf-8 -*-
#!/usr/bin/python
import argparse, datetime, glob, os
from mate import parsing, createNonExistingFolders
from retokenisation import retokeniser
from conll import makeEmpty

memory="40G"

def parseFile(infile, lemodel, tagmodel, parsemodel, folderpref="mate/parses/"):
	timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
	if folderpref: prelimfolder=folderpref+"_prelim/"
	else: prelimfolder=folderpref+timestamp+"_prelim/"
	parsefile = parsing(infile=infile, lemodel=lemodel, tagmodel=tagmodel,parsemodel=parsemodel , outfolder=prelimfolder, memory=memory) # , depparse=False
	#parsefile="mate/parses/2016-09-22_01:18/Louise_Liotard_F_85_et_Jeanne_Mallet_F_75_SO-2-one-word-per-line.conll14_parse"
	print "retokenizing..."
	newname=retokeniser(parsefile, addtoout="_retok")
	print "retokenization done"
	if folderpref: outfolder=folderpref+"/"
	else: outfolder=folderpref+timestamp+"/"
	createNonExistingFolders(outfolder)
	emptyname=makeEmpty(newname, outfolder=outfolder)
	parsefile = parsing(infile=emptyname, lemodel=modeldir+args.get("lemmodel",None), tagmodel=modeldir+args.get("tagmodel",None), parsemodel=modeldir+args.get("parsemodel",None), outfolder=outfolder, memory="40G")


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='wrapper for mate parser with orfeo dictionaries')
	
	parser.add_argument('-ci','--conllinfile', help='file to be parsed', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-cf','--conllfilter', help='files to be parsed', type=lambda s: unicode(s, 'utf8'), required=False)
	parser.add_argument('-md','--modeldir', help='folder containing the models', type=lambda s: unicode(s, 'utf8'), required=True)
	parser.add_argument('-lm','--lemmodel', help='lemmatizing model', type=lambda s: unicode(s, 'utf8'), required=False, nargs='?', default="LemModel")
	parser.add_argument('-tm','--tagmodel', help='tagging model', type=lambda s: unicode(s, 'utf8'), required=False, nargs='?', default="TagModel")
	parser.add_argument('-pm','--parsemodel', help='parsing model', type=lambda s: unicode(s, 'utf8'), required=False, nargs='?', default="ParseModel")

	args = vars(parser.parse_args())
	modeldir=args.get("modeldir",".")
	infile=args.get("conllinfile",None)
	conllfilter=args.get("conllfilter",None)
	lemodel=modeldir+args.get("lemmodel",None)
	tagmodel=modeldir+args.get("tagmodel",None)
	parsemodel=modeldir+args.get("parsemodel",None)
	if infile:	
		parseFile(infile, lemodel, tagmodel, parsemodel)
	elif conllfilter:
		timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
		for infile in glob.glob(conllfilter):
			head, tail = os.path.split(infile) # put the parse output next to the infile
			parseFile(infile, lemodel, tagmodel, parsemodel, folderpref=head+"/"+timestamp)
	
	
	# python parser.py -ci mate/AParser/echantillon/Louise_Liotard_F_85_et_Jeanne_Mallet_F_75_SO-2-one-word-per-line.conll14 -lm mate/AParser/LemModel -tm mate/AParser/TagModel -pm mate/AParser/ParseModel 
	# python parser.py -ci mate/AParser/echantillon/Louise_Liotard_F_85_et_Jeanne_Mallet_F_75_SO-2-one-word-per-line.conll14 -md mate/AParser/
	# python parser.py -ci mate/AParser/echantillon/Louise_Liotard_F_85_et_Jeanne_Mallet_F_75_SO-2-one-word-per-line.conll14 -md mate/AParser/
	# python parser.py -cf "mate/AParser/echantillon/*.conll14" -md mate/AParser/
	# python parser.py -cf "mate/AParser/tcof/*.conll14" -md mate/AParser/
	
	
	