#!/usr/bin/python
# -*- coding: utf-8 -*-

#import cgi
#from xml.dom import minidom
#from xml.dom.ext import PrettyPrint
#from datetime import date
#from time     import mktime, time, asctime, localtime
from sqlite3   import connect
#from os       import environ
#from sys      import exit

#import traceback,
#import sys, os, re
#import makeXML
#import codecs

from config import *

#sys.path.append('modules')

debug=False

	
def open():
	db = connect(dbpath)
	cursor = db.cursor()	
	return db, cursor


### stuff only needed for importing xml to corpus 

def xml2SentenceListe(filename,minWords=3,letterMinQuota=0.7,upperMaxQuota=0.3, minSentPerArticle=3):
	""" xml input file: 	type est républicain CNRTL
		output: 	artiList: list of articles: one line per sentence, double new line for paragraphs
			sentences: list of good sentences: (sentenceNumber, articleNumber, sentence)
	"""
	
	#maxartis=1
	
	repoint = re.compile(ur"((?<! [0-9A-ZÇÑÄÂÀÁÅÃÆÉÈËÊĒÌÍÎÏŒØÓÒÔÚÙÜÝ])([\.\?\!…] +[»\" ]*)(?=[« ]*?[A-ZÇÑÄÂÀÁÅÃÆÉÈËÊĒÌÍÎÏŒØÓÒÔÚÙÜÝ])|_)")
	#(?<!\n[«»\-\" ])[«»\-\" ]*
	startWords=ur"(Il|Elle|Ils|Elles|À|Et|Si|On|C'est|Sur) "
	#reStartWords = re.compile(ur"(?<!\n) "+startWords,re.U)
	reFindStartWords = re.compile(ur"(\w[»\" ]*)([\- ]*?"+startWords+")",re.U)
	
	respace= re.compile(ur"\s+",re.U+re.M)
	reellipsis= re.compile(ur"\.\.\.")
	renotLetter=re.compile(ur"[\W0-9]",re.U)
	reSentEnd=re.compile(ur"([\.\?\!…][»\" ]*)$")
	reSentStart=re.compile(ur"^[«»\-\" ]*[0-9A-ZÇÑÄÂÀÁÅÃÆÉÈËÊĒÌÍÎÏŒØÓÒÔÚÙÜÝ]")
	reUpper=re.compile(ur"[A-ZÇÑÄÂÀÁÅÃÆÉÈËÊĒÌÍÎÏŒØÓÒÔÚÙÜÝ]")
	
	doc = minidom.parse(filename)
	sentences=[]
	badSent=[]
	articles = doc.getElementsByTagName("div")
	artiList=[]
	articount=0
	#totalphrasecount=0
	cc=0
	for arti in articles:
		
		keys = arti.attributes.keys()
		if "type" in keys and  arti.attributes["type"].value == "article":
			
			
			#print "___________________",
			#print arti.toprettyxml()
			sennb=0
			artigoodsents,artibadsents = [],[]
			#for h in arti.getElementsByTagName("head") :
				#print "!!!!",h.nodeName, h.attributes
			headers=[h for h in arti.getElementsByTagName("head") if not h.attributes ]
			
			parags=arti.getElementsByTagName("p")
			#print arti.childNodes,headers, parags
			if len(headers)==1 and len(parags)>0: # only if the article has a unique title and at least a paragraph
				#print "title", unicode(headers[0].childNodes[0].nodeValue)
				#print "number parags",len(parags)		
				artitext= respace.sub(u" ", unicode(headers[0].childNodes[0].nodeValue))+"\n\n"
				
				for p in parags:
					
					mapar = unicode(p.childNodes[0].nodeValue)
					# make text nice:					
					mapar = respace.sub(u" ",mapar)
					mapar = reellipsis.sub(u"…",mapar).strip()
					# sentences in a line:
					mapar = unicode(repoint.sub(ur"\1*\n",mapar).strip())
					# some sentence startes that are not preceded by correct punctuation
					if reFindStartWords.search(mapar):
						#print "\n\navant===================="
						#print mapar.encode("utf-8")
						#print "après===================="
						mapar = reFindStartWords.sub(r"\1*\n\2",mapar)#.encode("utf-8")
						cc+=1
					#adding paragraph to artitext:
					artitext+=mapar.replace("*\n","\n")+"\n\n"	
					#print mapar.encode("utf-8")
					
					#looking at eache potential sentence:
					phrlist = mapar.split("*\n")
					for s in phrlist:
						bloed=renotLetter.sub("",s)
						noUpper=reUpper.sub("",s)
						#totalphrasecount+=1
						sennb+=1
						# testing if
						# 1. enough letters, 2. not too many upper cases 
						# 3. sentence ends and 4. starts correctly
						# 5. enough words
						#if len(s.split())<minWords: print "!!!!!!!!!!!!",s,len(s.split())
						if float(len(bloed))>letterMinQuota*float(len(s)) and float(len(noUpper))>upperMaxQuota*float(len(s)) and reSentEnd.search(s) and reSentStart.search(s) and len(s.split())>=minWords:
							
							artigoodsents+=[(sennb,articount,s.strip())]
							
							
						else: 
							artibadsents+=[(sennb,articount,s.strip())]
			
			if len(artigoodsents)>=minSentPerArticle:
				if not articount%100 : print articount,"articles"
				artiList+=[artitext.strip()]
				sentences+=artigoodsents
				badSent+=artibadsents
				articount+=1
		#if articount>=maxartis: 
			#print "breaking::::::::"
			#break

	print "nb articles",len(artiList)
	#print cc,"remplacement d'urgence"
	#print sennb,"total"#,mapar.split("\n")
	print len(badSent),"bad"
	
	print len(sentences),"good"
	
	#print badSent
	#print sentences
	
	return artiList,sentences


