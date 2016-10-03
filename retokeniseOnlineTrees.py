#! usr/bin/python
#! coding: utf-8

import database, retokenisation, newmate, pprint, sys

def modifyAllTreesFromAllUsers(project):
	sql = database.SQL(project)
	db, cursor = sql.open()
	command = "select sentences.rowid, sentences.nr, sentences.textid, trees.userid, trees.rowid from sentences, texts, trees where sentences.textid=texts.rowid and trees.sentenceid = sentences.rowid;"
	cursor.execute(command)
	answer = cursor.fetchall()
	print len(answer), "trees to update"
	lastpourc=-1
	for nr, (sid, snr, tid, uid, treeid) in enumerate(answer):
		pourc = int(float(nr)/len(answer)*100)
		if pourc!=lastpourc: sys.stdout.write( "{pourc}%\r".format(pourc=pourc) )
		sys.stdout.flush()
		dic=sql.gettree(None,None,treeid, indb=db,incursor=cursor)
		if dic and dic["tree"]:
			sentencetree=dic["tree"]
			#print "Resgmentation en cours de ", " ".join([node["t"] for i, node in sentencetree.iteritems()]), "id=", treeid, "by user", uid
			#newtree=retokenisation.retokenizeTree(sentencetree)
			newtree=retokenisation.segmentationChiffres(sentencetree)
			#pprint.pprint(newtree)
			sql.enterTree(cursor, newtree, sid, uid, tokensChanged=True)
			#print "Tree", treeid," successfully updated."
	print "Done."
	db.commit()
	db.close()


if __name__ == "__main__":
	project="OrfeoGold2016"
	newpath=newmate.backupOldDatabase(project, "./oldprojects/")
	print "copie de la base dans", newpath
	modifyAllTreesFromAllUsers(project)


