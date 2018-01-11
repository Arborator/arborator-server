#!/usr/bin/python
# -*- coding: utf-8 -*-

#######################################################################################
# this file contains loads of useful functions
# - for importing files containing treebanks (parse files) into the arborator
# - and also for correction during or after the import process

#simple usage, for example, to import a group of mate parse files into the database:
	#readinallmates("test_mini_db","corpus/mate/",filepattern="*_Parse")
#this will import all files in corpus/mate that fit the pattern into the database creating a new text under the name of the file
#the filename will be abreviated: see the readinallmates function itself
		
#######################################################################################


debug=False
#debug=1
#debug=2
#debug=3

maxlength=5000 # maxlength of words per sentence, longer ones are ignored

logfile=None
#logfile="log.treebankfiles.txt"


# problem of token names:
# import token name: how the token is named in the xml file: defined here, will also be used for the internal storage of read in conll files
# export token name: how the token feature is encoded in the database: defined in the project's config file

tokenname="t"


# central functions:
# rhapsodie2Sentences: reads in rhapsodie file format into tree internal representation
# correctRhapsodie: corrects a tree list following correction dictionaries
# checkSentence: corrects an individual tree
# enterSentences: puts a tree list into the database





#import cgi
from xml.dom import minidom
#from xml.dom.ext import PrettyPrint
from datetime import date
from time     import mktime, time, asctime, localtime
from sqlite3   import connect
from os       import environ
from sys      import exit
import sys, os, re, json
import codecs,urllib
import collections
import traceback, copy
from glob import glob


try: 	import jellyfish
except: pass
try:	from nltk.featstruct import unify
except:	pass

import database
import config
import conll

# erase old logfile
if logfile:
	lf=codecs.open(logfile,"w","utf-8")
	lf.close()

#def simpleEnterFolder(sql, annotatorName):
	#for filename in glob(os.path.join(conlldirpath, filepattern)):
	
def simpleEnterSentences(sql, trees, dbtextname, annotatorName, eraseAllAnnos, sentencefeatures={}, preserveSampleWithSameName=False):
	"""
	takes a list of trees (nodedics)
	puts them into the database
	if preserveSampleWithSameName: add _ to names to create new name of sample
	"""
	ti = time()
	db,cursor=sql.open()
	if preserveSampleWithSameName:
		while sql.getUniqueId(cursor, "texts", ["textname"],[dbtextname])!=None:
			dbtextname+="_"
	textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
	print "textid",textid
	if eraseAllAnnos: 
		db.close()
		sql.removeText(textid)
		db,cursor=sql.open()
		textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
		print "textid",textid
	if debug: 
		print "found",len(trees),"trees to enter"
		print "entering an annotation by",annotatorName, "into annotations of textid",textid
			
	userid = sql.enter(cursor, "users",["user"],(annotatorName,))
	sql.realname(annotatorName, cursor)
	if not userid:
		print "the user is not in the database"
		return
	
	scounter,wcounter=0,0

	for i,tree in enumerate(trees): # for every sentence
		scounter+=1
		sentence=" ".join([tree[j].get("t","") for j in sorted(tree)])
		#cursor.execute("select rowid from sentences,texts  where nr=? and sentence=?;",
		sentenceid = sql.getUniqueId(cursor, "sentences", ["nr","sentence","textid"], [scounter,sentence,textid])
		#print "found sentenceid",sentenceid
		if not sentenceid:
			sentenceid = sql.enter(cursor, "sentences",["nr","sentence","textid"],(scounter,sentence,textid,))
			#print "made sentenceid",sentenceid
		sql.enter(cursor, "sentencesearch",["nr","sentence","textid"],(scounter,sentence,textid,))
		if sentencefeatures:
			for a,v in sentencefeatures[i].iteritems():
				sql.enter(cursor, "sentencefeatures",["sentenceid","attr","value"],(sentenceid,a,v,))
		#print tree
		ws, sent, treeid = sql.enterTree(cursor, tree, sentenceid, userid)
		#print "ws, sent, treeid",ws, sent, treeid
		wcounter+=ws
		#if debug:print "----",scounter,"of",len(tree),sent.encode("utf-8")," - it took",time()-ti,"seconds up to now for",wcounter, "words - ", float(wcounter)/(time()-ti),'words per second.'
	
	db.commit()
	db.close()	
	
	if debug:print "it took",time()-ti,"seconds"
	return textid
	
