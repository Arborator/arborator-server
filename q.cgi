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


import os, cgitb, cgi,time, sys, glob
import config, conll, database

cgitb.enable()
#<script type="text/javascript" src="script/jquery.js"></script>
		#<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
#<script src="//code.jquery.com/jquery-1.10.2.js"></script>
#<script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>
#<script type="text/javascript" src="script/jquery-ui-1.11.4.custom.min.js"></script>
#<link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">
		#<script type="text/javascript" src="script/raphael.export.js"></script>

def printhtmlheader():
	print """<html><head>
		<title>Arborator – Quickedit</title>
		<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
		<script type="text/javascript" src="script/jquery.js"></script>
		<script type="text/javascript" src="script/raphael.js"></script>
		
		<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
		<script type="text/javascript" src="script/jquery.cookie.js"></script>
		
		<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
		
		<script type="text/javascript" src="script/arborator.draw.js"></script>
		<script type="text/javascript" src="script/q.js"></script>
		<script type="text/javascript" src="script/jsundoable.js"></script>
		<script type="text/javascript" src="script/colpick.js"></script>
		
		<link href="css/arborator.css" rel="stylesheet" type="text/css">
		<link href="css/colpick.css" rel="stylesheet" type="text/css">
	</head>"""
	
def printheadline():	
	print 	"""<body id="body">
			<div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
				<a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0" title="Arborator Main Page"></a>
				<img src="images/q.png" border="0" title="Arborator – Quickedit">
				<a style="position: fixed;right:1px;top:1px;right:5px;" id='help' title="restart the help animation"><img src="images/help.png" style="vertical-align: text-top" border="0">Help</a>
			</div>
			<div id="center" class="center" style="width:100%;float:right;top:0px;">
				<div id="trees">
			</div>
		"""

def printfooter():
	print "</div>"
	print '</body></html>'	
	
def printexport():
	print """
	<form method="post" action="convert_svg.cgi?project=quickie" name="ex" id="ex" style=" position:fixed;top:6px;right:30px;display:none;"  target="_blank">
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
	
def printforms():
	print """<div id="toggle" class="toggle" title="click here to show and hide the CoNLL input"></div>
	<div id="boxx" class="boxx">
		<div class="arrow" title="you can click here (or anywhere else outside the box) when you have finished editing the CoNLL format or sentence text area">⬌</div>
		<div id="textual" class="textual">Paste and edit CoNLL file below:
			<TEXTAREA NAME="conll" id="conll" title="Here you can paste and edit CoNLL files with 4, 10 or 14 columns" style="width:100%; height:400; background-image: url('images/conll10.png'); background-repeat: no-repeat; background-position: 95% bottom; ">1	faut	falloir	V	_	_	0	root	_	_
2	que	que	CS	_	_	1	obj	_	_
3	tu	tu	Cl	_	_	6	sub	_	_
4	me	me	Cl	_	_	6	obl	_	_
5	les	le	Cl	_	_	6	obj	_	_
6	donnes	donner	V	_	_	2	dep	_	_

1	c'	ce	Cl	_	_	2	sub	_	_
2	est	être	V	_	_	0	root	_	_
3	plus	plus	Adv	_	_	4	dep	_	_
4	simple	simple	Adj	_	_	2	pred	_	_</TEXTAREA>
	"""
	
	print """
	<div style='float:xxx;'>
	
		<div ><span style='float:left;'>additional functions</span> <input type='text' id='addfuncs'  style='width:100%' title='Here you can add additional functions that do not appear in the CoNLL data (space or comma separated) in order to make them appear in the drop down menu when editing.' >  </input></div>
		
		<div ><span style='float:left;'>additional POS tags</span> <input type='text' id='addcats'  style='width:100%;' title='Here you can add additional categories that do not appear in the CoNLL data (space or comma separated) in order to make them appear in the drop down menu when editing.' >  </input> </div>
		
		<div >or paste your sentences here:
		<TEXTAREA NAME="sentences" id="sentences"  title='Here you can provide unanalyzed textual data, one sentence per line. You can then interactively add the syntactic analysis of your sentences. This will erase all the existing trees'  style="width:100%; height:100;"></TEXTAREA>
		</div>
		
	</div>
	
	<div style='float:right;'>
		<img  id="style" src='images/style.png' border='0' title='style' style='top:0px;'> 
		
	</div>
	<div id="styledialog" title="Design your dependency tree" style="background-color: white;">
		<div id="stylefunctions" title="functions">
	
		</div>
		<div style='float:right;'>
			<input type="checkbox" id="styleconllcheck">include style information in CoNLL
		</div>
	</div>
	
	"""
	#print "" checked="checked"
	print ""
	print "<br>"
	print """"""
	print "</div></div>"

def printmenues():
	print """	
	<div id="funcform" style="display:none;position:absolute;">
		<form  method="post" id="func" name="func" >
			<select id="funchoice" class='funcmenu' onClick="changeFunc(event);" size=0 style="height:0; width:80px;"  >
			</select>
		</form>
	</div>
	<div id="catform" style="display:none;position:absolute;">
		<form  method="post" id="cat" name="cat" >
			<select id="catchoice" class='funcmenu' onClick="changeCat();"  size=0 style="height:0; width:80px;"  >
			</select>
		</form>
	</div>
	"""
	
def printdialogs():
	print """
	<div id="dialog" title="Confirmation" style="display: none;" >
		<div class="ui-state-error ui-corner-all" style="margin: 40px;padding: 10pt 0.7em;">
			<h2 id="question">Are you sure?</h2>
		</div>
	</div>
	<div id="b" class="rbubble" style="right: 650px;top: 44px; position: absolute;display:none;">Paste a CoNLL file content here</div>
	<div id="bb" class="rbubble" style="right: 650px;top: 533px;position: absolute;">Or paste the sentences you want to analyze here.<br/>One sentence per line.</div>
	<div id="bbb" class="lbubble" style="left: 400px;top: 400px;position: absolute;">As soon as you click anywhere else, the graph is updated and you can modify the dependencies by dragging one word over the other.</div>
	<div id="bbbb" class="lbubble" style="left: 400px;top: 35px;position: absolute;">You can export the graph in various formats by clicking on the green arrow.</div>
	
	"""

##############################################################################################"

def start():
	form = cgi.FieldStorage()
	thisfile = os.environ.get('SCRIPT_NAME',".")
	
	print "Content-Type: text/html\n" # blank line: end of headers

##############################################################################################"

if __name__ == "__main__":
	start()
	printhtmlheader()
	printheadline()
	printforms()
	printexport()
	printmenues()
	printdialogs()
	printfooter()
