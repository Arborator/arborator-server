#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2013 Kim Gerdes
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

import os, cgitb, cgi,time, sys, glob
import config, database

import codecs


from time import asctime, localtime

sys.path.append('modules')
from logintools import login
from logintools import isloggedin
from logintools import logout

cgitb.enable()



##############################################################################################"

def start():
	form = cgi.FieldStorage()
	thisfile = os.environ.get('SCRIPT_NAME',".")
	userdir = 'users/'

	logint = form.getvalue("login",None)
	if logint == "logout":
		print logout(userdir) # printing cookie header. important!
		print "Content-Type: text/html\n" # blank line: end of headers
		print '<script type="text/javascript">window.location.href=".";</script>'
	project = (form.getvalue("project",None))
	if project: project =project.decode("utf-8")
	
	action = form.getvalue("action",None)
	if action: action =action.decode("utf-8")
	if action:
		if action.startswith("project_"):project=action[8:]
	if project: action=u"project_"+project
	if action:
		#action, userconfig = login(form, userdir, thisfile, action.encode("utf-8"))
		try:action, userconfig = login(form, userdir, thisfile, action)
		except:
			print "Content-Type: text/html\n" # blank line: end of headers
			print "Error! Can't read the user config files. Please check that the user files are readible by the apache user"
			sys.exit("something's wrong")
	else:
		action, userconfig = login(form, userdir, thisfile, action)
	adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"].decode("utf-8"),userconfig["realname"].decode("utf-8")
	
	print "Content-Type: text/html\n" # blank line: end of headers
	projectconfig=None
	try:	
		projectconfig = config.configProject(project) # read in the settings of the current project
	except:
		print "Error! Can't read the configuration files. Please check that the files project.cfg, functions.cfg, and categories.cfg are present in the project folder	"
		sys.exit("something's wrong")
	if not projectconfig:
		##print "Content-Type: text/html\n" # blank line: end of headers
		print "something went seriously wrong: can't read the configuration of the project"
		if project: print project.encode("utf-8")
		##print "Content-Type: text/html\n" # blank line: end of headers
		print '<script type="text/javascript">window.location.href=".";</script>'
		sys.exit("something's wrong")
	try:
		sql=database.SQL(project)
		userid = sql.userid(username, realname)
	except Exception , e:
		from sqlite3 import OperationalError
		if isinstance(e, OperationalError) and str(e)in["attempt to write a readonly database","unable to open database file"]:
			print "Error! Make your database and the path leading there from the arborator base modifiable by the apache user!"
		else:
			print "strange error accessing the database.<br>",str(e)
		sys.exit("something's wrong")
	
	if (not projectconfig) and (not action):
		print "something went seriously wrong: can't read the configuration of the project",project.encode("utf-8")
		#print '<script type="text/javascript">window.location.href=".";</script>'
		sys.exit("something's wrong")
	
	if not adminLevel:
		print "something went seriously wrong: a common can't access the configedit file"
		if project: print project.encode("utf-8")
		##print "Content-Type: text/html\n" # blank line: end of headers
		print '<script type="text/javascript">window.location.href=".";</script>'
		sys.exit("user went astraw!"+username)
	
	return project,projectconfig,sql,thisfile,username,userid,adminLevel,form

	
	
def export(textname, exportNumber, exportType, project):
	
	print "<h2>Exporting",textname,"(text number",exportNumber,")</h2>"
	
	if textname:
		fc,users,sc,doublegovs=sql.exportAnnotations(int(exportNumber), textname, exportType )
		if fc==0: 	print "<div style='padding:10;' class='ui-state-error ui-corner-all'>No files were exported, probably because the file is assigned to nobody.</div><br/>"
		else:		
			print "Exported",fc,"files and a total of",sc,"sentences.<br/><br/>"
			if exportType in ["allconll","allxml"]:
				print "Exported all existing annotated trees into",
				if exportType =="allconll": print textname+".user.trees.conll files.<br/>"
				else: print textname+".user.trees.rhaps.xml files.<br/>"
			else: 
				print "Exported complete files for each assignment into"
				if exportType =="todoconll": print textname+".user.complete.conll10 files.<br/>"
				else: print textname+".user.complete.rhaps.xml files.<br/>"
		print "<br/><div style='padding:10;'  class='ui-state-highlight ui-corner-all'>",
		if fc==1:print "The export file for",users[0],"is"
		else: print "All the",fc,"export files (for",(", ".join(users)).encode("utf-8")+") are"
		print " in the export folder <strong style='color:#DD137B'><a href='projects/{project}/export' target='_blank'>inside the project folder</a></strong> on the server.</div><br/>".format(project=project)
		if doublegovs: print "<div style='padding:10;' class='ui-state-error ui-corner-all'>Achtung!<br/> The annotation contains multiple governors for one or more nodes. The lines have been doubled, and thus this is not a common Conll format!</div>"
	else:
		print "problem: no textname"
	
