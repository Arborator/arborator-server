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


import os, cgitb, cgi, time, sys, glob, codecs
sys.path.append('modules')
from logintools import login
from logintools import isloggedin
from logintools import logout
from lib import config


verbose=False
######################### functions

def sizeofFile(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


##############################################"




########################## default values

##########################

cgitb.enable()
form = cgi.FieldStorage()
project = form.getvalue("project",None)
if project: project =project.decode("utf-8")
if not project:
	try:project = config.projects[0]
	except:print "something seriously wrong: can't find any projects"
projectconfig = config.configProject(project) # read in the settings of the current project
cachedir = projectconfig["configuration"]["corpusfolder"]+"/"

#thisscript = os.environ.get('SCRIPT_NAME', '')

thisfile = os.environ.get('SCRIPT_NAME',".")
#.split("/")[-1]

action = None
userdir = 'users/'
#action, userconfig = login(form, userdir, thisfile, action)
#adminLevel,username = int(userconfig["admin"]),userconfig["username"]
#userid = xmlsqlite.username2userid(username)
#adminLevel,username = 0,"guest"

test = isloggedin("users/")
logint = form.getvalue("login",None)
if logint == "logout":
	cookieheader = logout(userdir)
	print cookieheader
else: cookieheader="rien"

print "Content-Type: text/html\n" # blank line: end of headers
#<script type="text/javascript" src="script/raphael.js"></script>

######################   head    ###########################


print """
<html>
<head><title>Arborator: File uploader</title>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<script type="text/javascript" src="script/jquery.js"></script>
<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
<script type="text/javascript" src="script/jquery.fileupload-ui.js"></script>
<script type="text/javascript" src="script/jquery.fileupload.js"></script>
<link href="css/arborator.css" rel="stylesheet" type="text/css">
<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
<link rel="stylesheet" type="text/css" href="css/jquery.fileupload-ui.css" media="screen" />


<script type="text/javascript"></script>
</head>
"""


########################################### body #####################################
print '<body id="body">'
print """<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
		<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
		<a href='project.cgi?project={project}' style='position: fixed;left:120px;top:5px'>{project} Annotation Project</a>
			<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>Uploader</span>
		</div>
		<div id="center" class="center" style="width:100%;font-size:1em">
		""".format(project=project.encode("utf-8"))


################################ reactions after clicks/uploads



#####################################  printing always:


print """
<form method="post" action="viewer.cgi" style="display: none;" id="fileform" >
        <input type="hidden" id="filename" name="filename" value="">
        <input type="hidden" id="filetype" name="filetype" value="">
        <input type="hidden" id="project" name="project" value="{project}">
</form>""".format(project=project.encode("utf-8"))

print """<div class="ui-widget ui-widget-content ui-corner-all box">
<div id="file_upload" class="file_upload">
	<table id="files">
	<tbody>"""
	
print """	<tr>
	<div class="ui-widget ui-widget-content ui-corner-all box">	<h3> Upload analysis (CoNLL, text, ...)</h3>
		<form enctype="multipart/form-data" method="POST" action="uploadFile.cgi" class="file_upload">
			<input type="hidden" id="project" name="project" value="{project}">
			<input type="file" multiple="" name="files[]">
			<button type="submit">Upload</button>
			
			<br/><br/>
		
	
			<label><input name="type" type="radio" checked="checked" value="conll">Analysis Conll style</label>
			<label><input name="type" type="radio" value="sentline">A sentence per line</label>
			<label><input name="type" type="radio" value="standard" id="standardtext">Standard text:</label>
			
			<label class="standardtext"><input name="analyze" type="radio" value="no" class="standardtext">Don't analyze</label>
			<label class="standardtext"><input name="analyze" type="radio" value="english" class="standardtext">Analyze English</label>
			<label class="standardtext"><input name="analyze" type="radio" value="chinese" class="standardtext">Analyze Chinese</label>
			<label class="standardtext"><input name="analyze" type="radio" value="french" class="standardtext">Analyze French</label>
		</form>
	</div>	
</tr>
		
	
""".format(project=project.encode("utf-8"))
	
for infile in sorted(glob.glob(os.path.join("corpus/conll/", '*.*'))): #  os.path.join(foldername, '*.*')
	filename=os.path.basename(infile).decode("utf-8")
	try:
		f=codecs.open(infile,"r","utf-8")
	except Exception as e: 
		print "can't read",filename,"!\n <br>",e,"<br><br>"
		continue
	ns=1
	conll=None
	try:
		for li in f:
			if not li.strip():ns+=1
			elif not conll and "\t" in li:
				n = len(li.split("\t"))
				#print n,li.encode("utf-8"),"<br>"
				if n==4:	conll=4
				if n==10:	conll=10
				elif n==13:	conll=10 # orfeo file format: conll10 + begin, end, speaker
				elif n==14:	conll=14
		if not li.strip():ns-=1 # if last line empty, we counted one too much
	except:
		pass
	f.close()
	if conll:
		thumbnail="conll"+str(conll)+".png"
		filesize=sizeofFile(os.path.getsize(infile))
		
		
		href=projectconfig["configuration"]["url"]+u"corpus/conll/"+filename
		#print (u"é{r}".format(r=href)).encode("utf-8")
		print (u"""
		<tr data-id="{filename}" data-type="{datatype}">
			<td class="file_download_preview"><a target="_blank" href="{href}"><img src="images/{thumbnail}"></a></td>
			<td class="file_name"><a target="_blank" title="Table view of the original file" href="{href}">{simplefilename}</a></td>
			<td class="file_size">{size}</td>
			<td class="file_sentencenumber" colspan="2">{numbersentences} sentences.</td>
			<td class="file_view"><button onclick="enterDB(this)" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only" role="button" aria-disabled="false" title="Add to the database" style="height: 1.4em;width: 1.4em;"><span class="ui-button-icon-primary ui-icon ui-icon-upload"></span></button></td>
		</tr>""".format(filename=infile.decode("utf-8") ,datatype="conll"+str(conll) ,simplefilename=filename, href=href , size=filesize , thumbnail=thumbnail , numbersentences=ns )).encode("utf-8")
		

	else:	print "<tr>???",filename.encode("utf-8"),"couldn't read or strange datatype<br></tr>"
	#<td class="file_view"><button onclick="viewer(this)" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only" role="button" aria-disabled="false" title="Graphic view of this file" style="height: 1.4em;width: 1.4em;"><span class="ui-button-icon-primary ui-icon ui-icon-image"></span></button></td>

	# TODO: implement trashing files:
	#<td class="file_view"><button onclick="trash(this)" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only" role="button" aria-disabled="false" title="Trash the file" style="height: 1.4em;width: 1.4em;"><span class="ui-button-icon-primary ui-icon ui-icon-trash"></span><span class="ui-button-text">Start</span></button></td>
		
		
print """

        <tr style="display: none;" class="file_upload_template">
            <td class="file_upload_preview"></td>
            <td class="file_name"></td>
            <td class="file_size"></td>
            <td class="file_upload_progress"><div></div></td>
            <td class="file_upload_start"><button>Start</button></td>
            <td class="file_upload_cancel"><button>Cancel</button></td>
        </tr>
        <tr style="display: none;" class="file_download_template">
            <td class="file_download_preview"></td>
            <td class="file_name"><a></a></td>
            <td class="file_size"></td>
            <td class="file_sentencenumber"  colspan="2"></td>
            <td class="file_import"><button style="height: 1.4em;width: 1.4em;" title="Graphic view of this file" aria-disabled="false" role="button" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only" onclick="viewer(this)"><span class="ui-button-icon-primary ui-icon ui-icon-image"></span><span class="ui-button-text">Start</span></button></td>
            <td class="file_view"><button style="height: 1.4em;width: 1.4em;" title="Add to the database" aria-disabled="false" role="button" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-icon-only" onclick="enterDB(this)"><span class="ui-button-icon-primary ui-icon ui-icon-upload"></span><span class="ui-button-text">Start</span></button></td>

        </tr>
    </tbody>
    </table>
<script type="text/javascript" src="script/upload.js"></script>
"""
#<td colspan="2" class="file_sentencenumber"></td>






print "</div></div>"














if test != False and logint != "logout":
	userconfig, cookieheader = test
	print '<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">'
	print "logged in as",userconfig["realname"]
	print '<a href="'+thisfile+'?login=editaccount">edit the account '+userconfig["username"]+'</a>'
	print '<a href="'+thisfile+'?login=logout">logout</a>'
	if userconfig["username"] == "admin":print '<a href="'+thisfile+'?login=admin">Administration</a>'
	print "</div>"
	
print '</body></html>'










