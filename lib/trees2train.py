#! usr/bin/python
#! coding: utf-8

import conll, datetime, codecs, time, sys, os, glob
from database import SQL
from pprint import pprint

"""
TODO :
- documenter scripts
- mettre en place le cron
"""

#ti = time.time()-86400




def exportUniqueSentences(project, mode="lasttree",pattern=False):
	"""
	exports one tree per sentences: the first time the sentence is found, the newest tree
	"""
	sql = SQL(project)
	db,cursor=sql.open()
	sentences={} # toks -> tree
	outdir=os.path.join("..","projects",project,"export")
	try: os.mkdir(outdir)	
	except OSError: pass
	outfile=os.path.join(outdir,"allSentences.conll")
	if pattern:
		command="""select trees.rowid,userid,max(timestamp) from trees, sentences, texts where texts.rowid=sentences.textid and sentences.rowid=trees.sentenceid 
		and textname like "{pattern}"
		group by sentenceid order by trees.rowid;""".format(pattern=pattern)
	else:
		command="""select trees.rowid,userid,max(timestamp) from trees, sentences, texts where texts.rowid=sentences.textid and sentences.rowid=trees.sentenceid 
		group by sentenceid order by trees.rowid;"""
	for i,(treeid,userid,timestamp,) in enumerate(cursor.execute(command).fetchall()):
		tree=sql.gettree(treeid=treeid, indb=db, incursor=cursor)["tree"]
		toks=tuple(tree[i]["t"] for i in tree)
		print "___",i, "\r",
		if toks not in sentences:
			sentences[toks]=tree
	print "writing file with",len(sentences),"sentences..."
	conll.trees2conllFile([sentences[toks] for toks in sorted(sentences)], outfile=outfile, columns=10)
	return outfile


def exportGoodTexts(project, lastHuman=False, onlyValidated=True, pattern=False):
	"""
	TODO :
	- ajouter parametre p/selectionner Texte
	ex : "UD_ZH_[number]"
	"""
	outfiles=[]
	sql = SQL(project)
	db,cursor=sql.open()
	goodTexts={}
	if onlyValidated:onlyValidated="and todos.status=1"
	else: onlyValidated=""
	# take all texts where a validator has validated
	if pattern: command="select distinct * from texts, todos, users where texts.rowid=todos.textid and users.rowid=todos.userid and texts.textname {pattern};".format(pattern=pattern) # like 'UD_ZH%'
	else: 
		command="select distinct * from texts, todos, users where texts.rowid=todos.textid and todos.type=1 {onlyValidated} and users.rowid=todos.userid;".format(onlyValidated=onlyValidated)
		
	for row in cursor.execute(command): 
		textname, nrtokens, userid, textid, validator, status, comment, user, realname = row

			
		goodTexts[textid]=(textname, userid, user)
		print "i'll take",textname,"validated by",user,"with", nrtokens, "tokens"
	sentenceValidationInValidatedText(cursor, sql, db)
	outdir=os.path.join("..","projects",project,"export")
	try: os.mkdir(outdir)	
	except OSError: pass

	for textid,(textname, userid, user) in goodTexts.iteritems():
		textname=textname.replace("-one-word-per-line.conll14_Parse","")
		
		if lastHuman: outfile=os.path.join(outdir,textname+".lastHuman.conll")
		else: outfile=os.path.join(outdir,"validated."+textname+"."+user+".conll")
		print "doing",textname,textid
		trees=[]
		
		if lastHuman:
			snr2all={}
			for row in cursor.execute("""
			select sentences.nr as snr, trees.rowid as treeid, users.user, trees.timestamp 
			from sentences, trees, users 
			where sentences.textid=? 
			and sentences.rowid=trees.sentenceid 
			and users.rowid = trees.userid; """,(textid,)):
				snr,treeid,user,timestamp=row
				snr2all[snr]=snr2all.get(snr,[])+[(timestamp,user,treeid)]
			lastpourc=-1	
			for c,snr in enumerate(sorted(snr2all)):
				pourc = int(float(c)/len(snr2all)*100)
				if pourc!=lastpourc: print "___{pourc}%___\r".format(pourc=pourc),
				
				lastusersnotparser=sorted([(timestamp,user,treeid) for (timestamp,user,treeid) in snr2all[snr] if user not in ["parser","mate"]])
				if len(lastusersnotparser) > 0:
					time, u, tid = lastusersnotparser[-1] # last tree by human
				else:
					time, u, tid = sorted(snr2all[snr])[-1] # last tree by whoever
				#print "je prends l'arbre de",u
				trees+=[sql.gettree(treeid=treeid, indb=db, incursor=cursor)["tree"]]
			
		else:
			
			for (treeid,sentencenr,) in cursor.execute("select trees.rowid, sentences.nr from texts, trees, sentences where texts.rowid=? and trees.userid=? and trees.sentenceid = sentences.rowid and sentences.textid=texts.rowid order by sentences.nr;",(textid,userid,)).fetchall(): 
				#print "ooo",sentencenr,"\r",
				print "nr",sentencenr,"_____\r",
				trees+=[sql.gettree(treeid=treeid, indb=db, incursor=cursor)["tree"]]
		
		print "exporting",len(trees),"trees into",outfile
		outfiles+=[outfile]
		conll.trees2conllFile(trees, outfile, columns=10)
	return outfiles