def reaction(project,projectconfig,sql,userid,form,query):
	
	
	filename = form.getvalue("filename",None)
	if filename: # upload file	
		from treebankfiles import uploadConll
		filetype = form.getvalue("filetype",None)
		print "trying to upload",filename,filetype,"into the database of the project",project.encode("utf-8")
		if filetype in ["conll4","conll10","conll14"]:
			print "---------- here we go"
			nrsentences = uploadConll(sql,filename)
		
			print """<div class="ui-widget ui-widget-content ui-corner-all box">I added {nrsentences} sentences from {filename}.</div>""".format(nrsentences=nrsentences,filename=filename)
		else:	print """<div class="ui-widget ui-widget-content ui-corner-all box">Strange filetype: {filename}.</div>""".format(filename=filename)

	eraseNumber = form.getvalue("eraseNumber",None)
	if eraseNumber: # erase text
		print "erasing text number ",eraseNumber,"<br/>"
		sc=sql.removeText(int(eraseNumber))
		print "erased",sc,"sentences."

	#statustextid = form.getvalue("statustextid",None)
	#if statustextid: # erase text
		##print "statustextid, text number:",statustextid,"<br/>"
		#sql.statustext(int(statustextid),userid)

	exportNumber = form.getvalue("exportNumber",None)
	textname=None
	if exportNumber: # export text
		print '<div class="ui-widget ui-widget-content ui-corner-all box" >'
		
		textname = form.getvalue("textname",None)
		exportType = form.getvalue("exportType",None)
		#print exportNumber,type(exportNumber)
		exportNumber=int(exportNumber)
		if exportNumber==-1 :
			for t,tid in sorted( [(t,tid) for tid,t,nrtokens in sql.getall(None, "texts", None, None)]):
				export(t, tid, exportType, project)
			
		else: export(textname, exportNumber, exportType, project)
		
		print '</div>'

		
	userchoice = form.getlist('userchoice')
	textid = form.getvalue("textid",None)

	if userchoice and textid: # change todos
		removeid = int(form.getvalue("removeid",0))
		validator = int(form.getvalue("validator",0))
		if removeid:
			sql.removetextfromuser(int(textid),removeid)
		else:
			u=userchoice[0].split("(")[-1][:-1]
			sql.addtext2user(textid,u,validator)
			
		
		
	
	if query: # search results	
		print """<div class="ui-widget ui-widget-content ui-corner-all box"  style="text-align:-moz-center;">"""
		
		res = sql.snippetSearch(query)
		if res: 
			print "<h2>Search results for {query}:</h2>".format(query=query)
			print res.encode("utf-8")
		else: print "no results for {query}</h2>".format(query=query)
		print """</div>"""
		
	