def enterSentences(sql, cursor, sentences, filename, textid, annotatorName, eraseAllAnnos, notenter=["order"], sentencefeatures={}, defaultAnnotatorName="parser", tokname=None):
	"""
	takes a list of nodedics (sentences)
	
	puts them into the database
	
	"""
	#print "found",len(sentences),"sentences to enter"
	
	if debug: print "entering",filename,"as annotation by",annotatorName, "into annotations of textid",textid
	
	if not tokname:tokname=tokenname
	
	shortname = filename.split("/")[-1]
	
	userid = sql.enter(cursor, "users",["user"],(annotatorName,))
	sql.realname(annotatorName, cursor)
	if not userid:
		print "the user is not in the database"
		return
	
	
	scounter,wcounter=0,0
	ti = time()
	if eraseAllAnnos:
		# TODO : remove trees completely with all features!
		sql.clean(cursor, "sentences",["textid"],(textid,)) # erase all existing sentences for this textid
		sql.clean(cursor, "sentencesearch",["textid"],(textid,)) # erase all existing sentences for this textid
		
		#{0: {'deps': [4]}, 1: {'head': 2, 'word': u'``', 'deps': [], 'lemma': u'--', 'tag': u'$(', 'rel': u'-PUNCT-', 'id': 1}, 2: {'head': 4, 'word': u'Ross', 'deps': [1, 3], 'lemma': u'--', 'tag': u'NE', 'rel': u'SUBJ', 'id': 2}, 3: {'head': 2, 'word': u'Perot', 'deps': [], 'lemma': u'--', 'tag': u'NE', 'rel': u'APP', 'id': 3}, 4: {'head': 0, 'word': u'w\xe4re', 'deps': [2, 5, 8], 'lemma': u'--', 'tag': u'VAFIN', 'rel': u'ROOT', 'id': 4}, 5: {'head': 4, 'word': u'vielleicht', 'deps': [], 'lemma': u'--', 'tag': u'ADV', 'rel': u'ADV', 'id': 5}, 6: {'head': 8, 'word': u'ein', 'deps': [], 'lemma': u'--', 'tag': u'ART', 'rel': u'DET', 'id': 6}, 7: {'head': 8, 'word': u'pr\xe4chtiger', 'deps': [], 'lemma': u'--', 'tag': u'ADJA', 'rel': u'ATTR', 'id': 7}, 8: {'head': 4, 'word': u'Diktator', 'deps': [6, 7, 9], 'lemma': u'--', 'tag': u'NN', 'rel': u'PRED', 'id': 8}, 9: {'head': 8, 'word': u"''", 'deps': [], 'lemma': u'--', 'tag': u'$(', 'rel': u'-PUNCT-', 'id': 9}}
		
		
		#for snode in sentences:
			#print snode

		for i,tree in enumerate(sentences): # for every sentence
			#print "ooooooooooooooooo",len(tree)
			
			if len(tree)<maxlength:
				scounter+=1
				
				sentence=" ".join([tree[j].get(tokname,"") for j in sorted(tree)])
				sentenceid = sql.enter(cursor, "sentences",["nr","sentence","textid"],(scounter,sentence,textid,))
				sql.enter(cursor, "sentencesearch",["nr","sentence","textid"],(scounter,sentence,textid,))
				#print sentencefeatures
				if tree.sentencefeatures:
					for a,v in tree.sentencefeatures.iteritems():
						sql.enter(cursor, "sentencefeatures",["sentenceid","attr","value"],(sentenceid,a,v,))
				
				# enter first tree for sentencewcounter, sent, treeid
				ws, sent, treeid = sql.enterTree(cursor, tree, sentenceid, userid, notenter=notenter, intokenname=tokname)
				wcounter+=ws
				
				if debug:print "----",scounter,"of",len(sentences),sent.encode("utf-8")," - it took",time()-ti,"seconds up to now for",wcounter, "words - ", float(wcounter)/(time()-ti),'words per second.'
				#' expected time remaining', float(scounter)/(time()-ti)*(len(sentences)-scounter)
			else:
				print "ooooooh"
				if logfile:
					f=codecs.open("toolong.txt","a","utf-8")
					f.write("\t".join([filename, str(len(nodes)),unicode(tree)])+"\n")
					f.close()
				
					f=codecs.open(logfile,"a","utf-8")
					f.write("tooooooooooooooooolong: \n"+ filename+"\n"+unicode(tree)+"\n\n\n")
					f.close()

	else: # not erasing, adding
		#print "enterSentences qqq"
		
		r = sql.getall(cursor, "sentences",["textid"], [textid])

		mini=0
		
		for tree in sentences: # for every sentence
			if len(tree)<maxlength:
				
				
				#print tree
				
				distas=[]
				
				scounter+=1
				inssentence=" ".join([tree[j].get(tokname,"") for j in sorted(tree)])
				entered=False
				for sentenceid,nr,sentence,textid in r[mini:]: 
					#print "found:",sentence
					#print "looking for:",inssentence
					#print len(tree),len(sentence.split()),len(tree)==len(sentence.split())
					if sentence==inssentence:
						mini=nr
						origdic=getorigdic(sql,cursor,sentenceid,defaultAnnotatorName)
						#origdic=sql.gettree(sid=sentenceid,username=defaultAnnotatorName)["tree"]
						if len(origdic)==len(tree):
							if debug: print "standard entry",inssentence
							ws, sent, treeid = sql.enterTree(cursor, tree, sentenceid, userid, notenter=notenter, intokenname=tokname)
						else:
							if debug: print "try fuzzy entry",inssentence
							ws, sent, treeid = fuzzyEnterSentence(tree,origdic,sql, cursor, filename, textid, annotatorName, scounter,sentence, sentenceid, inssentence, userid, notenter=notenter)
						wcounter+=ws
						if debug :
							if sent:print "---",sent.encode("utf-8"),"sentence"
							else:
								print "ooooooh"
								if logfile:
									
									f=codecs.open(logfile,"a","utf-8")
									f.write("no sentence: \n"+ filename+"\n"+unicode(tree)+"\n\n\n")
									f.close()
								
						entered=True
						break
					else: 
						distas+=[(jellyfish.levenshtein_distance(unicode(sentence).encode("utf-8"), unicode(inssentence).encode("utf-8")), (tree, sentenceid, sentence))]
					
				if not entered: 
					print "couldn't find '"+inssentence+"' in", shortname,"! Haven't yet entered the annotation"
					if distas:
						tree, sentenceid, sentence = sorted(distas)[0][1] # get best sentence
						print "will try to enter instead\n",inssentence,"\ninto\n",sentence
						origdic=getorigdic(sql,cursor,sentenceid,defaultAnnotatorName)
						ws, sent, treeid = fuzzyEnterSentence(tree,origdic,sql, cursor, filename, textid, annotatorName, scounter,sentence, sentenceid, inssentence, userid, notenter=notenter)
						wcounter+=ws
					else:
						print "no data under that name:",shortname
						#enterSentences(sql, cursor, sentences, filename, textid, annotatorName, eraseAllAnnos=True, notenter=notenter, sentencefeatures=sentencefeatures, defaultAnnotatorName=defaultAnnotatorName, tokname=tokname)
						
						
			
			else:
				print "ooooooh"
				if logfile:
					f=codecs.open("toolong.txt","a","utf-8")
					f.write("\t".join([filename, str(len(nodes)),unicode(tree)])+"\n")
					f.close()
				
					f=codecs.open(logfile,"a","utf-8")
					f.write("tooooooooooooooooolong: \n"+ filename+"\n"+unicode(tree)+"\n\n\n")
					f.close()
			
			
	#db.commit()
	if debug:print "it took",time()-ti,"seconds"

def getorigdic(sql,cursor,sentenceid,defaultAnnotatorName):
	sqltokenname=sql.projectconfig["shown features"]["0"]	
	
	dbexe = cursor.execute("""select features.nr, trees.rowid, trees.sentenceid, features.attr, features.value 
						from trees, features, users
						where trees.rowid=features.treeid and trees.userid=users.rowid and users.user=? and trees.sentenceid=?;""",(defaultAnnotatorName, sentenceid,))
	
	tree={}
	for nr,treeid,sid,attr,value, in dbexe.fetchall():
		#print nr,treeid,sid,attr,value
		tree[nr]=tree.get(nr,{})
			
		if attr==sqltokenname:
			tree[nr][tokenname]=value
		else:
			tree[nr][attr]=value
		govdic={}
		for _,_,_,govid,function in sql.getall(cursor, "links", ["treeid", "depid"], [treeid, nr]):
			govdic[govid]=function
		tree[nr]["gov"]=govdic
	#print "888888888888888888",tree
	#dic={}
	#for _,sid,a,v in self.getall(cursor, "sentencefeatures", ["sentenceid"], [sid]):
		#dic[a]=v
	#dic["tree"]=tree ## maybe test whether "tree" is already an attribute?
	
	
	#origdic=sql.gettree(sid=sentenceid,username=defaultAnnotatorName)["tree"]
	#for i in origdic:
		#origdic[i][tokenname]=origdic[i][sqltokenname]
		#del origdic[i][sqltokenname]
	return tree
	
def fuzzyEnterSentence(tree,origdic, sql, cursor, filename, textid, annotatorName, scounter,sentence, sentenceid, inssentence, userid, notenter):
	ws, sent, treeid =0,None,None
	# t=sql.projectconfig["shown features"]["0"]
	restree = correcttokens(copy.deepcopy(tree),origdic)
	print "end strict stuff"
	if not restree: 
		print "\n\nthis didn't work out. we try again, less strict"
		restree = correcttokens(copy.deepcopy(tree),origdic, strict=False)
	if not restree:
		print "ooooooh"
		if logfile:
			f=codecs.open(logfile,"a","utf-8")
			f.write("\t".join([filename,str(textid), annotatorName, str(scounter),sentence])+"\n\n\n")
			f.close()
		
	if len(origdic)==len(restree):
		print "will really enter ",inssentence,"into",sentence,"!!!!\n"
		#if sentence.startswith("alors j' emprunte la rue de Strasbourg"):
			#for i,d in  restree.iteritems():print i,d 
			#for i,d in  origdic.iteritems():print i,d 
			#print sentence
			#1/0
			
		ws, sent, treeid = sql.enterTree(cursor, restree, sentenceid, userid, newTokens=False, notenter=notenter, intokenname=tokenname)
	else: 
		print "could not enter!!!!!"
	return ws, sent, treeid 

	