def getTreesForSents(sents, trees, annotators, parserid, cursor, db, sql):
	"""
	for each entry in sents,
	adds new trees to trees and annotators
	"""
	for i,(sid,nr,sentence,teid) in enumerate(sents):
		print "\r",i,
		if parserid>=0:
			tr=list(cursor.execute("select trees.rowid,* from trees, users where sentenceid=? and userid<>? and userid=users.rowid order by timestamp DESC limit 1;",(sid,parserid)).fetchall())
		else:
			tr=list(cursor.execute("select trees.rowid,* from trees, users where sentenceid=? and userid=users.rowid order by timestamp DESC limit 1;",(sid,)).fetchall())
		#print trees
		if len(tr):
			treeid, sidd, usid, annotype, status, comment, ts, user, realname=tr[0]
			tree=sql.gettree(treeid=treeid, indb=db, incursor=cursor)["tree"]
			#print tree
			trees+=[tree]
			annotators[user]=annotators.get(user,0)+1
		#print sentence,trees


def lastTreeForAllSamples(project, onlyHuman=True, combine=False):
	outdir=os.path.join("..","projects",project,"export")
	try: os.mkdir(outdir)	
	except OSError: pass
	sql = SQL(project)
	db,cursor=sql.open()
	if onlyHuman:
		parserid=0
		for pid, in cursor.execute("select rowid from users where user='parser';"): parserid=pid
	else:
		parserid=-1
	sents=list(cursor.execute("select rowid, * from sentences;").fetchall())
	print "todo:",len(sents),"sentences"
	
	annotators={}
		
	if combine:
		trees=[]
		getTreesForSents(sents, trees, annotators, parserid, cursor, db, sql)
		outfile=os.path.join(outdir,project+".lastHumanTreeForAllSamples.conll")	
		conll.trees2conllFile(trees, outfile=outfile, columns=10)
		print "wrote",outfile
		
	else:
		for tid,textname,nrtokens in list(cursor.execute("select rowid, * from texts;")):
			print tid, textname, nrtokens
			sents=list(cursor.execute("select rowid, * from sentences where textid=?;",(tid,)).fetchall())
			trees=[]
			getTreesForSents(sents, trees, annotators, parserid, cursor, db, sql)
			if textname.endswith(".conll_parse"): textname=textname[:len(".conll_parse")]
			outfile=os.path.join(outdir,textname+".lastHumanTrees.conll")	
			conll.trees2conllFile(trees, outfile=outfile, columns=10)
			print "wrote",outfile
	print annotators


def getSpecificTrees(db, cursor, nrutids, annotatorIds):
	trees=[]
	for nr in sorted(nrutids): # for each sentence
		tree=None
		for aid in annotatorIds: # for each interesting annotator id
			if aid in nrutids[nr]:
				tree=sql.gettree(treeid=nrutids[nr][aid], indb=db, incursor=cursor)["tree"]
				trees+=[tree]
				#print "atree:",tree
				break
		if not tree:
			print "problem: no tree for nr",nr,"type",type(nr)
			print "annotatorIds",annotatorIds				
			return []
			#raise Exception('no tree', nr)
	return trees


