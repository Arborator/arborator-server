#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2012 Kim Gerdes
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
import config, conll, database

cgitb.enable()







#//filename="";
			#//filetype="";


def printhtmlheader():

	print """<html><head>
		<title>Arborator - Quickedit</title>
		<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">

		<script type="text/javascript" src="script/jquery.js"></script>
		<script type="text/javascript" src="script/raphael.js"></script>
		<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
		<script type="text/javascript" src="script/jquery.fileupload-ui.js"></script>
		<script type="text/javascript" src="script/jquery.fileupload.js"></script>
		<script type="text/javascript" src="script/jquery.dimensions.js"></script>
		<script type="text/javascript" src="script/splitter-152.js"></script>
		<script type="text/javascript">
			editable=true;
			project="quickie";
			treeid=null;
			
		</script>
		<script type="text/javascript" src="script/arborator.draw.js"></script>
		<script type="text/javascript" src="script/jsundoable.js"></script>
		<script type="text/javascript" src="script/arborator.edit.js"></script>
		<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
		<link href="css/arborator.css" rel="stylesheet" type="text/css">
		<style type="text/css" media="all">
		.splitter {
			height: 92%;
			margin: -1 auto;
		}
		.splitter-pane {
			overflow: auto;
		}
		.splitter-bar-horizontal {
			height: 10px;
			background-image: url(images/hgrabber.gif);
			background-repeat: no-repeat;
			background-position: top;
		}
		.splitter-bar-horizontal-docked {
			width: 10px;
			background-image: url(img/hdockbar-trans.gif);
			background-repeat: no-repeat;
			background-position: center;
		}
		.splitter-bar.ui-state-highlight {
			opacity: 0.7;
		}
		.splitter-iframe-hide {
			visibility: hidden;
		}
		</style>
		<script type="text/javascript">

		</script>
		<script type="text/javascript"> 
			function settings() 
			{
				tab=8; 			// space between tokens
				line=25 		// line height
				dependencyspace=220; 	// y-space for dependency representation
				xoff=8; 		// placement of the start of a depdency link in relation to the center of the word
				linedeps=6; 		// y distance between two arrows arriving at the same token (rare case)
				pois=4; 		// size of arrow pointer
				tokdepdist=15; 		// distance between tokens and depdendency relation
				funccurvedist=8;	// distance between the function name and the curves highest point
				depminh = 15; 		// minimum height for dependency
				worddistancefactor = 2; // distant words get higher curves. this factor fixes how much higher.
				rootTriggerSquare = 50; // distance from top of svg above which root connections are created and minimum width of this zone (from 0 to 50 par example the connection jumps to the middle)
				extraspace=50 // extends the width of the svg in order to fit larger categories
				defaultattris={"font": '14px "Arial"', "text-anchor":'start'};
				attris = {"t":		{"font": '18px "Arial"', "text-anchor":'start',"fill": '#000',"cursor":'move',"stroke-width": '0'}, 
					"cat":	{"font": '12px "Times"', "text-anchor":'start',"fill": '#036',"cursor":'pointer'},
					"lemma":	{"font": '14px "Times"', "text-anchor":'start',"fill": '#036'},
					"depline":	{"stroke": '#999',"stroke-width":'1',"stroke-dasharray": ''},
					"deptext":	{"font": '12px "Times"', "font-style":'italic', "fill": '#999',"cursor":'pointer'},
					"dragdepline":	{"stroke": '#8C1430',"stroke-width":'2',"stroke-dasharray": ''},
					"dragdeplineroot":	{"stroke": '#985E16',"stroke-width":'2',"stroke-dasharray": ''},
					"source":	{"fill": '#245606'},
					"target":	{"fill": '#8C1430',"cursor": 'url("images/connect.png"),pointer', "font-style":'italic'}, 
					"form":	{"font-style":'italic'}
					};
				colored={"dependency":null}; //object of elements to be colored. the colors have to be defined in config.py. just leave the object empty {} if you don't want colors
				attris[shownfeatures[categoryindex]]=attris["cat"]
				colored[shownfeatures[categoryindex]]=null;
			}
			
			function makeSplitter()
			{
				$("#CentralSplitter").splitter({
					type: "h",
					sizeTop: 250,
					dock: "top",
					dockSpeed: 500,
					
				});
			}
			
			
			function conllize()
			{
				var words=$("#sentence").val().split(" ");
				var conll="";
				for (i in words)
				{		
					var word = words[i] ;
					console.log(word,i);
					conll=conll+(parseInt(i)+1)+"\\t"+word+"\\t"+word+"	N	_	_	0	root	_	_\\n";
				}
				$("#conll").val(conll);
			
			}
		</script>
		
	</head>"""
	"""anchorToWindow: true
	outline: true, resizeToWidth: true,
	minLeft: 100,
		minRight: 100,
		
		//dockKey: 'Z',	// Alt-Shift-Z in FF/IE
		//accessKey: 'I'	// Alt-Shift-I in FF/IE
	"""
	
	
