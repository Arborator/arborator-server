#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2015 Kim Gerdes
# kim AT gerdes. fr
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of the GNU General Public License
# from http://www.gnu.org/.  For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####
#print 'Content-type: text/html\n\nxxxxx'
import sys,cgi,os,datetime,cgitb, codecs
from time import time
from lib.configobj import ConfigObj
sys.path.append('modules')
from logintools import isloggedin
from lib.database import SQL


form = cgi.FieldStorage()

test = isloggedin("users/")
try:	admin = int(test[0]["admin"])
except:	pass

project = form.getvalue('project',"").decode("utf-8")
csv = form.getvalue('csv',None)

if test:
	cgitb.enable(logdir="dir")
else:
	#sys.exit()
	project="depexo"
	project="lingCorpus"
	admin=5
	csv=True
	


class Evaluation:
	def __init__(self,cats=0,deps=0,funcs=0,lemmas=0,nbwords=0):
		self.cats=cats
		self.deps=deps
		self.funcs=funcs
		self.lemmas=lemmas
		self.nbwords=nbwords
		self.total=self.computeTotalEvaluation()
		
	def __add__(self, other):
		return Evaluation(self.cats+other.cats, self.deps+other.deps, self.funcs+other.funcs, self.lemmas+other.lemmas, self.nbwords+other.nbwords)
		
	def computeTotalEvaluation(self):
		if self.nbwords:
			#print "<br>computeTotalEvaluation",((float(self.cats)/self.nbwords)*sql.categoriesEval + (self.deps/self.nbwords)*sql.governorsEval + (self.funcs/self.nbwords)*sql.functionsEval + (self.lemmas/self.nbwords)*sql.lemmasEval ) / sql.evalTot * 100
			return ((float(self.cats)/self.nbwords)*sql.categoriesEval + (self.deps/self.nbwords)*sql.governorsEval + (self.funcs/self.nbwords)*sql.functionsEval + (self.lemmas/self.nbwords)*sql.lemmasEval ) / sql.evalTot * 100
		else:
			#print "<br>computeTotalEvaluation self.nbwords zero<br>"
			return 0
	def __str__(self):
		return "Evaluation: " + str(self.__dict__)
	
	def htmltable(self):
		out =  "<table class='whitableNarrow'>"
		out += "<tr><th>"+"</th><th>".join([str(x) for x in sorted(self.__dict__ )  ])+"</th></tr>"
		out += "<tr><td>"+"</td><td>".join([str(int(round(self.__dict__[x],0))) for x in sorted(self.__dict__ ) ])+"</td></tr>"
		out += "</table>"
		return out
		
	
def evaluateTree(usertree, teachertree):
	"""
	compares a usertree with the teacher's tree
	each identical cat and lemma adds a point
	each correct gov or func _set_ adds a point, so if a word has more than one governor, all the governors together make up one point
	returns an Evaluation object
	"""
	correctcats,correctdeps,correctfuncs,correctlemmas=(0,0.0,0.0,0)
	cc=sql.catName
	for i in usertree:
		if i in teachertree:
			#print "_____",cc,teachertree[i]
			#print usertree[i]
			if teachertree[i][cc]==usertree[i].get(cc,None):correctcats+=1
			if teachertree[i].get("lemma","")==usertree[i].get("lemma"," "):correctlemmas+=1
			#print "<br>",usertree[i]["gov"]
			govlen=0.0
			if "gov" in teachertree[i]: govlen=float(len(teachertree[i]["gov"]))
			if not govlen:govlen=1.0
			if "gov" in teachertree[i]:
				for g,func in teachertree[i]["gov"].iteritems():
					#print g,usertree[i]["gov"],g in usertree[i]["gov"]
					if "gov" in usertree[i]:
						if g in usertree[i]["gov"]:correctdeps+=1/govlen
						#print correctdeps
						if func == usertree[i]["gov"].get(g,None):correctfuncs+=1/govlen
			else:
				correctdeps+=1
				correctfuncs+=1
		else:
			pass
			#print "no teacher tree for",usertree[i]

	return Evaluation(correctcats,correctdeps,correctfuncs,correctlemmas,len(teachertree))

def attributeSentences(textid, username, userid):
	"""
	attributes sentences to students that didn't even open one of the texts.
	(users that don't have any tree in the whole project, will not be added)
	"""
	sql.getAllSentences(textid, username, userid, dbcrsr=(db,cursor)) # attributes sentences of the text to the user
	usertotevalu = Evaluation()
	for snr,sid,s,treeid in sql.getAllSentences(textid, username, userid, useradmindic.get(username,0), dbcrsr=(db,cursor)):
		# for each sentence attributed to the user from this text
		teachertree = teacherTrees.get(sid,sql.gettree(sid,teacherid)["tree"])
		tree = sql.gettree(sid,userid)["tree"]
		# adding the correct annotations item-wise:
		usertotevalu = usertotevalu + evaluateTree(tree, teachertree)
	return usertotevalu

