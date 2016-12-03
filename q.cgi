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
from lib import config, conll, database
cgitb.enable()

def printhtmlheader():
	print """<html><head>
		<title>Arborator – Quickedit</title>
		<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
		
	
		
		<script type="text/javascript" src="script/jquery.js"></script>
		<script type="text/javascript" src="script/raphael.js"></script>
		
		<script type="text/javascript" src="script/jquery-ui-1.8.18.custom.min.js"></script>
		<script type="text/javascript" src="script/jquery.cookie.js"></script>
		
		<link rel="stylesheet" type="text/css" href="css/jquery-ui-1.8.18.custom.css" media="screen" />
		
		<script type='text/javascript' > 
		var currentsvg = "mmmm"; 
		</script>
		<script type="text/javascript" src="script/arborator.draw.js"></script>
		<script type="text/javascript" src="script/q.js"></script>
		<script type="text/javascript" src="script/jsundoable.js"></script>
		<script type="text/javascript" src="script/colpick.js"></script>
		
		<link href="css/arborator.css" rel="stylesheet" type="text/css">
		<link href="css/colpick.css" rel="stylesheet" type="text/css">

		
		<script type="text/javascript" src="annodoc/jquery.svg.min.js"></script>
		<script type="text/javascript" src="annodoc/jquery.svgdom.min.js"></script>
		<script type="text/javascript" src="annodoc/jquery.timeago.js"></script>
		<script type="text/javascript" src="annodoc/jquery-ui.min.js"></script>
		<script type="text/javascript" src="annodoc/waypoints.min.js"></script>
		<script type="text/javascript" src="annodoc/jquery.address.min.js"></script>

		<!--brat helper modules-->
		<script type="text/javascript" src="annodoc/configuration.js"></script>
		<script type="text/javascript" src="annodoc/util.js"></script>
		<script type="text/javascript" src="annodoc/annotation_log.js"></script>
		
		<!--<script type="text/javascript" src="annodoc/webfont.js"></script>-->
		<!--brat modules-->
		<script type="text/javascript" src="annodoc/dispatcher.js"></script>
		<script type="text/javascript" src="annodoc/url_monitor.js"></script>
		<script type="text/javascript" src="annodoc/visualizer.js"></script>

		// embedding configuration
		<script type="text/javascript" src="annodoc/config.js"></script>
		// project-specific collection data
		<script type="text/javascript" src="annodoc/collections.js"></script>

		// NOTE: non-local libraries
		<script type="text/javascript" src="annodoc/annodoc.js"></script>
		<script type="text/javascript" src="annodoc/conllu.js"></script>
				
		<link rel="stylesheet" href="annodoc/font-awesome.min.css">
		<link rel="stylesheet" type="text/css" href="annodoc/style.css"/>
		<link rel="stylesheet" type="text/css" href="annodoc/style-vis.css"/>
		<link rel="stylesheet" type="text/css" href="annodoc/hint.css"/>
		
		
		
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
	#print """
	#<p>The <code>acl:relcl</code> relation is used for relative clauses modifying
#a nominal. The relation points from the head of the nominal to the
#head of the relative clause.</p>



#<div class="annodoc">
#<pre><code class="language-conllu"># I wrote the letter with a quill.
#1  donner  donner  VERB  _  VerbForm=Inf  0  root  _  give
#2  les  le  DET  _  Definite=Def|Number=Plur  3  det  _  the
#3  jouets  jouet  NOUN  _  Gender=Masc|Number=Plur  1  dobj  _  toys
#4  à  à  ADP  _  _  6  case  _  to
#5  les  le  DET  _  Definite=Def|Number=Plur  6  det  _  the
#6  enfants  enfant  NOUN  _  Gender=Masc|Number=Plur  1  nmod  _  children
#</code></pre>


#<pre><code class="language-sdparse">J'ai vu l' homme qui t' aime \\n I saw the man who loves you
#acl:relcl(homme, aime)
#nsubj(aime, qui)
#dobj(aime, t')
#</code></pre>



#<pre><code class="language-conllu"># I wrote the letter with a quill.
#1   Я         ja         PRON   _   Case=Nom|Number=Sing|Person=1|PronType=Prs        2   nsubj   _   I
#2   написал   napisat'   VERB   _   Gender=Masc|Number=Sing|VerbForm=Part|Voice=Act   0   root    _   wrote
#3   письмо    pis'mo     NOUN   _   Case=Acc|Gender=Neut|Number=Sing                  2   dobj    _   the-letter
#4   пером     pero       NOUN   _   Case=Ins|Gender=Neut|Number=Sing                  2   nmod    _   with-a-quill
#</code></pre>