def printheadline(textname):	
	print 	"""<body id="body">
			<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
			<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
				<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>{textname}</span>
			</div>
			<div id="center" class="nav" style="width:100%;float:right;top:0px;">
				<button id="button" class="fg-button ui-state-default ui-corner-all ui-state-enabled" role="button" onClick="quickPut();" style="float:right;z-index:33;"><span class="ui-button-text">CoNLL table to graphical trees</span></button>
				<button id="button" class="fg-button ui-state-default ui-corner-all ui-state-disabled" role="button" onClick="allTreesConll();return false;" style="float:right;z-index:33;"><span class="ui-button-text">Graphical trees to CoNLL table</span></button>
			</div>
			<div id="center" class="center" style="width:100%;float:right;top:0px;">
		""".format(textname=textname)
	
	#<form method="post" action="editor.cgi" name="save" id="save" class="nav" style="width:100%;top:0px;float:right;">
#<input type="button" id="sav" name="sav" value="all trees are saved" style="width:155px;z-index:33;" class="fg-button ui-state-default ui-corner-all ui-state-disabled" onClick="saveAllTrees();">
	#</form>			

def printfooter():
	#print '<script src="script/upload.js"></script>	'
	#print """<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">You are not logged in &nbsp;&nbsp;&nbsp;
	#<a href=".">login on the start page</a>"""
	print "</div>"
	print '</body></html>'
	#&nbsp;&nbsp;&nbsp;<a href="admin.cgi?project={project}">Corpus Administration</a>
	
	
def printexport():
	print """
	<form method="post" action="convert_svg.cgi?project=quickie" name="ex" id="ex" style=" position:fixed;top:6px;right:30px;display:none;" >
		<input type="hidden" id="source" name="source" value="">
		<select id="exptype" name="type" class="ui-button ui-state-default ui-corner-all" style="height:16px;font: italic 10px Times,Serif;border:thin solid silver;" >
			<option>pdf</option>
			<option>ps</option>
			<option>odg</option>
			<option>jpg</option>
			<option>png</option>
			<option value="tif">tiff</option>
			<option>svg</option>
		</select>
		<input type="button" title="export" value="export" class="ui-button ui-state-default ui-corner-all" onClick="exportTree();"  style="padding: 0.0em 0.0em;" >
	</form>
	"""

	
def printforms(conlltext):
	
	#<br><br>
	#<div id="projectbox" style="text-align:-moz-center;" class="ui-widget ui-widget-content ui-corner-all box">
	#</div> <FORM method="post" action="quickedit.cgi" id="conllform"	
		
		
		#</FORM>
	#<button id="button" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" role="button" onClick="$('#conllform').submit()"><span class="ui-button-text">Show trees</span></button>
	print """Paste CoNLL file below:<TEXTAREA NAME="conll" id="conll" style="font: normal 10px Sans-Serif;width:100%; height:200;" """,
		
	if conlltext:print ">"+conlltext #.decode("utf-8")
	else: print """>1	faut	falloir	V	_	_	0	root	_	_
2	que	que	CS	_	_	1	obj	_	_
3	tu	tu	Cl	_	_	6	sub	_	_
4	me	me	Cl	_	_	6	obl	_	_
5	les	le	Cl	_	_	6	obj	_	_
6	donnes	donner	V	_	_	2	dep	_	_

1	c'	ce	Cl	_	_	2	sub	_	_
2	est	être	V	_	_	0	root	_	_
3	plus	plus	Adv	_	_	4	dep	_	_
4	simple	simple	Adj	_	_	2	pred	_	_"""
	print """</TEXTAREA>"""
	print """<script type="text/javascript">
		$("textarea").focus(function () {nokeys=true;}).blur(function () {console.log("lost focus")});
		</script>
	"""
	print "<div ><span style='float:left;'>additional functions</span> <input type='text' id='addfuncs'  style='width:88%'>  </input> </div>"
	print "<div ><span style='float:left;'>additional categories</span> <input type='text' id='addcats'  style='width:88%;'>  </input> </div>"
	print "<br>"
	print """<div ><span style='float:left;'>sentence</span> <input type='text' id='sentence'  style='width:88%;'>  </input> </div>
	<button style="float:right;z-index:33;" onclick="conllize();" role="button" class="fg-button ui-state-default ui-corner-all ui-state-enabled" id="button"><span class="ui-button-text">CoNLL table to graphical trees</span></button>
	"""

	
