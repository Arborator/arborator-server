#!/usr/bin/python
# -*- coding: utf-8 -*-

#######################################################################################
# this file contains functions to update the trees of a specific user, in particular for the update when a new parse model has been trained and applied

#simple usage, for example, to import a group of mate parse files into the database:
	#updateParseResult("test_mini_db", "corpus/mate/", filepattern="*_Parse")
#this will import all files in corpus/mate that fit the pattern into the database overwriting the corresponding user's tree in the corresponding sample
		
#######################################################################################

import sys, os, re, json, codecs
from time import time
from glob import glob

import database
import conll


debug=False

	
def enterNewAnnotation(sql, db, cursor, sentences, textid, annotatorName="parser", notenter=["order"], sentencefeatures={}, tokname="t"):
	"""
	takes a list of nodedics (sentences) and puts them into the database erasing an existing annotation
	
	sql, db, cursor of open database
	sentences: nodedics to enter
	textid: textid of the sample to be modified
	annotatorName: name to be modified (TODO: check what happens if annotatorName not yet present in the db)
	notenter: features to skip
	sentencefeatures: features per sentence (to be added below the sentence, for example parser information)
	
	"""
	print "entering",len(sentences),"annotations by", annotatorName,"into textid",textid
	
	
	
	userid = sql.enter(cursor, "users",["user"],(annotatorName,))
	sql.realname(annotatorName, cursor)
	if not userid:
		print "the user is not in the database"
		return
	
	
	scounter,wcounter=0,0
	ti = time()

	r = sql.getall(cursor, "sentences",["textid"], [textid])
	if len(r) != len(sentences):
		print "something fishy here:", len(sentences), "sentences to enter onto",len(r),"existing sentences"
		return
	
	for nodedic, (sentenceid,nr,sentence,textid) in zip(sentences,r): # for every sentence
		if debug: print "_____",sentenceid, nr, sentence, textid
		inssentence=" ".join([nodedic[j].get(tokname,"") for j in sorted(nodedic)])
		
		if sentence.replace(" ","") != inssentence.replace(" ",""):
			print "something fishy here:", inssentence, "analysis to be put on sentence",sentence
			return
		
		# remove everything of the existing tree
		cursor.execute("delete from features where treeid in (select trees.rowid from trees where trees.sentenceid =? and trees.userid=?);",(sentenceid,userid,))
		cursor.execute("delete from links    where treeid in (select trees.rowid from trees where trees.sentenceid =? and trees.userid=?);",(sentenceid,userid,))
		cursor.execute("delete from trees    where trees.sentenceid =? and trees.userid=?;",(sentenceid,userid,))
		
		# put the new tree in
		ws, sent, treeid = sql.enterTree(cursor, nodedic, sentenceid, userid, notenter=notenter, intokenname=tokname)
		
		if sentencefeatures:
			for a,v in sentencefeatures[i].iteritems():
				
				cursor.execute("UPDATE sentencefeatures SET value=? WHERE sentenceid=? and attr=?",(v,sentenceid,a,))# TODO: check what happens if new sentencefeature attribute
				#sql.enter(cursor, "sentencefeatures",["sentenceid","attr","value"],(sentenceid,a,v,))
			
			
	db.commit()
	print "this sample took",time()-ti,"seconds to enter"
	
	
	
	
def updateParseResult(projectname, conlldirpath, filepattern="*.trees.conll14", annotatorName="parser", removeToGetDB="-one-word-per-line.conll14_parse"):
	sql = database.SQL(projectname)
	db,cursor=sql.open()
	print  "updateTrees:",glob(os.path.join(conlldirpath, filepattern))
	for filename in glob(os.path.join(conlldirpath, filepattern)):
		print "entering",filename
		sentences=conll.conllFile2trees(filename)
		dbtextname = os.path.basename(filename)[:-len(removeToGetDB)]
		textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
		
		if not textid:
			print "couldn't find the database named",textid
			return
		enterNewAnnotation(sql, db,cursor, sentences, textid, annotatorName=annotatorName)







	
	

if __name__ == "__main__":
	print "bonjour"
	updateParseResult("OrfeoGold2016", "mate/parses/2016-07-13/", filepattern="*_Parse")
	print "ok"
	
	
	