def correcttokens(tree, origdic, strict=True):
	"""
	tree is checked
	origdic is the parser's annotation whose tokens are relevant
	strict: first trying to match exactly the parser's tokens
	"""
	if debug: 
		print "\n=================== start correcttokens tree"
		if strict:print "strict!!!"
		else: print "not strict!!!!"
		for i,d in  tree.iteritems():print i,d[tokenname],d 
		print "with origdic"
		for i,d in  origdic.iteritems():print i,d[tokenname],d 
	
	newtree={}
	try:
		for nr in sorted(origdic):
			#print origdic[nr]
			#print nr, origdic.get(nr,{tokenname:"___________verystrange"})[tokenname],tree.get(nr,{tokenname:"___________verystrange"})[tokenname]
			
			if nr in tree and tree[nr][tokenname]==origdic[nr][tokenname]: # found perfect matching token, copying everything to the new node
				#print "ok"
				newtree[nr]=tree[nr]
			else:
				#print "___problem"
				i=0
				intdic,normal2ins={},{}
				
				smalltoks=tree[nr][tokenname].encode("utf-8").split()
				if strict:
					
					while tree[nr][tokenname].startswith(" ".join([origdic[ii][tokenname] for ii in range(nr,nr+i+1)])): # making the insertion dict if words fit on one another:
						intdic["i"+str(i+1)]=origdic[nr+i]
						normal2ins[nr+i]="i"+str(i+1)
						i+=1
				else: 
					while i<len(smalltoks) and jellyfish.levenshtein_distance(    origdic[nr+i][tokenname].encode("utf-8"), smalltoks[i]   ) / len ( smalltoks[i] ) <= .5:
						intdic["i"+str(i+1)]=origdic[nr+i]
						normal2ins[nr+i]="i"+str(i)
						i+=1
				#print intdic
				
				if len(intdic)>1: # we found a token that has to be separated
					for ind in intdic: # copy good internal governors
						newgov={}
						for govi in intdic[ind]["gov"]:
							if govi in normal2ins: newgov[normal2ins[govi]]=intdic[ind]["gov"][govi]
						intdic[ind]["gov"]=newgov
					intdic["i1"]["gov"]={"i0":"root"} 
					intdic["i"+str(i)]["child"]=True
					#print intdic
					newtree=integrate(tree,nr,intdic)
					return correcttokens(newtree, origdic, strict) # start over because indeces changed
					
				else: # just wrong token for example ce != c'
					#print "changed token from",tree[nr][t],"to",origdic[nr][t]
					newtree[nr]=tree[nr]
					newtree[nr][tokenname]=origdic[nr][tokenname]
	except Exception, err:
		if debug:print traceback.format_exc()
		if logfile:
			f=codecs.open(logfile,"a","utf-8")
			f.write(traceback.format_exc()+"\n\n\n")
			f.close()
		#1/0
		return {}
	return newtree	
	
	
def enterConll(dbname,filename,annotatorName=None, eraseAllAnnos=False, dbtextname=None, corrdic={"tag":"cat","t":"orthotext"}): 
	""" 
	TODO: think about when to erase all tokens and features of existing annotations. maybe put warnings and confirm?
	"""
	sql = database.SQL(dbname)
	db,cursor=sql.open()
	sentences=conll.conllFile2trees(filename,corrdic)
	
	if dbtextname:
		textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
	else:
		#M016.XML.Paola.trees.conll10
		if filename[-14:-2]=='.trees.conll':
			dbtextname=".".join(filename.split("/")[-1].split(".")[:-3])
			
			# TODO: remove:
			dbtextname= "Rhap-"+dbtextname[:2] + "0" + dbtextname[2:4]+"-Synt.xml"
			#print dbtextname
			
			textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
			#print textid
			if not annotatorName: annotatorName=filename.split(".")[-3]
		else:
			dbtextname=filename.split("/")[-1]
			textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
			
	enterSentences(sql,cursor,sentences,filename, textid,annotatorName,eraseAllAnnos )
	db.commit()
	db.close()
	return len(sentences)
	
	
def uploadConll(sql, filename, annotatorName=None, eraseAllAnnos=True): 
	""" 
	important function, called from project.cgi!!!
	
	"""

	db,cursor=sql.open()
	sentences=conll.conllFile2trees(filename)
	#print sentences
	if not annotatorName: annotatorName=sql.importAnnotatorName
	
	dbtextname = filename.split("/")[-1].decode("utf-8")
	for exten in ".conll10 .conllu .conll14 .malt .tab .txt.conll_parse .txt.conll_parse.orig".split():
		if dbtextname.endswith(exten):
			dbtextname=dbtextname[:-len(exten)]
			break
	
	#if dbtextname.endswith("") or dbtextname.endswith("") or  dbtextname.endswith("") or dbtextname.endswith("") or dbtextname.endswith("") or dbtextname.endswith("") :
		#dbtextname=".".join(dbtextname.split(".")[:-1])
	
	textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
	
			
	enterSentences(sql, cursor, sentences, filename, textid, annotatorName, eraseAllAnnos, tokname="t" )
	db.commit()
	db.close()
	return len(sentences)


def enterDegraded(project, filenameGood, filenameDegraded=None, goodAnnotatorName="prof", degradedAnnotatorName="parser", eraseAllAnnos=True): 
	"""
	if filenameDegraded is not given, the files have to be named xxx.orig and xxx.deg
	"""
	if not filenameDegraded: 
		filenameDegraded=filenameGood[:-len(".orig")]+".deg"
		
	dbtextname = filenameGood.split("/")[-1] #.decode("utf-8")
	if dbtextname.endswith(".orig"): dbtextname=dbtextname[:-len(".orig")]
	for exten in ".conll10 .conll14 .malt .tab .txt.conll_parse .txt.conll_parse.orig".split():
		if dbtextname.endswith(exten):
			dbtextname=dbtextname[:-len(exten)]
			break
		
	sql=database.SQL(project)
	print filenameGood
	trees=conll.conllFile2trees(filenameGood)
	
	simpleEnterSentences(sql, trees, dbtextname, annotatorName=goodAnnotatorName, eraseAllAnnos=True)
	
	#db,cursor=sql.open()
	#textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
	#enterSentences(sql, cursor, trees, dbtextname, textid, goodAnnotatorName, eraseAllAnnos=True)
	#db.commit()
	#db.close()
	
	trees=conll.conllFile2trees(filenameDegraded)
	textid=simpleEnterSentences(sql, trees, dbtextname, annotatorName=degradedAnnotatorName, eraseAllAnnos=False)
	print "==",sql.getNumberTokensPerText(textid, recompute=True)
	
	
		
		
		
def update(d, u):
		""" used in rhapsodie2Sentences"""
		
		for k, v in u.iteritems():
			if isinstance(v, collections.Mapping):
				r = update(d.get(k, {}), v)
				d[k] = r
			else:
				d[k] = u[k]
		return d
	
	
def rhapsodie2Sentences(filename):
		
		doc = minidom.parse(filename)
		
		pivs, tokens, lexemes, deps, nodedics = {},{},{},{},{}
		wtypedic={"pivot":pivs,"tokens":tokens,"lexemes":lexemes}
		dtypedic={"syntax":deps}
		
		# all dictionaries look like this: u'lex565': (<DOM Element: word at 0xb617e2cc>, 566)
		for wordgroup in doc.getElementsByTagName("words"):# looking at all the wordgroups
			currentdic = wtypedic.get(wordgroup.getAttribute("type"),None) # if they are mentioned in the wtypedic, read them in
			if currentdic=={}:
				order=0
				for w in wordgroup.getElementsByTagName("word"):
					order+=1
					currentdic[w.getAttribute("id")]=w,order
		
		depcounter = 0
		sentences,sentencefeatures=[],[]
		for depgroup in doc.getElementsByTagName("dependencies"):
			currentdic = dtypedic.get(depgroup.getAttribute("type"),None)
			if currentdic=={}: # i found the syntax depgroup
				for dependency in depgroup.getElementsByTagName("dependency"): # for each dependency = one sentence
					
					lexiddic = {}
					nodes={}
					sentencefeature={}
					for i in range(dependency.attributes.length):
						a=dependency.attributes.item(i)
						sentencefeature[a.name]=a.value
					
					for link in dependency.getElementsByTagName("link"): 
					# this takes all the links and all the depids mentioned here and adds them as words. unlinked words are not taken into account. no testing on govids either...
						l,order=lexemes.get(link.getAttribute("depid"),None)
						if l: # for each dep node of the link:
						# TODO: check if 'order' still used anywhere!!!
							d={'lexid': link.getAttribute("depid"), tokenname: l.getAttribute("orthotext"), 
								'lemma': l.getAttribute("lemma"), 'order':order, 
								'gov':{ link.getAttribute("govid"): link.getAttribute("func")}
								}
														
							for fs in l.getElementsByTagName("features"):
								for i in range(fs.attributes.length):
									a=fs.attributes.item(i)
									d[a.name]=a.value
							
							#if (not d[tokenname]) and l.getAttribute("text"): d[tokenname] = l.getAttribute("text")
							#if (not d[tokenname]) and d.get(tokenname,None): d[tokenname] = d.get(tokenname,None)
							if debug and (not d[tokenname]):
								print "no token!!!!",filename
								print d
								for fs in l.getElementsByTagName("features"):
									print fs
									for i in range(fs.attributes.length):
										a=fs.attributes.item(i)
										d[a.name]=a.value
										print a,a.name,a.value
								1/0
							nodes[order]=update(nodes.get(order,{}),d)
							depcounter+=1
							
						else:
							print "error! lexeme",l,"does not exist. Error in XML file."
							1/0
					if len(nodes)<maxlength:
						nodedic={}
						lexidid = {}
						for i,(order,d) in enumerate(sorted(nodes.items())):
							nodedic[i+1]=d
							lexidid[d["lexid"]]=i+1
						for i in nodedic:
							newgov={}
							for g,f in nodedic[i].get('gov',{}).iteritems():
								if g: newgov[lexidid.get(g)]=f
								else:newgov[0]=f
							nodedic[i]['gov']=newgov
						sentences+=[nodedic]
						sentencefeatures+=[sentencefeature]
					else:
						print sentencefeature
						print "ooooooh"
						if logfile:
							f=codecs.open("toolong.txt","a","utf-8")
							f.write("\t".join([filename, str(len(nodes)),sentencefeature["markupIU"]])+"\n")
							f.close()
						
							f=codecs.open(logfile,"a","utf-8")
							f.write("toolong: \n"+ filename+"\n\n\n"+str(len(nodes))+"\t"+sentencefeature["markupIU"]+"\n\n\n")
							f.close()
						
						#1/0
						
					

		print len(sentences),"sentences with",depcounter,"dependencies"
		print "_________________________"
		
		return sentences,sentencefeatures
		
