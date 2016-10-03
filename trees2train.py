#! usr/bin/python
#! coding: utf-8

import conll, datetime, codecs, time, sys
from database 	import SQL
from pprint import pprint

"""
TODO :
- documenter scripts
- mettre en place le cron
"""

#ti = time.time()-86400

def databaseQuery(cursor,table="all", values=[]):
	
	if table == "all":
		command="select distinct trees.rowid, texts.textname, users.user, sentences.nr, trees.* from texts, trees, sentences, users where trees.status = 1 and trees.sentenceid = sentences.rowid and sentences.textid=texts.rowid and trees.userid=users.rowid ;"
	elif table == "validator":
		command="select distinct trees.rowid, texts.textname, users.user, sentences.nr, trees.* from texts, trees, sentences, users, todos where trees.status = 1 and trees.sentenceid = sentences.rowid and sentences.textid=texts.rowid and trees.userid=users.rowid and todos.userid=users.rowid and todos.type=1 and todos.textid=texts.rowid;"
	
	elif table=="duplicate":
		command="""
		select sentences.rowid as sid, trees.rowid as treeid, users.user as annotator, todos.userid as validatorid, trees.timestamp 
		from sentences, todos, trees, users where todos.status = 1 
		and sentences.textid=todos.textid 
		and sentences.rowid=trees.sentenceid 
		and users.rowid = trees.userid 
		and sentences.rowid not in  (select sentenceid from trees,  (select sentences.rowid as y from sentences, todos  where todos.status = 1 and sentences.textid=todos.textid) as x  where x.y = trees.sentenceid and trees.status = 1);

		"""
	cursor.execute(command, values)
	a = cursor.fetchall()
	return a

def sentenceValidationInValidatedText(cursor, sql, db):
	print "sentenceValidationInValidatedText"
	sids2all={}
	answer=databaseQuery(cursor, table="duplicate")
	for nr, (sid, treeid, user, validid, timestamp) in enumerate(answer):
		sids2all[sid]=sids2all.get(sid, [])+[(treeid, user, validid, timestamp)]
	lastpourc=-1
	for c,sid in enumerate(sids2all):
		pourc = int(float(c)/len(sids2all)*100)
		if pourc!=lastpourc: sys.stdout.write( "{pourc}%\r".format(pourc=pourc) )
		sys.stdout.flush()
		#print "sid",sid
		usernotparser=sorted([(treeid, user, validid, timestamp) for (treeid, user, validid, timestamp) in sids2all[sid] if user != "parser"])
		if len(usernotparser) > 0:
			treeid2get, _, vid, _=usernotparser[-1]
		else:
			treeid2get, _, vid,_ =sids2all[sid][0]
		#print treeid2get
		dic=sql.gettree(None,None,treeid2get, indb=db,incursor=cursor) # dic -> get tree == on récupère l'arbre
		if dic and dic["tree"]:
			sentencetree=dic["tree"]
			#print sentencetree
			wcounter, sent, newtreeid = sql.enterTree(cursor, sentencetree, sid, vid, intokenname="t")
			#print "tree number", treeid, "has been copied. New number =", newtreeid, "New annotator :", userid
			cursor.execute("UPDATE trees SET status=1 WHERE sentenceid=? AND userid=?",(sid,vid,))


def checkTree(sentencetree):
	for i, node in sentencetree.iteritems():
		if "gov" in sentencetree[i].keys():
			for gi in node["gov"]:
				if gi==i:
					return False, "self", i
			if -1 in node["gov"]:
				return False, "nogov", i
		else:
			return False, "nogov", i
	return True, "ok"

def corrigerNumerotation(arbre):
	indexcorrection = {0:0} # ancien indice --> nouvel indice
	problem = False
	for compteur, ind in enumerate(sorted(arbre.keys())):
		indexcorrection[ind]=compteur+1
		if compteur+1 != ind:
			problem = True
	if problem:
		arbrecorrige = {}
		for i, node in arbre.iteritems():
			#print"before", node["gov"]
			node["id"]=indexcorrection[i]
			newgov={}
			for gi,f in node["gov"].iteritems():
				newgov[indexcorrection[gi]]=f
			node["gov"]=newgov
			#print "after",node["gov"]
			arbrecorrige[indexcorrection[i]]=node
		return arbrecorrige
	return arbre