def corpus2db(sentences, articles, corpusName):
	
	#sentences: list of good sentences: (sentenceNumber, articleNumber, sentence)
	
	db,cursor=open()
	cursor.execute("INSERT OR IGNORE INTO corpora (name) VALUES (?) ",(corpusName,))
	cursor.execute('select rowid from corpora where name=?', (corpusName,))
	corpusid, = cursor.fetchone()
	
	for i,article in enumerate(articles):	
		cursor.execute("INSERT OR IGNORE INTO articles (text, corpusid, articlenb) VALUES (?,?,?) ",(article,corpusid,i,))
	
	
	# nb of words, nb of chars, sentence, article number, phrasenumber
	for sentenceNumber, articleNumber, sentence in sentences:	
		cursor.execute("INSERT OR IGNORE INTO sentences (sentence,corpusid,articlenb,sentencenb) VALUES (?,?,?,?) ",(sentence,corpusid,articleNumber,sentenceNumber,))
	
		
	db.commit()
	db.close()
	
	
	
	
def xmldb(xmlfile, corpusName):
	
	artis,ses=xml2SentenceListe(xmlfile)
	print "artis:",len(artis)
	print "sentences:",len(ses)
	corpus2db(ses,artis,corpusName)
	

### end: stuff only needed for importing xml to corpus 

############################# distributing sentences ###############################

