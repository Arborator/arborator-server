#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2015 Kim Gerdes
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

import os, cgitb, cgi, sys
sys.path.append('modules')
from logintools import login
from logintools import isloggedin
from logintools import logout
from lib import config, database
cgitb.enable()

# global variables:
project,projectEsc,projectconfig,sql,thisfile,textid,textname,username,userid,adminLevel,todo,validator,validvalid,exotype,opensentence,sentencenumbe,addEmptyUser=None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None

graphical=0
##############################################
######################### functions

def printhtmlheader():
	"""
	all strings in parameters are already in utf-8
	
	"""
	print (u"""<html><head>
		<title>Arborator - Editor - {title}</title>
		<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">

		<script type="text/javascript" src="script/jquery.js"></script>
		<script type="text/javascript" src="script/raphael.js"></script>
		<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>

		<script type="text/javascript" src="script/arborator.draw.js"></script>
		<script type="text/javascript" src="script/jsundoable.js"></script>
		<script type="text/javascript" src="script/arborator.edit.js"></script>
		<script type="text/javascript" src="script/raphael.export.js"></script>
		
		<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
		<link href="css/arborator.css" rel="stylesheet" type="text/css">""".format(title=textname)).encode("utf-8")
	
	
	config.jsDefPrinter(projectconfig) # prints all general, text-independant, stuff for javascript: categories, functions, etc
	
	#print """<script type="text/javascript"> numbersent=""",snr,";"
	print """<script type="text/javascript"> numbersent=1;"""
	print "project= '"+projectEsc.encode("utf-8")+"';"
	#print "uid= '"+"3"+"';" # TODO!
	print "textname= '"+textname.encode("utf-8")+"';"
	print "textid= '"+str(textid)+"';"
	print "userid= "+str(userid)+";"
	print "username= '"+username.encode("utf-8")+"';"
	if adminLevel or (sql.validatorsCanModifyTokens and validator) or sql.usersCanModifyTokens:
		tokenModifyable=1
	else: tokenModifyable=0
	print "tokenModifyable= "+str(tokenModifyable)+";"
	print "todo= '"+str(todo)+"';"
	print "validator= '"+str(validator)+"';"
	if addEmptyUser: print "addEmptyUser= '"+str(addEmptyUser)+"';"
	else: print "addEmptyUser= null;"
	print "validvalid= '"+str(validvalid)+"';"
	print "opensentence= '"+str(opensentence)+"';"
	print "editable= "+str(sql.editable)+";"
	print "filename = null;" # stuff for use in viewer not editor...
	print "nr = null;"
	print "filetype = null;"
	print "function settings() {"
	print projectconfig["look"]["look"]
	print """colored={"dependency":null}; //object of elements to be colored. the colors have to be defined in the configuration. just leave the object empty {} if you don't want colors
	attris[shownfeatures[categoryindex]]=attris["cat"]
	colored[shownfeatures[categoryindex]]=null;
	}
	
	</script>
	</head>"""
	

def printheadline():
	
	if os.path.exists("projects/"+project.encode("utf-8")+"/"+project.encode("utf-8")+".png"):img="<img src='projects/"+project.encode("utf-8")+"/"+project.encode("utf-8")+".png' align='top' height='18'>"
	else: img=""
	
	if adminLevel:openbutton= '<input type="button" id="openall" name="openall" value="open all" style="width:105px;z-index:33;" class="fg-button ui-state-default ui-corner-all " onClick="openAllTrees();">'
	else:openbutton=""
	
	print 	"""<body id="body">
			<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
			<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
			<a href="project.cgi?project={project}" style='position: fixed;left:120px;top:5px;color:white;' title="project overview">{img} {project} Annotation Project</a>
				<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>{textname} &nbsp; {quantityInfo} </span>
			</div>
			<div id="center" class="center" style="width:100%;">
			<form method="post" action="editor.cgi" name="save" id="save" class="nav" style="top:0px;right:150px;">
				<input type="button" id="sav" name="sav" value="all trees are saved" style="width:155px;z-index:33;" class="fg-button ui-state-default ui-corner-all ui-state-disabled" onClick="saveAllTrees();">
				{openbutton}
			</form>
			<div id="loader" ><img src="images/ajax-loader.gif"/></div>
		""".format(textname=textname.encode("utf-8"), quantityInfo=quantityInfo,project=project.encode("utf-8"),img=img,openbutton=openbutton)
	if os.path.exists("sitemessage.html"):print open("sitemessage.html").read()

	
	#ui-state-disabled