def printhtmlheader(project):
	
	print """<html>
			<head>
			<title>Arborator - {project} Project</title>""".format(project=project)
	print """
	<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
	<script type="text/javascript" src="script/jquery.js"></script>
	<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
	<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen"/>
	<link href="css/arborator.css" rel="stylesheet" type="text/css">
	<script type="text/javascript">	
	project="{project}";
	userid="{userid}";
	username="{username}";
	""".format(project=project,userid=userid,username=username)
	
	print """
	$('html').click(function() {
		$("#exportdiv").css({ display: 'none' } );	
		$("#userform").css({ display: 'none' } );	
		});

	edit = function(textid,opensentence) {
		$("#textid").attr("value", textid );
		$("#opensentence").attr("value", opensentence );
		$("#editorform").submit();
	}
	remove = function(textid, text) {
		$("#eraseNumber").attr("value",textid);
		$("#question").html("Are you sure that you want to erase the text "+text+" from the database?")
		$('#dialog').dialog('open');
		}
	exportAnnos = function(textid, text, offset) {
		$("#exportNumber").attr("value",textid);
		$("#textname").attr("value",text);
		offset.left=offset.left-280;
		$("#exportdiv").offset(offset).css({ display: 'inline' } );
		}	
	exportGo = function(type) {
		$("#exportType").attr("value",type);
		console.log($("#export"))
		$("#export").submit();
		$("#dialog").html("<img src='images/loading.gif'>");
		$("#dialog").dialog({
			height: 230,
 			width:150,
			modal: true,
			title:"Please wait!!!<br>This can be long.",
			buttons: {}
			});
		$('#dialog').dialog('open');
	}
	adduser = function(textid, text, offset) {
		$("#userform").offset(offset).css({ display: 'inline' } );
		//console.log(textid,text,$("#textid"));
		$("#utextid").attr("value",textid);
		$("#uremove").attr("value",0);
		}
		
	userchoice = function(v) {
		$("#validator").attr("value",v);
		$("#uremove").attr("value",0);
				
		$("#useraddremove").submit();	
		}
	
	userremove = function(tid,uid) {	
		$("#utextid").attr("value",tid);
		$("#uremove").attr("value",uid);
		$("#useraddremove").submit();
		}
	nextstatus = function(tid) {
		//console.log("nextstatus",tid)	
	
		$.ajax({
			type: "POST",
			url: "statusChange.cgi",
			data: {"project":project,"userid":userid,"username":username,"textid":tid}, 
			success: function(answer){
					$("#textStatus"+tid).html(answer.status);
					//console.log("changed!",answer);
					
				},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				console.log("error",project,erasetreeid)
				
				}
			});
	
	
	
	
	
		//$("#statustextid").attr("value",tid);
		//$("#nextstatusform").submit();
		}	
		
		
	$(function () {
		$("#dialog").dialog({
			bgiframe: true,
			autoOpen: false,
			height: 350,
 			width:400,
			modal: true,
			buttons: {
				
				Cancel: function() {
					$(this).dialog('close');
				},
				"OK": function() {
					$(this).dialog('close');					
					$("#erase").submit();
				}
				}
			});

	})
	

	getEvaluation = function(project,uid) {
		$("#evalubutton"+uid).replaceWith("<img id='evalubutton"+uid+"' src='images/ajax-loader.gif'>");
		$.ajax({
			type: "GET",
			url: "getEvaluation.cgi",
			data: {"project":project,"uid":uid}, 
			success: function(data){
					$("#evalubutton"+uid).replaceWith(data);
					//console.log("got!"+answer);
			
				},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				console.log("error",project)
				alert("error erasing"+XMLHttpRequest+ '\\n'+textStatus+ "\\n"+errorThrown);
				}
			});
		
	}
	
	
	
	checkConfig = function() {
		$("#ent").hide();
		$("#wait").show();
		
		$.ajax({
			type: "POST",
			url: "configCheck.cgi",
			data: {"config":$("#configurationArea").val(),"cats":$("#catconfigurationArea").val(),"funcs":$("#funcconfigurationArea").val(),"project":project}
			})
			.done(function(data){
					if (typeof data.answer === "undefined") $("#message").html(data);
					else $("#message").html(data.answer);
					console.log("got!"+data.answer);
				})
			.fail(function(XMLHttpRequest, textStatus, errorThrown){
				console.log("error",project)
				alert("error in config"+XMLHttpRequest+ '\\n'+textStatus+ "\\n"+errorThrown);
				})
			.always(function() {
				$("#ent").show();
				$("#wait").hide();
				$("#message").show();
				});
			
				
				
		
		
		
	}
	
	</script>
	
	</head>
	"""
	
	
	
def printheadline(project):
	if os.path.exists("projects/"+project+"/"+project+".png"):img="<img src='projects/"+project+"/"+project+".png' align='top' height='18'>"
	else: img=""
	query = form.getvalue("searchtext","")
	print 	"""<body id="body">
			<div id="center" class="center" style="width:100%">
				<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
				<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
				<a href='project.cgi?project={project}' style='position: fixed;left:120px;top:5px;color:white;' title="project overview">{img} {project} Annotation Project</a>
				<div style='margin:5 auto;' id='sentinfo'>Configuration</div>
					
				</div>
		""".format(project=project,img=img,query=query)
	if os.path.exists("sitemessage.html"):print open("sitemessage.html").read()
	return query


		