def exportConllByAnnotators(project, annotators=["prof","Sy","parser"]):
	"""
	exports complete project
	for every sentence, trees of annotators in given order.
	if no tree: throw error 
	
	"""
	outfiles=[]
	sql = SQL(project)
	db,cursor=sql.open()
	goodTexts={}
	outdir=os.path.join("..","projects",project,"export")
	try: os.mkdir(outdir)	
	except OSError: pass
	try:	annotatorIds=tuple(a for (a,) in [list(cursor.execute("select rowid from users where user =?;",(annotator,) ))[0] for annotator in annotators])
	except:
		print "some required annotator IDs are not in the database"
		return
	#print annotators, annotatorIds
	
	for textid, textname, nrtokens in list(cursor.execute("select rowid, * from texts;" )):  # for each text
		print "doing",textname,"with", nrtokens, "tokens"
		nrutids={}
		for nr,userid,treeid in list(cursor.execute("select nr,userid,trees.rowid as treeid from trees, sentences where sentenceid=sentences.rowid and userid in {annotatorIds} and  textid = ? order by nr;".format(annotatorIds=annotatorIds),(textid,))):
			nrutids[nr]=nrutids.get(nr,{})
			nrutids[nr][userid]=treeid
		trees=getSpecificTrees(db, cursor, nrutids, annotatorIds)
		if trees:
			if textname.endswith(".conll"): textname=textname[:-len(".conll")]
			outfile=os.path.join(outdir,textname)
			conll.trees2conllFile(trees, outfile=outfile, columns=10)
			print len(trees),"trees"
			outfiles+=[outfile]
		else:
			print "skipped",textname
	return outfiles

lemmacorrection=dict( [(a.split(":")[0],a.split(":")[1]) for a in u"""
c' est-à-dire que:c'est-à-dire que
est-ce-que:est-ce que
quelques-un:quelques-uns
Ax-~~:Ax~
festiv-été:Festiv-été
t-il:il
ouvre-moi:ouvrir
trouve-moi:trouver
rappelle-moi:rappeler
débrouille-toi:débrouiller
met-il:mettre
es-tu:être
doit-on:devoir
moment-là:moment
gars-là:gars
jour-là:jour
bruit-là:bruit
mois-là:mois
festival-là:festival
côté-là:côté
jeunes-là:jeunes
niveau-là:niveau
celui-là:celui
lui-même:lui
sapeurs-pompier:sapeur-pompier
proposition-là:proposition
petit-à-petit:petit à petit
groupe-là:groupe
titre-là:titre
stylo-là:stylo
pays-là:pays
sens-là:sens
faut-il:falloir
passe-moi:passer
appelez-le:appeler

""".strip().split("\n")])

def correctLemmas(tree):
	for iii in tree: 
		tree[iii]["tag2"]="_"
		if tree[iii]["lemma"] in lemmacorrection:
			tree[iii]["lemma"]=lemmacorrection[tree[iii]["lemma"]]