#def printfooter(project,username,thisfile, now):
def printfooter():
	now=lastseens,now=sql.usersLastSeen()	
	print (u"""<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">logged in as {username}&nbsp;&nbsp;&nbsp;
	<a href="{thisfile}?login=logout&project={project}">logout</a>""".format(username=username,project=projectEsc,thisfile=thisfile)).encode("utf-8")
	if username!="guest": print (u'&nbsp;&nbsp;&nbsp;<a href="{thisfile}?login=editaccount&project={project}">edit the account {username}</a>'.format(username=username,project=projectEsc,thisfile=thisfile)).encode("utf-8")
	if adminLevel > 1: print (u'&nbsp;&nbsp;&nbsp;<a href="{thisfile}?login=admin&project={project}">User Administration</a>'.format(project=projectEsc,thisfile=thisfile)).encode("utf-8")
	
	nowstring=u'<a  title="Ask questions or share your feelings with {r}..." href="mailto:{email}?subject=The%20Arborator%20is%20driving%20me%20crazy!">{r} ({u})</a>'
	now = [nowstring.format(u=u,r=r,email=email) for (u,r,email) in now if u!= username]
	if len(now)==1: print (u'&nbsp;&nbsp;&nbsp;You are not alone! This other user is online now: '+now[0]).encode("utf-8")
	elif len(now)>1: print( u'&nbsp;&nbsp;&nbsp;You are not alone! These other users are online now: '+u", ".join(now)).encode("utf-8")
	print "</div>"
	print '</body></html>'
	#&nbsp;&nbsp;&nbsp;<a href="admin.cgi?project={project}">Corpus Administration</a>
	
	
#def printexport(project):
def printexport():
	print """
	<form method="post" action="convert_svg.cgi?project={project}" name="ex" id="ex" style=" position:fixed;top:6px;right:30px;display:none;" >
		<input type="hidden" id="source" name="source" value="">
		<select id="exptype" name="type" class="ui-button ui-state-default ui-corner-all" style="height:16px;font: italic 10px Times,Serif;border:thin solid silver;" >
			<option>pdf</option>
			<option>ps</option>
			<option>odg</option>
			<option>jpg</option>
			<option>png</option>
			<option value="tif">tiff</option>
			<option>svg</option>
			<option>conll</option>
			<option>xml</option>
		</select>
		<input type="button" title="export" value="export" class="ui-button ui-state-default ui-corner-all" onClick="exportTree();"  style="padding: 0.0em 0.0em;" >
	</form>
	""".format(project=projectEsc.encode("utf-8"))
	
def printmenues():
	#print projectconfig.functions
	# form for functions and form for categories
	print """	
	<div id="funcform" style="display:none;position:absolute;">
		<form  method="post" id="func" name="func" >
			<select id="funchoice" class='funcmenu' onClick="changeFunc(event);"  size=""" +str( len(projectconfig.functions))+""" style="height:"""+str( len(projectconfig.functions)*13.5)+"""px; width:80px;"  >"""
	for f in projectconfig.functions:
		#print "___",f.encode("utf-8")
		print "<option style='color: "+projectconfig.funcDic[f]["stroke"].encode("utf-8")+";'>"+f.encode("utf-8")+"</option>"	
	print """
			</select>
		</form>
	</div>
	
	<div id="catform" style="display:none;position:absolute;">
		<form  method="post" id="cat" name="cat" >
			<select id="catchoice" class='funcmenu' onClick="changeCat();"  size=""" +str( len(projectconfig.categories))+""" style="height:"""+str( len(projectconfig.categories)*13.5)+"""px; " >"""

	for i,c in enumerate(projectconfig.categories): 
		print "<option style='color: "+projectconfig.catDic[c]["fill"].encode("utf-8")+";'>"+c.encode("utf-8")+"</option>"	
	
	print """
			</select>
		</form>
	</div>
	<div style="border-top:1px solid #EEE;">&nbsp;</div>	
	"""
	
	# form for compare
	print """
		<div class="ui-widget ui-widget-content ui-corner-all" style="position: absolute; padding: 5px;z-index:20;display:none;" id="compbox">
			<form id="compform" name="compform" method="POST">
				<div id="complist">
				</div><br>
				<div align="center" id="compasubmit">
					<img class="compare" src="images/compare.png" border="0" align="bottom" onclick='compareSubmit()'>
				</div>
			</form>
		</div>
		"""
	# form for check
	print """
		<div class="ui-widget ui-widget-content ui-corner-all" style="position: absolute; padding: 5px;z-index:20;display:none;" id="checkbox">
			
				<div id="checklist">
				</div><br>
				<div align="center">
					<img src="images/check.png" border="0" align="bottom">
				</div>
			
		</div>
		"""