def printmyassignments(project,sql,projectconfig,userid): # assigned texts
	
	txt = u"""
	
	<div class="ui-widget ui-widget-content ui-corner-all box"  style="text-align:-moz-center;">
	You have been assigned the following texts of the <b>{project}</b> Project<br/>
	""".format(project=project)

	txt += u"""Please select the text to annotate:<br/><br/><table class="whitable">"""
	txt += u"	<tr><td>text name</td><td>number of sentences</td><td>number of tokens</td><td>trees modified by you</td><td>status</td></tr>"
	scount,mcount,tcount=0,0,0
	for _,_,tid,todotype,status,comment in sql.getall(None, "todos",["userid"], [userid]):
		try:
			tid,t,nrtokens = sql.getall(None, "texts",["rowid"],[tid])[0]
		except:
			sql.removeText(tid)
			print "we found a todo for a non existing text and removed it."
			continue
		try: todotype=int(todotype)
		except: todotype=0
		
		
		if todotype:txt += u"	<tr><td><b><span class='val'>validation of <br></span><a  style='cursor:pointer;' onclick=edit('"+str(tid)+"',1)>"+ t +"</a></b></td>"
		else:	txt += u"	<tr><td><b><a  style='cursor:pointer;' onclick=edit('"+str(tid)+"',1)>"+ t +"</a></b></td>"
		sn=sql.getnumber(None, "sentences", ["textid"], [tid])
		scount+=sn
		txt += u"		<td>"+str(sn)+"</td>"
		tn=sql.getNumberTokensPerText(tid)
		tcount+=tn
		txt += u"		<td>"+str(tn)+"</td>"
		txt += u"		<td>&nbsp;"
		mc = sql.getNumberTreesPerUserAndText(userid,tid)
		mcount+=mc
		txt += str(mc)
		txt += u"</td>"
		txt += u"		<td><a  style='cursor:pointer;dispay:block' id='textStatus"+str(tid)+"' "
		txt+= "onclick=nextstatus('"+str(tid)+"')>"+ projectconfig["text status"].get(status,"ooooo") +"</a></td>" 
		txt += u"</tr>"
	txt += u"	<tr> </tr><tr><td>a total of:</td><td>{scount}</td><td>{tcount}</td><td>{mcount}</td></tr>".format(scount=scount,mcount=mcount,tcount=tcount)
	txt += u"</table></div>"

	if scount: print txt.encode("utf-8")
	else: print u"""<div class="ui-widget ui-widget-content ui-corner-all box"  style="text-align:-moz-center;">
	You have not been assigned any text of the <b>{project}</b> Project<br/></div>
	""".format(project=project).encode("utf-8")


def printalltexts(project,sql,adminLevel):############################# all texts of the project
	nrt,stotal,ttotal,tanno,tvali=sql.getNumberTexts(),0,0,0,0
	print """
	<div class="ui-widget ui-widget-content ui-corner-all box"  style="text-align:-moz-center;" id='projectbox'>
	The <b>{project}</b> Project has {nrt} texts and {nrs} sentences. <br/>
	""".format(project=project,nrt=nrt,nrs=sql.getNumberSentences())
	print """<br/><table class='whitable'>"""
	print "	<tr><td>text name</td><td>number of sentences</td><td>number of tokens</td><td >annotators</td><td>validator</td><td title='non sollicitated trees by users not assigned to this text are listed here.'>other trees</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>" # style='width:300'
	#print "<tr><td>text name</td><td>number of sentences</td><td>annotators</td><td>validators</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>" # style='width:300'


	for t,tid,nrtokens in sorted( [(t,tid,nrtokens) for tid,t,nrtokens in sql.getall(None, "texts",None,None)]): # got to get it in alphabetical order
		print "	<tr ><td><b><a  style='cursor:pointer;dispay:block'  onclick=edit('"+str(tid)+"',1)>"+ t +"</a></b></td>"
		sn=sql.getnumber(None, "sentences", ["textid"], [tid])
		stotal+=sn
		print "		<td>{sn}</td>".format(sn=sn)
		if not nrtokens:
			nrtokens=sql.getNumberTokensPerText(tid)
		ttotal+=nrtokens
		print "		<td>{tn}</td>".format(tn=nrtokens)
		
		#a,v,tannot,tvalit = sql.assignmenttableline(tid,adminLevel)
		
		a,v = "",""
		tannot,tvalit=0,0
		#us=[]
		for _,uid,tid,todotype,status,comment in sql.getall(None, "todos",["textid"], [tid], orderby="order by userid"):
			try: todotype=int(todotype)
			except: todotype=0
			#try: status=int(status)
			#except: status=0
			res= sql.getall(None, "users",["rowid"], [uid])
			if res :
				uid,user,realname = res[0]
				
				if not realname:
					realname=sql.realname(user)
				
				#us+=[realname]
				#av="			<div  style='float:left;margin-right:10px;'>"+realname.encode("utf-8")
				av=u"			<div  style='float:left;margin-right:10px;'>"+realname
				#.encode("utf-8")
				if status!="0": 
					av+= "<i><sub>"+ projectconfig["text status"].get(status,"ooo")+ "</i></sub>"
				if adminLevel:
					av+= "			<div class='ui-button-icon-primary ui-icon ui-icon-circle-minus' style='float:right;cursor:pointer;margin-right:15px;'  onclick='var e=arguments[0];e.stopPropagation();userremove({tid},{uid});'></div>".format(tid=tid,uid=uid)
				
				av+="</div>"
				if todotype: # validators
					v+=av
					tvalit+=1
				else: # annotators
					
					a+=av
					tannot+=1
		#aorv= a or v
		
		if not a: a="<div  style='float:left;margin-right:15px;'>nobody yet</div>"
		a= "		<td>"+a+"</td>"
		if not v: v="<div  style='float:left;margin-right:15px;'>nobody yet</div>" 
		v= "		<td>"+v+"</td>"
		
		
		
		
		tanno+=tannot
		tvali+=tvalit
		print a.encode("utf-8"),v.encode("utf-8")
		
		#oss="&nbsp;"
		
			#if u not in us:	oss+=u+ " "
		#print "		<td>&nbsp;",", ".join ( [unicode(u) for u, in sql.treesForText(tid) if u not in us] ).encode("utf-8"),"</td>"
		print "		<td>&nbsp;","</td>"
		print "		<td>"	
		if adminLevel:print """			<div style='float:left;cursor:pointer;' title='asign this text to a user' onclick="var e=arguments[0];e.stopPropagation();adduser({tid},'{t}',$(this).offset()); ">asign<div style='float:right;cursor:pointer;' class='ui-button-icon-primary ui-icon ui-icon-person' ></div></div>&nbsp;&nbsp;&nbsp; """.format(tid=tid,t=t)
		else: print "			&nbsp;"
		print "		</td>"
		if adminLevel:
			print """		<td><span style='cursor:pointer;'onclick="var e=arguments[0];e.stopPropagation();exportAnnos({tid},'{t}',$(this).offset());"  title='export annotations of this text' ><img src="images/dbexport.bw.png" border="0"></span></td>""".format(tid=tid,t=t)
		else:print """		<td>&nbsp;</td>"""
			
		if adminLevel>1:print """		<td><span class='ui-button-icon-primary ui-icon ui-icon-trash' style='cursor:pointer;' onclick="var e=arguments[0];e.stopPropagation();remove({tid},'{t}');"  title='remove all sentences from this file from database' ></span></td>""".format(tid=tid,t=t)
		else: print """		<td>&nbsp;</td>""".format(tid=tid,t=t)

		print "	</tr>"
		
	if adminLevel:allexport="""<span style='cursor:pointer;'onclick="var e=arguments[0];e.stopPropagation();exportAnnos(-1,'all',$(this).offset());"  title='export all annotations - very slow! blocks the database!' ><img src="images/dbexport.bw.png" border="0"></span>"""
	else:allexport=""
	if nrt: print """<TFOOT>	<tr style='padding-top:20;'><td>{nrt} texts</td><td>{stotal} sentences</td><td>{ttotal} tokens</td><td>{tanno} annotation assignments<br> (an average of {ava:.2f} assignments per text)</td><td>{tvali} validation assignments <br> (an average of {avv:.2f} validators per text)</td><td>&nbsp;</td><td>&nbsp;</td><td>{allexport}&nbsp;</td><td>&nbsp;</td></tr> 	</TFOOT>""".format(stotal=stotal, ttotal=ttotal, nrt=nrt, tanno=tanno,tvali=tvali, ava=float(tanno)/nrt,avv=float(tvali)/nrt,allexport=allexport)
	print "</table></div>"


	