#</div>


	#"""
	
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
	print """
	<div id="toggleAndBoxx" class="toggleAndBoxx">
	<div id="toggle" class="toggle" title="click here to show and hide the CoNLL input"></div>
	<div id="boxx" class="boxx">
		<div class="arrow" title="you can click here (or anywhere else outside the box) when you have finished editing the CoNLL format or sentence text area">⬌</div>
		<div id="textual" class="textual">Paste and edit CoNLL file below:
			<TEXTAREA NAME="conll" id="conll" title="Here you can paste and edit CoNLL files with 4, 10 or 14 columns" style="width:100%; height:400; background-image: url('images/conll10.png'); background-repeat: no-repeat; background-position: 95% bottom; "># conllu format
1	faut	falloir	V	_	_	0	root	_	must
2	que	que	C	_	_	4	mark	_	that
3	tu	tu	Pron	_	_	4	nsubj	_	you
4	fasses	faire	V	_	_	1	ccomp	_	make
5	envie	envie	N	_	_	4	dobj	_	desire
6-7	aux	aux	P+D	_	_	_	_	_	to_the
6	à	à	P	_	_	8	case	_	to
7	les	le	D	_	_	8	det	_	the
8	enfants	enfant	N	_	_	4	iobj	5:nmod	kids
9	de	de	P	_	_	10	mark	_	to
10	faire	faire	V	_	_	5	ccomp	_	make
11-12	du	du	P+D	_	_	_	_	_	of_the
11	de	de	P	_	_	13	case	_	of
12	le	le	D	_	_	13	det	_	the
13	bruit	bruit	N	_	_	10	dobj	_	noise

# conllu format using SpaceAfter=No
1	Can	can	AUX	MD	VerbForm=Fin	3	aux	_	_
2	you	you	PRON	PRP	Case=Nom|Person=2|PronType=Prs	3	nsubj	_	_
3	use	use	VERB	VB	VerbForm=Inf	0	root	_	_
4	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
5	'	'	PUNCT	``	_	6	punct	_	SpaceAfter=No
6	find	find	VERB	VB	VerbForm=Inf	10	compound	_	_
7	my	my	PRON	PRP$	Number=Sing|Person=1|Poss=Yes|PronType=Prs	8	nmod:poss	_	_
8	phone	phone	NOUN	NN	Number=Sing	6	dobj	_	SpaceAfter=No
9	'	'	PUNCT	''	_	6	punct	_	_
10	feature	feature	NOUN	NN	Number=Sing	3	dobj	_	_
11	to	to	PART	TO	_	12	mark	_	_
12	track	track	VERB	VB	VerbForm=Inf	3	advcl	_	_
13	someone	someone	NOUN	NN	Number=Sing	16	nmod:poss	_	_
14	else	else	ADJ	JJ	Degree=Pos	13	amod	_	SpaceAfter=No
15	's	's	PART	POS	_	13	case	_	_
16	phone	phone	NOUN	NN	Number=Sing	12	dobj	_	SpaceAfter=No
17	?	?	PUNCT	.	_	3	punct	_	_

# I wrote the letter with a quill.
1	Я	ja	PRON	_	Case=Nom|Number=Sing|Person=1|PronType=Prs	2	nsubj	_	I
2	написал	napisat'	VERB	_	Gender=Masc|Number=Sing|VerbForm=Part|Voice=Act	0	root	_	wrote
3	письмо	pis'mo	NOUN	_	Case=Acc|Gender=Neut|Number=Sing	2	dobj	_	the-letter
4	пером	pero	NOUN	_	Case=Ins|Gender=Neut|Number=Sing	2	nmod	_	with-a-quill</TEXTAREA>
	"""
	
	print """
	<div style='float:xxx;'>
	
		<div ><span style='float:left;'>additional functions</span> <input type='text' id='addfuncs'  style='width:100%' title='Here you can add additional functions that do not appear in the CoNLL data (space or comma separated) in order to make them appear in the drop down menu when editing.' value='nsubj csubj nsubjpass csubjpass dobj ccomp xcomp iobj vocative aux mark discourse auxpass expl cop neg root advmod dislocated nmod advcl nummod acl amod appos det nmod case compound mwe goeswith name foreign list parataxis remnant reparandum conj cc punct dep'></input></div>
		
		<div ><span style='float:left;'>additional POS tags</span> <input type='text' id='addcats'  style='width:100%;' title='Here you can add additional categories that do not appear in the CoNLL data (space or comma separated) in order to make them appear in the drop down menu when editing.' value='ADJ ADP PUNCT ADV AUX SYM INTJ CONJ X NOUN DET PROPN NUM VERB PART PRON SCONJ _'>  </input> </div>
		
		<div >or paste your sentences here:
		<TEXTAREA NAME="sentences" id="sentences"  title='Here you can provide unanalyzed textual data, one sentence per line. You can then interactively add the syntactic analysis of your sentences. This will erase all the existing trees'  style="width:100%; height:100;"></TEXTAREA>
		</div>
		
	</div>
			<input type="checkbox" id="annodoccheck"><label for="annodoccheck"><img src='images/annodoc.png' border='0' title='show annodoc graph' style='top:0px;'>  </label>

	
	
		
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
	print "</div></div></div>"

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
			
	<input type="button" id="drawbutton" value="draw" class="ui-button ui-state-default ui-corner-all" onClick='$("#funchoice").empty(); $("#catchoice").empty();$("#stylefunctions").empty();$("#trees").empty();readConll();setupStyleDialog();drawTrees();nokeys=false;'  style="display: none;" >

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
