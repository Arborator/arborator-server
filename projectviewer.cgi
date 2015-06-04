#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2011 Kim Gerdes
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
import config, conll

sys.path.append('modules')
from logintools import login
from logintools import isloggedin
from logintools import logout



##############################################"




########################## default values
verbose=False

######################### functions

def sizeofFile(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0: return "%3.1f%s" % (num, x)
        num /= 1024.0

def printheader():
	print """<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
		<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
			<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>Viewer &nbsp; {filename} &nbsp; {sentencenumber} sentences</span>
		</div>
		<div id="center" class="center" style="width:100%;font-size:1em">
		""".format(filename=filename, sentencenumber=sentencenumber)
	#print """<div class="arbortitle fg-toolbar ui-widget-header ui-helper-clearfix">
	#<a href='.' style='position: absolute;left:0px;'><img src="images/vakyarthaNano.png" border="0"></a>"""

	#if treeid and treeusername:streeid="N° "+str(treeid)+ " by "+treeusername
	#else:streeid="All annotations -- problem"

	#print "<span style='text-align:center;margin:0 auto;position: relative;top:0px;' id='sentinfo'>"+streeid+"</span></div></div>"

	#print '<form method="post" action="editor.cgi" name="save" id="save" class="nav" style="top:0px;right:150px;">'
	#print """
	#<input type="hidden" id="treeid" name="treeid" value='"""+treeid+"""'>
	#<input type="hidden" id="sentenceid" name="sentenceid" value='"""+sentenceid+"""'>
	#<input type="hidden" id="username" name="username" value='"""+username+"""'>
	#<input type="hidden" id="defaultC" name="defaultC" value="">
	#<a class="fg-button ui-state-default fg-button-icon-left ui-corner-all" style="float:left;height:19px;"  onclick="zoom();">
	#<span id="zzz" class="ui-icon ui-icon-zoomout"/>zoom</a>
	#"""
	#print """<input type="button" id="sav" name="sav" value="saved" style="width:80px;z-index:33;" class="fg-button ui-state-default ui-corner-all"  onClick="saveTree(false);">	"""
	#if userconfig["username"] == "admin":
		#print """<input type="button" id="sav" name="sav" value="save as" style="width:80px;z-index:33;" class="fg-button ui-state-default ui-corner-all"  onClick="openTable();">"""
		#print """<input type="button" id="prev" name="prev" value="⇽" style="width:40px;" class="fg-button ui-state-default ui-corner-all"  onClick="prevnext(-1);">"""
		#print """<input type="button" id="next" name="next" value="⇾" style="width:40px;" class="fg-button ui-state-default ui-corner-all"  onClick="prevnext(1);">	"""
	#print "^^^",defaultShow,deftreeid
	#if defaultShow in ["yes","difference","evaluation"] and deftreeid:
		#print """<input type="button" id="defaultComp" name="defaultComp" value="compare" style="width:80px;z-index:33;" class="fg-button ui-state-default ui-corner-all"  onClick="$('#defaultC').attr('value', 'yes' );submit()">"""
	#print """<input type="button" id="surf" name="surf" value="list" style="width:40px;" class="fg-button ui-state-default ui-corner-all"  onClick="window.location.href='surf.cgi'";">"""
	#print '</form>'

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


	
def printmenues():
	
	print """
	<div id="holder" style="background:white; position:relative;"> </div> 

	<div id="funcform" style="display:none;position:absolute;">
		<form  method="post" id="func" name="func" >
			<select id="funchoice" class='funcmenu' onClick="changeFunc();"  size=""" +str( len(projectconfig.functions))+""" style="height:"""+str( len(projectconfig.functions)*13.5)+"""px; width:80px;"  >"""
	for f in projectconfig.functions:
		print "<option style='color: "+projectconfig.funcDic[f]["stroke"]+";'>"+f+"</option>"	
	#for i,f in enumerate(projectconfig.functions+[projectconfig["configuration"]["erase"]]): 
		#print "<option style='color: #"+fcolors[i]+";'>"+f+"</option>"	
	
	print """
			</select>
		</form>
	</div>
	<div id="catform" style="display:none;position:absolute;">
		<form  method="post" id="cat" name="cat" >
			<select id="catchoice" class='funcmenu' onClick="changeCat();"  size=""" +str( len(projectconfig.categories))+""" style="height:"""+str( len(projectconfig.categories)*13.5)+"""px; " >"""

	for i,c in enumerate(projectconfig.categories): 
		print "<option style='color: #"+ccolors[i]+";'>"+c+"</option>"	
	
	print """
			</select>
		</form>
	</div>
	<div style="border-top:1px solid #EEE;">&nbsp;</div>	
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
#{u'configuration': {u'functionsfilename': u'deps.WCDG', u'categoriesfilename': u'tags.STTS', u'defaultfunction': u'ADV', u'defaultcategory': u'NN', u'defaultNumberSentences': u'50', u'newTree': u'nouvel arbre', u'erase': u'--ERASE--', u'root': u'ROOT', u'categoryindex': u'1', u'useFixedColorscheme': u'True', u'defaultUser': u'default', u'showAllTrees': u'True', u'directory': u'nvakyartha', u'url': u'http://localhost/nvakyartha/', u'ericfuncsfilename': u'ericfuncs.config', u'ericcatsfilename': u'ericcats.config', u'arboratorCache': u'cache'}, u'shown features': {u'0': u't', u'1': u'categories', u'2': u'lemma'}, u'evalutation scores': {u'words': u'10', u'governors': u'30', u'functions': u'30', u'categories': u'30', u'lemmas': u'0'}, u'visible to everyone': {u'0': u'guest'}}


	
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
<title>Arborator - Viewer - +"""+filename+"""</title>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<script type="text/javascript" src="script/jquery.js"></script>
<script type="text/javascript" src="script/raphael.js"></script>
<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
<script type="text/javascript" src="script/jsundoable.js"></script>
<script type="text/javascript" src="script/vakyartha.draw.js"></script>
<script type="text/javascript" src="script/vakyartha.edit.js"></script>
<link href="css/arborator.css" rel="stylesheet" type="text/css">
<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />

<script type="text/javascript">editable=false;conllview=true;</script>

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