def addASentence(annoexoid,userid,corpusid,nbAnnos,nbWordsPers,common):
	if debug:	print"** adding a sentence"
	nbWords=0
	foundSentence=False
	db,cursor=open()
	# get half finished annotation sentences
	sqlcom="""select annoexoattribution.userid,sentences.rowid,sentences.sentence
			from
			(select rowid as sentid from
				(select  sentences.rowid, annoexoattribution.userid
					from sentences,  annoexoattribution 
					where annoexoattribution.annoexoid=?
					and sentences.rowid=annoexoattribution.sentenceid
					) group by rowid having  COUNT( userid) <?
				), sentences, annoexoattribution
			where sentid=sentences.rowid
			and annoexoattribution.annoexoid=?
			and sentences.rowid=annoexoattribution.sentenceid
					;
			"""
	u2s,s2u,s2sent={},{},{}
	slist=[]
	u2s[userid]=[]
	for u,s,sent in db.execute(sqlcom, (annoexoid,nbAnnos,annoexoid,)):
		#print u,s,sent
		u2s[u] =	u2s.get(u,[])+[s]
		s2u[s] = 	s2u.get(s,[])+[u]
		slist+=[s]
		s2sent[s]=sent
	# compute correspondance
	#print "u2s,s2u",u2s,s2u
	for s in slist: # try all half annototed sentences
		#sent=s2sent[s]
		if s not in u2s[userid]: # s not already attributed to userid
			bad=False
			if debug:	print "trying sentence",s
			for u in s2u[s]: # try all users that have this sentence
				if u!=userid:
					#computeCorrespondance
					corr=computeCommons(1,nbWordsPers,u,userid,s)
					if debug:	print "corr",corr,"with user",u
					#commonw=0
					#for commonsent in list(set(u2s[u]) & set(u2s[userid]))+[s]: # all common sentences including the hypthetical s
						
						#commonw+=len(s2sent[commonsent].split())
					#print "commonsent",list(set(u2s[u]) & set(u2s[userid])),"user",u
					#if (float(commonw)/nbWordsPers)*100 > common:
					if corr*100>common:
						bad=True
						if debug:	print "bad user:",u,
						if debug:	print "thus, bad sentence",s
						break
				if bad==True:
					if debug:	print "next sentence"
					break
			if not bad:
				foundSentence=True
				if debug:	print "found",s
				sentid,sentence=s,s2sent[s]
				break
	
	
	if not foundSentence:
		sqlcom="""SELECT sentences.rowid, sentences.sentence  FROM sentences LEFT JOIN annoexoattribution ON (sentences.rowid = annoexoattribution.sentenceid ) 
			WHERE annoexoattribution.rowid IS NULL 
			and sentences.corpusid=?"""
		sentid,sentence, = cursor.execute(sqlcom,(corpusid,)).fetchone()
	
	cursor.execute("INSERT OR IGNORE INTO annoexoattribution (annoexoid,userid,sentenceid) VALUES (?,?,?) ",(annoexoid,userid,sentid,))
	if debug:	print "added",sentid#,sentence
		
	db.commit()
	db.close()
	
def getAllAttributions(annoexoid):
	db,cursor=open()
	sqlcom="""select annoexoattribution.userid,sentences.rowid,sentences.sentence
			from sentences, annoexoattribution
			where annoexoattribution.sentenceid=sentences.rowid
			and annoexoattribution.annoexoid=?
			and sentences.rowid=annoexoattribution.sentenceid
			;
			"""
	treesqlcom="""select distinct users.realname, users.user, trees.rowid
		from trees, words, users
			where trees.sentenceid=?
			and trees.userid=?
			and words.treeid=trees.rowid
			and users.rowid=trees.userid
			;
			"""
	u2s,s2u,s2sent,s2treeuser={},{},{},{}
	slist=[]
	
	for u,s,sent in db.execute(sqlcom, (annoexoid,)):
		# for each user id, sentence id, sentence that was attributed
		#print u,s,sent
		u2s[u] =	u2s.get(u,[])+[s]
		s2u[s] = 	s2u.get(s,[])+[u]
		slist+=[s]
		s2sent[s]=sent
		treeid = cursor.execute(treesqlcom,(s,u,)).fetchone()
		if treeid: s2treeuser[s]=[(treeid[0],treeid[1],treeid[2])]
		else: s2treeuser[s]=[]
	#print "s2treeuser",s2treeuser	
	#db.commit()
	db.close()
	
	#print "getAllAttributions",u2s
	return u2s,s2u,s2sent,s2treeuser


	
	