def printdialogs():
	
	print """
	<div id="dialog" title="Confirmation" style="display: none;" >
		<div class="ui-state-error ui-corner-all" style="margin: 40px;padding: 10pt 0.7em; font-weight:100;">
			<h2 id="question">Are you sure?</h2>
		</div>
	</div>
	
	<div id="fdialog" title="Features">
		<form method="post" action="editor.cgi" id="featureform">
			
			<input type="hidden" id="eusername" name="username" value="">
			<input type="hidden" id="esentenceid" name="sentenceid" value="">
			<table id="featab" class="ui-widget ui-widget-content" style="width:100%;">
				<thead>
					<tr class="ui-widget-header ">
						<th>Attribute</th>
						<th>Value</th>
					</tr>
				</thead>
				<tbody  id="featabody"></tbody>
			</table>
		</form>
	
	</div>
	"""


##############################################################################################"

def start():
	global project,projectEsc,projectconfig,sql,thisfile,textid,textname,username,userid,adminLevel,todo,validator,addEmptyUser,validvalid,exotype,opensentence,quantityInfo,graphical
	form = cgi.FieldStorage()
	thisfile = os.environ.get('SCRIPT_NAME',".")
	userdir = 'users/'

	logint = form.getvalue("login",None)
	if logint == "logout":
		print logout(userdir) # printing cookie header. important!
		print "Content-Type: text/html\n" # blank line: end of headers
		print '<script type="text/javascript">window.location.href=".";</script>'
	project = form.getvalue("project","")
	projectEsc=""
	if project: 
		project =project.decode("utf-8")
		projectEsc=project.replace("'","\\'").replace('"','\\"')
	action = form.getvalue("action",None)
	if action: 
		action =action.decode("utf-8")
		if action.startswith("project_"):project=action[8:]
	if project: action="project_"+project
	
	try:
		action, userconfig = login(form, userdir, thisfile, action)
	except IOError, e:
		print "Content-Type: text/html\n" # blank line: end of headers
		print "login failed",e
		sys.exit()
	#try:
		
	#except IOError, e:
		#print "login failed",e
		#sys.exit()
		#raise IOError('Reading user file failed: %s' % e)
	#except:
		#print "login failed"
	adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"].decode("utf-8"),userconfig["realname"].decode("utf-8")
	
	print "Content-Type: text/html\n" # blank line: end of headers
	projectconfig=None
	try:	projectconfig = config.configProject(project) # read in the settings of the current project
	except:	pass
	if not projectconfig:
		#print "Content-Type: text/html\n" # blank line: end of headers
		print "something went seriously wrong: can't read the configuration of the project",project.encode("utf-8")
		#print '<script type="text/javascript">window.location.href=".";</script>'
		#sys.exit("something's wrong")


	sql=database.SQL(project)
		
	textid = form.getvalue("textid",None)
	if textid: 	textid=int(textid)
	else:		textid=1
	try:
		_,textname,_ = sql.getall(None, "texts",["rowid"],[textid])[0]
	except:
		print "something went seriously wrong: The text you are looking for does not seem to exist!",project.encode("utf-8")
		textname="text not found!"
	userid = sql.userid(username,realname)
	opensentence = form.getvalue("opensentence",1)

	todo = sql.gettodostatus(userid,textid)
	validator=0
	if todo>0: validator=int(todo) # -1 and 0 => 0, 1 => 1
	
	validvalid=sql.validvalid(textid)
	
	exotype, exotoknum =sql.getExo(textid)
	#print "uu",sql.exotypes[exotype],sql.exotypes[exotype]=="graphical feedback"
	if sql.exotypes[exotype] in ["teacher visible","graphical feedback", "percentage"] :
		addEmptyUser=username
	if sql.exotypes[exotype] in ["teacher visible"] :
		validvalid+=[sql.userid(sql.teacher)]
	if sql.exotypes[exotype]=="graphical feedback":
		graphical=1
	if exotoknum and not adminLevel: 	quantityInfo = ">"+str(exotoknum)+" tokens"
	else: 					quantityInfo = str(sql.getnumber(None, "sentences",["textid"],[textid]))+" sentences"
	

	