#def enterConll(dbname,filename,annotatorName=None, eraseAllAnnos=False, dbtextname=None): 
def enterRhapsodie(sql,inputfilename,annotatorName, eraseAllAnnos,  clean=True, corrlist=False):		
		
		print "______________________________________________________________reading",inputfilename
		if logfile:
			f=codecs.open(logfile,"a","utf-8")
			f.write("______________________________________________________________reading"+ inputfilename+"\n"+annotatorName+"\n\n\n")
			f.close()
			
		if clean: sql.cleanDatabase(inputfilename)
		
		db,cursor=sql.open()
		
		if corrlist: 	sentences, sentencefeatures=correctRhapsodie(inputfilename, corrlist)
		else:		sentences, sentencefeatures=rhapsodie2Sentences(inputfilename)
		
		#print sentences
		#print sentencefeatures
		
		#1/0
		
		annotatorName=sql.projectconfig["configuration"]["baseAnnotatorName"]
		dbtextname=inputfilename.split("/")[-1]
		textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
		print "______________",len(sentences)," sentences ready to enter into database. textname:",dbtextname,"textid",textid
		enterSentences(sql,cursor,sentences,inputfilename, textid,annotatorName,eraseAllAnnos, sentencefeatures=sentencefeatures )

		db.commit()
		db.close()
		return len(sentences)
	
	
	
def correcttree2nodedic(tree,catname="cat"):
		""" 
		takes the conll string representation of a single tree and creates a dictionary for it
		here special format: spacelemmas
		"""
	
		nodedic={}
		for line in tree.split('\n'):
			line=line.strip()
			
			#print "___",line
			if line:
				cells = line.split('\t')
				nrCells = len(cells)
				if nrCells in [6,7]:
					if nrCells == 6:
						nr, t, lemma, tag, head, rel = cells
						#nr,head = int(nr), int(head)
						if int(head)>=0:nodedic['i'+nr]={'id':'i'+nr,tokenname: t,'lemma': lemma, catname: tag, 'gov':{'i'+head: rel} }
						else:nodedic['i'+nr]={'id':'i'+nr,tokenname: t,'lemma': lemma, catname: tag, 'gov':{} }
					elif nrCells == 7:
						nr, t, lemma, tag, head, rel, child = cells
						
						#nr,head = int(nr), int(head)
						#if lemma2!="_": lemma=lemma2 # TODO: find out what the difference between these columns is!!!!!!
						if int(head)>=0:nodedic['i'+nr]={'id':'i'+nr,tokenname: t,'lemma': lemma, catname: tag, 'gov':{'i'+head: rel} }
						else:nodedic['i'+nr]={'id':'i'+nr,tokenname: t,'lemma': lemma, catname: tag, 'gov':{} }
						
						
						if child.strip()=="-":
							nodedic['i'+nr]["child"]=True
						else:
							print child,cells,"--- strange line:"
							print line
				else:
					print "strange line"
					print line
					print "in:"
					print tree
			
					
		return nodedic
	
	
	
	
	####################### functions for the batch correction of Rhapsodie
	
def glue(sentencedic,nodenum,direction):
		"""
		glues the nodenum (t and lemma) to the neighboring node in the direction
		ignores govs etc du nodenum
		gives back new sentencedic
		
		"""
		
		if debug>2:print "================== glueing"
		newsentencedic={}
		try:
			intchi=nodenum+direction
			if direction<0:
				sentencedic[intchi][tokenname]
				sentencedic[nodenum][tokenname]
				sentencedic[intchi][tokenname]=sentencedic[intchi][tokenname]+sentencedic[nodenum][tokenname]
				sentencedic[intchi]['lemma']=sentencedic[intchi]['lemma']+sentencedic[nodenum]['lemma']
			else:
				sentencedic[intchi][tokenname]=sentencedic[nodenum][tokenname]+sentencedic[intchi][tokenname]
				sentencedic[intchi]['lemma']=sentencedic[nodenum]['lemma']+sentencedic[intchi]['lemma']
				
			
			
			l = [0]+sorted(sentencedic)[:nodenum-1]+sorted(sentencedic)[nodenum:]
			if debug>1:print "lllll",l
			
			
			
			# correct wrong gov links
			for i in sorted(sentencedic):
				if nodenum in sentencedic[i]['gov'].keys():
					sentencedic[i]['gov'][intchi]=sentencedic[i]['gov'][nodenum]
					del sentencedic[i]['gov'][nodenum]		
			
			
			#print 'lllll',l
			# bring all in a new list with new indeces based on l
			
			for newi,oldi in enumerate(l):
				if newi:# not 0
					newsentencedic[newi]=sentencedic[oldi]
					govdic={}
					for govi,dep in sentencedic[oldi]['gov'].iteritems():
						
						govdic[l.index(govi)]=dep
					newsentencedic[newi]['gov']=govdic
		
		except Exception, err:
			print traceback.format_exc()
			print nodenum
			print direction
			print "oldoldold((((((((((((("
			for i in sorted(sentencedic):
				print i,sentencedic[i]
			print ")))))))))))))))"
			print "newnewnew((((((((((((("
			for i in sorted(newsentencedic):
				print i,newsentencedic[i]
			print ")))))))))))))))"
			print traceback.format_exc()
			if logfile:
				f=codecs.open(logfile,"a","utf-8")
				f.write(traceback.format_exc()+str(nodenum)+"\n" +str(intchi)+"\n" +  "\n\n\n"+unicode(sentencedic)+"\n\n\n"+unicode(newsentencedic)+"\n\n\n")
				f.close()
			return sentencedic
			#raise ShitError
		
		#del sentencedic[nodenum]

		if debug>1:
			print "((((((((((((("
			for i in sorted(newsentencedic):
				print i,newsentencedic[i]
			print ")))))))))))))))"
			
		return newsentencedic
	
	
	