def printAllCommons(annoexoid,nbWordsPers):
	u2s,s2u,s2sent,s2treeuser=getAllAttributions(annoexoid)
	s2wl={}
	for s in s2u.keys():
		s2wl[s]=float(len(s2sent[s].split())) 
	
	for u,s in u2s.iteritems():
		#wl=s2wl[s]
		for uu,ss in u2s.iteritems():
			if u<uu:
				#wwl=s2wl[ss]
				c=list(set(s)&set(ss))
				#if debug:	print "u",u,"uu",uu,":",s,ss,c,"common",
				cwl=0
				for sss in c:
					cwl+=s2wl[sss]
				#if debug:	print cwl,cwl/nbWordsPers

def computeCommons(annoexoid,nbWordsPers,u1=1,u2=2,hyposen=None):
	u2s,s2u,s2sent,s2treeuser=getAllAttributions(annoexoid)
	s2wl={}
	for s in s2u.keys():
		s2wl[s]=float(len(s2sent[s].split())) 
	
	
	u2s[u1]=u2s.get(u1,[])
	u2s[u2]=u2s.get(u2,[])
	c=list(set(u2s[u1])&set(u2s[u2]))
	if hyposen: c+=[hyposen]
	#print "u",u,"uu",uu,":",s,ss,c,"common",float(len(c))/len(s),
	cwl=0.0
	for sss in c:
		cwl+=s2wl[sss]
	#print cwl,cwl/nbWordsPers
	return cwl/nbWordsPers
	

def removeAttributions(annoexoid,userid):
	db,cursor=open()
	rc=cursor.execute("delete from annoexoattribution where annoexoid=? and userid=? ",(annoexoid,userid,) ).rowcount
	if debug:	print "removeAttributions: I just deleted", rc, "rows"
	db.commit()
	db.close()
	
def searchAnnoexo(annoexoid,userid):
	"""
	serch for all the annotations of userid in the annoexe with id annoexeid
	gives back loads of information 
	"""
	nbWords=0
	db,cursor=open()
	
	sqlcom="""select annoexo.corpusid, annoexo.nbAnnos, annoexo.nbWordsPers, annoexo.common
			from annoexo 
				where annoexo.rowid=?
			;
			"""
	re=cursor.execute(sqlcom,(annoexoid,)).fetchone()
	if re:
		corpusid, nbAnnos, nbWordsPers, common, = re
	else: 
		print "error"
		return 
	
	sids,sentences,articles=[],{},[]
	sqlcom="""select sentences.rowid,sentences.sentence, articles.text, annoexo.corpusid, annoexo.nbAnnos, annoexo.nbWordsPers, annoexo.common
			from sentences, articles, annoexo, annoexoattribution 
				where annoexoattribution.userid=?
				and annoexo.rowid=?
				and annoexoattribution.annoexoid=annoexo.rowid
				and sentences.rowid=annoexoattribution.sentenceid
				and articles.corpusid=annoexo.corpusid
				and sentences.articlenb=articles.articlenb
			;
			"""
	
	for sid, sentence, article, corpusid, nbAnnos, nbWordsPers, common in db.execute(sqlcom, (userid,annoexoid,)):
		l= len(sentence.split())
		nbWords+=l
		sids+=[sid]
		sentences[sid]=sentence
		articles+=[article]
	db.commit()
	db.close()
	return sids,sentences,nbWords,articles, corpusid, nbAnnos, nbWordsPers, common

def getSentencesAnnoexo(annoexoid,userid):
	"""
	get all the sentences for userid for the annoexe annotation exercice
	
	"""
	sids,sentences,nbWords,articles, corpusid, nbAnnos, nbWordsPers, common=searchAnnoexo(annoexoid,userid)
	if debug:	print "user",userid,"____________start nbWords,nbWordsPers",nbWords,nbWordsPers
	while nbWords<nbWordsPers:
		if debug:	print "________________________ nbWords,nbWordsPers",nbWords,nbWordsPers
		
		
		addASentence(annoexoid,userid,corpusid,nbAnnos,nbWordsPers,common)
		sids,sentences,nbWords,articles, corpusid, nbAnnos, nbWordsPers, common=searchAnnoexo(annoexoid,userid)
	#nbWords OK	
	print  "You got",nbWords,"words to annotate, the minimum for this exercice being",nbWordsPers,"words. Hopefully you like the sentences. Enjoy annotating!"
	return sids,sentences
		#print article