#def main(project,sql,textid,userid,adminLevel,todo,validvalid,validator):
def main():
	########### essential loop: all the sentences:
	
	for snr,sid,s,tid in sql.getAllSentences(textid, username, userid, adminLevel):
		#print adminLevel, validvalid, validator
		treelinks, firsttreeid, sentenceinfo=sql.links2AllTrees(sid,snr,username,adminLevel, todo, validvalid, validator,addEmptyUser=addEmptyUser)
		status=""
		if todo>=0:status=sql.gettreestatus(sid,userid)
		status="<span id='status{nr}' class='status' onClick='nexttreestatus({sid},{nr})'>{status}</span>".format(status=status,sid=sid, nr=snr)
		connectRight=""
		if adminLevel or (sql.validatorsCanConnect and validator):
			connectRight='''<img class="connectRight" src="images/chain.png" border="0" align="bottom" id='connectRight{nr}' nr='{nr}' title="connect with next tree (+ctrl: split at selcted word)"> '''.format(nr=snr)
		exo=""
		if exotype>1: # 0: no exercise, 1: no feedback
			exo='''<img class="check" src="images/check.png" border="0" align="bottom" id='check{nr}' nr='{nr}' title="check annotation" graphical={graphical}> '''.format(nr=snr, graphical=graphical)
		print '''<div id='sentencediv{nr}' class='sentencediv' style="margin:10px;" sid={sid}  nr={nr}>
				<a id='toggler{nr}' class="toggler" treeid="{firsttreeid}" nr="{nr}" >
					{nr}: {sentence} &nbsp;
				</a> 
				<span id="othertrees{nr}" > {treelinks} </span>
				<img class="saveimg" src="images/save.png" border="0" align="bottom" id='save{nr}' title="save">
				<img class="undoimg" src="images/undo.png" border="0" align="bottom" id='undo{nr}'>
				<img class="redoimg" src="images/redo.png" border="0" align="bottom" id='redo{nr}'> 
				{status}
				<img class="exportimg" src="images/export.png" border="0" align="bottom" id='export{nr}' nr='{nr}' title="export"> 
				{connectRight}
				{exo}
			</div><p><small>{sentenceinfo}</small></p>'''.format(sentence=s.encode("utf-8"),nr=snr, sid=sid, firsttreeid=firsttreeid, project=project.encode("utf-8"), userid=userid, treelinks=treelinks.encode("utf-8"), status=status,connectRight=connectRight,exo=exo,sentenceinfo=sentenceinfo.encode("utf-8"))
		#print "addEmptyUser",addEmptyUser
	#print '<div id="holder" style="background:white; position:relative;"> </div> '


##############################################################################################"

		
if __name__ == "__main__":
	start()
	#printhtmlheader(project.encode("utf-8"),projectconfig,textid,textname.encode("utf-8"),username.encode("utf-8"),userid,todo,validator,addEmptyUser,opensentence,sql)
	printhtmlheader()
	
	#printheadline(project.encode("utf-8"),textname.encode("utf-8"),quantityInfo)
	printheadline()
	printexport()
	#print "todo",todo
	#main(project,sql,textid,userid,adminLevel,todo,validvalid,validator)
	main()
	
	printmenues()
	printdialogs()
	
	printfooter()
	
	
	
