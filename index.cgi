#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2008-2015 Kim Gerdes
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

import cgitb, cgi, os, sys
sys.path.append('modules')
from logintools import isloggedin
from logintools import logout
from lib import config
thisfile = os.environ.get('SCRIPT_NAME',"index.cgi").split("/")[-1]
cgitb.enable()
form = cgi.FieldStorage()

thisfile = os.environ.get('SCRIPT_NAME',".")
userdir = 'users/'

logint = form.getvalue("login",None)
if logint == "logout":
	print logout(userdir) # printing cookie header. important!
	print "Content-Type: text/html\n" # blank line: end of headers
	print '<img src="images/arboratorNano.png" border="0"> Logging out...'
	print '''<script type="text/javascript">setTimeout('window.location.href=".";',1000)</script>'''
	sys.exit()
project = form.getvalue("project",None)
if project: 
	try:	project=project.decode("utf-8")
	except:	pass
if len(config.projects)==1:project=config.projects[0]

action = form.getvalue("action",None)
if action:
	action=action.decode("utf-8")
	if action.startswith("project_"):project=action[8:]
if project: action="project_"+project

logintest = isloggedin(userdir)
if logintest:
	userconfig = logintest[0]
#action, userconfig = login(form, userdir, thisfile, action)
	adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"],userconfig["realname"]
else:
	#adminLevel, username, realname = 0,"guest","guest"
	adminLevel, username, realname = 0,None,None
print "Content-Type: text/html\n" # blank line: end of headers

projectconfig=None
try:	projectconfig = config.configProject(project) # read in the settings of the current project
except:	pass

######################   head    ###########################

print """
<html>
<head><title>Arborator</title>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">

<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
<link href="css/arborator.css" rel="stylesheet" type="text/css">
<link rel="icon" type="image/png" href="favicon.ico">
<script type="text/javascript" src="script/jquery.js"></script>
<script type="text/javascript" src="script/raphael.js"></script>
<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>

<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-11144858-1']);
  _gaq.push(['_setDomainName', '.ilpga.fr']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
  
var BrowserDetect = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera",
			versionSearch: "Version"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			   string: navigator.userAgent,
			   subString: "iPhone",
			   identity: "iPhone/iPod"
	    },
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};
BrowserDetect.init();

</script></head>
"""

########################################### body #####################################

print """

<body id="body">

<div class="arbortitle fg-toolbar ui-widget-header ui-helper-clearfix">
	<a href='.' style='position: absolute;left:0px;'><img src="images/arboratorNano.png" border="0"></a>
	<span style='text-align:center;margin:0 auto;position: relative;top:0px;' id='sentinfo'>Welcome to the Arborator website!</span>
</div>
"""

if os.path.exists("sitemessage.html"):print open("sitemessage.html").read()

if project :
	print '<form method="post" action="project.cgi" name="enter" id="enter" class="nav" style="top:4px;right:220px;z-index: 9999;">'
	if logintest and logint != "logout" : buttonname="Enter"# enter
	else: buttonname="Login"
	print (u"""<input type="button" id="ent" name="ent" value="{buttonname}" style="width:80px;" class="fg-button ui-state-default ui-corner-all"  onClick="window.location.href='project.cgi?project={project}'">""".format(project=project.replace("'","\\'").replace('"','\\"'), buttonname=buttonname)).encode("utf-8")
	#print """<input type="button" id="visit" name="ent" value="Visit" style="width:80px;" class="fg-button ui-state-default ui-corner-all" onClick="window.location.href='visit.cgi'";">"""

	print "</form>"

print """
<div id="dialog" style="display: none;width:500px" title="Login">
</div>
"""

print """<div class='center'>
	<div class="ui-widget ui-widget-content ui-corner-all" style="font-size:23px;margin-top:37px;padding:10px">
	
	<div style="text-align:center;">
		<object height="300" width="500" data="images/arborator.svg" type="image/svg+xml"></object>
	
	
"""

print """<p style="text-align:center;">The Arborator software is aimed at collaboratively annotating dependency corpora.</p>
	<div class='ui-state-highlight ui-corner-all' style='padding: 1em; margin: 20px;clear: both;'><a href='q.cgi'><img src="images/q.png" border="0"><br/>Quick access without login:<br/>Simple graphical editor of CoNLL files</a></div>

	<div class="ui-state-highlight ui-corner-all" style="padding-bottom: 1em; margin: 20px;">"""
	
if project or len(config.projects)==1:
	try:
		projectconfig = config.configProject(project) # read in the settings of the current project
	except:
		print "some problem with the configuration of the project",project.encode("utf-8")
		
	finally:
		print "this page gives acces to the <b>",project.encode("utf-8"),"</b> annotation project.<br/>"
		print '<form method="post" action="project.cgi" name="enter" id="enter2">'
		if logintest and logint != "logout" : buttonname="Enter"# enter
		else: buttonname="Login"
		print (u"""C'mon in: Click on <input type="button" id="ent" name="ent" value="{buttonname}"  style="font:normal .8em Arial;padding-top: 2px;width:80px;" class="fg-button ui-state-default ui-corner-all"  onClick="window.location.href='project.cgi?project={project}'">""".format(project=project.replace("'","\\'").replace('"','\\"'),buttonname=buttonname)).encode("utf-8")
		print "</form>"
		if len(config.projects)>1: print "<p><small><a href='.?project='>For access to other annotation projects on this site click here</a></small></p>"