def printdialogs():
	
	print """
	<div id="dialog" title="Confirmation" style="display: none;" >
		<div class="ui-state-error ui-corner-all" style="margin: 40px;padding: 10pt 0.7em;">
			<h2 id="question">Are you sure?</h2>
		</div>
	</div>
	
	<div id="fdialog"  title="Features"  style="display: none;">
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
	form = cgi.FieldStorage()
	thisfile = os.environ.get('SCRIPT_NAME',".")
	#userdir = 'users/'

	#logint = form.getvalue("login",None)
	#if logint == "logout":
		#print logout(userdir) # printing cookie header. important!
		#print "Content-Type: text/html\n" # blank line: end of headers
		#print '<script type="text/javascript">window.location.href=".";</script>'
	#project = form.getvalue("project",None)
	#action = form.getvalue("action",None)
	#if action:
		#if action.startswith("project_"):project=action[8:]
	#if project: action="project_"+project
	#action, userconfig = login(form, userdir, thisfile, action)
	#adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"],userconfig["realname"]
	print "Content-Type: text/html\n" # blank line: end of headers
	#projectconfig=None
	#try:	projectconfig = config.configProject(project) # read in the settings of the current project
	#except:	pass
	#if not projectconfig:
		##print "Content-Type: text/html\n" # blank line: end of headers
		#print "something went seriously wrong: can't read the configuration of the project",project
		#print '<script type="text/javascript">window.location.href=".";</script>'
		#sys.exit("something's wrong")


	#sql=database.SQL(project)
		
	conlltext = form.getvalue("conll",None)
	
	

	
	#if not textid:textid=1
	#_,textname = sql.getall(None, "texts",["rowid"],[textid])[0]	
	#userid = sql.userid(username,realname)
	opensentence = form.getvalue("opensentence",1)

	#todo = sql.gettodostatus(userid,textid)
	#validator=0
	#if todo>0: validator=todo # -1 and 0 => 0, 1 => 1
	
	
	
	
	
	
	return thisfile,opensentence,conlltext

	
def main(conlltext):

	print """
	<div id="loader" ><img src="images/ajax-loader.gif"/></div>
	<script type="text/javascript">"""
	#numbersent=""",i,";"
	#print "filename= '"+filename+"';"
	#print "filetype= '"+filetype+"';"
	print "opensentence= '0';"
	print '</script>'
	print '<div id="trees" style="width:100%;"> </div>'
	if conlltext:
		conlltext, trees, sentences, conlltype, functions, categories = conll.conlltext2trees(conlltext) # , correctiondic={"tag":"cat"}
		filename = conll.tempsaveconll(conlltext," ".join(sentences),conlltype)
		#print "<br><br>",filename
		functions,funcDic,categories,catDic = config.simpleJsDefPrinter(functions, categories)
		#print "<br><br>"," ".join(sentences), filename
		
		print """
		<script type="text/javascript">
		filename = 'corpus/temp/{filename}';
		filetype = 'conll{conlltype}';
		
		</script>
		""".format(filename=filename,conlltype=conlltype)
		
		#//$(document).ready(function(){
			#//makeSplitter();
			#//$('#CentralSplitter').trigger('dock');
			#//}
		
		for i,s in enumerate(sentences):########### essential loop: all the sentences:

			print '''<div style="margin:10px"><a class="toggler" nr="{nr}">{nr}: {sentence} </a></div>'''.format(sentence=s.encode("utf-8"),nr=i)
		printmenues(functions,funcDic,categories,catDic)
	
	
	
	
	
	return conlltext	
	
	#for sid,snr,s,tid in sql.getall(None, "sentences",["textid"],[textid]):
		
		#treelinks, firsttreeid=sql.links2AllTrees(sid,snr,username,adminLevel, validator)
		#status=""
		#if todo>=0:status=sql.gettreestatus(sid,userid)
		#status="<span id='status{nr}' class='status' onClick='nexttreestatus({sid},{nr})'>{status}</span>".format(status=status,sid=sid, nr=snr)
		#print '''<div id='sentencediv{nr}' class='sentencediv' style="margin:10px;" sid={sid}  nr={nr}>
				#<a class="toggler" treeid="{firsttreeid}" nr="{nr}" >
					#{nr}: {sentence} &nbsp;
				#</a> 
				#<span id="othertrees{nr}" > {treelinks} </span>
				#<img class="saveimg" src="images/save.png" border="0" align="bottom" id='save{nr}' title="save">
				#<img class="undoimg" src="images/undo.png" border="0" align="bottom" id='undo{nr}'>
				#<img class="redoimg" src="images/redo.png" border="0" align="bottom" id='redo{nr}'> 
				#{status}
				#<img class="exportimg" src="images/export.png" border="0" align="bottom" id='export{nr}' nr='{nr}' title="export"> 
				
			#</div>'''.format(sentence=s.encode("utf-8"),nr=snr, sid=sid, firsttreeid=firsttreeid, project=project, userid=userid, treelinks=treelinks, status=status)
	
	#print '<div id="holder" style="background:white; position:relative;"> </div> '


