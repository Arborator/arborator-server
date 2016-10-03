#!/usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import print_function

import glob, os, conll, codecs, pinyin #, json #, goslate
from conll import conll2trees, trees2conll10
from googleapiclient.discovery import build

def translate(q,source='zh',target='en', maxiAtOnce=100):
	
	service = build('translate', 'v2', developerKey='AIzaSyBES6QPcKqvY4pHsaMkr8piFsS2Mwe029w')
	translations=[]
	
	for wordgroup in [q[i:i+maxiAtOnce] for i in xrange(0, len(q), maxiAtOnce)]:
		res = service.translations().list(source=source, target=target, q=wordgroup ).execute()
		translations+=[td["translatedText"] for td in res["translations"]]
		
	return translations

#translate(u"准许 一 位 人士 入境 的 权力".split())


for conllinfile in glob.glob(os.path.join("corpus/conll/", 'CONV*.*')):
	
	print conllinfile
	trees=conll2trees(conllinfile)
	path,base = os.path.split(conllinfile)
	translateDic={}
	counter=0
	for tree in trees:
		for i,node in tree.iteritems():
			node["tag2"]=pinyin.get(node["t"])
			translateDic[node["t"]]=None
		counter+=1
		if not counter%100: print counter,"trees"
	
	words = sorted(translateDic)
	print len(words), "words"
	trads = translate(words)
	translateDic = dict(zip(words, trads))
	print len(translateDic),"translations"
	for tree in trees:
		for i,node in tree.iteritems():
			node["gloss"]=translateDic[node["t"]]
		counter+=1
		if not counter%100: print counter,"trees"
			#lines+=[u" ".join(words+[u"．"])]
	trees2conll10(trees,path+"/"+"UD-"+base[len("CONV-CORREC-"):])
	