def printuserassignments(project,projectconfig,sql,adminLevel, lastseens):
	parser=projectconfig["configuration"]["baseAnnotatorName"]
	teacher=projectconfig["configuration"].get("teacher",None)
	if teacher:
		teacherid=sql.userid(teacher)
	print """
	
	<div class="ui-widget ui-widget-content ui-corner-all box"  style="text-align:-moz-center;">
	The assignments of the <b>{project}</b> Project<br/>
	""".format(project=project)
	print """<br/><table class='whitable'>"""
	print """	<tr>
		<td>user name</td>
		<td>assigned texts: <br> text name (trees modified by user, total number of sentences, total number of tokens, status)</td>
		<td>total number of modified trees</td>
		<td>total number of sentences / <br>  total number of tokens</td> 
		<td>last seen</td> <td>last modification</td> """
	#if teacher: print "<td>result</td>"
	print "	</tr>"
	#scount,tcount=0,0
	
	
	
	for uid,u,rea in sql.getall(None, "users",None,None, orderby="order by realname"):
		if u!=parser:
			textids=[]
			treeidlists=[]
			totaltokens=[]
			titles=[]
			#sentenceidlists=[]
			txt=""
			sc,tc,tnrtrees,lastmodif=0,0,0,[]
			for _,uid,tid,todotype,status,comment in sql.getall(None, "todos",["userid"], [uid]): # for all the assignments (texts) for the given user
				try:		todotype=int(todotype)
				except: 	todotype=0
				textids+=[tid]
				status=projectconfig["text status"].get(status,"?")
				tid,t,nrtokens = sql.getall(None, "texts",["rowid"],[tid])[0]
				sn=sql.getnumber(None, "sentences", ["textid"], [tid])
				
				treenrs=sql.treeNrsForUserAndText(uid,tid)
				trees=sorted([(int(n),asctime(localtime(o))) for (sid,n,o,trid,) in treenrs])
				treeidlists+=[ [ (trid,sid) for (sid,n,o,trid,) in treenrs] ]
				nrtrees=len(treenrs)
				lastmodif+=[o for (sid,n,o,trid,) in treenrs]
				
				
				if sn==nrtrees:	trees="All"
				else:		trees=str(trees).replace("(","\n").replace("),","").replace("'","").replace(",",":").replace(")","")[1:-1] or "None"
				
				tn=nrtokens
				sc+=sn
				tc+=tn
				totaltokens+=[tn]
				titles+=[t]
				tnrtrees+=nrtrees
				if todotype:	txt+= "<span class='val'>"
				txt+= """			<span title="modified trees: {trees}">{t} (<span class='val'>{nrtrees}</span>/{sn}/{tn}/{status})</span>&nbsp;&nbsp;""".format(t=t,sn=sn,tn=tn,status=status,nrtrees=nrtrees,trees=trees)
				if todotype:	txt+= "</span>  "
			if sc:	
				print "	<tr ><td><b>{u}</b></td><td>".format(u=u)
				print txt
				avt="<span class='val'>{tnrtrees} ({avt:.1f}%)</span>".format(tnrtrees=tnrtrees,avt=float(tnrtrees)/sc*100)
			else:	
				continue
				print "uuu"
				avt=" 0"
			if lastmodif:		lastmodif=asctime(localtime(sorted(lastmodif)[-1]))
			if sc:			lastseen=asctime(localtime(lastseens.get(u,(0,0))[0]))
			else:			lastseen= "&nbsp;"
			print "			&nbsp;</td><td><b>{avt}</td><td>{sc}/{tc}<td>{lastseen}</td><td>{lastmodif}</td></b></td></tr>".format(tnrtrees=tnrtrees,avt=avt  ,sc=sc,tc=tc, lastseen=lastseen, lastmodif=lastmodif or "&nbsp;")	
			
			if teacher:
				
				print "<tr><td>{rea} </td><td colspan=5>".format(rea=rea.encode("utf-8"))
			
				print '''<input type="button" onclick="getEvaluation('{project}',{uid});" class="fg-button ui-state-default ui-corner-all" style="width:155px;z-index:33;" value="get {rea}'s evaluation" name="evalubutton{uid}" id="evalubutton{uid}" cursor="pointer">'''.format(project=project,uid=uid, rea=rea.encode("utf-8"))
				print "</td></tr>"
				print "<tr><td colspan=6 style='padding-bottom:20;'></td></tr>"
				#break
				
	print "</table></div>"
	if adminLevel>1:
		print """<div class="ui-widget ui-widget-content ui-corner-all box">
	<a href="uploader.cgi?project={project}"><span class='ui-button-icon-primary ui-icon ui-icon-folder-open' style='' title='add conll or xml files containing annotations to the database' ></span>Add files to the database</a>
	</div></div></div></div></div></div>&nbsp;<br/>&nbsp;""".format(project=project)
	
	return now


	