else:
	print '<div>Please choose your annotation project:</div>'
	for project in sorted(config.projects):
		if os.path.exists(("projects/"+project+"/"+project+".png").encode("utf-8")):img=u"<img class='project_logo' src='projects/"+project+"/"+project+u".png' align='top'>"
		else: img=""
		print 	'<div class="ui-widget ui-widget-content ui-corner-all" style="float:left;margin:1.2em;"><p>',
		if logintest:
			print (u'<a href="project.cgi?project={project}">{img} {project}'.format(project=project, img=img)).encode("utf-8"),
		else:
			print (u'<a href="?project={project}">{img} {project}'.format(project=project, img=img)).encode("utf-8"),
		print '</a></p></div>'
		#print '<div style="clear: both;"></div>'
	
	print '<div style="clear: both;"></div>'


print "</div><div class='ui-state-highlight ui-corner-all' style='padding: 1em; margin: 20px;clear: both;'><a href='https://github.com/kimgerdes/arborator/wiki'>Short usage guide (wiki page)</a></div>"


#print """<br/><br/>

	#<table style="text-align:center;width:100%:background:none;"><tr><td>
	#<div class="ui-widget ui-widget-content ui-corner-all" ><p><a href='http://arborator.ilpga.fr'><img border="0" src="images/arboratorNano.png"><br>The Arborator website</a></p></div>
	#</td><td>
	#<div class="ui-widget ui-widget-content ui-corner-all" ><p>The French user and annotation guide:<br><a href='http://arborator.ilpga.fr/wiki' >Guide d'annotation</a></p></div>
	#</td><td>
	#<div class="ui-widget ui-widget-content ui-corner-all" ><p><a href='http://rhapsodie.ilpga.fr/'><img border="0" src="images/rhapsodie.png"><br>The Rhapsodie project's syntax site</a></p></div>

	
	#</td></tr></table>
	



#&nbsp;
#""" <img border='0' src='images/firefox.png' align='middle'> 

print '''</div></div><br/>
<div class='ui-widget ui-widget-content ui-corner-all' style='padding: 2em; margin-left: 199px; margin-right: 199px;clear: both;text-align:center;position: relative;'>
	<p style="font-size:.7em;margin:1;">
		<img border="0" src="images/arboratorNano.png" align='middle'>
Arborator is free software.
	</p><br><hr>
	<table style='margin-top:0;width:100%'><tr><td>
	<p style="font-size:.7em;margin:1;">
	<a href="http://www.gnu.org/licenses/agpl-3.0.html">
It is realeased under the 
	</p> <p style="font-size:.7em;margin:1;">
	
		<img src="images/Affero_General_Public_License_3.png" align='middle'>
licence
	</td>
	
	</tr>
	</table></a></p> <p style="font-size:.7em;margin:1;">   
It can <a href="http://rhapsodie.ilpga.fr/wiki/Arborator#site_administration_and_installation">easily be installed on any Apache server.</a>
	</p><p style="font-size:.7em;margin:1;">
This software relies on your browser's SVG capacity and is written principally for use in the 
	<img border="0" src="images/firefox.grey.png" align='middle'> 
Firefox browser.
	<br><br>
	<script>
		if (BrowserDetect.browser=="Firefox") document.write("You are using Firefox "+BrowserDetect.version+" on "+BrowserDetect.OS+". Everything should work fine.");
		else if (BrowserDetect.browser=="Chrome") document.write("You are using Chrome "+BrowserDetect.version+" on "+BrowserDetect.OS+". This Browser is not fully tested.");
		else document.write("You are using an unsupported browser ("+BrowserDetect.browser+" "+BrowserDetect.version+" on "+BrowserDetect.OS+"). Arborator is fully functional only on Firefox.");
	</script>
</p>
<br>
<div class="ui-widget ui-widget-content ui-corner-all"  style='
font:italic normal .8em/1em Times, serif;text-align:center;margin:0 auto;padding:1em;'>
	written by <a href='http://gerdes.fr'>Kim Gerdes</a><br/><br/>
	<a href='http://www.univ-paris3.fr/'>Sorbonne nouvelle</a>,
	<a href='http://ilpga.fr/'>ILPGA</a>,
	<a href='http://lpp.univ-paris3.fr/'>LPP</a>
	(<a href='http://lpp.univ-paris3.fr/'>CNRS</a>)
	
	<br><br>
	
	<a href="https://github.com/kimgerdes/arborator"><img style="position: absolute; top: 0; right: 0; border: 0;" src="images/forkme.png" alt="Fork me on GitHub"></a>

</div>
</div>



'''
#	<a href='http://english.cas.cn/'>Chinese Academy of Sciences</a>,
#	<a href='http://english.ia.cas.cn/'>Institute of Automation</a>,
#	<a href='http://nlpr-web.ia.ac.cn/'>NLPR</a>
#
#<td>
#</a></p> <p style="font-size:.7em;margin:1;">
#<a href="https://launchpad.net/arborator">
#downloadable on
#</p> <p style="font-size:.7em;margin:1;"> 
	#<img src="images/launchpad.png"  align='bottom'></p>
#</td>

print " <br><br>"

if username:
	
	print '<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">'
	print "logged in as",username
	print '&nbsp;&nbsp;&nbsp;<a href="'+thisfile+'?login=logout">logout</a>'
	if username!="guest":
		
		print '&nbsp;&nbsp;&nbsp;<a href="'+thisfile+'?login=editaccount">edit the account '+username+'</a>'
	if adminLevel > 1: print '&nbsp;&nbsp;&nbsp;<a href="'+thisfile+'''?login=admin">User Administration</a>''' # &nbsp;&nbsp;&nbsp;<a href="admin.cgi">Corpus Administration</a>
	print "</div>"

	#if userconfig["username"] == "admin":print '<a href="'+thisfile+'?login=admin">Administration</a>'

print '</body></html>'