def fusionForgottenTrees(project="Platinum",fusdir="../projects/OrfeoGold2016/platinum/*", annotators=["admin"]):
	"""
	takes trees from project ordered by annotators. if they exist fuse them into the fusdir
	result has the extension "cool.conll"
	,"Sy","Marion"
	"""
	
	#print lemmacorrection
	sys.path.insert(0, '../tools')
	import difflib
	outfiles=[]
	sql = SQL(project)
	db,cursor=sql.open()
	goodTexts={}
	outdir=os.path.join("..","projects",project,"exportcool")
	try: os.mkdir(outdir)	
	except OSError: pass
	for annotator in annotators:
		print [list(cursor.execute("select rowid from users where user =?;",(annotator,) ))]
	annotatorIds=tuple(a for (a,) in [list(cursor.execute("select rowid from users where user =?;",(annotator,) ))[0] for annotator in annotators])
	print annotators, annotatorIds
	
	for textid, textname, nrtokens in list(cursor.execute("select rowid, * from texts;" )):  # for each text
		print "\n__________________________doing",textname,"with", nrtokens, "tokens"
		nrutids={}
		for nr,userid,treeid in list(cursor.execute("select nr,userid,trees.rowid as treeid from trees, sentences where sentenceid=sentences.rowid and userid in {annotatorIds} and  textid = ? order by nr;".format(annotatorIds=annotatorIds),(textid,))):
			nrutids[nr]=nrutids.get(nr,{})
			nrutids[nr][userid]=treeid
		trees={}
		for nr in sorted(nrutids): # for each sentence
			tree=None
			for aid in annotatorIds: # for each interesting annotator id
				if aid in nrutids[nr]:
					tree=sql.gettree(treeid=nrutids[nr][aid], indb=db, incursor=cursor)["tree"]
					trees[nr]=tree
					#print "atree:",tree
					break
			#if not tree:
				#print "problem: no tree for nr",nr,"type",type(nr)
				#print "annotatorIds",annotatorIds				
				#raise Exception('no tree', nr)
		#print trees
		print len(trees),"trees from", project
		print textname,textname.split(".")[0]
		btextname=os.path.basename(textname).split(".")[0] 
		if btextname.endswith("-one-word-per-line"): btextname=btextname[:-len("-one-word-per-line")]
		#print glob.glob(fusdir),[os.path.basename(fi).split(".")[0] for fi in glob.glob(fusdir)]
		cooltrees=[]
		ptrees,ftrees=0,0
		for fi in glob.glob(fusdir):
			if btextname == os.path.basename(fi).split(".")[0] :
				print "yes",btextname
				fustrees=conll.conllFile2trees(fi)
				print len(fustrees),"ftrees",fi
				for nr,ftree in enumerate(fustrees):
					if nr+1 in trees:
						#print "added tree",nr+1,"from database"
						#ptree=platinum(trees[nr+1])
						ptree=trees[nr+1]
						for iii in ptree: 
							ptree[iii]["tag2"]="_"
							if ptree[iii]["lemma"] in lemmacorrection:
								ptree[iii]["lemma"]=lemmacorrection[ptree[iii]["lemma"]]
						cooltrees+=[ptree]
						#print nr+1,"tree from",project#,tree
						ptrees+=1
						if ftree.sentence() != u" ".join([ptree[i].get("t","") for i in sorted(ptree)]):
							print "\n_________",nr+1
							print ftree.sentence() 
							print u" ".join([ptree[i].get("t","") for i in sorted(ptree)])
							#for l in difflib.context_diff(ftree.sentence() ,u" ".join([ptree[i].get("t","") for i in sorted(ptree)])):print l
							
						#print "dbtree",platinum(trees[nr+1])
					else:						
						for iii in ftree: 
							ftree[iii]["tag2"]="_"
							if ftree[iii]["lemma"] in lemmacorrection:
								ftree[iii]["lemma"]=lemmacorrection[ftree[iii]["lemma"]]
						#print nr+1,"tree from",fusdir#,tree
						ftrees+=1
						cooltrees+=[ftree]
						#print "added tree",nr+1,"from fustrees",fi
				outfile=os.path.join(outdir,textname+".cool.conll")
				conll.trees2conllFile(cooltrees, outfile=outfile, columns=10)
				print "wrote",outfile
				print ptrees,"ptrees, ",ftrees,"ftrees"
				break
		if len(cooltrees)==0:print "nothing for",btextname
		outfiles+=[outfile]
		#qsdf
	return outfiles

def createNonExistingFolders(path):
	print "createNonExistingFolders",path
	head, tail = os.path.split(path)
	if head=="":
		if tail and not os.path.exists(tail): os.makedirs(tail)
	else:
		createNonExistingFolders(head)
	if head and not os.path.exists(head): os.makedirs(head)
	
def addArbitraryPuncs(infolder,outfolder):
	createNonExistingFolders(outfolder)
	for conllinfile in glob.glob(os.path.join(infolder, '*')):
		if os.path.isfile(conllinfile):
			print conllinfile
			trees=conll.conllFile2trees(conllinfile)
			for i,tree in enumerate(trees):
				m=max(tree)
				splitcode=".,!?;:()"
				p=splitcode[i%len(splitcode)]
				tree[m+1]={u'tag': u'PUNC', u'lemma': p, u't': p, 'gov': {0: u'punc'}}
			conll.trees2conllFile(trees, os.path.join(outfolder,os.path.basename(conllinfile)), columns=14)

def splitSentenceFile(infile,splitcode="abc"):
	"""
	splits the lines of a file in different files with the extensions given as letters in splitcode
	careful: "a"=append mode -> next run it adds to the existing file!
	"""
	with codecs.open(infile,"r","utf-8") as f:
		for c,li in enumerate(f):
			print c, li, c%len(splitcode)
			with codecs.open(infile.split(".")[0]+"."+splitcode[c%len(splitcode)],"a","utf-8") as out:
				out.write(li)