def printmenues(project,sql):
	
	parser=projectconfig["configuration"]["baseAnnotatorName"]
	print """<form method="get" action="editor.cgi" style="display: none;" id="editorform" >
			<input type="hidden" id="project" name="project" value="{project}">
			<input type="hidden" id="textid" name="textid" value="">
			<input type="hidden" id="opensentence" name="opensentence" value="1">
			
			<img src="images/ajax-loader.gif" border="0">
			<img src="images/loading.gif" border="0">
		</form>
	""".format(project=project)

	print """<form method="post" action="project.cgi?project={project}" style="display: none;" id="nextstatusform" >
			<input type="hidden" id="statustextid" name="statustextid" value="">
		</form>
	""".format(project=project)
	#<input type="hidden" id="project" name="project" value="{project}">
	print """<div id="userform" style=" position:absolute;display: none;" onclick="var e=arguments[0];e.stopPropagation();">
			<form  method="post" action="project.cgi?project={project}" id="useraddremove" name="useradd">
				<select id="userchoice" name="userchoice" style="width:180px;"  >""".format(project=project)
	for uid,user,realname in sql.getall(None, "users",None,None):
			if user!=parser:
				#print [user]
				print "			<option>",
				if realname: print realname.encode('utf-8'),
				print " ("+user+")</option>"

		
	print """		</select>
				<div class='ui-button-icon-primary ui-icon ui-icon-circle-check' style='cursor:pointer; float:right;' onclick="var e=arguments[0];e.stopPropagation();userchoice(1);"  title='asign this user as validatator' ></div>
				<div class='ui-button-icon-primary ui-icon ui-icon-circle-plus' style='cursor:pointer; float:right;' onclick="var e=arguments[0];e.stopPropagation();userchoice(0);"  title='asign this user as annotator' ></div>
				<input type="hidden" id="utextid" name="textid" value="">
				<input type="hidden" id="uremove" name="removeid" value="false">
				<input type="hidden" id="validator" name="validator" value="0">
			</form>
		</div>"""

		
	print """<div class="ui-widget ui-widget-content ui-corner-all" style="position: absolute; padding: 5px;z-index:20;display:none;font-size:.8em;" id="exportdiv">
			<form id="export" name="export" method="POST"  action="project.cgi?project={project}" >
			
			
			
			<div id="radioset" class="ui-buttonset" style="margin-left:15px">
				export complete files per assignment as<br>
					<label for="radio1" class="ui-state-active ui-button ui-widget ui-state-default ui-button-text-only ui-corner-left" onclick='exportGo("todosconll")' title="All assignments are exported as complete CoNLL files, independently of whether the annotator has actually changed the tree or not from the original parse tree. CoNLL files only contain the form, the lemma, the category, and the dependency.">
						<span class="ui-button-text">
							CoNLL file
						</span>
					</label><label for="radio2" class="ui-state-active ui-button ui-widget ui-state-default ui-button-text-only  ui-corner-right" onclick='exportGo("todosxml")' title="All assignments are exported as complete XML files, independently of whether the annotator has actually changed the tree or not from the original parse tree.">
						<span class="ui-button-text">
								XML file
						</span>
					</label>
					
			</div>
			<br>
			<div id="radioset" class="ui-buttonset" style="margin-left:15px">
				export all trees by any annotator as<br>
					<label for="radio1" class="ui-state-active ui-button ui-widget ui-state-default ui-button-text-only ui-corner-left"  onclick='exportGo("allconll")' title="All trees that any annotator has saved are exported, including the original parse trees. The resulting CoNLL files don't necessarily contain all sentences.  CoNLL files only contain the form, the lemma, the category, and the dependency.">
						<span class="ui-button-text">
							CoNLL file
						</span>
					</label><label for="radio2" class="ui-state-active ui-button ui-widget ui-state-default ui-button-text-only  ui-corner-right" onclick='exportGo("allxml")' title="All trees that any annotator has saved are exported, including the original parse trees. The resulting XML files don't necessarily contain all sentences.">
						<span class="ui-button-text">
								XML file
						</span>
					</label>
					
			</div>
			<br>
			<div id="radioset" class="ui-buttonset" style="margin-left:15px">
				export most recent trees by any annotator as<br>
					<label for="radio1" class="ui-state-active ui-button ui-widget ui-state-default ui-button-text-only ui-corner-left"  onclick='exportGo("lastconll")' title="The most recent tree for every sentence is exported, this may be the original parse trees. CoNLL files only contain the form, the lemma, the category, and the dependency.">
						<span class="ui-button-text">
							CoNLL file
						</span>
					</label><label for="radio2" class="ui-state-active ui-button ui-widget ui-state-default ui-button-text-only  ui-corner-right" onclick='exportGo("lastxml")' title="The most recent tree for every sentence is exported, this may be the original parse trees.">
						<span class="ui-button-text">
								XML file
						</span>
					</label>
					
			</div>
			<input type="hidden" id="exportNumber" name="exportNumber" value="">
			<input type="hidden" id="exportType" name="exportType" value="">
			<input type="hidden" id="textname" name="textname" value="">
			</form>
		</div>
		
		<div id="dialog" title="Confirmation" style="display: none;" >
			<div class="ui-state-error ui-corner-all" style="margin: 40px;padding: 10pt 0.7em;">
				<h2 id="question">Are you sure that you want to erase the text?</h2>
			</div>
		</div>
		<form method="post" action="project.cgi?project={project}" style="display: none;" id="erase" >
			<input type="hidden" id="eraseNumber" name="eraseNumber" value="">
			
		</form>
		
		""".format(project=project)