def integrate(sentencedic,nodenum,intdic):
		"""
		integrates the intdic into sentencedic at position nodenum
		an empty intdic kicks out the node in a proper manner (other dependencies are still ok)
		
		gives back new sentencedic
		
		"""
		intgov,intchi=None,None
		newsentencedic={}
		if debug>2: 
			print "================== integrating"
			for i in sorted(intdic):
				print i,intdic[i]
			print "into ((((((((((((("
			for i in sorted(sentencedic):
				print i,sentencedic[i]
			print ")))))))))))))))"
		try:
			l = [0]+sorted(sentencedic)[:nodenum-1]+sorted(intdic)+sorted(sentencedic)[nodenum:]
			if debug>2: print "lllll",l
			
			
			for i in sorted(intdic):
			
				sentencedic[i]=sentencedic[nodenum].copy()
				#intdic[i][tokenname]
				sentencedic[i][tokenname]=intdic[i][tokenname]
				sentencedic[i]['lemma']=intdic[i]['lemma']
				sentencedic[i]['cat']=intdic[i]['cat']
				sentencedic[i]['gov']=intdic[i].get('gov',{})
				
				
				if 'i0' in intdic[i].get('gov',{}).keys(): # found the gov: the one that has a root link
					sentencedic[i]['gov']=sentencedic[nodenum]['gov']
					intgov=i
				if "child" in intdic[i]: # found the child bearer
					intchi = i
			if not intgov:# if no governor is indicated, i guess it's the first word
				intgov="i1"
				if intgov in sentencedic: sentencedic[intgov]['gov']=sentencedic[nodenum]['gov']
			if not intchi: intchi=intgov
			
			# correct wrong gov links
			for i in sorted(sentencedic):
				if nodenum in sentencedic[i]['gov'].keys():
					sentencedic[i]['gov'][intchi]=sentencedic[i]['gov'][nodenum]
					del sentencedic[i]['gov'][nodenum]		
			
			
			#print 'lllll',l
			# bring all in a new list with new indeces based on l
			newsentencedic={}
			for newi,oldi in enumerate(l):
				if newi:# not 0
					newsentencedic[newi]=sentencedic[oldi]
					govdic={}
					for govi,dep in sentencedic[oldi]['gov'].iteritems():
						if govi>=0 and govi in l:govdic[l.index(govi)]=dep
					newsentencedic[newi]['gov']=govdic
		except Exception, err:
			print traceback.format_exc()
			print "oldoldold((((((((((((("
			for i in sorted(sentencedic):
				print i,sentencedic[i]
			print ")))))))))))))))"
			print "newnewnew((((((((((((("
			for i in sorted(newsentencedic):
				print i,newsentencedic[i]
			print ")))))))))))))))"
			print "intdic((((((((((((("
			for i in sorted(intdic):
				print i,intdic[i]
			print ")))))))))))))))"
			print nodenum
			print intdic
			
			if logfile:
				f=codecs.open(logfile,"a","utf-8")
				f.write(traceback.format_exc()+"\n\n\n"+unicode(sentencedic)+"\n\n\n"+unicode(newsentencedic)+"\n\n\n")
				f.close()

			raise ShitError
		#del sentencedic[nodenum]

		if debug>2:
			print "result:((((((((((((("
			for i in sorted(newsentencedic):
				print i,newsentencedic[i]
			print ")))))))))))))))"
			
		return newsentencedic
	
def checkSentence(iii,s,corrlist,rec=0):
	"""
	iii: index of sentence in the sentence list
	s: sentence in nodedic format
	rec: recursion level
	"""
	#print "_____________________________________________"
	#if rec>10:
		#print s,rec
		#1/0
	if debug: print "checking sentence",iii,"rec",rec,"len(s)",len(s)
	
	
	# TODO: kick out:
	if rec<1:
		#print "____________________________"
		#for i in s:	print i,s[i][tokenname], s[i]
		#print "____________________________"
		
		
		for i in s:
			#print s
			if "gov" in s[i]:
				for g in s[i]["gov"]:
					if s[i]["gov"][g].endswith("_invisible"):
						s[i]["gov"][g]=s[i]["gov"][g].replace("_invisible","_inherited")
	
	
	if rec<3:
				
		
		for i in sorted(s):
			
			if debug>1:
				try:
					print "checking:",i,s[i][tokenname]
					
					#s[i]
					#print s[i]["lemma"],s[i]["lemma"] in corrdic,i in s
					#print corrdic
				except:
					print "index",i,"is gone"
				#if s[i]['cat']=="unknown" and s[i][tokenname]=="d'":
				#if s[i][tokenname]==u"écrivant":
					#print "********************************************************"
					#for i in sorted(s):
						#print s[i]
					##print s
					#1/0
			#print i,s[i]		
			
			
			if i in s:
				for matchdic,insdic in corrlist:
					if unify(s[i],matchdic):
						
						
						#( s[i]["lemma"] in corrdic or s[i][tokenname] in corrdic):
						if debug>1:
							print "èèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèè"
							#if s[i]["lemma"] in corrdic : print corrdic[s[i]["lemma"]]
							#else:print corrdic[s[i][tokenname]]
							print s[i]
							print "matched oooooooooooooooooooooooooooooooo"
							print matchdic
							print "èèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèèè"
						#if s[i]["lemma"] in corrdic : insdic=corrdic[s[i]["lemma"]]
						#else:insdic=corrdic[s[i][tokenname]]
						if isinstance(insdic,int):# glueing. in this case insdic contains the direction of the token glueing
							s = glue(copy.deepcopy(s),i,insdic)
							s = checkSentence(iii,copy.deepcopy(s),corrlist,rec+1)
						else:
							s = integrate(copy.deepcopy(s),i,insdic)
							if len(insdic)>1:
								s=checkSentence(iii,copy.deepcopy(s),corrlist,rec+1)
			#elif i in s and  ( s[i]["lemma"] in gluedic or s[i][tokenname] in gluedic) :
				#if debug>1:
					#print "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
					#if s[i]["lemma"] in gluedic :print gluedic[s[i]["lemma"]]
					#else:print gluedic[s[i][tokenname]]
					#print "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
				#if s[i]["lemma"] in gluedic : insdic=gluedic[s[i]["lemma"]]
				#else:insdic=gluedic[s[i][tokenname]]
				#news = glue(s,i,insdic)
				#s=checkSentence(iii,news,corrlist,rec+1)
			
			
	return s			


def correctionDics(correctionfilename):
	
	if debug: print "reading the correction file",correctionfilename
	corrf=codecs.open(correctionfilename,"r","utf-8")
			
	corrlist=[]
	#currtoken=None
	currdic={}
	currconlltree=""
	
	for line in corrf:
		line=line.split("#")[0] # comments
		#if (line.strip()+" ")[0]!="#":
		if line.strip():
			#if "#" in line: 
			if currdic: # second or further line of a block
				if line.startswith("<-"):
					corrlist+=[(currdic,-1)]
					currconlltree=""
					currdic={}
				elif line.startswith("->"):
					#gluedic[currtoken]=1
					corrlist+=[(currdic,1)]
					currconlltree=""
					currdic={}
				else:
					currconlltree+=line
			else: # first line of a block
				trucs=line.split("\t")
				if len(trucs)>3:
					_,currtoken,currlemma,currcat=trucs[:4] # [0].strip()
					currdic={}
					for (a,v) in [(tokenname,currtoken),("lemma",currlemma),("cat",currcat)]:
						v=v.strip()
						if v: currdic[a]=v
					
				else:
					print "strange line:",line
					currconlltree=""
					currdic={}	
		else: # empty line
			if currconlltree.strip():
				corrlist+=[(currdic,correcttree2nodedic(currconlltree))]
				#corrdic[currtoken]=correcttree2nodedic(currconlltree)			
			
			currconlltree=""
			currdic={}		
	if debug:
		for matchdic,insdic in corrlist:
			print matchdic
			if isinstance(insdic, int):
				print insdic
			else:
			
				for i in sorted(insdic):
					print i,insdic[i]
			print "_______________"
	
			
	return corrlist



