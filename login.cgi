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
import os, cgitb, cgi,time, sys, glob
import config, database 

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

#print "Content-Type: text/html\n" # blank line: end of headers

#thisscript = os.environ.get('SCRIPT_NAME', '')

thisfile = os.environ.get('SCRIPT_NAME',".")
#.split("/")[-1]

action = None
userdir = 'users/'
test = isloggedin("users/")
logint = form.getvalue("login",None)
if logint == "logout":
	#cookieheader = 
	print logout(userdir)
	#print "Content-Type: text/html\n" # blank line: end of headers
	#print ")))))))))))))))))))"
	print '<script type="text/javascript">window.location.href=".";</script>'
#else: cookieheader="rien"



#adminLevel,username = 0,"guest"


project = form.getvalue("project",None)

#project="Rhapsodie"
projectconfig=None
try:
	projectconfig = config.configProject(project) # read in the settings of the current project
except:
	pass
if not projectconfig:
	print "Content-Type: text/html\n" # blank line: end of headers
	print "something went seriously wrong: can't read the configuration of the project",project
	#print "Content-Type: text/html\n" # blank line: end of headers
	print '<script type="text/javascript">window.location.href=".";</script>'
	sys.exit("something's wrong")



action, userconfig = login(form, userdir, thisfile+'?project='+project, action)
adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"],userconfig["realname"]

#cachedir = projectconfig["configuration"]["cacheFolder"]+"/"

sql=database.SQL(project)
userid = sql.userid(username, realname)
#realname = sql.realname(username)


######################   head    ###########################
#print "Content-Type: text/html\n" # blank line: end of headers


print """
<html>
	<head><title>Arborator - {project} Project</title>
	<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
	<script type="text/javascript" src="script/jquery.js"></script>
	<script type="text/javascript" src="script/raphael.js"></script>
	<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
	<script type="text/javascript" src="script/jquery.fileupload-ui.js"></script>
	<script type="text/javascript" src="script/jquery.fileupload.js"></script>
	<link href="css/arborator.css" rel="stylesheet" type="text/css">
	<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
	<link rel="stylesheet" type="text/css" href="css/jquery.fileupload-ui.css" media="screen" />""".format(project=project)
print """
	<script type="text/javascript">	
	edit = function(textid) {
		$("#textid").attr("value", textid );
		$("#username").attr("value", "moi" );
		$("#editorform").submit();
	}
	</script>
	<script src="script/upload.js"></script>
</head>
"""

#


########################################### body #####################################

print """<body id="body">
		<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
		<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
			<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>{project} Project</span>
		</div>
		<div id="center" class="center" style="width:100%;font-size:.8em">
""".format(project=project)


################################ reactions after clicks/uploads
if login:
	
	print "ooooooooooooooooooooooooooooooooooooooo o"*55
	print '<script type="text/javascript">window.location.href="project.cgi?project={project}";</script>'.format(project=project)
else:
	print "uuuuuuuuuuu"*55
print '</body></html>'