##############################################################################################"

		
if __name__ == "__main__":
	thisfile,opensentence,conlltext=start()
	printhtmlheader()
	printheadline("Quickedit")
	
	printexport()
	
	print """<div id="CentralSplitter"  style="width:90%;border:0px;font: normal 10px Sans-Serif;width:100%;  padding: 0;" class="ui-widget ui-widget-content" >
		<div style="max-height: 220px;"> """
	print """</div>
		<div style="background:white;width:100%; ">"""
	conlltext=main(conlltext)
	print """</div>
	</div> """
	printforms(conlltext)
	
	
	#printmenues(functions,funcDic,categories,catDic)
	printdialogs()
	printfooter()








	
	
	
	
	
	
	
	
	
	


































def old ():


	########################## default values
	verbose=False

	######################### functions

	def sizeofFile(num):
		for x in ['bytes','KB','MB','GB','TB']:
			if num < 1024.0: return "%3.1f%s" % (num, x)
			num /= 1024.0



	def printexport():
		print '<form method="post" action="convert_svg.cgi" name="ex" id="ex" style=" position:fixed;top:6px;right:30px; " >'
		print """<input type="hidden" id="source" name="source" value=""> """
		
		print '<input type="button" name="export" value="export" class="ui-button ui-state-default ui-corner-all" onClick="exportTree();" >'
		#<button id="expbut" class="ui-button ui-state-default ui-corner-all">export</button>
		print """
		<select id="exptype" name="type" class="ui-button ui-state-default ui-corner-all" style="height:16px;font: italic 10px Times,Serif;border:thin solid silver;" >
			<option>pdf</option>
			<option>ps</option>
			<option>odg</option>
			<option>jpg</option>
			<option>png</option>
			<option value="tif">tiff</option>
			<option>svg</option>
			<option>xml</option>
		</select>
		</form>
		"""


	

	def printfeaturedialog():
		print """
		<div id="dialog"  style="display: none;" title="Features">
			<form method="post" action="editor.cgi" id="featureform">
				
				<input type="hidden" id="eusername" name="username" value="">
				<input type="hidden" id="esentenceid" name="sentenceid" value="">
				<table id="featab" class="ui-widget ui-widget-content" style="width:100%">
					<thead>
						<tr class="ui-widget-header ">
							<th>Attribute</th>
							<th>Value</th>
						</tr>
					</thead>
					<tbody  id="featabody"></tbody>
				</table>
			</form>
		<div  style="font-size:10px;"><span id="sente">sentence</span></div>
		</div>
		"""


	##########################

	cgitb.enable()
	form = cgi.FieldStorage()
	#cachedir=path+'cache/'

	thisfile = os.environ.get('SCRIPT_NAME',".")

	action = None
	userdir = 'users/'
	#action, userconfig = login(form, userdir, thisfile, action)
	#adminLevel,username = int(userconfig["admin"]),userconfig["username"]
	#adminLevel,username = 0,"guest"

	test = isloggedin("users/")
	logint = form.getvalue("login",None)
	if logint == "logout":
		cookieheader = logout(userdir)
		print cookieheader
	else: cookieheader="rien"


	project = form.getvalue("project",None)
	if not project:
		print "something went seriously wrong: you got here without choosing a project first!!!"
		#try:project = config.projects[0]
		#except:print "something seriously wrong: can't find any projects"
	projectconfig = config.configProject(project) # read in the settings of the current project
	#{u'configuraration': {u'functionsfilename': u'deps.WCDG', u'categoriesfilename': u'tags.STTS', u'defaultfunction': u'ADV', u'defaultcategory': u'NN', u'defaultNumberSentences': u'50', u'newTree': u'nouvel arbre', u'erase': u'--ERASE--', u'root': u'ROOT', u'categoryindex': u'1', u'useFixedColorscheme': u'True', u'defaultUser': u'default', u'showAllTrees': u'True', u'ericfuncsfilename': u'ericfuncs.config', u'ericcatsfilename': u'ericcats.config', u'arboratorCache': u'cache'}, u'shown features': {u'0': u't', u'1': u'categories', u'2': u'lemma'}, u'evalutation scores': {u'words': u'10', u'governors': u'30', u'functions': u'30', u'categories': u'30', u'lemmas': u'0'}, u'visible to everyone': {u'0': u'guest'}}


		
	filename = form.getvalue("filename",None)
	filetype = form.getvalue("filetype",None)
	#if not filename:
		#filename="corpus/conll/test.conll.6.conll10"
		#filetype = "conll10"
		
	print "Content-Type: text/html\n" # blank line: end of headers
		
	######################   head    ###########################
	print "<html><head>"
	try :
		basefilename=filename.split("/")[-1]
		sentencenumber=int(basefilename.split(".")[-2])
		#simplefilename=".".join(basefilename.split(".")[:-2])

	except: 
		sentencenumber="unknown"
		#simplefilename=filename
		basefilename=filename
		#print """  <script type="text/javascript">top.location="uploader.cgi"</script></head><body>oh</body>"""
		#sys.exit("something's wrong")

	print """
	<title>Arborator - Quickedit - +"""+filename+"""</title>
	<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
	<script type="text/javascript" src="script/jquery.js"></script>
	<script type="text/javascript" src="script/raphael.js"></script>
	<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
	<script type="text/javascript" src="script/jsundoable.js"></script>
	<script type="text/javascript" src="script/arborator.draw.js"></script>
	<script type="text/javascript" src="script/arborator.edit.js"></script>
	<link href="css/arborator.css" rel="stylesheet" type="text/css">
	<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />

	<script type="text/javascript">editable=false;quickie=true;</script>

	</head>


	<body id="body">
	"""


	########################################### body #####################################


	printheader()

	################################ reactions after clicks/uploads



	#####################################  printing always:


	#print """<div class="ui-widget ui-widget-content ui-corner-all box">
	#{sentencenumber} sentences.
	#</div>""".format(sentencenumber=sentencenumber)

	#fcolors,ccolors = 
	config.jsDefPrinter(projectconfig)

	#if not useFixedColorscheme:
		#print """
		#<script type="text/javascript">
		#fcolors=""",
		#conll.conll2functioncolordico(filename)
		#print '</script>'

	print "\n"


	for i,s in conll.conll2sentences(filename):

		print '''<div style="margin:10px"><a class="toggler" href="#" nr="{nr}">{nr}: {sentence} </a></div>'''.format(sentence=s.encode("utf-8"),nr=i)

	
	print """
	<script type="text/javascript">
	numbersent=""",i,";"
	print "filename= '"+filename+"';"
	print "filetype= '"+filetype+"';"
	print "opensentence= '0';"
	print '</script>'


	printmenues()
	printfeaturedialog()


	#print """
		#<form method="post" action="editor.cgi" style="display: none;" id="editform" >
			#<input type="hidden" id="treeid" name="treeid" value="">
			#<input type="hidden" id="sentenceid" name="sentenceid" value="">
			#<input type="hidden" id="username" name="username" value="">
		#</form>
	#"""

	print """<div class="ui-widget ui-widget-content ui-corner-all box">
	<a href="uploader.cgi">View other corpus files</a>
	</div>"""



	if test != False and logint != "logout":
		userconfig, cookieheader = test
		print '<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">'
		print "logged in as",userconfig["realname"]
		print '<a href="'+thisfile+'?login=editaccount">edit the account '+userconfig["username"]+'</a>'
		print '<a href="'+thisfile+'?login=logout">logout</a>'
		if userconfig["username"] == "admin":print '<a href="'+thisfile+'?login=admin">Administration</a>'
		print "</div>"
		
	print '</body></html>'