def correctRhapsodie(rhapsodiexmlfilename,corrlist):
	"""
	
	
	"""
	sentences, sentencefeatures = rhapsodie2Sentences(rhapsodiexmlfilename)
	
	newsentences = [checkSentence(i,s,corrlist) for i,s in enumerate(sentences)]
	
	#TODO: get rid of this:
	for sf in sentencefeatures:
		for atr in sf:
			if atr=="markupIU":
				sf["markupIU"]=sf["markupIU"].replace(u"ESPERLUETTE",u"&")
	
	#newsentences = [checkSentence(i,s,corrlist,gluelist) for i,s in enumerate([sentences[10]])]
	#newsentences=[sentences[10]]
	print "end:correctRhapsodie_______________",rhapsodiexmlfilename,"\n\n"
	
	return newsentences, sentencefeatures


def findspacelexemes(filename,spacelemmas):
		
		#db,cursor=self.open()
		doc = minidom.parse(filename)
		
		pivs, tokens, lexemes, deps, nodedics = {},{},{},{},{}
		wtypedic={"pivot":pivs,"tokens":tokens,"lexemes":lexemes}
		dtypedic={"syntax":deps}
		
		# all dictionaries look like this: u'lex565': (<DOM Element: word at 0xb617e2cc>, 566)
		for wordgroup in doc.getElementsByTagName("words"):# looking at all the wordgroups
			currentdic = wtypedic.get(wordgroup.getAttribute("type"),None) # if they are mentioned in the wtypedic, read them in
			if currentdic=={}:
				order=0
				for w in wordgroup.getElementsByTagName("word"):
					order+=1
					currentdic[w.getAttribute("id")]=w,order
		
		depcounter = 0
		sentences=[]
		for depgroup in doc.getElementsByTagName("dependencies"):
			currentdic = dtypedic.get(depgroup.getAttribute("type"),None)
			if currentdic=={}: # i found the syntax depgroup
				for dependency in depgroup.getElementsByTagName("dependency"): # for each dependency = one sentence
					
					lexiddic = {}
					nodes={}
					
					for link in dependency.getElementsByTagName("link"): 
					# this takes all the links and all the depids mentioned here and adds them as words. unlinked words are not taken into account. no testing on govids either...
						l,order=lexemes.get(link.getAttribute("depid"),None)
						if l: # for each dep node of the link:
														
							#print "lex::::",l,order
							#print l
							d={'lexid': link.getAttribute("depid"), tokenname: l.getAttribute("text"), 'lemma': l.getAttribute("lemma"), 'order':order, 
							'gov':{ link.getAttribute("govid"): link.getAttribute("func")}
							}
							
							#print d,d["lemma"]," " in d["lemma"] 
							
							
							
							#print spacelemmas
							
							for fs in l.getElementsByTagName("features"):
								for i in range(fs.attributes.length):
									a=fs.attributes.item(i)
									
									d[a.name]=a.value
							#if not d[tokenname] and d[tokenname]: d[tokenname] = d[tokenname]
							#print d[tokenname]
							
							if " " in d["lemma"] or "'" in d["lemma"] or "-" in d["lemma"] or "_" in d["lemma"] or " " in d[tokenname] or "'" in d[tokenname] or "-" in d[tokenname] or "_" in d[tokenname]:
								spacelemmas[d["lemma"]]=( d[tokenname],  spacelemmas.get(d["lemma"],("",0," "))[1]+1,     spacelemmas.get(d["lemma"],("",0," "))[2]+" "+filename.split("/")[-1])
								# spacelemmas has 3 elements: token, counter, file list
								
								
								#for a in fs.attributes:
									#d[a.name]=a.value
							#if nodes.get(order,{}):
								#print nodes
								#print d
								#print self.update(nodes.get(order,{}),d)
								#print "________________________________________________________"
							nodes[order]=update(nodes.get(order,{}),d)
							
						else:
							print "error! lexeme",l,"does not exist. Error in XML file."
							1/0
					
					
					
					
					
					
					nodedic={}
					lexidid = {}
					for i,(order,d) in enumerate(sorted(nodes.items())):
						nodedic[i+1]=d
						lexidid[d["lexid"]]=i+1
					for i in nodedic:
						newgov={}
						for g,f in nodedic[i].get('gov',{}).iteritems():
							if g: newgov[lexidid.get(g)]=f
							else:newgov[0]=f
						nodedic[i]['gov']=newgov

					
					#for a,v in  nodedic.iteritems():
						#print a,v["lemma"]
						#print v
					sentences+=[nodedic]
					depcounter+=1
					

		print "_____",depcounter,"dependencies"
		print "_________________________"
		print len(sentences),"sentences"				
		
		
		return spacelemmas

	
	
###################### useful::::::::::::
	
	
def findrhapsodiespacelemmas(path):
	sql = database.SQL("Rhapsodie")	
	#print sql.cleanDatabase("output_D211.xml")
	spacelemmas={}
	for infile in os.listdir(path):
		print "current file is: " + infile
		if unicode(infile).lower().endswith(".xml"):
			spacelemmas=findspacelexemes(path+infile,spacelemmas)
			# spacelemma has 3 elements: token, counter, file list

	outf=codecs.open("spacelemmas.txt","w","utf-8")
	for k in spacelemmas:
		outf.write(k+"\t"+unicode(spacelemmas[k][0])+"\t"+str(spacelemmas[k][1])+"\t"+spacelemmas[k][2]+"\n")
	outf.close()
	


def readinallrhapsodie(projectname,rhapsodiexmlfilepath,repair=False,pattern=None):
	"""
	all rhapsodiexml files found in the rhapsodiexmlfilepath are read into the projectname database via the enterRhapsodie function
	if a repair file is given, it will be used
	"""
	sql = database.SQL(projectname)
	annotatorName=sql.projectconfig["configuration"]["baseAnnotatorName"]
	eraseAllAnnos=True
	#eraseAllAnnos=False
	if repair:	corrlist=correctionDics(repair)
	else: 		corrlist=False
	
	if pattern:
		for i,infile in enumerate(glob(os.path.join(rhapsodiexmlfilepath, pattern))):
			enterRhapsodie(sql,infile,annotatorName, eraseAllAnnos,clean=True,corrlist=corrlist)
	
	else:
		files=os.listdir(rhapsodiexmlfilepath)
		for i,infile in enumerate(files):
			#print "________________________________________current file is: " + rhapsodiexmlfilepath+infile
			print "file",i+1,"of",len(files)
			if infile.lower().endswith(".xml") :
				enterRhapsodie(sql,rhapsodiexmlfilepath+infile,annotatorName, eraseAllAnnos,clean=True,corrlist=corrlist)
	print "readinallrhapsodie ok\n\n"
		
	
def readinsinglerhapsodie(projectname,rhapsodiexmlfile,eraseAllAnnos=False,repair=False):
	sql = database.SQL(projectname)
	annotatorName=sql.projectconfig["configuration"]["baseAnnotatorName"]
	eraseAllAnnos=True
	if repair:corrlist=correctionDics(repair)
	else: corrlist=False
	enterRhapsodie(sql,rhapsodiexmlfile,annotatorName, eraseAllAnnos,clean=True,corrlist=corrlist)
	print "ok"

	
	
		
		
		
		
		
		
		
		
		
		
		

