#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, json, codecs, copy, collections, re, hashlib, os, glob
from itertools import izip

#d = defaultdict(int)

def readconll(gold,parse,attached=True):
	"""
	attached: only count relation if governor is correctly predicted
	"""
	actual={} # actual relation : number
	predic={} # predicted relation : number
	actualpredic={} # actual relation to dic { predicted relation : number }
	with codecs.open(gold,"r","utf-8") as goldf, codecs.open(parse,"r","utf-8") as parsef:
		for g, p in izip(goldf, parsef):
			gcells = g.split('\t')
			pcells = p.split('\t')
			if len(gcells)==14:
				nr, t, lemma, lemma2, tag, tag2, morph, morph2, head, ghead, rel, grel, _, _ = gcells
				nr, t, lemma, lemma2, tag, tag2, morph, morph2, head, phead, rel, prel, _, _ = pcells
				if (not attached) or (attached and ghead==phead):
					#print ghead,phead,grel,prel
					actualpredic[grel]=actualpredic.get(grel,{})
					actualpredic[grel][prel]=actualpredic[grel].get(prel,0)+1
					predic[prel]=predic.get(prel,0)+1
				actual[grel]=actual.get(grel,0)+1
	return actual, predic, actualpredic

def writeTable(conf,actual, predic, actualpredic, info):
	conf.write("\t".join([info,"#"]+sorted(actualpredic))+"\n")
	for grel in sorted(actualpredic):
		conf.write("\t".join([grel,str(actual[grel])]+[str(actualpredic[grel].get(prel,0)) for prel in sorted(actualpredic)])+"\n")
	conf.write("\n")
	
	ftoline={}
	alltp=0
	allpredic=0
	allactual=0
	conf.write("\t".join(["",	"#",		"tp",		"found",		"precision",		"recall",		"fscore"])+"\n")
	for grel in sorted(actualpredic):
		tp=actualpredic[grel].get(grel,0)
		precision=float(tp)/predic[grel]
		recall=float(tp)/actual[grel]
		alltp+=tp
		allpredic+=predic[grel]
		allactual+=actual[grel]
		
		if precision+recall:	fscore=round(2.0*precision*recall/(precision+recall),2)
		else: fscore=0.0
		line="\t".join([grel,	str(actual[grel]),str(tp),	str(predic[grel]), 	str(round(precision,2)),str(round(recall,2)),	str(fscore)])+"\n"
		ftoline[fscore]=ftoline.get(fscore,[])+[line]
		conf.write(line)
	conf.write("\n")
	
	conf.write("\t".join([info,	"#",		"tp",		"found",		"precision",		"recall",		"fscore"])+"\n")
	for fscore in sorted(ftoline,reverse=True):
		conf.write("".join(ftoline[fscore]))
	conf.write("\n")
	
	conf.write("\t".join(["#",		"tp",		"found",		"precision",		"recall",		"fscore"])+"\n")
	precision=float(alltp)/allpredic
	recall=float(alltp)/allactual
	if precision+recall:	fscore=round(2.0*precision*recall/(precision+recall),2)
	else: fscore=0.0
	line="\t".join([str(allactual),str(alltp),	str(allpredic), 	str(round(precision,2)),str(round(recall,2)),	str(fscore)])+"\n"
	conf.write(line)
	conf.write("\n")

def confusion(gold,parse):
	actual, predic, actualpredic= readconll(gold,parse,attached=False)
	with codecs.open(parse+".confusion.tsv","w","utf-8") as conf:
		writeTable(conf,actual, predic, actualpredic, "corr func")
		
	actual, predic, actualpredic= readconll(gold,parse,attached=True)
	with codecs.open(parse+".confusion.tsv","a","utf-8") as conf:
		writeTable(conf,actual, predic, actualpredic, "corr attach")
		
		
		
		
if __name__ == "__main__":
	confusion("test","emptytest_parse")

