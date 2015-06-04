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



#import time, re, sha, Cookie,  sys,codecs
import os, cgitb, cgi,time, sys
#from xml.dom import minidom
#import arboratorsession, 
import config

sys.path.append('modules')
from logintools import login
from logintools import isloggedin
from logintools import logout


verbose=False
######################### functions

##############################################"




########################## default values

##########################

cgitb.enable()
form = cgi.FieldStorage()



#thisscript = os.environ.get('SCRIPT_NAME', '')

thisfile = os.environ.get('SCRIPT_NAME',".")
#.split("/")[-1]

action = None
userdir = 'users/'
#action, userconfig = login(form, userdir, thisfile, action)
#adminLevel,username = int(userconfig["admin"]),userconfig["username"]
#userid = xmlsqlite.username2userid(username)
#adminLevel,username = 0,"guest"

#project = form.getvalue("project",None)
#if not project:
	#try:project = config.projects[0]
	#except:print "something seriously wrong: can't find any projects"
#projectconfig = config.configProject(project) # read in the settings of the current project

#cachedir = projectconfig["configuration"]["cacheFolder"]+"/"


test = isloggedin("users/")
logint = form.getvalue("login",None)
if logint == "logout":
	cookieheader = logout(userdir)
	print cookieheader
else: cookieheader="rien"

print "Content-Type: text/html\n" # blank line: end of headers

######################   head    ###########################
#<link rel="stylesheet" type="text/css" href="css/ui.jqgrid.css">
#<script src="script/grid.locale-en.js" type="text/javascript"></script>
#<script src="script/jquery.jqGrid.min.js" type="text/javascript"></script>

print """
<html>
<head><title>Arborator: Vakyartha</title>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">

<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
<link href="css/vakyartha.css" rel="stylesheet" type="text/css">

<script type="text/javascript" src="script/jquery.js"></script>
<script type="text/javascript" src="script/raphael.js"></script>
<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
<script type="text/javascript">

treeid=0;

$(function () {
	//$('#dialog').load('surf.cgi');
	//$('#center').height( $(document).height() -37)
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
					//alert(treeid);
					$("#eraseNumber").attr("value",treeid);
					$("#erase").submit();
					}
				}
			});

	//readTable();

	});

dial = function (tid) {
	treeid=tid;
	$("#treeid").html("N°"+treeid);
	$('#dialog').dialog('open');
}

edit = function(tid,unam,sentenceid) {
	if (tid==-111) {alert("Holy shit! The parser gave no analysis...");return};
	if (tid==0 || tid==null) {alert("Holy shit! no tree id");return};
	$("#treeid").attr("value", tid );
	$("#sentenceid").attr("value", sentenceid );
	$("#username").attr("value", unam );
	$("#editform").submit();
}


startloading = function() {
	$("#sentext").html("Analyzing <br>"+$("#newsentence").attr("value")+"")
	$('#loading').show();
	//alert("*** "+$("#newsentence").attr("value")+"_"+$("input[name=analysis]:checked").val());
	$.post("uploadSentence.cgi", {"newsentence":$("#newsentence").attr("value"),"analysis":$("input[name=analysis]:checked").val()},
		function(results){
			$("#loading").hide();
			edit(results.treeid,'visitor',results.sentenceid);
			},
		"json").error(function() { alert("Holy shit! There was an error when parsing..."); $("#loading").hide();})
   
return false;

}

</script>
</head>
"""


########################################### body #####################################

print """<body id="body">
		
		<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
		<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/vakyarthaNano.png" border="0"></a>
			<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>Visiting Vākyārtha</span>
		</div>
		<div id="center" class="center" style="width:100%;font-size:.8em">
"""


################################ reactions after clicks/uploads



#####################################  printing always:


print """
<div class="ui-widget ui-widget-content ui-corner-all box">
<h3> Analyze sentence:</h3>
<form method="post" style="width:100%;" id="sentenceform" onSubmit="startloading();">

	<div style="width:100%;">sentence<input type="text" name="newsentence"  id="newsentence" style="width:100%;"/></div>
	<input type="radio" name="analysis" value="rhapsodie" checked/>parse French Rhapsodie style&nbsp;&nbsp;
	<input type="radio" name="analysis" value="frmg" /> parse French FRMG &nbsp;&nbsp;
	<input type="radio" name="analysis" value="no" />don't parse sentence &nbsp;&nbsp;
	<br><br>
	<div  style="text-align:center;">
		<input id="ad" name="ad" value="enter sentence" type="button" class="fg-button ui-state-default ui-corner-all" onClick="startloading();";>
	</div>
</form>

</div>
<div id="loading" style="text-align:center;display:none;"><p><img src="images/gears.gif" /><br><span id="sentext">Please Wait...</span></p></div>

<script type="text/javascript">
$("#newsentence").keyup(function(event){
  if(event.keyCode == 13){
    $("#ad").click();
  }
});
</script>


"""
#<div id="content" style="text-align:center;"><p>Blöd...</p></div>
#for pid,proj in xmlsqlite.projects():
	#print '<br/><h1><a href="surf.cgi?project='+str(pid)+'">'+proj+'</a></h1>'
	#print xmlsqlite.sentenceTable(111,username,project=pid,exo=exo,onlyUser=None).encode("utf-8") # ACHTUNG: adminlevel 111
	


print "<br/><br/> <br/> <br/>"

	#<div id="dialog" title="Confirmation" style="display: none;" >
		#<div class="ui-state-error ui-corner-all" style="margin: 40px;padding: 10pt 0.7em;">
			#<h1>Are you sure that you want to erase the analysis <span id="treeid"> </span>?</h1>
		#</div>
	#</div>

	#<form method="post" action="surf.cgi" style="display: none;" id="erase" >
		#<input type="hidden" id="eraseNumber" name="eraseNumber" value="">
	#</form>
	#<form method="post" action="surf.cgi" style="display: none;" id="filter" >
		#<input type="hidden" id="onlyUser" name="onlyUser" value="">
		#<input type="hidden" id="onlyExo" name="onlyExo" value="">
	#</form>
print """
	<form method="post" action="editor.cgi" style="display: none;" id="editform" >
		<input type="hidden" id="treeid" name="treeid" value="">
		<input type="hidden" id="sentenceid" name="sentenceid" value="">
		<input type="hidden" id="username" name="username" value="">
	</form>
"""
#print """</td></tr>
	#<tr height="12px"><td >
#"""


if test != False and logint != "logout":
	userconfig, cookieheader = test
	print '<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">'
	print "logged in as",userconfig["realname"]
	print '<a href="'+thisfile+'?login=editaccount">edit the account '+userconfig["username"]+'</a>'
	print '<a href="'+thisfile+'?login=logout">logout</a>'
	if userconfig["username"] == "admin":print '<a href="'+thisfile+'?login=admin">Administration</a>'
	print "</div>"
	
print '</body></html>'