def makeTable(texts,students,project,theader="",thstart="",thth="\t",thend="\n",trstart="",tdtd="\t",trend="\n",tfooter="", detailTable=False):
	"""
	draws the html table
	used for two cases:
		csv: detailTable = False
		html: detailTable = True
	"""
	
	out = theader
	out += thstart + thth.join(["student","login"]+[textname for textname,textid,nrtokens in sorted(texts)]+["total %"]) + thend
	
	
	for real,username,userid in sorted(students, key=lambda s: s[0].lower()):
		print real.encode("utf-8"),"<br>"
		usertotevalu = Evaluation()
		res=[]
		for textname,textid,nrtokens in sorted(texts):
			evalu = texts[(textname,textid,nrtokens)].get(userid,attributeSentences(textid, username, userid))
			# if a student didn't even open a text and thus doesn't have sentences attributed to her,
			# the function attributeSentences does the distribution.
			res += [evalu]
			#print evalu,"<br>"
			usertotevalu = usertotevalu + evalu
		
		outline = trstart+tdtd.join([real,username]+[ str(int(round(x.total,0)))+" {ht}".format(ht=x.htmltable() if (detailTable and x.nbwords>0)  else "") for x in res ] +[ ("<span style='font-weight: bold;'>" if detailTable else "") +str(round(usertotevalu.total,1))+("</span>" if detailTable else "") +" {ht}".format(ht=usertotevalu.htmltable() if (detailTable and usertotevalu.nbwords>0) else "" )])+trend
		#evalfile.write(outline)
		out += outline
	out += tfooter
	return out

def sampleStats(textid, dbcrsr):
	"""
	function for overview of annotation by students
	"""
	db,cursor=dbcrsr
	r = sql.getall(cursor, "sentences",["textid"], [textid])
	users=[]
	sentencelengths=[]
	modifiedtags=[]
	modifieddeps=[]
	allusers={}
	if r:
		for sentenceid,nr,sentence,textid in r: # for each sentence of the text:
			
			treeDict=dict([ (user, (treeid,uid,realname,timestamp)) for treeid,uid,user,realname,timestamp in sql.treesForSentence(sentenceid, dbcrsr=dbcrsr)])
			timeDict=dict([ (timestamp,user) for (user, (treeid,uid,realname,timestamp)) in treeDict.iteritems() ])
			
			lastuser=timeDict[sorted(timeDict,reverse=True)[0]]
			treeid,uid,realname,timestamp=treeDict[lastuser]
			if lastuser not in users: users+=[lastuser]
			
			parser=timeDict[sorted(timeDict,reverse=True)[-1]]
			ptreeid,puid,prealname,ptimestamp=treeDict[parser]
			
			for ts,user in timeDict.iteritems(): 
				if user!=parser:
					allusers[user]=allusers.get(user,0)+1
			
			modifiedtag = sql.nrDifferent(treeid, ptreeid, "tag", dbcrsr)
			modifiedtags +=[modifiedtag]
			modifieddep = sql.nrDifferent(treeid, ptreeid, None, dbcrsr)
			modifieddeps +=[modifieddep]
			
			sentencelength = sql.getnumber(cursor, "features", ["treeid","attr"], [treeid,"t"])
			#print "sentencelength",sentencelength
			sentencelengths+=[sentencelength]
			
		asentencelength=sum(sentencelengths)/float(len(sentencelengths))
		amodifiedtag=sum(modifiedtags)/float(len(modifiedtags))
		percentmodtags=round(sum(modifiedtags)/float(sum(sentencelengths))*100,2)
		amodifieddep=sum(modifieddeps)/float(len(modifieddeps))
		percentmoddeps=round(sum(modifieddeps)/float(sum(sentencelengths))*100,2)

		userinfo = ", ".join([u+":"+str(c) for u,c in allusers.iteritems()])
			
		return len(r), asentencelength, amodifiedtag, percentmodtags, amodifieddep, percentmoddeps, userinfo
					

userdir="users/"
RESERVEDNAMES = ['config', 'default', 'temp', 'emails', 'pending',"user_files_go_in_"]
useradmindic={}
for user in [entry[:-4] for entry in os.listdir(userdir) if os.path.isfile(userdir+entry) and entry[:-4] not in RESERVEDNAMES and not entry[0]=="."]:
	thisuserc = ConfigObj(userdir+user+'.ini')
	useradmindic[user]=int(thisuserc.get('admin',0))

sql=SQL(project)
project=project.encode("utf-8")
teacherTrees={} # sid -> teacher tree
students={} # real, username, userid -> None
texts={} # textname,textid,nrtokens -> {userid1 --> (correctcats,correctdeps,correctfuncs,correctlemmas,correctTotal), userid2->...} 

teacherid=sql.userid(sql.teacher)
useradmindic[sql.teacher]=5 # treat teacher as admin

#print 'Content-type: text/html\n\n'

db,cursor=sql.open()

try:	mtime = os.path.getmtime(os.path.join("projects",project,"arborator.db.sqlite"))
except OSError: mtime = 0
last_modified_date = datetime.datetime.fromtimestamp(mtime)

