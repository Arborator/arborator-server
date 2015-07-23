#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2013 Kim Gerdes
# kim AT gerdes. fr
# http://arborator.ilpga.fr/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public License (the "License")
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of of version 3 of the GNU Affero General Public License
# from http://www.gnu.org/licenses/agpl-3.0.html 
# For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####

from datetime import datetime
from time     import mktime, time, asctime, localtime
from sqlite3   import connect, OperationalError
import sys, os, re, json
from configobj import ConfigObj
import codecs
import config
import rhapsoxml

debug=False
#debug=True

if debug:import traceback

class SQL:
	def __init__(self, project):
		#,config.projects[0].encode('utf-8')
		if not project:
			try:project = config.projects[0]
			except:print "something went seriously wrong: can't find any projects"
		self.projectconfig = config.configProject(project) # read in the settings of the current project
		self.dbpath = ("projects/"+project+"/"+self.projectconfig["configuration"]["db"]).encode('utf-8')
		self.exportpath = "projects/"+project+"/"+self.projectconfig["configuration"]["exportfolder"]+"/"
		self.visibleToEveryone = dict([(v,None) for v in self.projectconfig["visible to everyone"].values()])
		self.baseAnnotatorName = self.projectconfig["configuration"]["baseAnnotatorName"]
		self.exoBaseAnnotatorName = self.projectconfig["configuration"].get("exoBaseAnnotatorName",self.baseAnnotatorName)
		self.teacher = self.projectconfig["configuration"].get("teacher","admin")
		
		self.newTree = self.projectconfig["configuration"]["newTree"]
		self.tokenName = self.projectconfig["shown features"]["0"]
		self.catName = self.projectconfig["shown features"][self.projectconfig["configuration"]["categoryindex"]]
		self.treeorder = self.projectconfig["configuration"]["treeorder"]
		self.showTreesOfValidatedTexts = None
		if self.projectconfig["configuration"]["showTreesOfValidatedTexts"] in self.projectconfig["text status"]:
			self.showTreesOfValidatedTexts = self.projectconfig["configuration"]["showTreesOfValidatedTexts"]
		self.allVisibleForNonAnnotators=int(self.projectconfig["configuration"].get("allVisibleForNonAnnotators","0"))
		self.validatorsCanModifyTokens=int(self.projectconfig["configuration"].get("validatorsCanModifyTokens","0"))
		self.usersCanModifyTokens=int(self.projectconfig["configuration"].get("usersCanModifyTokens","0"))
		self.sentencefeaturesAlways=int(self.projectconfig["configuration"].get("sentencefeaturesAlways","0"))
		
		
		self.editable=self.projectconfig["configuration"]["editable"]
		
		self.governorsVal=int(self.projectconfig["evalutation scores"]["governors"])
		self.functionsVal=int(self.projectconfig["evalutation scores"]["functions"])
		self.categoriesVal=int(self.projectconfig["evalutation scores"]["categories"])
		self.lemmasVal=int(self.projectconfig["evalutation scores"]["lemmas"])
		self.evalTot=float(self.governorsVal+self.functionsVal+self.categoriesVal+self.lemmasVal)
		
		self.exotypes=["no exercise","no feedback","percentage","graphical feedback","teacher visible"] # TODO: get this into configuration. important: only if index >1 the user gets the check button, see the main function in editor.cgi
		
		

	def open(self):
		db = connect(self.dbpath, check_same_thread = False)
		
		cursor = db.cursor()
		cursor.execute("PRAGMA journal_mode=WAL;")
		
		return db, cursor
		
	def enter(self, cursor, table, colons, values, computeId=True):
		"""
		general function to add data into the database
		"""
		#open("logger.txt","a").write("enter "+str(colons)+"\n")
		#print "INSERT OR IGNORE INTO "+table+" (" + ",".join(colons)+ ") VALUES (" + ",".join(len(values)*"?")+ ") ;"
		#print values
		cursor.execute("INSERT OR IGNORE INTO "+table+" (" + ",".join(colons)+ ") VALUES (" + ",".join(len(values)*"?")+ ") ;", values)
		if computeId:
			cursor.execute("select rowid from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + ";",values)
			id=cursor.fetchone()
			if id:
				id,=id
				return int(id)
			else:
				return None
			
			
		else: return None
	
	def clean(self, cursor, table, colons, values):
		cursor.execute("delete from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + ";",values)
	
	def getall(self, cursor, table, colons=[], values=[], tries=0, orderby=""):
		# TODO: check if this retry loop is really useful...
		
		if tries<2:
			try:
				if cursor:
					#print "select rowid,* from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + ";",values
					
					if colons: cursor.execute("select rowid,* from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + " "+orderby+ ";",values)
					else: cursor.execute("select rowid,* from "+table+ " "+orderby+ ";")
					return cursor.fetchall()
				else:
					db,cursor=self.open()
					if colons: cursor.execute("select rowid,* from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + " "+orderby + ";",values)
					else: cursor.execute("select rowid,* from "+table+ " "+orderby+ ";")
					a = cursor.fetchall()	
					db.close()
					return a
					
			except Exception , e:
				from sqlite3 import OperationalError
				if isinstance(e, OperationalError) and str(e)in["attempt to write a readonly database","unable to open database file"]:
					print "Error! Make your database and the path leading there from the arborator base modifiable by the apache user!"
					sys.exit("something's wrong")
					
				else:
					if debug:print traceback.format_exc()
					#print msg
					return self.getall(cursor, table, colons, values, tries+1)
				#


			#except Exception, msg:

		else:
			print "problem with database. try to refresh the page!"



	def getUniqueId(self, cursor, table, colons, values):
		if colons: cursor.execute("select rowid,* from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + ";",values)
		else: cursor.execute("select rowid,* from "+table+ ";")
		a = cursor.fetchone()
		if a: return int(a[0])
		else: return None


	def getnumber(self, cursor, table, colons, values):
		if cursor:
			if colons: cursor.execute("select count(*) from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + ";",values)
			else: cursor.execute("select count(*) from "+table+ ";")
			return cursor.fetchone()[0]
		else:
			db,cursor=self.open()
			if colons: cursor.execute("select count(*) from "+table+"  where "+ " and ".join( [c+"=?" for c in  colons ] ) + ";",values)
			else: cursor.execute("select count(*) from "+table+ ";")
			a = cursor.fetchone()[0]
			db.close()
			return a



	def getNumberTexts(self):
		"""
		returns number of texts in the table
		"""
		db,cursor=self.open()
		cursor.execute("""select count(*) from texts""")
		number=cursor.fetchone()[0]
		db.close()
		return number

	def getNumberSentences(self):
		"""
		returns number of sentences in the table
		"""
		db,cursor=self.open()
		cursor.execute("""select count(*) from sentences""")
		number=cursor.fetchone()[0]
		db.close()
		return number

	def getNumberTreesPerUserAndText(self, uid, tid):
		"""
		returns number of trees the user has saved
		"""
		db,cursor=self.open()
		cursor.execute("""select count(*) from trees, sentences where sentences.textid=? and trees.userid=? and sentences.rowid=trees.sentenceid;""",(tid,uid,))
		number=cursor.fetchone()[0]
		db.close()
		return number

	def getNumberTokensPerText(self, tid, recompute=False):
		"""
		returns number of tokens
		"""
		db,cursor=self.open()

		for _,_,number in self.getall(cursor, "texts",["rowid"], [tid]):
			break
		try:
			if recompute: raise bloedError
			number=int(number)
			db.close()
			return number
		except:


			cursor.execute("""select count(*) from features, sentences, trees, users where users.user=? and users.rowid=trees.userid and trees.rowid=features.treeid and trees.sentenceid=sentences.rowid and sentences.textid=? and features.attr=?;""",(self.baseAnnotatorName,  tid, self.tokenName, ))

			number=cursor.fetchone()[0]
			cursor.execute('update texts set nrtokens=? where rowid=?', (number,tid,))

			db.commit()
			db.close()
			return number


	def enterTree(self,cursor, nodedic, sentenceid, userid, notenter=[], intokenname=None, tokensChanged=False):
		"""
		takes the db cursor, nodedic, sentenceid, userid, t (the name of the feature that serves as the token = invariable by the annotators)
		drops tree into database
		returns word counter

		called in two cases:
		- a new tree is entered whose tokens are not in the base yet
		- a tree is saved: a treeid already exists, all the features are erased first
		"""
		#open("logger.txt","a").write("enterTree "+str( [cursor, nodedic, sentenceid, userid, notenter, intokenname, tokensChanged])+"\n")
		#print nodedic, sentenceid, userid, intokenname
		if not intokenname:  intokenname=self.tokenName

		wcounter=0
		timestamp = mktime( datetime.now().timetuple() ) # contrary: asctime(localtime(timestamp))


		treeid=self.getUniqueId(cursor, "trees", ["sentenceid","userid","annotype"],[sentenceid, userid, 0])
		if treeid:
			#open("logger.txt","a").write("enterTree2 treeid existed\n")
			self.clean(cursor, "features",["treeid"],(treeid,))
			self.clean(cursor, "links",["treeid"],(treeid,))
			cursor.execute("update trees set timestamp=? where sentenceid=? and userid=? and annotype=?;",(timestamp, sentenceid, userid, 0,))

		else:
			#open("logger.txt","a").write("enterTree2 treeid didn't exist\n")
			treeid=self.enter(cursor, "trees",["sentenceid","userid","annotype","status","timestamp"],(sentenceid,userid,0,"0",timestamp),True) # createIfNotExists
			self.clean(cursor, "features",["treeid"],(treeid,)) # erase all existing features for this treeid, should be a useless line. just in case...
			self.clean(cursor, "links",["treeid"],(treeid,))


		sent=""

		for i in sorted(nodedic.keys()): # for every token

			tok=nodedic[i].get(intokenname,"")
			sent+=tok+" "
			if tokensChanged:
				cursor.execute("update features set value=? where features.attr=? and features.nr=? and features.treeid=(select trees.rowid from trees where trees.sentenceid =?)",(tok, self.tokenName, i, sentenceid,))

			wcounter+=1
			# enter attributes for token
			for attr in nodedic[i]:
				if attr not in notenter:
					val=nodedic[i][attr]
					if type(val).__name__=='list':
						# not nice: values tabseparated. but not used for the moment
						#for v in val: # doesn't work because database doesn't allow multiple features of same attr
						self.enter(cursor, "features",["treeid","nr","attr","value"],(treeid,wcounter,attr,"\t".join(val),), computeId=False)
					elif type(val).__name__=='dict': # should only happen for attr="gov"
						for gov in val:
							self.enter(cursor, "links",["treeid","depid","govid","function"],(treeid,wcounter,gov,val[gov],), computeId=False)
					else: # atomic value
						#if attr!=t:
						if attr==intokenname: attr=self.tokenName # change the token name in the nodedic to the project's token name
						self.enter(cursor, "features",["treeid","nr","attr","value"],(treeid,wcounter,attr,val,), computeId=False)
		return wcounter, sent.strip(), treeid



	def saveTree(self, sentenceid, userid, words, tokensChanged=False):
		""" 	js to sqlite
			called from save.cgi
			gets a special format tree: words (ids are still strings etc)
			calls enterTree for entering
			returns the new tree id
		"""
		db,cursor=self.open()


		nodedic={}
		for i in words:
			nodedic[int(i)]={}
			for k in words[i]:
				if k=="features":
					for a in words[i][k]:
						nodedic[int(i)][a]=words[i][k][a]
				else:
					nodedic[int(i)][k]=words[i][k]
		#open("logger.txt","a").write("saveTree "+str(nodedic)+"\n"+str(tokensChanged)+"\n")

		wcounter, sent, treeid = self.enterTree(cursor, nodedic, sentenceid, userid,tokensChanged=True)
		#open("logger.txt","a").write("___return to saveTree "+str(nodedic)+"\n"+str(tokensChanged)+"\n")
		if tokensChanged:
			for (nnr,ty) in tokensChanged:
				if ty==1:self.duplicateNode(nnr,sentenceid, cursor)
				elif ty==-1:self.eraseNode(nnr,sentenceid, cursor)

			sent=" ".join([a for a, in cursor.execute("select value from features where attr='t' and treeid in (select trees.rowid from trees, users where trees.sentenceid =? and users.user=? and users.rowid=trees.userid) ORDER BY nr ;",(sentenceid,self.baseAnnotatorName,)).fetchall()])

			cursor.execute("UPDATE sentences SET sentence=? WHERE rowid=? ",(sent,sentenceid,))
			cursor.execute("UPDATE sentencesearch SET sentence=? WHERE rowid=? ",(sent,sentenceid,))
		db.commit()
		db.close()
		if tokensChanged:
			return treeid,self.gettree(None,None,treeid), sent
		return treeid, None, None



	def duplicateNode(self,nnr,sentenceid, cursor):

		cursor.execute("update features set nr=-nr where nr>=? and features.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr,sentenceid,))
		cursor.execute("update features set nr=1-nr where nr<0 and features.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(sentenceid,))
		cursor.execute("insert into features (treeid, nr,attr,value) select treeid,nr-1,attr,value from features where nr=? and features.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr+1,sentenceid,))

		cursor.execute("update links set depid=depid+1 where depid>=? and links.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr,sentenceid,))
		cursor.execute("update links set govid=govid+1 where govid>=? and links.treeid  in (select trees.rowid from trees where trees.sentenceid =?)",(nnr,sentenceid,))

		cursor.execute("insert into links (treeid, govid, depid, function) select treeid, govid-1, depid, function from links where govid=? and links.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr+1,sentenceid,))
		cursor.execute("insert into links (treeid, govid, depid, function) select treeid, govid, depid-1, function from links where depid=? and links.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr+1,sentenceid,))


	def eraseNode(self,nnr,sentenceid, cursor):

		cursor.execute("delete from features where nr=? and treeid in (select trees.rowid from trees where trees.sentenceid =?);",(nnr,sentenceid,))
		cursor.execute("delete from links where govid=? and treeid in (select trees.rowid from trees where trees.sentenceid =?);",(nnr,sentenceid,))
		cursor.execute("delete from links where depid=? and treeid in (select trees.rowid from trees where trees.sentenceid =?);",(nnr,sentenceid,))
		cursor.execute("update features set nr=-nr where nr>=? and features.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr,sentenceid,))
		cursor.execute("update features set nr=-1-nr where nr<0 and features.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(sentenceid,))
		cursor.execute("update links set depid=depid-1 where depid>=? and links.treeid in (select trees.rowid from trees where trees.sentenceid =?)",(nnr,sentenceid,))
		cursor.execute("update links set govid=govid-1 where govid>=? and links.treeid  in (select trees.rowid from trees where trees.sentenceid =?)",(nnr,sentenceid,))




	def exportAnnotations(self, textid, textname, exportType):
		"""conll and xml export
		called from project.cgi
		for export of complete sets of annotations
		"""
		db,cursor=self.open()

		scounter, fcounter, users=0,0,[]
		doublegovs=False
		renolet=re.compile("\W",re.U+re.I)
		basefilename=renolet.sub(".",textname.strip().replace(" ","_").replace("?",""))
		if not os.path.exists(self.exportpath.encode("utf-8")): os.makedirs(self.exportpath.encode("utf-8"))
		importannoname=self.baseAnnotatorName
		parserid=self.getUniqueId(cursor, "users", ["user"],[importannoname])


		if exportType in ["todosconll", "todosxml"]: 	# only todos are exported, __complete__ conll or xml files are created, non existing trees are filled up with parser trees

			for _,uid,_,annotype,status,comment in self.getall(cursor, "todos",["textid"], [textid]): # for each assignment of the text to someone:
				a= self.getall(cursor, "users",["rowid"], [uid])
				if a :
					uid,user,realname = a[0]
					users+=[user]
					filename = self.exportpath+basefilename + "."+user
					if annotype: filename += ".valid."
					if exportType=="todosconll":
						filename+=".complete.conll10"
					else:
						alltext="\n"
						doc,tokens,lexemes, dependencies, text = rhapsoxml.baseXml()
						filename+=".complete.rhaps.xml"

					outf=codecs.open(filename.encode("utf-8"),"w","utf-8") #open the file to write in

					for sid, snr, sentence, _ in self.getall(cursor, "sentences", ["textid"], [textid]): # for each sentence of the text

						if annotype: # try to get a validated tree
							t = self.getall(cursor, "trees", ["sentenceid", "userid", "annotype"], [sid, uid, 1])
							if t: treeid,sid,uid,annoty,sta,comm,ti = t[0]
							else: t = self.getall(cursor, "trees", ["sentenceid", "userid" ], [sid, uid])
						else: # if not the normal tree by the user
							t = self.getall(cursor, "trees", ["sentenceid", "userid" ], [sid, uid])
						if t: # the tree exists annoted by the user.
							treeid,sid,uid,annoty,sta,comm,ti = t[0]
						else:# the user did not touch the tree assigned to him or her.
							t = self.getall(cursor, "trees", ["sentenceid", "userid" ], [sid, parserid])
							if t:
								treeid,sid,parserid,annoty,sta,comm,ti, = t[0]
							else:
								print "error: no parsed tree found for sentenceid", sid,"!!! parserid:",parserid,"<br/>\n"
								#1/0
								continue

						if exportType=="todosconll":
							doublegovs=self.conllSentenceExport(sid, cursor,treeid,outf)
						else:
							alltext+=self.xmlSentenceAdd(sid, cursor,treeid,doc,tokens, lexemes,  dependencies)
						scounter+=1
					if exportType=="todosxml":
						text.appendChild(doc.createTextNode(alltext))
						xml= doc.toprettyxml(indent="     ")
						outf.write(xml)
					outf.close()
					fcounter+=1

		elif exportType in ["lastconll", "lastxml"]: 	# for every sentence, the most recent tree is exported

			r = self.getall(cursor, "sentences",["textid"], [textid])
			users=[]
			if r:
				self.exportpath+u"é"
				basefilename+u"é"
				filename = self.exportpath+basefilename + u".most.recent"
				if exportType=="lastconll":
					filename+=".trees.conll10"
				else:
					alltext="\n"
					doc,tokens,lexemes, dependencies, text = rhapsoxml.baseXml()
					filename+=".trees.rhaps.xml"
				outf=codecs.open(filename.encode("utf-8"),"w","utf-8")

				for sentenceid,nr,sentence,textid in r: # for each sentence of the text:


					treeDict=dict([ (user, (treeid,uid,realname,timestamp)) for treeid,uid,user,realname,timestamp in self.treesForSentence(sentenceid)])
					# order by timestamp
					timeDict=dict([ (timestamp,user) for (user, (treeid,uid,realname,timestamp)) in treeDict.iteritems() ])

					lastuser=timeDict[sorted(timeDict,reverse=True)[0]]
					treeid,uid,realname,timestamp=treeDict[lastuser]
					if lastuser not in users: users+=[lastuser]
					if exportType=="lastconll":
						doublegovs=self.conllSentenceExport(sentenceid, cursor, treeid, outf)
					else:
						alltext+=self.xmlSentenceAdd(sentenceid, cursor, treeid, doc, tokens, lexemes,  dependencies)
					scounter+=1

				if exportType=="lastxml":
					text.appendChild(doc.createTextNode(alltext))
					xml= doc.toprettyxml(indent="     ")
					outf.write(xml)
				outf.close()
				fcounter+=1

			users=["most recent modification (including trees from "+", ".join(users)+")"]

		elif exportType in ["allconll","allxml"]: # all __trees__ of all users are exported
			r = self.getall(cursor, "sentences",["textid"], [textid])
			if r:
				uid2stid={}
				for sentenceid,nr,sentence,textid in r: # for each sentence of the text:
					rr=self.getall(cursor, "trees",["sentenceid"], [sentenceid])
					if rr:
						for treeid,sid,uid,ty,sta,comm,ti in rr: # for each tree on the sentence:
							uid2stid[(uid,ty)]=uid2stid.get(uid,[])+ [  (sid,treeid)] # keep it in memory
				for uid,ty in uid2stid:
					a= self.getall(cursor, "users",["rowid"], [uid])
					if a :
						uid,user,realname = a[0]

						if ty: user = user+"-valid"
						users+=[user]
						#print uid,user,realname
						filename = self.exportpath+basefilename + "."+user
						if exportType=="allconll":
							filename+=".trees.conll10"
						else:
							alltext="\n"
							doc,tokens,lexemes, dependencies, text = rhapsoxml.baseXml()
							filename+=".trees.rhaps.xml"
						outf=codecs.open(filename.encode("utf-8"),"w","utf-8")
						#if textid==18: print uid2stid
						for sid,treeid in uid2stid[(uid,ty)]:
							if exportType=="allconll":
								doublegovs=self.conllSentenceExport(sid, cursor, treeid, outf)
							else:
								#print uid,sid,treeid,"<br>"
								alltext+=self.xmlSentenceAdd(sid, cursor, treeid, doc, tokens, lexemes,  dependencies)
							scounter+=1
					if exportType=="allxml":
						text.appendChild(doc.createTextNode(alltext))
						xml= doc.toprettyxml(indent="     ")
						outf.write(xml)
					outf.close()
					fcounter+=1



		return fcounter,users,scounter,doublegovs


	def conllSentenceExport(self, sid, cursor,treeid,outf):
		doublegovs=False

		d={}
		for nr,at,va, in cursor.execute("""select features.nr, features.attr, features.value
					from trees, features
					where trees.rowid=features.treeid and trees.rowid=?;""",(treeid,)).fetchall():
			d[nr]=d.get(nr,{})
			d[nr][at]=va
		for nr in sorted(d):
		#for tokid, nr, tok, sid in self.getall(cursor, "tokens", ["sentenceid"], [sid]): # for each token:
			#f = self.getall(cursor, "features", ["treeid", "tokenid"], [treeid, tokid])
			#d = dict([(attr, val) for _,_,_,attr,val in f])
			g = self.getall(cursor, "links", ["treeid", "depid"], [treeid, nr])
			gd = dict([(govid,function) for _,trid,depid,govid,function in g if govid>=0]) #trid==treeid and
			tok=d[nr].get(self.tokenName,d[nr].get("token",d[nr].get("t","_")))
			cat=d[nr].get(self.catName,d[nr].get("tag",d[nr].get("tag1","_")))
			#print d[nr],tok, d[nr].get("lemma","_"), cat
			for gg in gd:
				line = "\t".join([str(nr),		tok, d[nr].get("lemma","_"), cat, d[nr].get("tag2","_"), "_",	str(gg),gd[gg],	"_","_"])
				outf.write(line+"\n")
			if not gd: outf.write("\t".join([str(nr),	tok, d[nr].get("lemma","_"), cat, d[nr].get("tag2","_"), "_",	"_","_",	"_","_"])+"\n")
			elif len(gd)>1:doublegovs=True
		outf.write("\n")
		return doublegovs


	def xmlSentenceAdd(self, sid, cursor,treeid,doc,tokens, lexemes,  dependencies):
		"""
		called for each sentence

		"""
		_,_,sentence,_=self.getall(cursor, "sentences",["rowid"], [sid])[0]

		d={}
		for nr,at,va, in cursor.execute("""select features.nr, features.attr, features.value
					from trees, features
					where trees.rowid=features.treeid and trees.rowid=?;""",(treeid,)).fetchall():
			d[nr]=d.get(nr,{})
			d[nr][at]=va
		for nr in sorted(d):
			g = self.getall(cursor, "links", ["treeid", "depid"], [treeid, nr])
			gd = dict([(govid,function) for _,trid,depid,govid,function in g if govid>=0])
			d[nr]["gov"]=gd

		rhapsoxml.addFeat2doc(d, doc, self.tokenName,"lemma", tokens, lexemes, dependencies)
		return sentence+"\n"


	def removeText(self, tid):
		db,cursor=self.open()
		scounter=0
		for sid,snr, s,t, in self.getall(cursor, "sentences",["textid"],[tid]):
			for treeid,sid,uid,annoty,sta,comm,ti, in self.getall(cursor, "trees",["sentenceid"],[sid]):
				#for treeid,_,uid, in self.getall(cursor, "trees",["sentenceid"],[sid]):
					self.clean(cursor, "features", ["treeid"], [treeid])
					self.clean(cursor, "trees", ["rowid"], [treeid])
			#self.clean(cursor, "tokens", ["sentenceid"], [sid])
			scounter+=1
		self.clean(cursor, "sentences",["textid"],(tid,)) # erase all existing sentences for this textid
		self.clean(cursor, "sentencesearch",["textid"],(tid,)) # erase all existing sentences for this textid
		self.clean(cursor, "texts",["rowid"],(tid,)) # erase all existing texts for this textid
		self.clean(cursor, "todos",["textid"],(tid,)) # erase all existing todos for this textid

		db.commit()
		return scounter




	def gettree(self,sid=None,uid=None,treeid=None, username=None, indb=None, incursor=None):
		"""
		gets tree if
		- treeid is known
		or
		- uid and sid is known
		or
		- username and sid is known

		returns the dictionary of the tree
		"""
		if indb:
			db=indb
			cursor=incursor
		else:
			db,cursor=self.open()
		#print sid,uid,treeid
		if treeid:

			dbexe = db.execute("""select features.nr, trees.rowid, trees.sentenceid, features.attr, features.value
					from trees, features
					where trees.rowid=features.treeid and trees.rowid=?;""",(treeid,))
		elif sid:


			if uid:
				dbexe = db.execute("""select features.nr, trees.rowid, trees.sentenceid, features.attr, features.value
						from trees, features
						where trees.rowid=features.treeid and trees.userid=? and trees.sentenceid=?;""",(uid, sid,))
			else:
				dbexe = db.execute("""select features.nr, trees.rowid, trees.sentenceid, features.attr, features.value
						from trees, features, users
						where trees.rowid=features.treeid and trees.userid=users.rowid and users.user=? and trees.sentenceid=?;""",(username, sid,))

		else:
			print "problem gettree",sid,uid,treeid
			sys.exit()

		nodedic={}
		t=self.tokenName
		for nr,treeid,sid,attr,value, in dbexe:
			nodedic[nr]=nodedic.get(nr,{})
			#nodedic[nr][t]=token
			nodedic[nr][attr]=value
			govdic={}
			for _,_,_,govid,function in self.getall(cursor, "links", ["treeid", "depid"], [treeid, nr]):
				govdic[govid]=function
			nodedic[nr]["gov"]=govdic
		dic={}
		if not self.sentencefeaturesAlways: # if sentencefeaturesAlways no need to send it again whith the individual tree
			for _,sid,a,v in self.getall(cursor, "sentencefeatures", ["sentenceid"], [sid]):
				dic[a]=v
		dic["tree"]=nodedic ## maybe test whether "tree" is already an attribute?

		# exo stuff:
		if username!=self.teacher: # to avoid recursion
			try:
				cursor.execute("""select type from exos, sentences where exos.textid=sentences.textid and sentences.rowid = ?;""",(sid,))
				exotype,=cursor.fetchone()
			except:
				exotype = 0
			if exotype>1:
				dic["goodtree"]=self.gettree(sid=sid, username=self.teacher, indb=db, incursor=cursor)["tree"]





		if not indb: db.close()
		return dic



	def tree2json(self, sid=None,uid=None,treeid=None):
		if sid:		nodedic = self.gettree(sid,uid)
		elif treeid:	nodedic = self.gettree(None,None,treeid)
		print json.dumps(nodedic, sort_keys=True)


	def compare(self, treeids):
		"""
		for graphical diff between trees
		"""
		trees={}

		cc=self.catName # cat name: cat or tag

		comparedic={}
		for treeid in treeids:
			thisnodedic=self.gettree(None,None,treeid)["tree"] # TODO: turn this loop into a unique SQL query to make it faster!
			trees[treeids[treeid]] = thisnodedic

		comparedic=thisnodedic
		for i in thisnodedic:
			comparedic[i]["cgov"]=comparedic[i].get("cgov",{})
			good=True
			for tu in trees:
				t = trees[tu]

				comparedic[i]["cgov"][tu]=t[i]["gov"].items()
				comparedic[i]["agov"]=comparedic[i].get("agov",{})
				for g,f in t[i]["gov"].items():
					comparedic[i]["agov"][str(g)+"___"+f]=comparedic[i]["agov"].get(str(g)+"___"+f,[])+[tu]
				#cat compare
				comparedic[i]["ccat"]=comparedic[i].get("ccat",{})
				comparedic[i]["ccat"][tu]=t[i].get(cc,"undefined")
				comparedic[i]["acat"]=comparedic[i].get("acat",{})
				comparedic[i]["acat"][t[i].get(cc,"undefined")]=comparedic[i]["acat"].get(t[i].get(cc,"undefined"),[])+[tu]
		for i in comparedic:
			comparedic[i]["gov"]={}
			for (gf),ul in comparedic[i]["agov"].iteritems():
				g,f = gf.split("___")
				g=int(g)

				if len(ul)==len(treeids):
					comparedic[i]["gov"][g]= [(f,["ok"])]
				else:
					comparedic[i]["gov"][g]=comparedic[i]["gov"].get(g,[])+[(f,ul)]

			comparedic[i][cc]=[]
			for (c),ul in comparedic[i]["acat"].iteritems():


				if len(ul)==len(treeids):
					comparedic[i][cc]= [(c,["ok"])]
				else:
					comparedic[i][cc]=comparedic[i].get(cc,[])+[(c,ul)]

		for i in comparedic:
			del comparedic[i]["agov"]
			del comparedic[i]["cgov"]
			del comparedic[i]["acat"]
			del comparedic[i]["ccat"]


		dic={}


		# TODO: this just uses the last treeid. all compared trees should have the same sentenceid. this is not tested.
		if not self.sentencefeaturesAlways: # if sentencefeaturesAlways no need to send it again whith the individual tree
			db,cursor=self.open()
			for at,va, in cursor.execute("""select sentencefeatures.attr, sentencefeatures.value
						from trees, sentences,sentencefeatures
						where sentencefeatures.sentenceid=sentences.rowid and trees.sentenceid=sentences.rowid and trees.rowid=?;""",(treeid,)).fetchall():
				dic[at]=va
			db.close()
		dic["tree"]=comparedic ## maybe test whether "tree" is already an attribute?

		print json.dumps(dic, sort_keys=True)

	def computeTotalEvaluation(self,gcats,gdeps,gfuncs,glemmas,tottok):
		return ((gcats/tottok)*self.categoriesVal + (gdeps/tottok)*self.governorsVal + (gfuncs/tottok)*self.functionsVal + (glemmas/tottok)*self.lemmasVal ) /    self.evalTot  * 100


	def evaluateTree(self, usertree, teachertree):

		correctcats,correctdeps,correctfuncs,correctlemmas=0,0,0,0
		cc=self.catName
		for i in usertree:
			if i in teachertree:
				#print "_____",cc,teachertree[i]
				#print usertree[i]
				if teachertree[i][cc]==usertree[i].get(cc,None):correctcats+=1
				if teachertree[i].get("lemma","")==usertree[i].get("lemma"," "):correctlemmas+=1
				#print "<br>",usertree[i]["gov"]
				govlen=float(len(teachertree[i]["gov"]))
				if not govlen:govlen=1.0
				if teachertree[i]["gov"]:
					for g,func in teachertree[i]["gov"].iteritems():
						#print g,usertree[i]["gov"],g in usertree[i]["gov"]
						if g in usertree[i]["gov"]:correctdeps+=1/govlen
						#print correctdeps
						if func == usertree[i]["gov"].get(g,None):correctfuncs+=1/govlen
				else:
					correctdeps+=1
					correctfuncs+=1
			else:
				print "no teacher tree for",usertree[i]

		return correctcats,correctdeps,correctfuncs,correctlemmas

	def evaluateUser(self,uid, tid=None, consolidateLine=True):
		"""
		if tid (textid) is given: only this text
		else: all assignment for the user
		"""

		print "----------",uid,tid,consolidateLine

		out=""

		textids=[]
		treeidlists=[]
		totaltokens=[]
		titles=[]
		if tid:
			textids+=[tid]
			tid,t,nrtokens = self.getall(None, "texts",["rowid"],[tid])[0]

			treenrs=self.treeNrsForUserAndText(uid,tid)
			trees=sorted([(int(n),asctime(localtime(o))) for (sid,n,o,trid,) in treenrs])
			treeidlists+=[ [ (trid,sid) for (sid,n,o,trid,) in treenrs] ]

			totaltokens+=[nrtokens]
			titles+=[t]
		else:
			for _,uid,tid,todotype,status,comment in self.getall(None, "todos",["userid"], [uid]): # for all the assignments (texts) for the given user

				textids+=[tid]
				tid,t,nrtokens = self.getall(None, "texts",["rowid"],[tid])[0]

				treenrs=self.treeNrsForUserAndText(uid,tid)
				trees=sorted([(int(n),asctime(localtime(o))) for (sid,n,o,trid,) in treenrs])
				treeidlists+=[ [ (trid,sid) for (sid,n,o,trid,) in treenrs] ]

				totaltokens+=[nrtokens]
				titles+=[t]

		teacher=self.projectconfig["configuration"].get("teacher",None)
		if teacher:	teacherid=self.userid(self.teacher)

		out+= "<table><tr><td>text</td><td>correctcats</td><td>correctdeps</td><td>correctfuncs</td><td>correctlemmas</td><th>tokens</th><th>score/100</th></tr>"

		#print teacherid
		tottottok=0
		goods=[0,0,0,0]
		db,cursor=self.open()

		a= self.getall(cursor, "users",["rowid"], [uid])
		if a :
			uid,user,realname = a[0]
		out+=" --- ".join([str(uid),user,unicode(realname)])
		print uid, user, realname

		for textid,treeids,title,tottok in zip(textids,treeidlists,titles,totaltokens): # for each text assigned to the user

			gcats,gdeps,gfuncs,glemmas=0,0,0,0
			for treeid, sid in treeids:
				utree = self.gettree(None,None,treeid)["tree"]
				ttree = self.gettree(sid,teacherid,None)["tree"]

				gc,gd,gf,gl=self.evaluateTree(utree, ttree)
				gcats+=gc
				gdeps+=gd
				gfuncs+=gf
				glemmas+=gl
			score=self.computeTotalEvaluation(gcats,gdeps,gfuncs,glemmas,	float(tottok))
			out+= "<tr><th>{title}</th><td>{gcats}</td><td>{gdeps}</td><td>{gfuncs}</td><td>{glemmas}</td><th>{tottok}</th><th>{score:.{digits}f}</th></tr>".format(title=title,gcats=gcats,gdeps=gdeps,gfuncs=gfuncs,glemmas=glemmas,tottok=tottok,score=score,digits=2)
			correctcats,correctdeps,correctfuncs,correctlemmas=goods
			goods[0]+=gcats
			goods[1]+=gdeps
			goods[2]+=gfuncs
			goods[3]+=glemmas
			tottottok+=tottok
		gcats,gdeps,gfuncs,glemmas=goods
		score=self.computeTotalEvaluation(gcats,gdeps,gfuncs,glemmas,	float(tottottok))
		out+= "<tr><th>=</th><td>{gcats}</td><td>{gdeps}</td><td>{gfuncs}</td><td>{glemmas}</td><th>{tottok}</th><th style='font-weight: bold;'>{score:.{digits}f}</th></tr>".format(title=title,gcats=gcats,gdeps=gdeps,gfuncs=gfuncs,glemmas=glemmas,tottok=tottottok,score=score,digits=2)
		out+= "</td></tr></table>"
		if consolidateLine:
			import unicodedata
			out=''.join(c for c in unicodedata.normalize('NFD', unicode(realname)) if unicodedata.category(c) != 'Mn').replace(" ","-")+"\t"+str(score)

		return out


	def userid(self,username,realname=None):
	# get the userid for username
		db,cursor=self.open()
		if realname:
			uid = self.enter(cursor, "users", ["user","realname"], [username, realname])
			if not uid and self.getUniqueId(cursor, "users", ["user"],[username]):
				self.clean(cursor, "users",["user"],(username,))
				try:uid = self.enter(cursor, "users", ["user","realname"], [username, realname])
				except:uid = self.enter(cursor, "users", ["user","realname"], [username.decode("utf-8"), realname.decode("utf-8")])
			db.commit()

		else: uid = self.enter(cursor, "users", ["user"], [username]) # should only be called if realname is already entered, because realname will be None...
		db.close()
		return uid


	def realname(self,user):
		database,cursor=self.open()
		cursor.execute('select realname from users where user=?', (user,))
		realna, = cursor.fetchone()
		if not realna:
			#from configobj import ConfigObj
			if os.path.exists("users/"+user+".ini"):
				config = ConfigObj("users/"+user+".ini")
				realna = config["realname"].decode("utf-8")
			else: realna = "no real name"
			cursor.execute('update users set realname=? where user=?', (realna,user,))

			database.commit()
		return realna


	def addtext2user(self,textid,user, validator):
		database,cursor=self.open()
		uid=self.userid(user)
		self.clean(cursor, "todos",["userid","textid"],(uid,textid,))
		# status 0 corresponds to "todo":
		self.enter(cursor, "todos", ["userid","textid","type","status"], [uid,textid,validator,0], computeId=False)



		database.commit()
		database.close()




	def removetextfromuser(self,textid,uid):
		database,cursor=self.open()
		self.clean(cursor, "todos",["userid","textid"],(uid,textid,))
		database.commit()
		database.close()


	def treesForSentence(self,sid):
		database,cursor=self.open()
		cursor.execute("""select trees.rowid, trees.userid, users.user, users.realname, trees.timestamp
					from trees, users
					where users.rowid=trees.userid and trees.sentenceid=?;""",(sid,))

		return cursor.fetchall()

	def treesForText(self,tid):
		"""
		gives all the realnames of all trees for a given textid
		"""
		importannoname=self.baseAnnotatorName
		database,cursor=self.open()
		cursor.execute("""select distinct users.realname
					from trees, users,sentences
					where users.rowid=trees.userid and trees.sentenceid=sentences.rowid and users.user!=? and sentences.textid=?;""",(importannoname,tid,))

		return cursor.fetchall()

	def uidForText(self,tid):
		"""
		gives all the uids of all trees for a given textid
		"""
		#importannoname=self.baseAnnotatorName
		database,cursor=self.open()
		cursor.execute("""select distinct users.rowid
					from trees, users,sentences
					where users.rowid=trees.userid and trees.sentenceid=sentences.rowid and sentences.textid=?;""",(tid,))

		return cursor.fetchall()

	def treeNrsForUserAndText(self,uid,textid):
		"""
		called from project.cgi
		used for the all assignments table
		"""
		database,cursor=self.open()
		cursor.execute("""select sentences.rowid, sentences.nr, trees.timestamp, trees.rowid from trees, sentences where trees.userid=? and trees.sentenceid=sentences.rowid and sentences.textid=?;""",(uid,textid,))
		return cursor.fetchall()



	def eraseTree(self, treeid, sentencenr, username, adminLevel):
		"""
		called from eraseTree.cgi
		"""
		db,cursor=self.open()
		t = self.getall(cursor, "trees", ["rowid"], [treeid])

		if t: 	treeid,sid,uid,annoty,sta,comm,ti = t[0]
		else:
			print "error: no sentence id found for the treeid",treeid
			sys.exit()

		if len(self.treesForSentence(sid))==1: # don't completely erase the last tree, because we need to preserve the tokens
			cursor.execute('UPDATE features SET value="" WHERE treeid=? AND attr!=?;',(treeid,self.tokenName,))
			cursor.execute("DELETE from links WHERE treeid=?;",(treeid,))
			baseAnnotatorID=self.getUniqueId(cursor, "users", ["user"],[self.baseAnnotatorName])
			cursor.execute("UPDATE trees SET userid=? WHERE rowid=?;",(baseAnnotatorID,treeid,))


		else:
			self.clean(cursor, "features", ["treeid"], [treeid])
			self.clean(cursor, "links", ["treeid"], [treeid])
			self.clean(cursor, "trees", ["rowid"], [treeid])
		db.commit()

		return self.links2AllTrees(sid,sentencenr,username,adminLevel,validator=0)[0] # return just the html with the new list of trees for the sentence
		#except:return "" # needed if last tree was erased


	def connectRight(self, sid1, sentencenr1):
		"""
		called from connect.cgi
		"""
		db,cursor=self.open()

		t = self.getall(cursor, "sentences", ["rowid"], [sid1])
		if t: 	sid1,nr1,sentence1,textid = t[0]
		else:
			print "error: no sentence id found for the sentence id",sid1
			sys.exit()

		if int(nr1)!=int(sentencenr1):
			print "error: nr!=sentencnr",nr1,sentencenr1
			sys.exit()

		t = self.getall(cursor, "sentences", ["nr","textid"], [nr1+1,textid])
		if t: 	sid2,nr2,sentence2,textid = t[0]
		else:
			print "error: no next sentence found",nr1+1
			sys.exit()

		parserid=self.getUniqueId(cursor, "users", ["user"],[self.baseAnnotatorName])

		userid2coupleTrees={}
		uidTotid1=dict((uid,(tid,ts)) for tid, uid, _, _, ts in self.treesForSentence(sid1))
		uidTotid2=dict((uid,(tid,ts)) for tid, uid, _, _, ts in self.treesForSentence(sid2))

		#for tid, uid, user, _, ts in self.treesForSentence(sid1):
			#print "___",uid, user
		#for tid, uid, user, _, ts in self.treesForSentence(sid2):
			#print "___",uid, user


		userid2coupleTrees=dict((uid,(uidTotid1.get(uid,(self.getUniqueId(cursor,"trees",["sentenceid","userid"],[sid1,parserid]) ,0)) ,uidTotid2.get(uid,(self.getUniqueId(cursor,"trees",["sentenceid","userid"],[sid2,parserid]) ,0))))
		  for uid in set(uidTotid1.keys()+uidTotid2.keys()))

		#print "userid2coupleTrees",userid2coupleTrees
		#print "len",len(userid2coupleTrees)

		tree1already=[]

		for uid,((treeid1,ts1),(treeid2,ts2)) in userid2coupleTrees.iteritems():
			#print "\noooooo",uid
			tree1 = self.gettree(treeid=treeid1, indb=db,incursor=cursor)
			tree2 = self.gettree(treeid=treeid2, indb=db,incursor=cursor)

			#print "tree1",tree1
			#print "len",len(tree1["tree"])
			#print "tree2",tree2
			#print "len",len(tree2["tree"])

			m = max(tree1["tree"].keys())
			#print m
			for i,node in tree2["tree"].iteritems():
				node["gov"]=dict(((j+m if j else 0),f) for j,f in node["gov"].iteritems())
				if treeid1 not in tree1already: tree1["tree"][i+m]=node

			if treeid1 not in tree1already:
				if "markupIU" in tree1 and "markupIU" in tree2:
					tree1["markupIU"]=tree1["markupIU"]+" "+tree2["markupIU"]

			wcounter, sent, treeid = self.enterTree(cursor, tree1["tree"], sid1, uid,tokensChanged=True)

			tree1already+=[treeid1]

		cursor.execute("UPDATE sentences SET sentence=? WHERE rowid=? ",(sent,sid1,))
		cursor.execute("UPDATE sentencesearch SET sentence=? WHERE rowid=? ",(sent,sid1,))
		if "markupIU" in tree1:
			cursor.execute("UPDATE sentencefeatures SET value=? WHERE sentenceid=? and attr=?",(tree1["markupIU"],sid1,"markupIU",))# TODO:generalize this to any sentencefeature

		for uid,((treeid1,ts1),(treeid2,ts2)) in userid2coupleTrees.iteritems():
			self.clean(cursor, "features", ["treeid"], [treeid2])
			self.clean(cursor, "links", ["treeid"], [treeid2])
			self.clean(cursor, "trees", ["rowid"], [treeid2])

		self.clean(cursor, "sentences",["rowid"],(sid2,)) # erase all existing sentences for this textid
		self.clean(cursor, "sentencesearch",["rowid"],(sid2,)) # erase all existing sentences for this textid
		cursor.execute("UPDATE sentences SET nr=nr-1 WHERE nr>? and textid=?",(nr1,textid,))

		db.commit()
		db.close()


	def splitSentence(self, sid, sentencenr, toknr):
		"""
		called from connect.cgi
		"""
		db,cursor=self.open()
		toknr=int(toknr)
		sentencenr=int(sentencenr)
		t = self.getall(cursor, "sentences", ["rowid"], [sid])
		if t: 	sid,snr,sentence,textid = t[0]
		else:
			print "error: no sentence id found for the sentence id",sid
			sys.exit()

		if int(snr)!=sentencenr:
			print "error: nr!=sentencnr",snr,sentencenr
			sys.exit()

		t = self.getall(cursor, "trees", ["sentenceid"], [sid])
		if t: 	tid,_,uid,_,_,_,_ = t[0]
		else:
			print "error: no tree found found. sentenceid:",sid
			sys.exit()

		if toknr+1 not in self.gettree(treeid=tid, indb=db,incursor=cursor)["tree"]:
			print "error: no next token found after token nr:",toknr
			sys.exit()

		#parserid=self.getUniqueId(cursor, "users", ["user"],[self.baseAnnotatorName])

		uidToTrees={}

		for tid,_,uid,annotype,status,comment,timestamp in t:

			tree = self.gettree(treeid=tid, indb=db,incursor=cursor)

			#print "\n$$$$$",tid
			#print tree
			#print tree["tree"][toknr]

			markup1,markup2=[],tree["markupIU"].split()
			s1,s2=[],[]

			newtree={}
			for i,node in sorted(tree["tree"].items()):
				if i>toknr:
					s2+=[node[self.tokenName]]
					node["gov"]=dict(((j-toknr if j>toknr else 0),f) for j,f in node["gov"].iteritems())
					newtree[i-toknr]=node
					del tree["tree"][i]
				else:
					node["gov"]=dict(((0 if j>toknr else j),f) for j,f in node["gov"].iteritems())
					s1+=[node[self.tokenName]]
					while markup2:
						if node[self.tokenName]==markup2[0]:
							markup1+=[markup2.pop(0)]
							#print "good",markup1
							break
						markup1+=[markup2.pop(0)]	
					
			
			#print tree["tree"]
			#print
			#print newtree
			#print 
			uidToTrees[uid]=newtree
			
			wcounter, sent, treeid = self.enterTree(cursor, tree["tree"], sid, uid,tokensChanged=True)
			
		
		
								
		
		mu1= " ".join(markup1)
		mu2= " ".join(markup2)	
			
		se1= " ".join(s1)
		se2= " ".join(s2)
		
		#print s2,se2.encode("utf-8")
		
		
		cursor.execute("UPDATE sentences SET nr=nr+1 WHERE nr>? and textid=?",(sentencenr,textid,)) 
		cursor.execute("UPDATE sentences SET sentence=? WHERE rowid=? ",(se1,sid,))
		cursor.execute("UPDATE sentencesearch SET sentence=? WHERE rowid=? ",(se1,sid,))
		
		cursor.execute("UPDATE sentencefeatures SET value=? WHERE sentenceid=? and attr=?",(mu1,sid,"markupIU",))# TODO:generalize this to any sentencefeature
		
		newsid=self.enter(cursor, "sentences",["nr","sentence","textid"],(sentencenr+1,se2,textid),computeId=True)
		
		self.enter(cursor, "sentencefeatures",["sentenceid","attr","value"],(newsid,"markupIU",mu2) )
		
		for uid,newtree in uidToTrees.iteritems():
			wcounter, sent, treeid = self.enterTree(cursor, newtree, newsid, uid,tokensChanged=True)
		
		db.commit()
		db.close()
		
		
		return
		
		
		
			
	
	
	
	def links2AllTrees(self,sid,snr,username,adminLevel, todo=-1, validvalid=[],validator=False, addEmptyUser=None):
		"""
		for a given sentence id, gives the html with links to all the trees of the sentence
		validvalid: list of userids that should be shown because they have validated the text. if none is given, the validvalid is computed
		addEmptyUser: in case of teacher visible exercises, the user itself that needs to be automatically provided with an empty tree
		"""
		importannoname=self.baseAnnotatorName
		#
		
		if self.showTreesOfValidatedTexts and not validvalid:
			validvalid=self.validvalid(None, sid)
		
		
				
				
		if adminLevel or validator or (self.allVisibleForNonAnnotators and todo==-1):
			treeDict=dict([ (user, (treeid,uid,realname,timestamp)) for treeid,uid,user,realname,timestamp in self.treesForSentence(sid)])
		else: # common mortal:
			treeDict=dict([ (user, (treeid,uid,realname,timestamp)) for treeid,uid,user,realname,timestamp in self.treesForSentence(sid) if user in self.visibleToEveryone or user==username or uid in validvalid])
		
		# putting these trees in order:
		goodlist=[]
		if self.treeorder=="newest":
			# order by timestamp
			timeCouples=[ (timestamp,user) for (user, (treeid,uid,realname,timestamp)) in treeDict.iteritems() ]
			for ts,u in sorted(timeCouples,reverse=True): 
				goodlist+=[(u,treeDict[u])]
		elif self.treeorder=="user":
			# user first, then baseAnnotator, then others by alphabet
			bestusers=[username,importannoname]
			for u in bestusers:
				if u in treeDict:goodlist+=[(u,treeDict[u])]
			for u in sorted(treeDict,key=unicode.lower):
				if (u,treeDict[u]) not in goodlist: goodlist+=[(u,treeDict[u])]
		elif self.treeorder=="baseAnnotator":
			# baseAnnotator first, then user, then others by alphabet
			bestusers=[importannoname,username]
			for u in bestusers:
				if u in treeDict:goodlist+=[(u,treeDict[u])]
			for u in sorted(treeDict,key=unicode.lower):
				if (u,treeDict[u]) not in goodlist: goodlist+=[(u,treeDict[u])]
		else:
			# default: order by alphabet
			for u in sorted(treeDict,key=unicode.lower):
				goodlist+=[(u,treeDict[u])]
		
		#print "<br>____",adminLevel,sid,treeDict,goodlist
		
		if not goodlist or (addEmptyUser and addEmptyUser not in treeDict): # 
			# could happen in case of exo:
			# in case user hasn't created own tree, she should see tree of self.exoBaseAnnotatorName
			# in case tree of self.exoBaseAnnotatorName doesn't exist = tree of self.baseAnnotatorName without deps and cats
			userid = self.userid(username)
			exoBaseAnnoId = self.userid(self.exoBaseAnnotatorName)
			
			#open("logger.txt","a").write("___links2AllTrees____"+str(goodlist)+str(addEmptyUser and addEmptyUser not in treeDict)+str([username not in treeDict, treeDict,username])+"~~~~~~~\n"+str([ (user, (treeid,uid,realname,timestamp)) for treeid,uid,user,realname,timestamp in self.treesForSentence(sid)])+"\n")
			
			db,cursor=self.open()
			nodedic = self.gettree(sid=sid,username=self.exoBaseAnnotatorName,indb=db,incursor=cursor)["tree"]
			if nodedic: # found tree of self.exoBaseAnnotatorName, save it as user's tree
				if username not in treeDict:
					self.enterTree(cursor, nodedic, sid, userid)	
			else:	# no tree exists yet for self.exoBaseAnnotatorName, let's create it
				nodedic = self.gettree(sid=sid,username=self.baseAnnotatorName,indb=db,incursor=cursor)["tree"]
				self.enterTree(cursor, nodedic, sid, exoBaseAnnoId, notenter=["gov","tag"])
				self.enterTree(cursor, nodedic, sid, userid, notenter=["gov","tag"])	
			db.commit()
			db.close()
			if not goodlist:
				for treeid,uid,user,realname,timestamp in self.treesForSentence(sid):
					if user!=self.exoBaseAnnotatorName:
						goodlist+=[(username, (treeid, uid, username,0))]  #user, (treeid,uid,realname)		 +" ("+self.newTree+")"
			
			
		html=""
		if len(goodlist)>0:
			if adminLevel  :
				
				html += " ".join([u'''<a class='othertree' title='{title}' treeid='{treeid}' treecreator='{u}' nr='{snr}'>{u}</a><sup> <a onclick="eraseTree({snr},{treeid},'{u}');">x</a></sup>'''.format(treeid=treeid,u=u,snr=snr,title=unicode(realname)+" "+asctime(localtime(timestamp))) for (u,(treeid,uid,realname,timestamp)) in goodlist])
			else:
				html = " ".join([u'''<a class='othertree' treeid='{treeid}' title='{title}' treecreator='{u}' nr='{snr}'>{u}</a>'''.format(treeid=treeid,u=u,snr=snr,title=unicode(realname)+" "+asctime(localtime(timestamp))) for (u,(treeid,uid,realname,timestamp)) in goodlist])
		#else:
			#html=" "
		
		if len(goodlist)>1:
			objs="{"+",".join(['''"{u}":"{treeid}"'''.format(treeid=treeid,u=u) for (u,(treeid,uid,realname,timestamp)) in goodlist])+"}"
			colors=json.dumps(config.list2colors([u for (u,(treeid,uid,realname,timestamp)) in goodlist]))
			html+="""<img class="compare" src="images/compare.png" border="0" align="bottom" onclick='compare({o},{snr},{colors})' id="compa{snr}"  nr='{snr}'>""".format(o=objs, snr=snr, colors=colors[:-1]+',"ok":"cccccc"}')
		try:firsttreeid=goodlist[0][1][0]
		except:firsttreeid=0
		
		if self.sentencefeaturesAlways:
			dic={}
			db,cursor=self.open()
			for _,sid,a,v in self.getall(cursor, "sentencefeatures", ["sentenceid"], [sid]):
				if a in self.projectconfig.shownsentencefeatures:
					dic[a]=v
			db.close()
			sentenceinfo = "<br/>".join(dic.values())
		else:
			sentenceinfo = ""
				
				
		return html,firsttreeid, sentenceinfo
	
	def gettreestatus(self,sid,userid):
		status="no tree"
		db,cursor=self.open()
		
		for _,_,_,_,status,comment,_ in self.getall(cursor, "trees",["sentenceid","userid"], [sid,userid]):
			status=status
			if status==None:status=0
		db.close()
		if str(status) in self.projectconfig["text status"]: return self.projectconfig["text status"][str(status)]
		else: return str(status)
		
	def validvalid(self, textid, sid=None):
		"""
		gets a list of validators for a given text that have given their ok
		can also retrieve the list if given only a sentence id - maybe not a good idea?
		"""
		
			
		if self.showTreesOfValidatedTexts:
			database,cursor=self.open()
			if sid:
				cursor.execute("""select users.rowid from users, todos, sentences where users.rowid=todos.userid and todos.type=1 and todos.status=? and todos.textid=sentences.textid and sentences.rowid=?;""",(self.showTreesOfValidatedTexts,sid,))
			else:
				
				cursor.execute("""select users.rowid from users, todos where users.rowid=todos.userid and todos.type=? and todos.status=1 and todos.textid=? ;""",(self.showTreesOfValidatedTexts,textid,))
			return [i for i, in cursor.fetchall()]
		else:
			return []
		
	
	
	def statustree(self, sid, snr, visibletreeid, userid, username, textid, admin):
		"""
		called from statusChange.cgi
		
		since the user can change the status we know that she is annotator or validator
		usually, the user changes her own tree's status
		if she doesn't have a tree, we copy the visible tree and give it the new status
		
		"""
		answerdic={}
		status="no tree"
		db,cursor=self.open()
		
		for _,_,_,_,status,comment,_ in self.getall(cursor, "trees",["sentenceid","userid"], [sid,userid]):
			if not status:status=0
			status=int(status)+1
			if str(status) not in self.projectconfig["tree status"]: status=0
		if status=="no tree": # copy visible tree
			status=1
			nodedic = self.gettree(None,None,visibletreeid)["tree"]
			#print "jjj",nodedic
			t=self.tokenName
			tds = self.gettodostatus(userid,textid)
			if tds<1:tds=0 # tds=1 means this is a validator
			wcounter, sent, treeid = self.enterTree(cursor, nodedic, sid, userid, t)
			db.commit()
			links=self.links2AllTrees(sid,snr,username,admin,validator=tds)
			answerdic["links"]=links[0]
		cursor.execute("UPDATE trees SET status=? WHERE sentenceid=? AND userid=?",(status,sid,userid,))
		db.commit()
		db.close()
		answerdic["status"]=self.projectconfig["tree status"].get(str(status),"ooo")
		return answerdic
		
	
	def gettodostatus(self,userid,textid):
		"""
		-1: no todo
		0: simple annotation
		1: validation
		"""
		ty=-1
		db,cursor=self.open()
		for _,_,_,ty,status,comment in self.getall(cursor, "todos",["textid","userid"], [textid,userid]):
			ty=ty
		db.close()
		return ty
		
	def statustext(self, textid, userid):
		answerdic={}
		db,cursor=self.open()
		for _,_,_,ty,status,comment in self.getall(cursor, "todos",["textid","userid"], [textid,userid]):
			status=int(status)+1
			if str(status) not in self.projectconfig["text status"]: status=0
		try:
			self.clean(cursor, "todos", ["userid","textid"], [userid,textid])
			self.enter(cursor, "todos", ["userid","textid","type","status","comment"], [userid,textid,ty,status,comment], computeId=False)
			db.commit()
		except: print "database when problem changing status"
		db.close()
		answerdic["status"]=self.projectconfig["text status"].get(str(status),"ooo")
		return answerdic
	
		
	def usersLastSeen(self, seconds=600, userdir="users/"):
		db,cursor=self.open()
		users={}
		now=[]
		for uid,username,realname in self.getall(cursor,"users"):
			user = ConfigObj(userdir+username+'.ini')
			users[username]=(float(user.get("lastused",0)),realname)
			if mktime( datetime.now().timetuple() ) - float(user.get("lastused",0)) < seconds: 
				now+=[(username,realname,user.get("email",""))]
		
		return users,now
		
		
	
	
	
	def snippetSearch(self, query):
		"""
		3 separate cases for speed reasons:
		1. mixed query of words and features
		2. only features
		3. only words
		"""
		#TODO: security issue here: query is not escaped!!!!
		
		db,cursor=self.open()
		query=query.replace("'","''")
		words,featuresearch=[],[]
		for word in query.split():
			if ":" in word:
				both=word.split(":")
				featuresearch+=[ ( both[0],both[1]) ]
			else:
				words+=[word]
		
		if featuresearch:
			featurequery = "  "
			for attr, value in featuresearch:
				if attr=="func" or attr=="function":
					featurequery+= " and links.function='{value}' and links.treeid=trees.rowid ".format(value=value)
				else:
					featurequery+= " and features.attr='{attr}' and features.value='{value}'".format(attr=attr,value=value)
			#print featurequery	
			if words:
				query=" ".join(words)
				
				
				try:
					rc=cursor.execute("SELECT texts.textname, sentencesearch.rowid, sentencesearch.nr, sentencesearch.textid, snippet(sentencesearch) FROM sentencesearch, texts, features, trees, sentences, links  WHERE sentencesearch.sentence MATCH '{query}' AND sentencesearch.textid = texts.rowid and sentences.nr=sentencesearch.nr and features.treeid=trees.rowid and trees.sentenceid=sentences.rowid and sentences.textid=texts.rowid  {featurequery} ;	".format(query=query,featurequery=featurequery))
					print "SELECT texts.textname, sentencesearch.rowid, sentencesearch.nr, sentencesearch.textid, snippet(sentencesearch) FROM sentencesearch, texts, features, trees, sentences  WHERE sentencesearch.sentence MATCH '{query}' AND sentencesearch.textid = texts.rowid and sentences.nr=sentencesearch.nr and features.treeid=trees.rowid and trees.sentenceid=sentences.rowid and sentences.textid=texts.rowid  {featurequery} ;	".format(query=query,featurequery=featurequery)
				except OperationalError:
					# compatiblity for sqlite without fts module compilation
					rc=cursor.execute("SELECT texts.textname, sentencesearch.rowid, sentencesearch.nr, sentencesearch.textid, sentencesearch.sentence FROM sentencesearch, texts, features, trees, sentences, links  WHERE sentencesearch.sentence like '%{query}%' AND sentencesearch.textid = texts.rowid and sentences.nr=sentencesearch.nr and features.treeid=trees.rowid and trees.sentenceid=sentences.rowid and sentences.textid=texts.rowid  {featurequery} ;	".format(query=query,featurequery=featurequery))
					print "SELECT texts.textname, sentencesearch.rowid, sentencesearch.nr, sentencesearch.textid, sentencesearch.sentence FROM sentencesearch, texts, features, trees, sentences  WHERE sentencesearch.sentence like '%{query}%' AND sentencesearch.textid = texts.rowid and sentences.nr=sentencesearch.nr and features.treeid=trees.rowid and trees.sentenceid=sentences.rowid and sentences.textid=texts.rowid  {featurequery} ;	".format(query=query,featurequery=featurequery)
			else:
				
				rc=cursor.execute("SELECT texts.textname, sentences.rowid, sentences.nr, sentences.textid, 'not available' FROM texts, features, trees, sentences, links  WHERE sentences.textid = texts.rowid and features.treeid=trees.rowid and trees.sentenceid=sentences.rowid and sentences.textid=texts.rowid  {featurequery} ;	".format(featurequery=featurequery))
		
		else:
			try:
				rc=cursor.execute("SELECT texts.textname, sentencesearch.rowid, sentencesearch.nr, sentencesearch.textid, snippet(sentencesearch) FROM sentencesearch, texts WHERE sentencesearch.sentence MATCH '{query}' AND sentencesearch.textid = texts.rowid;".format(query=query))
			except OperationalError:
				rc=cursor.execute("SELECT texts.textname, sentencesearch.rowid, sentencesearch.nr, sentencesearch.textid, sentencesearch.sentence FROM sentencesearch, texts WHERE sentencesearch.sentence like '%{query}%' AND sentencesearch.textid = texts.rowid;".format(query=query))
		 
		html=""
		counter=0
		lastsnr=None
		for tname, sid,snr, textid,r, in rc:
			if snr!=lastsnr: # ugly hack to avoid the sqlite fts4 bug that doesn't allow "select distinct" searches
				counter+=1
				html+= "<tr><td>"+str(counter)+"</td><td><b><a style='cursor:pointer;' onclick=edit('"+str(textid)+"','"+str(snr)+"')>"+ tname +"</a></b></td>"
				html+= "<td><a  style='cursor:pointer;' onclick=edit('"+str(textid)+"','"+str(snr)+"')>"+str(snr)+"</a></td><td><a  style='cursor:pointer;' onclick=edit('"+str(textid)+"','"+str(snr)+"')>"+r+"</a></td></tr>"
				lastsnr=snr
			#
		db.close()
		if html:return "<table class='whitable'> <thead><tr><th>nr.</th><th>text</th><th>sentence</th><th>snippet</th></tr></thead>"+html+"</table>"
	
	def getExo(self, tid):
		
		db,cursor=self.open()
		try:
			cursor.execute("""select type from exos where textid=? ;""",(tid,))
			exotype,=cursor.fetchone()
		except:
			cursor.execute('''create table IF NOT EXISTS exos (textid INTEGER, type INTEGER, status TEXT, comment TEXT)''')
			exotype = None
		if not exotype: exotype=0
		return exotype
		db.close()
		
	
	def setExo(self, tid, exochoice):
		#print "___",self.exotypes.index(exochoice)
		db,cursor=self.open() 
		#print "$$$",
		cursor.execute('INSERT or REPLACE INTO exos(textid, type) VALUES(?, ?);', (tid, self.exotypes.index(exochoice),))
		#print "$$$",cursor.execute('UPDATE exos (textid, type) VALUES(?, ?));', (tid, self.exotypes.index(exochoice),))
		db.commit()
		db.close()
		
			#INSERT OR IGNORE INTO players (user_name, age) VALUES ("steven", 32); 

			#-- make sure it has the right data
			#UPDATE players SET user_name="steven", age=32 WHERE user_name="steven"; 
	#def getAllSenteces():
		#sid,snr,s,tid, exotype
	
	
	
	def cleanDatabase(self,filename=None):
		text="cleanDatabase <br/>\n"
		db,cursor=self.open()
		
		if filename:
			rc=cursor.execute("DELETE FROM texts WHERE textname = ?;",(filename,)).rowcount
			if rc:text+= "deleted " + str( rc)+ " texts, <br/>"
		
		rc=cursor.execute("DELETE FROM sentences WHERE NOT EXISTS (SELECT NULL FROM texts WHERE texts.rowid = sentences.textid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " sentences, <br/>"
		rc=cursor.execute("DELETE FROM sentencefeatures WHERE NOT EXISTS (SELECT NULL FROM sentences WHERE sentences.rowid = sentencefeatures.sentenceid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " sentences, <br/>"
		rc=cursor.execute("DELETE FROM sentencesearch WHERE NOT EXISTS (SELECT NULL FROM texts WHERE texts.rowid = sentencesearch.textid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " sentencesearch, <br/>"
		rc=cursor.execute("DELETE FROM todos WHERE NOT EXISTS (SELECT NULL FROM texts WHERE texts.rowid = todos.textid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " todos, <br/>"
		rc=cursor.execute("DELETE FROM todos WHERE NOT EXISTS (SELECT NULL FROM users WHERE users.rowid = todos.userid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " todos, <br/>"
		
		rc=cursor.execute("DELETE FROM trees WHERE NOT EXISTS (SELECT NULL FROM sentences WHERE sentences.rowid = trees.sentenceid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " trees, <br/>"
		rc=cursor.execute("DELETE FROM trees WHERE NOT EXISTS (SELECT NULL FROM users WHERE users.rowid = trees.userid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " trees, <br/>"
		
		rc=cursor.execute("DELETE FROM features WHERE NOT EXISTS (SELECT NULL FROM trees WHERE trees.rowid = features.treeid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " features, <br/>"
		rc=cursor.execute("DELETE FROM links WHERE NOT EXISTS (SELECT NULL FROM trees WHERE trees.rowid = links.treeid)").rowcount
		if rc:text+= "deleted " + str( rc)+ " features, <br/>"
		
		db.commit()
		db.close()
		return text
	
	
	def correctSentenceLength(self,gooduserid=2):
		db,cursor=self.open() 
		for textid,tname,nbt in self.getall(cursor, "texts",[], []):
			print "__________",textid,tname
			#textid=self.getUniqueId(cursor, "texts", ["textname"],["Amelie_PreudHomme"])
			#print textid
			for sid,snr,sentence,_ in self.getall(cursor, "sentences",["textid"], [textid]):
				
				goodnrtoks=0
				tidToToknr,tidToUid={},{}
				for tid,sidd,uid,aty,sta,com,tim in self.getall(cursor, "trees",["sentenceid"], [sid]):
					
					nt = self.getnumber(cursor, "features", ["treeid","attr"], [tid,"t"])
					#print tid,uid,nt
					if uid==gooduserid:	goodnrtoks=nt
					tidToToknr[tid]=nt
					tidToUid[tid]=uid
				for tid in tidToToknr:
					if tidToToknr[tid]>goodnrtoks:
						print "__sentence",snr
						print "problem",tid,uid,tidToToknr[tid]
						for _,user,real in self.getall(cursor, "users",["rowid"], [tidToUid[tid]]):
							print user,real
						rc=cursor.execute("delete from features where treeid=? and nr>?;",(tid,goodnrtoks)).rowcount
						print "deleted",rc,"features"
						rc=cursor.execute("delete from links where treeid=? and (depid>? or govid>?);",(tid,goodnrtoks,goodnrtoks)).rowcount
						print "deleted",rc,"links"
					
					
					
		db.commit()	
		db.close()
	
if __name__ == "__main__":
	print "bonjour"
	
	#sql=SQL("Rhapsodie")
	sql=SQL("lingCorpus")
	sql.correctSentenceLength()
	#sql.cleanDatabase()
	
	#sentenceid=41
	#userid=5
	#words=	{"1":{"index":1,"gov":{},"features":{"t":"euh","cat":"I","lemma":"euh"}},"2":{"index":2,"gov":{"0":"root"},"features":{"t":"eh ben","cat":"I","lemma":"eh bien"}},"3":{"index":3,"gov":{"4":"sub"},"features":{"t":"on","cat":"Cl","lemma":"cln"}},"4":{"index":4,"gov":{"0":"root"},"features":{"t":"a","cat":"V","lemma":"avoir"}},"5":{"index":5,"gov":{"4":"ad"},"features":{"t":"toujours","cat":"Adv","lemma":"toujours"}},"6":{"index":6,"gov":{"7":"det"},"features":{"t":"un","cat":"D","lemma":"un"}},"7":{"index":7,"gov":{"4":"ad"},"features":{"t":"peu","cat":"N","lemma":"peu"}},"8":{"index":8,"gov":{"4":"obj"},"features":{"t":"ceux","cat":"Pro","lemma":"celui"}},"9":{"index":9,"gov":{"8":"dep"},"features":{"t":u"là","cat":"Adv","lemma":u"là"}},"10":{"index":10,"gov":{"11":"sub"},"features":{"t":"qui","cat":"Qu","lemma":"qui"}},"11":{"index":11,"gov":{"8":"dep"},"features":{"t":"vieillissent","cat":"V","lemma":"vieillir"}}}

	#sql.saveTree(sentenceid,userid,words)
	#sql.compare({41: 'parser', 1355: 'wxcv', 1357: 'admin'})
	#sql.exportAnnotations( 30, "M016.XML", "todosxml")
	#print sql.validvalid(None, 84)
	#print sql.cleanDatabase()
	print "ok"
