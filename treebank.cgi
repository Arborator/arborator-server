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
#from xml.dom import minidom
#import arboratorsession, 
#import xmlsqlite
import conll
import config

sys.path.append('modules')
from logintools import login
from logintools import isloggedin
from logintools import logout


verbose=False
######################### functions

def sizeofFile(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0: return "%3.1f%s" % (num, x)
        num /= 1024.0


##############################################"




########################## default values

##########################

cgitb.enable()
form = cgi.FieldStorage()

#cachedir=path+'cache/'

thisfile = os.environ.get('SCRIPT_NAME',".")

project = form.getvalue("project",None)
if not project:
	try:project = config.projects[0]
	except:print "something seriously wrong: can't find any projects"
projectconfig = config.configProject(project) # read in the settings of the current project

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

filename = form.getvalue("filename",None)
filetype = form.getvalue("filetype",None)

print "Content-Type: text/html\n" # blank line: end of headers

######################   head    ###########################
print "<html><head>"
try :
        basefilename=filename.split("/")[-1]
        sentencenumber=int(basefilename.split(".")[-2])
        simplefilename=".".join(basefilename.split(".")[:-2])

except: print """  <script type="text/javascript">top.location="uploader.cgi"</script>"""

#<script type="text/javascript" src="script/jquery.scrollTo-min.js"></script>

print """
<title>Arborator: Vākyārtha - Treebank Surfer - +"""+simplefilename+"""</title>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">



<script type="text/javascript" src="script/jquery.js"></script>
<script type="text/javascript" src="script/raphael.js"></script>
<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>

<script type="text/javascript" src="script/vakyartha.draw.js"></script>

<link href="css/vakyartha.css" rel="stylesheet" type="text/css">
<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />


<script type="text/javascript">

var tokens=new Object();

getTree = function(id, nr, type) {
        delete tokens;
        tokens=new Object();
        $.getJSON(
	      "getTreeFromFile.cgi",
	      {
		    id: id,
		    nr: nr,
		    type: type
	      },
	      function(data)
		    {
				$.each(data, function(key, val) {
				        tokens[key]=val;
				});

			  start("holder"+nr);
			  // $.scrollTo( $("#holder"+nr).prev().prev(), 1000);
		    }
        );

        
}

makeEditable = function(id, nr, type) 
{
	for (var i in shownfeatures) 
			{	
			var f = shownfeatures[i];
			$("."+f).click(function()
				{
				alert($(this).attr("class"));
				//get(0).
				});
			}
}
</script>
</head>
"""
 #function(data) {
	      #alert("oooooo"+tokens+data);
	      #$.each(data.items, function(i,item){
	      #alert(i);
	      #tokens[i]=item;

	      #});
	      #alert("oooooo"+tokens);
        #}
        #).error(function() { alert("error reading tree data"); })
#$.ajaxSetup({"error":function(XMLHttpRequest,textStatus, errorThrown) {
      #alert(textStatus);
      #alert(errorThrown);
      #alert(XMLHttpRequest.responseText);
  #}});
#<script type="text/javascript" src="script/vakyartha.dependency.min.js"></script>

#<script type="text/javascript" src="script/jquery-1.4.2.min.js"></script>
#<script src="script/raphael-min.js" type="text/javascript"></script>
#<script src="script/vakyartha.dependency.min.js" type="text/javascript"></script>
#<link rel="stylesheet" type="text/css" href="css/jquery.fileupload-ui.css" media="screen" />


########################################### body #####################################

print """<body id="body">
		
		<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
		<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/vakyarthaNano.png" border="0"></a>
			<span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>Treebank Surfer &nbsp; {simplefilename} &nbsp; {sentencenumber} sentences</span>
		</div>
		<div id="center" class="center" style="width:100%;font-size:1em">
""".format(simplefilename=simplefilename, sentencenumber=sentencenumber)


################################ reactions after clicks/uploads



#####################################  printing always:


#print """<div class="ui-widget ui-widget-content ui-corner-all box">
#{sentencenumber} sentences.
#</div>""".format(sentencenumber=sentencenumber)

config.jsDefPrinter(projectconfig)

#if not useFixedColorscheme:
print """
<script type="text/javascript">
fcolors=""",
conll.conll2functioncolordico(filename)
print '</script>'

#{"suj":"06713e","objd":"0ce27c","compnom":"1353ba","prép":"19c4f8","dét":"203636","épi":"d14c47"} // you can define default colors for syntactic functions

#print conll.conll2tree(filename,219)
#fcolors = 

for i,s in conll.conll2sentences(filename):

        print '''<div style="margin:10px"><a class="toggler" href="#" nr="{nr}">{nr}: {sentence} </a></div>'''.format(sentence=s.encode("utf-8"),nr=i)

 
		    #$.scrollTo( $("#holder"+$(this).attr("nr")).prev().prev(), 2000);

 #$(this).after('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a id="edit'+nr+'" class="fadehover"><img src="images/edit.png" border="0" align="middle" class="a"><img src="images/editcolor.png" border="0" align="middle" class="b"></a>')

		    #$("img.a").hover(
			  #function() {
				#$(this).stop().animate({"opacity": "0"}, "slow");
			  #},
			  #function() {
				#$(this).stop().animate({"opacity": "1"}, "slow");
			  #});
			#$("img.a").click(
			  #function() {  
				#makeEditable()
				#$("img.a").attr({"opacity": "1"});
				#alert("u");
			  #});
		    
print """
<script type="text/javascript">
$(".toggler").click(function()
        {
	      if (!$(this).hasClass("expanded"))
	      {
		    
		    var nr=$(this).attr("nr")
		    
		    $(this).parent().after('<div id="holder'+nr+'" class="svgholder"> </div>');
		    getTree('"""+filename+"""',nr,'"""+filetype+"""');
		  
		    
	      }
	      else
	      {
		    $("#holder"+$(this).attr("nr")).remove();
		    $("#edit"+$(this).attr("nr")).remove();
	      }
	      $(this).toggleClass('expanded');
        });



$(".toggler:last").click();


</script>
"""

#$("holder"+$(this).attr("nr")).css("border","13px solid red");
#alert('clicked: '+ $(this).attr("nr"));


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