with codecs.open(os.path.join("projects",project,"stats."+str(last_modified_date)+".csv"),'w','utf-8') as evalfile:
	
	evalfile.write("\t".join(["textname","nr sents", "asentencelength", "amodifiedtag", "percentmodtags", "amodifieddep", "percentmoddeps", "userinfo"])+"\n")
	
	textcounter=0
	
	for textname,textid,nrtokens in sorted( [(textname,textid,nrtokens) for textid,textname,nrtokens in list(sql.getall(cursor, "texts", None, None))]): 
		# for each text
		texts[(textname,textid,nrtokens)]={}		
		exotype, exotoknum = sql.getExo(textid,(db,cursor))
		
		if exotype:
			uids=[userid for userid, in sql.uidForText(textid,(db,cursor))] # some tree exists for uids
			for userid in uids:
				# for each userid for whom we got a tree
				#numtok=0
				#print cursor, "users",["rowid"],[userid]
				#print "!!!",cursor.description
				#allu=list()
				#print userid,allu
				for _,username,real in sql.getall(cursor, "users",["rowid"],[userid]): # only executes once
					#print "<br><br><br>",userid,username,real.encode("utf-8"),"<br>"
					
					students[real,username,userid]=None
					usertotevalu = Evaluation()
					for snr,sid,s,treeid in sql.getAllSentences(textid, username, userid, useradmindic.get(username,0), dbcrsr=(db,cursor)):
						
						# for each sentence attributed to the user from this text
						
						teachertree = teacherTrees.get(sid,sql.gettree(sid,teacherid, indb=db, incursor=cursor)["tree"])
						
						tree = sql.gettree(sid,userid, indb=db, incursor=cursor)["tree"]
						#print "it took",time()-ti
						# adding the correct annotations item-wise:
						#print "before eval"
						
						usertotevalu = usertotevalu + evaluateTree(tree, teachertree)
						#print "after eval"
						#print "__",snr,usertotevalu,"<br>" # s.encode("utf-8"),
					
					texts[(textname,textid,nrtokens)][userid]=usertotevalu
				print 'Dummy: '+username,len(texts[(textname,textid,nrtokens)])
				
		else: # normal annotation: make some stats
			print "Dummy: __________",textname, textcounter
			evalfile.write("\t".join([textname] + [unicode(info) for info in sampleStats(textid,(db,cursor))])+"\n")
			#,str(nrsentences),str(asentencelength),str(amodifiedtag),str(amodifieddep),userinfo]			
				
			
		textcounter+=1	
		
			
if not exotype: 
	print "wrote stat file in project folder"
	sys.exit() # the rest is only if exo
				
if csv:
	print 'Content-type: text/csv'
	print "Content-Disposition:attachment;filename="+project+".csv\n"; 
	
	filecontent = makeTable(texts,students,project) #.encode("utf-8")
	#if not test:
		#print filecontent
	#else:
	try:
		mtime = os.path.getmtime(os.path.join("projects",project,"arborator.db.sqlite"))
	except OSError:
		mtime = 0
	last_modified_date = datetime.datetime.fromtimestamp(mtime)

	with codecs.open(os.path.join("projects",project,"evaluation."+str(last_modified_date)+".csv"),'w','utf-8') as evalfile:
		evalfile.write(filecontent)
	
		
	
else:
	print 'Content-type: text/html\n\n'
	if os.path.exists("projects/"+project+"/"+project+".png"):img="<img src='projects/"+project+"/"+project+".png' align='top' height='18'>"
	else: img=""
	print """<html>
		<head>
			<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
			<title>Arborator - {project} Project</title>
			<link media="screen" href="css/jquery-ui-1.8.18.custom.css" type="text/css" rel="stylesheet">
			<link href="css/arborator.css" rel="stylesheet" type="text/css">
		</head>
		<body id="body">
			<div id="center" class="center" style="width:100%">
				<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
				<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
				<a href="project.cgi?project={project}" style='position: fixed;left:120px;top:5px;color:white;' title="project overview">{img} {project} Annotation Project</a>
				<div style='margin:5 auto;' id='sentinfo'>Student results</div>
			</div>		
			<div id="projectbox" class="ui-widget ui-widget-content ui-corner-all box" style="text-align:-moz-center;">
		""".format(project=project,img=img)
					
	
	print makeTable(texts,students,project,theader="<table class='whitable'>",thstart="<tr><th>",thth="</th><th>",thend="</th></tr>",trstart="<tr><td>",tdtd="</td><td>",trend="</td></tr>",tfooter="</table>", detailTable=True).encode("utf-8")
	
	print "categories:",sql.categoriesEval,"%, "
	print "governors:",sql.governorsEval,"%, "
	print "functions:",sql.functionsEval,"%, "
	print "lemmas:",sql.lemmasEval,"%, "
	print "points in total:",sql.evalTot
	print '<br>Change these values in the <a href="configedit.cgi?project={project}">project configuration</a>.'.format(project=project)
	
	print """</div></body></html>"""


#if __name__ == "__main__":