def getValidatedTrees(project, folder, whoseTrees="validator"):
	sql = SQL(project)
	db,cursor=sql.open()
	sentenceValidationInValidatedText(cursor, sql, db)
	#on récupère les nouveaux arbres
	b = databaseQuery(cursor,table=whoseTrees)
	print len(b), u"trees to extract"
	sids2all={}
	trees=[]
	error_trees=[]
	textnames={}
	for nr, (treeid,textname,user, snr ,sid,uid,annotype,status,comment,timestamp) in enumerate(b):
		# TODO: remove:
		if textname.startswith("mandarinParsed"):continue
		sids2all[sid]=sids2all.get(sid, [])+[(timestamp, textname, user, snr, treeid)]
		textnames[textname]=None
	#print len(sids2all)
	print u"trees extracted from the samples",", ".join(sorted(textnames))
	lastpourc=-1
	for c,sid in enumerate(sids2all):
		pourc = int(float(c)/len(sids2all)*100)
		if pourc!=lastpourc: sys.stdout.write( "{pourc}%\r".format(pourc=pourc) )
		sys.stdout.flush()
		
		snr, treeid2get=sorted(sids2all[sid])[0][-2:]
		#print treeid2get, type(treeid2get)
		#lknlk
		dic=sql.gettree(None,None,treeid2get, indb=db,incursor=cursor) # dic -> get tree
		#if treeid2get==9669:
			#print 9669,dic
			
		if dic:
			sentencetree=dic["tree"]
			sentencetree=corrigerNumerotation(sentencetree)
			trees.append(sentencetree)
			#print " ".join(node["t"] for i,node in sentencetree.iteritems())
			if checkTree(sentencetree)[0] == False:
				if checkTree(sentencetree)[1] == "self":
					error_trees+=["\t".join([textname, str(snr), user, "node "+str(checkTree(sentencetree)[2])+" points to itself"])]
				else:
					error_trees+=["\t".join([textname, str(snr), user, "no gov at node "+str(checkTree(sentencetree)[2])])]
				trees.remove(sentencetree)
				#print "nr arbres",len(trees)
		lastpourc=pourc
	print len(error_trees), "arbre(s) avec erreurs."
	if len(error_trees) > 0:
		print "\t".join(["Texte", "num phrase", "correcteur", "cause"])
		for x in sorted(list(set(error_trees))):
			print x
		f=codecs.open(folder+"logs/log_erreurs."+datetime.datetime.now().strftime('%Y-%m-%d')+".tsv", "w", "utf-8")
		f.write("\t".join(["Texte", "num phrase", "correcteur", "cause"])+'\n')
		for e in error_trees:
			f.write(e+'\n')
		f.close()
		print "Erreurs dans", f.name
	print len(trees), "arbres restants pour entrainement"
	#Creation d'un fichier log
	db.commit()
	db.close()
	return trees

def printTree(project,treeid):
	sql = SQL(project)
	db,cursor=sql.open()
	dic=sql.gettree(None,None,treeid, indb=db,incursor=cursor) # dic -> get tree == on récupère l'arbre
	#print dic
	if dic and dic["tree"]:
		sentencetree=dic["tree"]
		#sentencetree=corrigerNumerotation(sentencetree)
		for i in sorted(sentencetree):
			print i, sentencetree[i]


if __name__ == "__main__":
	ti = time.time()
	#project="OrfeoGold2016"
	project="hongkongtvmandarin.2016-08-23_15:29"
	printTree(project,9669)
	#trees = getValidatedTrees("test_mini_db_backup")
	#conll.trees2conll10(trees, "./mate/test_200816.conll")
	#print "it took", (time.time()-ti)/60, "minutes."
	#pprint(trees2copy)
	
	
	
	