def databaseQuery(cursor,table="all", values=[]):
	
	if table == "all":
		command="select distinct trees.rowid, texts.textname, users.user, sentences.nr, trees.* from texts, trees, sentences, users where trees.status = 1 and trees.sentenceid = sentences.rowid and sentences.textid=texts.rowid and trees.userid=users.rowid ;"
	elif table == "validator":
		command="select distinct trees.rowid, texts.textname, users.user, sentences.nr, trees.* from texts, trees, sentences, users, todos where trees.status = 1 and trees.sentenceid = sentences.rowid and sentences.textid=texts.rowid and trees.userid=users.rowid and todos.userid=users.rowid and todos.type=1 and todos.textid=texts.rowid;"
	
	elif table=="duplicate":
		command="""
		select sentences.rowid as sid, trees.rowid as treeid, users.user as annotator, todos.userid as validatorid, trees.timestamp 
		from sentences, todos, trees, users where 
		todos.status=1 and todos.type=1 -- we want texts that are marked ok (status=1) by validators (type=1) not just vulgar annotators (type=0)
		and sentences.textid=todos.textid 
		and sentences.rowid=trees.sentenceid 
		and users.rowid = trees.userid 
		and sentences.rowid not in  (select sentenceid from trees,  (select sentences.rowid as y from sentences, todos  where todos.status=1 and todos.type=1 and sentences.textid=todos.textid) as x  where x.y = trees.sentenceid and trees.status = 1);

		"""
		
	
	cursor.execute(command, values)
	a = cursor.fetchall()
	return a

def sentenceValidationInValidatedText(cursor, sql, db):
	print "sentenceValidationInValidatedText: consolidating the database by creating trees for validators that don't have all the trees for texts they have marked as ok"
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
				if gi > len(sentencetree):
					return False, "weird link", i
			if -1 in node["gov"]:
				return False, "nogov", i
		else:
			return False, "nogov", i
	return True, "ok", 0

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
		#if textname.startswith("mandarinParsed"):continue
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

def split(conllfile,maxi):
	trees=conll.conllFile2trees(conllfile)
	for j,ts  in enumerate([trees[i:i+maxi] for i in range(0, len(trees), maxi)]):
		conll.trees2conllFile(ts,conllfile+str(j))
	

if __name__ == "__main__":
	ti = time.time()
	#project="OrfeoGold2016"
	#project="hongkongtvmandarin.2016-08-23_15:29"
	#printTree(project,9669)
	#trees = getValidatedTrees("test_mini_db_backup")
	#conll.trees2conllFile(trees, "./mate/test_200816.conll")
	#print "it took", (time.time()-ti)/60, "minutes."
	#pprint(trees2copy)
	#exportGoodTexts("OrfeoGold2016")
	
	#exportGoodTexts("OrfeoGold2016", lastHuman=True, onlyValidated=False)
	#addArbitraryPuncs("../projects/Platinum/exportcorrected/","../projects/Platinum/punc/")
	#splitSentenceFile("exo1sents.txt")

	#exportGoodTexts("HongKongTVMandarin", lastHuman=True, onlyValidated=False, pattern="UD_ZH%")
	#print exportConllByAnnotators("SyntaxeAlOuest", annotators=["prof","Sy"])
	#print exportConllByAnnotators("OrfeoGold2016", annotators=["Sy","Marion","parser"])
	
	#split("../projects/OrfeoGold2016/platinum/Rhaps.gold",1000)
	#print len(conll.conllFile2trees("../projects/Platinum/exportcool/Rhaps"))
	#fusionForgottenTrees()
	
	#exportGoodTexts("Platinum", lastHuman=True, onlyValidated=False)
	#addArbitraryPuncs("../projects/Platinum/export","../projects/Platinum/punc/")
	#print exportConllByAnnotators("Platinum", annotators=["Sy","admin","gold","parser"])
	#exportUniqueSentences("Platinum", pattern="ftb%")
	#exportUniqueSentences("Platinum", pattern="ftb-3-vadvv%")
	#exportUniqueSentences("templingCorpus2016")
	#lastHumanTreeForAllSamples("Platinum")
	#lastTreeForAllSamples("templingCorpus2016", onlyHuman=False, combine=True)
	lastTreeForAllSamples("Platinum", onlyHuman=False, combine=False)