def readinallmates(projectname,conlldirpath,filepattern="*.trees.conll14",eraseAllAnnos=True, steps=1000, importAnnotatorName=None, preserveSampleWithSameName=False):
	
	
	sql = database.SQL(projectname)
	#db,cursor=sql.open()
	
	for filename in glob(os.path.join(conlldirpath, filepattern)):
		print "entering",filename
		allsentences=conll.conllFile2trees(filename)
		
		for i in range(len(allsentences)/steps+1):
			 
			sentences=allsentences[steps*i:steps*(i+1)]
			
			#print sentences
			if importAnnotatorName:	annotatorName=importAnnotatorName
			else: annotatorName=sql.importAnnotatorName
			
			dbtextname = filename.split("/")[-1].decode("utf-8")
			if dbtextname.endswith(".conll07") or dbtextname.endswith(".conll10") or dbtextname.endswith(".conll14") or  dbtextname.endswith(".malt") or dbtextname.endswith(".tab") or dbtextname.endswith(".orfeo") or dbtextname.endswith(".conll_parse"):
				dbtextname=".".join(dbtextname.split(".")[:-1])
			if dbtextname.endswith(".trees"):
				dbtextname=".".join(dbtextname.split(".")[:-1])
				
			if dbtextname.endswith("-one-word-per-line.conll14_Parse"): # Chloé ! à adapter si besoin ou encore mieux généraliser de manière à ce que tout ce qui est devant le premier point suffit pour identifier un texte
				dbtextname=dbtextname[:-len("-one-word-per-line.conll14_Parse")]
			
			
				
				
			if steps<len(allsentences):
				dbtextname+=".no"+str(i)
				print dbtextname
			#textid = sql.enter(cursor, "texts",["textname"],(dbtextname,))
			
			#enterSentences(sql,cursor,sentences,filename, textid,annotatorName,eraseAllAnnos, tokname="t" )
			simpleEnterSentences(sql, sentences, dbtextname, annotatorName, eraseAllAnnos=True, sentencefeatures={}, preserveSampleWithSameName=preserveSampleWithSameName)
			
	#db.commit()
	#db.close()
	
	
	
	
	

def readinallconll(projectname,conllfilepath,useFileInfo=True,eraseAllAnnos=False):
	"""
	all conll10 files found in the conllfilepath are read into the projectname database
	"""
	sql = database.SQL(projectname)
	annotatorName=sql.projectconfig["configuration"]["importAnnotatorName"]
	#print sql.cleanDatabase("output_D211.xml")
	files=os.listdir(conllfilepath)
	for i,infile in enumerate(files):
		print "\n\n________________________________________current file is: " + conllfilepath+infile,"file",i+1,"of",len(files)
		if infile.lower().endswith(".conll10")  or infile.lower().endswith("-dependanaly.txt") or infile.lower().endswith(".trees.conll14"):
			#enterConll(dbname,filename,annotatorName=None, eraseAllAnnos=False, dbtextname=None): 
			if useFileInfo:
				enterConll(projectname,conllfilepath+infile, eraseAllAnnos)
			else: # todo: correct:
				enterConll(projectname,conllfilepath+infile,annotatorName, eraseAllAnnos)
			print "ok"
	
	
def readinsingleconll(projectname,conllfile,useFileInfo=True,eraseAllAnnos=False,checkExtension=True):
	"""
	all conll10 files found in the conllfilepath are read into the projectname database
	"""
	sql = database.SQL(projectname)
	annotatorName=sql.projectconfig["configuration"]["importAnnotatorName"]
	#print sql.cleanDatabase("output_D211.xml")

	print "________________________________________current file is: " + conllfile
	if conllfile.lower().endswith(".conll10") or not checkExtension:
		#enterConll(dbname,filename,annotatorName=None, eraseAllAnnos=False, dbtextname=None): 
		if useFileInfo:
			enterConll(projectname, conllfile, eraseAllAnnos)
		else: # todo: correct:
			enterConll(projectname,conllfile,annotatorName, eraseAllAnnos)
		print "ok"
	else:
		print "skipped",conllfile
	
def writeConfigs(project,allcats,allfuncs):
	with codecs.open("projects/"+project+"/categories.config","w","utf-8") as catfile, codecs.open("projects/"+project+"/functions.config","w","utf-8") as funcfile:
		
		for cat in sorted(allcats):
			catfile.write(cat+'	{"fill": "#69399d"}\n')
		for func in sorted(allfuncs):
			funcfile.write(func+'	{"stroke": "#000","stroke-width":"1","stroke-dasharray": ""}\n')
		funcfile.write('attention	{"stroke": "#DD137B","stroke-width":"1","stroke-dasharray": "- "}\n')



	

					
def computeDifference(tree):
	"""
	for a conll 14 tree with gold + parse results (lemma + lemma2, tag + tag2, ...)
	gives back scores: (l, t, g, f, len(tree) )
	l: number of correct lemmas
	t: number of correct tags
	g: number of correct govs
	l: number of correct function labels
	len(tree)
	"""
	l,t,g,f=0.0,0.0,0.0,0.0
	for i in tree:
		node=tree[i]
		if node["lemma"]==node["lemma2"]:	l+=1
		if node["tag"]==node["tag2"]:		t+=1
		if node["gov"].keys()[0]==node["gov2"].keys()[0]:
			g+=1
			if node["gov"].values()[0]==node["gov2"].values()[0]:
				f+=1
	#length=len(tree)
	#return length,l/length,t/length,g/length,f/length
	return l,t,g,f,len(tree)
		
		
		
						
def readInTestResults(projectname,conllfilename,gold="gold",parser="parser"):
	"""
	reads in the result of the mate transition parser into visually comparable results
	the result file is a conll 14 files with double annotation (lemma + lemma2, ...)
	"""
	print "________________________________________current file is: " + conllfilename
	shortname = conllfilename.split("/")[-1]
	if projectname: # really modifying the database
		
		sql = database.SQL(projectname)
		db,cursor=sql.open()
		textid = sql.enter(cursor, "texts",["textname"],(shortname,))
		goldid = sql.enter(cursor, "users",["user","realname"],(gold,gold,))
		parserid = sql.enter(cursor, "users",["user","realname"],(parser,parser,))
		
		
		sents={} # score of correct functions -> list of trees having that score. allows to sort by annotation quality. the list of trees are triples: ( goldtree,parsetree,info )
		goldsentences,parsesentences,sentencefeatures=[],[],[]
		l,t,g,f,length=0.0,0.0,0.0,0.0,0
		allcats,allfuncs={},{}
		
		sentences=conll.conllFile2trees(conllfilename)
		#print len(sentences)
		for tree in sentences:
			tl,tt,tg,tf,tlength=computeDifference(tree)
			#"lemma precision:"+str(round(tl/tlength,2))+
			info = " LAS:"+str(round(tf/tlength,3))+" UAS:"+str(round(tg/tlength,3))+" pos precision:"+str(round(tt/tlength,3))+u" n° tokens:"+str(tlength)
			
			
			goldtree,parsetree={},{}
			for i in tree:
				node=tree[i]
				goldtree[i]= {"id":node["id"],"t":node["t"],"lemma":node["lemma"],"tag":node["tag"],"morph":node["morph"],"gov":node["gov"]}
				parsetree[i]={"id":node["id"],"t":node["t"],"lemma":node["lemma2"],"tag":node["tag2"],"morph":node["morph2"],"gov":node["gov2"]}
				allcats[node["tag"]]=None
				allcats[node["tag2"]]=None
				allfuncs[node["gov"].values()[0]]=None
				allfuncs[node["gov2"].values()[0]]=None
				
			sents[tf/tlength]=sents.get(tf/tlength,[])+[ ( goldtree,parsetree,info ) ]
			(l,t,g,f,length)=map(sum,zip((l,t,g,f,length),(tl,tt,tg,tf,tlength) ))
		#	
		globalinfo = "lemma precision:"+str(round(l/length,2))+" pos precision:"+str(round(t/length,2))+" UAS:"+str(round(g/length,2))+" LAS:"+str(round(f/length,2))+u" n° tokens:"+str(length)+u" n° sentences:"+str(len(sentences))	
		print globalinfo
		treec=0
		for f in sorted(sents):
			for ( goldtree,parsetree,info ) in sents[f]:
				#print f, treec
				#print f, goldtree
				goldsentences+=[goldtree]
				parsesentences+=[parsetree]
				sentencefeatures+=[{"info":info}]
				treec+=1
		print "entering",len(parsesentences),"sentences"
		enterSentences(sql,cursor,goldsentences,shortname, textid,gold,eraseAllAnnos=True, sentencefeatures=sentencefeatures,tokname="t" )
		enterSentences(sql,cursor,parsesentences,shortname, textid,parser,eraseAllAnnos=False, defaultAnnotatorName="gold", tokname="t" )
		db.commit()
		db.close()
		
		writeConfigs(projectname,allcats,allfuncs)
		
		
	else:
		#only testing
		sentences=conll.conllFile2trees(conllfilename)
		l,t,g,f,length=0.0,0.0,0.0,0.0,0
		
		for s in sentences:
			(l,t,g,f,length)=map(sum,zip((l,t,g,f,length),computeDifference(s)))
			
		print "____"
		print "lemma precision:",l/length,"tag precision:",t/length,"UAS:",g/length,"LAS:",f/length
		print "n° tokens:",length,"n° sentences:",len(sentences)
		#print computeDifference(sentences[1])
		print sentences[1]
	
	
	

	
	