def printconfig(project,projectconfig):
	#project=project
	filecontent=codecs.open("projects/"+project.encode("utf-8")+"/project.cfg","r","utf-8").read()
	catfilecontent=codecs.open("projects/"+project.encode("utf-8")+"/"+projectconfig["configuration"]["categoriesfilename"].encode("utf-8"),"r","utf-8").read()
	funcfilecontent=codecs.open("projects/"+project.encode("utf-8")+"/"+projectconfig["configuration"]["functionsfilename"].encode("utf-8"),"r","utf-8").read()
	
	txt = u"""<div class="ui-widget ui-widget-content ui-corner-all box"  style="text-align:-moz-center;">
	This is the configuration file of the <b>{project}</b> Project.<br/> Please edit with care. Comments start with "#".
	""".format(project=project)
	#<p class="section-title">Configuration</p>
	txt+=u"""<textarea id="configurationArea" name="configurationArea" style="width:100%;height:400px;color:black;">{c}</textarea>""".format(c=filecontent)
	
	txt+=u"""<br/>Categories
	<textarea id="catconfigurationArea" name="catconfigurationArea" style="width:100%;height:400px;color:black;">{c}</textarea>""".format(c=catfilecontent)
	txt+=u"""<br/>Functions
	<textarea id="funcconfigurationArea" name="funcconfigurationArea" style="width:100%;height:400px;color:black;">{c}</textarea>""".format(c=funcfilecontent)
	txt+=u"""<input type="button" onclick="checkConfig()" class="fg-button ui-state-default ui-corner-all" style="font:normal .8em Arial;padding-top: 2px;width:80px;" value="Save" name="ent" id="ent"><div style="display:none;" id="message"></div><div style="display:none;" id="wait"><img id='ent' src='images/ajax-loader.gif'></div><br/>"""
	#txt+=unicode(projectconfig)
	txt+=u"</div>"
	print txt.encode("utf-8")
	
	
	
	print """<br/><br/><div class="ui-widget ui-widget-content ui-corner-all box">
	<h3>Useful links</h3>
	<p>The <a href='http://bulba.sdsu.edu/jeanette/thesis/PennTags.html'>Penn Treebank tags</a> and the <a href='./corpus/PTB.tags'>corresponding category file for the Arborator</a>.</p>
	<p>This <a href='http://csscolorpicker.com/'>color picker</a> comes in handy.</p>


	</div>
	"""


