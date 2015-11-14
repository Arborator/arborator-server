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

"""
page accessible from project.cgi for admins

allows edits of the configuration

"""

import os, cgitb, cgi, sys, glob
import config, database

import codecs

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
	print 	"""<body id="body">
			<div id="center" class="center" style="width:100%">
				<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
				<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
				<a href="project.cgi?project={project}" style='position: fixed;left:120px;top:5px;color:white;' title="project overview">{img} {project} Annotation Project</a>
				<div style='margin:5 auto;' id='sentinfo'>Configuration</div>
					
				</div>
		""".format(project=project,img=img)
	if os.path.exists("sitemessage.html"):print open("sitemessage.html").read()




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
	printheadline(project.encode("utf-8"))
		
	printconfig(project,projectconfig)
	
	lastseens,now=sql.usersLastSeen()
	printfooter(project,username,thisfile,now)
	
	