if __name__ == "__main__":
	print "bonjour"
	
	#readinsingleconll("Jiaotong-1","/home/kim/cloem/cloem-kim/site/cloems/wireless.txt-bea1a133308f0775a5913cb57844fd4a/chunks.txt-dependanaly.corrected.txt",useFileInfo=False,eraseAllAnnos=True,checkExtension=False)
	#readinsingleconll("orfeo","corpus/conll/crfp_PUB-BES-1_extrait.disf.parsed.conll",useFileInfo=False,eraseAllAnnos=True,checkExtension=False)
	#readinsingleconll("orfeo","corpus/conll/tcof_Ag_ael_08_extrait.disf.parsed.conll",useFileInfo=False,eraseAllAnnos=True,checkExtension=False)

	# /Documents
	#readinallrhapsodie("Rhapsodie","/home/kim/Dropbox/Rhapsodie/syntaxe-julie/xmls_newname/",repair="/home/kim/Dropbox/Rhapsodie/syntaxe-julie/settings/corrConll.txt")
	#readinallrhapsodie("Rhapsodie","/home/kim/Dropbox/Rhapsodie/rhapsodie-kimsPostcomputing/cool/",repair=None, pattern='*absolutely*.xml')
	
	#readinsinglerhapsodie("Rhapsodie","/home/kim/Dropbox/Rhapsodie/syntaxe-julie/xmls_newname/Rhap-D2009-Synt.xml",repair="/home/kim/Dropbox/Rhapsodie/syntaxe-julie/settings/corrConll.txt")
	
	#readinsinglerhapsodie("Rhapsodie","/home/kim/Dropbox/Rhapsodie/rhapsodie-kimsPostcomputing/cool/D0001.absolutely.cool.xml")
	
	#readinallconll("Rhapsodie","projects/Rhapsodie/verylastexport/",useFileInfo=True,eraseAllAnnos=False)
	
	#readinsingleconll("Rhapsodie","projects/Rhapsodie/lastexport/M014.XML.cricriben.trees.conll10",useFileInfo=True,eraseAllAnnos=False)
	
	#sql = SQL("Rhapsodie")	
	#sql = SQL("berlin")	
	#sql = SQL("xinying")
	#print sql.cleanDatabase("output_D211.xml")
	
	#readinallconll("xinying","corpus/conll/conll/")
	
	#readinallconll("Rhapsodie","/home/kim/Dropbox/programmation/arborator/trunk/projects/Rhapsodie/export/")
	#readinsingleconll("Occitan","corpus/occitanConll/Boece.conll10",useFileInfo=False,eraseAllAnnos=True)
	#sql.correctRhapsodie("corpus/xml/M201.XML","spacelemmas5.txt")
	#enterConll("Rhapsodie","corpus/conll/M016.XML.Sy.trees.conll10")
	#findrhapsodiespacelemmas("/home/kim/Dropbox/Rhapsodie/syntaxe-julie/xml_ok/")
	#readinsingleconll("Rhapsodie","projects/Rhapsodie/lastexport/D020.XML.Sy.trees.conll10",useFileInfo=True,eraseAllAnnos=False)
	
	#,annotatorName="Sy", eraseAllAnnos=False, dbtextname="M016.XML")
	#print sql.cleanDatabase()
	
	#sql.enterRhapsodie("corpus/xml/output_D211.xml")
	#sql.enterRhapsodie("corpus/xml/output_M024.xml")
	
	#sql.enterConll("corpus/conll/conll/4.csv.110.conll10.semantics.conll10")
	
	#readinallconll("lingCorpus","/home/kim/Documents/newmate/testimportdeps/")
	#readinsingleconll("lingCorpus","/home/kim/Documents/newmate/testimportdeps/Shi_Yu-dependanaly.txt",useFileInfo=False,eraseAllAnnos=True,checkExtension=False)
	
	
	#readinallmates("lingCorpus","/home/gerdes/arborator/corpus/coursLingCorpus/newparses/")
	#readinallmates("lingCorpus","/home/gerdes/arborator/corpus/coursLingCorpus/newparses/",filepattern="*Triv*")
	#readinallmates("lingCorpus","/home/gerdes/arborator/corpus/coursLingCorpus/newparses/",filepattern="*Pett*")
	#readinallmates("lingCorpus","/home/gerdes/arborator/corpus/coursLingCorpus/newparses/",filepattern="*Fum*")
	readinallmates("linguistiqueCorpus-Echantillons-2017","/home/gerdes/arborator/corpus/coursLingCorpus/2017parses3/",filepattern="*", preserveSampleWithSameName=True)
	#readinallmates("decoda","/home/gerdes/arborator/corpus/decoda/",filepattern="decoda.test*")
	
	#readinallmates("lingCorpus","/home/gerdes/arborator/corpus/2015lingCorpus/",filepattern="*")
	#readinallmates("test_mini_db","corpus/mate/",filepattern="*_Parse")
	#readinallmates("platinum","corpus/platinum/",filepattern="*")
	#readinallmates("Platinum","../projects/Platinum/exportcorrected/",filepattern="*",steps=10000,importAnnotatorName="gold")
	#readinallmates("lingCorpus2016","../tools/parses/",filepattern="*conll_parse",steps=10000,importAnnotatorName="parser")
	#readinallmates("Naija","../tools/parses/",filepattern="*_parse",steps=10000,importAnnotatorName="parser")
	#readinallmates("Uppsala","../corpus/Uppsala/",filepattern="*conllu",steps=10000,importAnnotatorName="parser")
		
	#readInTestResults(None,"/home/kim/Documents/newmate/canons/result-chin-canon-S2a-40-0.25-0.1-2-2-ht4-hm4-kk0-1")
	#readInTestResults("canons","/home/kim/Documents/newmate/canons/result-chin-canon-S2a-40-0.25-0.1-2-2-ht4-hm4-kk0-1")
	
	
	
	
	#enterDegraded("linguistiqueCorpus-Exo","/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/1a.orig")
	#enterDegraded("linguistiqueCorpus-Exo","/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/1b.orig")
	#enterDegraded("linguistiqueCorpus-Exo","/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/1c.orig")
	#enterDegraded("linguistiqueCorpus-Exo","/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/2a.orig")
	#enterDegraded("linguistiqueCorpus-Exo","/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/2b.orig")
	#enterDegraded("linguistiqueCorpus-Exo","/home/kim/Dropbox/programmation/arborator/trunk/projects/SyntaxeAlOuest/export/2c.orig")
	#enterDegraded("SyntaxeAlOuest","corpus/conll/2b.txt.conll_parse.orig","corpus/conll/2b.txt.conll_parse.deg")
	#enterDegraded("SyntaxeAlOuest","corpus/conll/2c.txt.conll_parse.orig","corpus/conll/2c.txt.conll_parse.deg")
	
	#from database import SQL
	#trees=conll.conllFile2trees("../tools/annotatedCorpora.conllu")
	#simpleEnterSentences(SQL("Naija"), trees, "Naija1", "parser", eraseAllAnnos=True)
	#print "ok"
	
	
	
 