def addAnnoTrees(userid, sentences={},s2treeuser={},exos={},total=0):
	db,cursor=open()

	#print userid+"***"
	sqlcom="""select distinct sentences.rowid,sentences.sentence, users.realname, users.user ,  
			trees.rowid, exos.rowid , exos.exo
				from trees, words, users, sentences, annoexoattribution, exos, annoexo
				where trees.userid=?
				and words.treeid=trees.rowid
				and users.rowid=trees.userid
				and annoexoattribution.sentenceid=sentences.rowid
				and trees.sentenceid=sentences.rowid
				and exos.rowid=annoexo.exoid
				and annoexoattribution.annoexoid=annoexo.rowid
				
			;
			"""
	for sid,sentence, realname, user, treeid, exoid, exoname in db.execute(sqlcom, (userid,)):		
		sentences[sid]=sentence
		s2treeuser[sid]=[(realname, user, treeid)]
		exos[sid]=[(exoid, exoname)]
		total+=1
		
	#print sentences
	db.close()
	return sentences,s2treeuser,exos,total
	

def getSentences(exoid,userid,onlyUser,start,number,adminlevel):
	
	#TODO adminlevel: show all annotated sentences
	#TODO start, number

	# TODO OOOOOOOOOO: reintroduce exo!!!!!!!
	
	exos={}
	#print "***<br>***<br>***<br>***<br>",exo
	db,cursor=open()
	if exo:
		sqlcom="""select annoexo.rowid
				from annoexo 
					where annoexo.exoid=?
				;
				"""
		re=cursor.execute(sqlcom,(exoid,)).fetchone()
		if re:
			annoexoid, = re
		else: 
			print "error"
			return 
		if debug:	print "annoexoid,userid",annoexoid,userid
		sids,sentences = getSentencesAnnoexo(annoexoid,userid)
		
		u2s,s2u,s2sent,s2treeuser = getAllAttributions(annoexoid)
		for s in sids:
			
			exos[s]=[(exoid,exo)]
	else:
		sentences,s2treeuser,exos=addAnnoTrees(userid)
		sids=sentences.keys()
	
	#print sentences
	return sentences,s2treeuser,exos,len(sids)
	
	
	
#def attributeSentences
	

if __name__ == "__main__":
	print "bonjour"
	
	# insert in corpus !!!!!!!!!!!!!! important !!!!!!!
	#xmldb("corpus/Annee2003/2003-02-24.xml","EstRep-2003-02-24")
	####################################################"
	for us in [5,6,7,8]: removeAttributions(1,us)
	#removeAttributions(1,6)
	#removeAttributions(1,7)
	#removeAttributions(1,4)
	##si,se = getSentencesAnnoexo(1,1)
	#print si#,se
	#print len(si),"sentences"
	#print" __________________"
	#si,se = getSentencesAnnoexo(1,2)
	#print si#,se
	#print len(si),"sentences"
	#print" __________________"
	#si,se = getSentencesAnnoexo(1,8)
	#print si#,se
	#print len(si),"sentences"
	#removeAttributions(1,3)
	print "========="
	a,b,c = getAllAttributions(1)
	
	print "(partly) distributed sentences",len(b)
	print b
	di={}
	for s,ul in b.iteritems():
		di[len(ul)]=di.get(len(ul),0)+1
	
	print "annotation number to sentences",di
	#computeCommons(1,1,2)
	printAllCommons(1,300)
	
	
	#c=0
	#for s in se:
		#for w in s.split():
			#c+=1
			#print c,w
	
	#addASentence(1,1,1,3,300,33)
	
	