#checkConfigProject(projectName, filename
	         
	         
	         
	
def printfooter(project,username,thisfile, now):
	"""
	"now" contains a list of all users currently online
	"""
	a=u"""<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">logged in as {username}&nbsp;&nbsp;&nbsp;
	<a href="{thisfile}?login=logout&project={project}">logout</a>""".format(username=username,project=project,thisfile=thisfile)
	print (u"""<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">logged in as {username}&nbsp;&nbsp;&nbsp;
	<a href="{thisfile}?login=logout&project={project}">logout</a>""".format(username=username,project=project,thisfile=thisfile)).encode("utf-8")
	if username!="guest": print (u'&nbsp;&nbsp;&nbsp;<a href="{thisfile}?login=editaccount&project={project}">edit the account {username}</a>'.format(username=username,project=project,thisfile=thisfile)).encode("utf-8")
	if adminLevel > 1: print (u'&nbsp;&nbsp;&nbsp;<a href="{thisfile}?login=admin&project={project}">User Administration</a>'.format(project=project,thisfile=thisfile)).encode("utf-8")
	#if adminLevel: print (u'&nbsp;&nbsp;&nbsp;<a href="configedit.cgi?project={project}">Edit Configuration</a>'.format(project=project)).encode("utf-8")
	nowstring=u'<a  title="Ask questions or share your feelings with {r}..." href="mailto:{email}?subject=The%20Arborator%20is%20driving%20me%20crazy!">{r} ({u})</a>'
	now = [nowstring.format(u=u,r=unicode(r),email=email) for (u,r,email) in now if u!= username]
	if len(now)==1: print (u'&nbsp;&nbsp;&nbsp;You are not alone! This other user is online now: '+now[0]).encode("utf-8")
	elif len(now)>1: print (u'&nbsp;&nbsp;&nbsp;You are not alone! These other users are online now: '+u", ".join(now)).encode("utf-8")
	print "</div>"
	print '</body></html>'
	#&nbsp;&nbsp;&nbsp;<a href="admin.cgi?project={project}">Corpus Administration</a>
	

		
if __name__ == "__main__":
	
	project,projectconfig,sql,thisfile,username,userid,adminLevel,form = start()
	
	printhtmlheader(project.encode("utf-8"))
	query=printheadline(project.encode("utf-8"))
	
	reaction(project,projectconfig,sql,userid,form,query)
	
	printconfig(project,projectconfig)
	
	#printmyassignments(project,sql,projectconfig,userid)
	#printalltexts(project.encode("utf-8"),sql,adminLevel)
	lastseens,now=sql.usersLastSeen()
	#if adminLevel:	printuserassignments(project.encode("utf-8"),projectconfig,sql,adminLevel, lastseens)
		
	#printmenues(project.encode("utf-8"),sql)
	printfooter(project,username,thisfile,now)
	
	










