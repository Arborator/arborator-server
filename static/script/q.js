/*!
 * arborator script for quickie 
 * version 1.0
 * http://arborator.ilpga.fr/
 *
 * Copyright 2014-2016, Kim Gerdes
 *
 * This program is free software:
 * Licensed under version 3 of the GNU Affero General Public License (the "License");
 * you may not use this file except in compliance with the License. 
 * You may obtain a copy of the License at http://www.gnu.org/licenses/agpl-3.0.html
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
 * See the License for the specific language governing permissions and limitations under the License. 
 *
 */ 


// needs arborator.draw.js
// does not need arborator.edit.js



conlls = {	10: 	{"id": 0, "t":1, "lemma": 2, "cat": 3, "xpos":4, "morph":5, "gov":6, "func":7, "xgov":8, "gloss":9}, 
// 		14: 	{"id": 0, "t":1, "lemma": 3, "cat": 5, "gov":8, "func":10}, 
		14: 	{"id": 0, "t":1, "lemma": 3, "cat": 5, "gov":9, "func":11}, 
		4: 	{"t":0, "lemma": 0, "cat": 1, "gov":2, "func":3} 
	}
el=10;
defaultCat="_"

inDrawTrees=false;
sentencesText="One sentence per line\nClick outside of this area when ready";

trees=[]; // list of tree objects
uextras=[]; // list of comments. each comment is a hashtable position(=line)->comment
conlltrees=[]; // list of conll strings


var root = 'annodoc/';
var webFontURLs = [
	root + 'Astloch-Bold.ttf',
	root + 'PT_Sans-Caption-Web-Regular.ttf',
	root + 'Liberation_Sans-Regular.ttf'
];

svgheader = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'


$(function() {

// 	console.log( "ready!" );
	$("#annodoccheck").prop('checked', false);
	$("#annodoccheck").button();
	$('#annodoccheck').change(function() {
		if (this.checked) {drawAnnodoc();$(this).button('option', 'label', 'Hide Annodoc graph');}
		else {$( ".annodoc" ).remove();$(this).button('option', 'label', 'Show Annodoc graph');}
	}); 
	settings();

	if (window.opener) 	// this window was opened by another window i.e. by depedit
		try {
			conllarea=window.opener.$(window.name); // use the name that depedit gave me to connect to the right conll area
			}
		catch(err) {
			console.log("problem with window.opener.$(window.name)");
			conllarea=$("#conll");
			$("#toggleAndBoxx").show();
		}
		
		
	else 			// this window is independent
		{
			conllarea=$("#conll");
			$("#toggleAndBoxx").show();
		}

	readConll();
	setupStyleDialog()
	drawTrees();

	$("#sentences").val(sentencesText)
	conllarea.focus(function() {
		nokeys=true;
	});
	conllarea.blur(function() {
// 		console.log("textarea changed!!");
		$("#funchoice").empty();
		$("#catchoice").empty();
		$("#stylefunctions").empty();
		$("#trees").empty();
		readConll();
		setupStyleDialog() 
		drawTrees();
		nokeys=false;
	});
	$('#sentences').focus(function() {
		nokeys=true;
	});
	$('#sentences').blur(function() {
// 		console.log("#sentences changed!!");
		nokeys=false;
		if (sentencesText!=$("#sentences").val()) // TODO: sentence really changed: set sentencesText
		{
			conllize();
			$("#trees").empty();
			readConll();
			setupStyleDialog() 
			drawTrees();
			sentencesText=$("#sentences").val();
		}
	});
	$('#addfuncs').focus(function() {
		nokeys=true;
	});
	$('#addfuncs').blur(function() {
		nokeys=false;
	});
	$('#addcats').focus(function() {
		nokeys=true;
	});
	$('#addcats').blur(function() {
		nokeys=false;
	});
	$(".toggle").on("click", function(e){
		$(this).toggleClass("expanded");
		$(".boxx").slideToggle();
	});
	
	$("#style").click(function()	{
		$( "#styledialog" ).dialog( "open" );
	});
	
	$( "#styledialog" ).dialog({
			bgiframe: true,
			autoOpen: false,
			height: 350,
 			width:400,
			draggable: true
			});
	
	$("#style").click(function()	{
		styling();
	});
	
	$("#help").click(function()	{
		help()
	});
	
	$('#styleconllcheck').change(function(){
		var c = this.checked ? '#f00' : '#09f';
		$('p').css('color', c);
	});
	
	
	
	
	conllarea.focus();
	
// 	help();
});


settings = function() 
	{
		shownfeatures=["t", "cat", "lemma","gloss"]; // recomputed in readConll
		erase="--ERASE--"
		categoryindex=1;
		tab=8; 			// space between tokens
		line=18 			// line height
		dependencyspace=200; 	// y-space for dependency representation
		xoff=8; 			// placement of the start of a depdency link in relation to the center of the word
		linedeps=6; 		// y distance between two arrows arriving at the same token (rare case)
		pois=4; 			// size of arrow pointer
		tokdepdist=15; 		// distance between tokens and depdendency relation
		funccurvedist=8;		// distance between the function name and the curves highest point
		depminh = 15; 		// minimum height for dependency
		worddistancefactor = -1; 	// distant words get higher curves. this factor fixes how much higher.
		rootTriggerSquare = 50; 	// distance from top of svg above which root connections are created and minimum width of this zone (from 0 to 50 par example the connection jumps to the middle)
		extraspace=50 		// extends the width of the svg in order to fit larger categories
		defaultattris={"font": '14px Arial', "text-anchor":'start'};
		attris = {"t":		{"font": '18px Arial', "text-anchor":'start',"fill": '#000',"cursor":'move',"stroke-width": '0'}, 
			"cat":	{"font": '12px Times', "text-anchor":'start',"fill": '#036',"cursor":'pointer'},
			"lemma":	{"font": '14px Times', "text-anchor":'start',"fill": '#036'},
			"depline":	{"stroke": '#000',"stroke-width":'1',"stroke-dasharray": ''},
			"deptext":	{"font": '12px Times', "font-style":'italic', "fill": '#000',"cursor":'pointer'},
			"dragdepline":	{"stroke": '#dd137b',"stroke-width":'2'},
			"dragdeplineroot":	{"stroke": '#654b6d',"stroke-width":'2'},
			"source":	{"fill": '#654b6d'},
			"target":	{"fill": '#dd137b',"cursor": 'url("images/connect.png"),pointer', "font-style":'italic'}, 
			"form":	{"font-style":'italic'}
			};
		colored={"dependency":null}; 	//object of elements to be colored. the colors have to be defined in config.py. just leave the object empty {} if you don't want colors
		attris[shownfeatures[categoryindex]]=attris["cat"]
		colored[shownfeatures[categoryindex]]=null;
		
		catDic={};
		var fd = $.cookie("funcDic");
		if (fd == null) funcDic = {};
		else funcDic= $.parseJSON(fd);
		
		editable=true;
		tokenModifyable=true;
	}


function drawTrees() {
	inDrawTrees=true;
	$.each(trees, function(i, tree){
		tokens=new Object();
		$.each(tree, function(key, val) 
			{
				tokens[key]=val;
			});
		start("holder"+i, i);
		$("#svg"+i).css("float","left").attr("nr",i);
	})
	$(".connect").css("top",dependencyspace-line)
	$(".cut").css("top",dependencyspace-line)
	inDrawTrees=false;
	final();
}


function final() {

	$(".toggler").click(function()
		{
			$('#holder'+$(this).attr("nr")).toggle(333)
		})
	$(".othertree").click(function()
		{
			toggleOpen($(this).parent().prev(),	$(this).attr("nr"), $(this).attr("treeid"));	
		})
	$(".saveimg").click(function()
		{
			var nr=$(this).parent().attr("nr");
			var sid=$(this).parent().attr("sid");
			
			saveTree(project,nr,sid,userid, username);
		});
	$(".undoimg").click(function()
		{
			var nr=$(this).parent().attr("nr");
			var sid=$(this).parent().attr("sid");
			currentsvg=$('#svg'+nr)[0];
			currentsvgchanged();
			currentsvg.undo.undo();
		});
	$(".redoimg").click(function()
		{
			var nr=$(this).parent().attr("nr");
			var sid=$(this).parent().attr("sid");
			currentsvg=$('#svg'+nr)[0];
			currentsvgchanged();
			currentsvg.undo.redo();
		});
	
	$(".connect").click(function()
		{
			
			var nr=parseInt($(this).parent().attr("nr"));
			currentsvg=$('#svg'+nr)[0];
			var basewords=currentsvg.words;
			var ind=Object.keys(basewords).length;
			var words=$('#svg'+(nr+1))[0].words
			var addnodes = Object.keys(words); //.sort();
			$.each(addnodes, function(i, nodei){
				var node = words[nodei]
				var newid = parseInt(nodei)+ind;
				node["index"]=newid;
				var newgov={};
				for (var j in node.gov) 
				{	
					var newgovind = parseInt(j)
					if (j!=0) newgovind+=ind
					newgov[newgovind]=node.gov[j];
				}
				node.gov = newgov;
				basewords[newid]=node;
			});
			var thisconll = wordsToConll(basewords);
			conlltrees.splice(nr,2,thisconll)
			conllarea.val(conlltrees.join("\n"));
			$("#trees").empty();
			readConll();
			setupStyleDialog() 
			drawTrees();
			
		});
	$(".cut").click(function()
		{
			var nr=parseInt($(this).parent().attr("nr"));
			currentsvg=$('#svg'+nr)[0];
			var allwords=currentsvg.words;
			var ind=isSelected.index;
			var newwords1={};
			var newwords2={};
			$.each(allwords, function(i, nodei){
				var node = allwords[i];
// 				console.log(allwords,nodei,allwords[i]);
				var newgov={};
				if (i<=ind)
					{
						for (var j in node.gov) 
						{	
							if (j<=ind) newgov[j]=node.gov[j];
						}
						newwords1[i]=node;
					}
				else
					{
						var newid = parseInt(i)-ind;
						node["index"]=newid;
						for (var j in node.gov) 
						{	
							if (j>ind) newgov[j-ind]=node.gov[j];
						}
						newwords2[newid]=node;
					}
				node.gov = newgov;
			});
			
			conlltrees.splice(nr,1,wordsToConll(newwords1),wordsToConll(newwords2))
			conllarea.val(conlltrees.join("\n"));
			$("#trees").empty();
			readConll();
			setupStyleDialog() 
			drawTrees();
			
		});
	
	$(".exportimg").click(function()
	{
		$("#ex").show();
		$("#ex").offset($(this).offset()).attr("nr",$(this).attr("nr"));
	});
	
	onkey();
	
	$("#dialog").dialog({
			bgiframe: true,
			autoOpen: false,
			height: 350,
 			width:400,
			modal: true,
			buttons: {
				
				Cancel: function() {
					$(this).dialog('close');
					return false;
				},
				"Burn it!!!": function() {
					$(this).dialog('close');
					reallyEraseTree();
					return true;
				}
				}
			});
	
	
// 'Erase node completely': function(){deleteNode($("#fdialog").attr("index"));} ,
// 				'Add as new node': function(){featureChanged(-1);} ,
	$("#fdialog").dialog({
				bgiframe: true,
				autoOpen: false,
				height: 450,
				width: 600,
				modal: true,
			});
	if (tokenModifyable>0) $("#fdialog").dialog({
				buttons: {
					'Erase this node': function() {eraseNode(parseInt($("#fdialog").attr("index"),10));$(this).dialog('close');},
					'Duplicate this node': function() {createNode(parseInt($("#fdialog").attr("index"),10));$(this).dialog('close');},
					Cancel: function() {$(this).dialog('close');},
					'OK': function(){featureChanged($("#fdialog").attr("index"));$(this).dialog('close');} 
				}
			});
	else	$("#fdialog").dialog({
				buttons: {
					Cancel: function() {$(this).dialog('close');},
					'OK': function(){featureChanged($("#fdialog").attr("index"));$(this).dialog('close');} 
				}
			});
		
	
	$(document).mouseup(function()
	{
		if(isDrag)
		{
			currentsvg.dragConnection.hide();
			isDrag = false;
		}
	}); 
	
	
// 	var svg = paper.toSVG();
// 	$("#e").html(svg);
// 	
}

	
function readConll() {
	// reads the conll representation of the whole treebank that is in the conll field
	categories={};
	addcats=$.trim($("#addcats").val())
	if (addcats) { $.each(addcats.split(/[,\s]+/), function(){ categories[this]=true;}) }
	
	functions={};
	addfuncs=$.trim($("#addfuncs").val())
	if (addfuncs) { $.each(addfuncs.split(/[,\s]+/), function(){functions[this]=true;}) }
	$.each(funcDic, function(key,val){functions[key]=true;});
	
	trees=[]; // list of tree objects
	uextras=[]; // list of comments. each comment is a hashtable position(=line)->comment
	conlltrees=[]; // list of conll strings
	treenr=0;
	
	var treelines = $.trim(conllarea.val()).split(/\n\s*\n\s*\n*/);
// 	console.log(232,treelines)
	$.each(treelines, function(i,treeline){ // splits the conll txt into tree segments:
		
		words=[]
		
		conlltrees.push(treeline);
		
		var data=conllNodesToTree(treeline);
		
		trees.push(data.tree);
		uextras.push(data.uextra)
		sentence="";
		$.each(words, function(jj,word){ // making the sentence with correct spacing:
			sentence+=word;
			if (jj+1 in data.tree && !(("NoSpaceAfter" in data.tree[jj+1]) && data.tree[jj+1]["NoSpaceAfter"]==true)) sentence+=" ";
		});
		gt=''
		if (treenr!=treelines.length-1) gt+='<div class="connect" title="connect with next sentence." id="connect'+i+'">&gt;</div>'
		gt += '<div class="cut" title="cut after selected word." id="cut'+i+'"><img src="images/cut.png"/></div>'
		$("#trees").append('<div id="sentencediv'+treenr+'" class="sentencediv" nr="'+treenr+'"> <a id="toggler'+treenr+'" class="toggler expanded" nr="'+treenr+'"> '+treenr+': '+sentence+' </a>		<img id="undo'+treenr+'" class="undoimg"	src="images/undo.png">				<img id="redo'+treenr+'" class="redoimg"	src="images/redo.png"> <img id="export'+treenr+'" class="exportimg" border="0" title="export the dependency graph in various image formats" nr="'+treenr+'" src="images/export.png" style="visibility: visible;"> </div> <div id="holder'+treenr+'" class="svgholder"	nr="'+treenr+'">'+gt+'</div>')
		
		treenr++;
	});
	conllarea.css("backgroundImage","url('images/conll"+el+".png')");	
	categories=$.map(categories, function(element,index) {return index}).sort() // to array
	$.each(categories, function(key, val) 
			{
				$("#catchoice").append("<option>"+val+"</option>")
			});
	$("#catchoice").attr("size",categories.length);
	$("#catchoice").css("height",categories.length*13.5);
	functions=$.map(functions, function(element,index) {return index}).sort() // to array
	functions.push("");
	functions.push(erase);
	
	// 	adapt which nodes should be shown depending on what we find on the first node
	firstnode=trees[0][Math.min.apply(Math,Object.keys(trees[0]))]; // take lowest existing treenode number
	shownfeatures = $.grep(shownfeatures, function (attri,i)
		{ // for each shownfeatures :
			if (i < 2 || ((attri in firstnode) && firstnode[attri]!=defaultCat)) { 
				// either the first two (token and cat) or non default value:
				return true; // keep it
				}
			return false; // kick it out
		});
	
}



function conllNodesToTree(treeline)
	// reads a conll representation of a single tree
	{
		var nodes = treeline.split('\n');
		var tree={};
		var uextra={};
		var lastid=0;
		var skipuntil=0;
		$.each(nodes, function(id,nodeline){ // for each conll line:
			var nodeline=$.trim(nodeline);
			if (nodeline.charAt(0) == "#") {
				if (!(lastid in uextra)) uextra[lastid]=[];
				uextra[lastid].push(nodeline)
				return true;
			}
			var elements = nodeline.split('\t');
			el=elements.length;
			// console.log(el,'###',nodeline,"***",elements);

			if (!(el in conlls) && el>10) el=10;
			if (el > 4) id=elements[conlls[el]["id"]];
			else if (elements[conlls[el]["t"]] != "_") id++;
			if (lastid!=id) // needed for the arborator encoding of multiple govs
			{
				var t=elements[conlls[el]["t"]];
				var tokids=id.split("-")
				if (tokids.length == 1) {
					tree[id]={}
					tree[id]["gov"]={};
					tree[id]["t"]=t;
					tree[id]["lemma"]=elements[conlls[el]["lemma"]];
					tree[id]["cat"]=elements[conlls[el]["cat"]];
					if (id>skipuntil) words.push(t);
					if (el==10) {
						tree[id]["xpos"]=elements[conlls[el]["xpos"]];
						tree[id]["morph"]=elements[conlls[el]["morph"]];
						tree[id]["gloss"]=elements[conlls[el]["gloss"]];
						if (tree[id]["gloss"]=="SpaceAfter=No"){
							tree[id]["gloss"]="_";
							tree[id]["NoSpaceAfter"]=true;
						}
						var xgov = elements[conlls[el]["xgov"]];
						if (xgov.indexOf(':') > -1){
							var xgovs=xgov.split("|");
							$.each(xgovs, function(ind,xg){ 
								// for each extra governor line:
								var xgs=xg.split(":")
								if (xgs.length >=2) {
									// if it's not just _
									var gov=xgs[0];
									var func= xgs.slice(1).join(":");
									tree[id]["gov"][gov]=func;
								}
								
							});

						}
					}
				}
				else if (tokids.length == 2){
					skipuntil = parseInt(tokids[1])
					words.push(elements[conlls[el]["t"]]);
					if (!(lastid in uextra)) uextra[lastid]=[];
					uextra[lastid].push(nodeline)
				}
				else {
					if (!(lastid in uextra)) uextra[lastid]=[];
					uextra[lastid].push(nodeline)
				}
			}
			gov = elements[conlls[el]["gov"]];
			if (gov!="" && gov!="_") 
			{
				if (gov==-1)
				{
					gov = elements[conlls[el]["gov"]+1];
				}
				var func = elements[conlls[el]["func"]];
				if (func.indexOf('::') !== -1) 
					{	
						var stydic = func.substring(func.indexOf("::") + 1);
						func = func.split("::")[0];
						if (stydic!="") funcDic[func] = $.parseJSON(stydic);
						$('#styleconllcheck').prop('checked', true);
					};
// 				func=func.replace(/\W+/g, "_");
				tree[id]["gov"][gov]=func;
				functions[func]=true;
			}
			categories[elements[conlls[el]["cat"]]]=true;
			lastid=id;
			});	
		return {tree:tree, uextra:uextra};
	}



				
			
function conllize()
	// sentences to conll
	{
		var conll="";
		$.each($.trim($("#sentences").val()).split(/\s*\n\s*/), function(i,sentence){
			var words=sentence.split(/\s+/);
			for (i in words)
			{		
				var word = words[i] ;
				conll=conll+(parseInt(i)+1)+"\t"+word+"\t"+word+"	"+defaultCat+"	_	_	0	root	_	_\n";
			}
			conll+="\n"
		})
		conllarea.val(conll);
	}


	
help = function() {	
	$("#b").fadeIn(2000).delay(2222).fadeOut(2000);
	$("#bb").delay(2222).fadeIn(2000).delay(1111).fadeOut(2000);
	$("#bbb").delay(4444).fadeIn(2000).delay(1111).fadeOut(2000);
	$("#bbbb").delay(6444).fadeIn(2000).delay(1111).fadeOut(2000);
}

styling = function() {	
	$('.color-box').colpick({
			colorScheme:'dark',
			layout:'rgbhex',
			color:'dd137b',
			onSubmit:function(hsb,hex,rgb,el) {
				$(el).css('background-color', '#'+hex);
				var name = $(el).attr('name');
				if (name in funcDic) 
					funcDic[name]["stroke"]='#'+hex;
				else 	funcDic[name]={"stroke":'#'+hex};
				$("#trees").empty();
				readConll();
				drawTrees();
				$(el).colpickHide();
				$.cookie("funcDic", JSON.stringify(funcDic), { expires: 365 });
			}
		});
	
	$( ".selector" ).change(function(handler) {
			var name=$(this).attr('name');
			if (name in funcDic) 
				funcDic[name]["stroke-dasharray"]=$(this).val();
			else 	funcDic[name]={"stroke":'#000',"stroke-dasharray":$(this).val()};
			$("#trees").empty();
			readConll();
			drawTrees();
		});

	$('#styledialog').dialog('open');
}



setupStyleDialog = function() {
	var lineStyles1='<select name="'
	var lineStyles2='" class="selector" title="line style">	<option value="" style="font-size:.6em;height:5px;" selected>─────</option>	<option value="- ">---------</option>	<option value=". " >┈┈┈┈┈</option> </select>'
	$("#stylefunctions").empty();
	$("#funchoice").empty();
	
	$.each(functions, function(i, val) 
			{
				$("#funchoice").append("<option style='color:"+((val in funcDic) ? funcDic[val]["stroke"] : "#000")+";'>"+val+"</option>")
				if (val!="" && val!=erase) 
				{
					$("#stylefunctions").append("<div><div class='color-box' style='background-color:"+((val in funcDic) ? funcDic[val]["stroke"] : "#000")+";' name='"+val+"'></div><div>"+val+" "+lineStyles1+val+lineStyles2+"</div></div><br>")
				}
			});
	$("#funchoice").attr("size",functions.length);
	$("#funchoice").css("height",functions.length*13.5);
}

currentsvgchanged = function () {

	var nr = $(currentsvg).attr("nr");
	$(".connect").hide();
	$(".cut").hide();
	$("#connect"+nr).show();
	if (isSelected && isSelected.index < Object.keys(currentsvg.words).length) // if selected word and not last word
	{
		$("#cut"+nr).attr("title","cut after selected word '"+isSelected.attr("text")+"'").show();
		
	}
}

wordsToConll = function (words) {
	thisconll=""
	var uextra=uextras[currentnr];
	if (0 in uextra) thisconll+=uextra[0].join("\n")+"\n";
	for (var i in words)
		{
			var n = words[i];
			var c=0;
			
			if ($.isEmptyObject(n.gov)) // no governors
			{					
				if (el == 4) 	ar = [n.features.t,n.features.cat,"_","_"];
				else if (el == 10) 	ar = [n.index,n.features.t,n.features.lemma,n.features.cat,n.features.xpos,n.features.morph,"_","_","_",( (("NoSpaceAfter" in n.features) && n.features["NoSpaceAfter"]==true) ? "SpaceAfter=No" : n.features.gloss)];
				else if (el == 14) 	ar = [n.index,n.features.t,"_",n.features.lemma,"_",n.features.cat,"_","_","_","_","_","_","_","_"]
				thisconll+=ar.join("\t")+"\n"
			}
			else // at least one governor
			{
				var ngovs = Object.keys(n.gov).sort();
				if (el == 10) { 
					// conllu case: pushing additional govs into special column
					var xgovsl=[]
					while (ngovs.length > 1) {
						var xj=ngovs.pop();
						var func = $('#styleconllcheck').prop('checked') ? n.gov[xj]+"::"+(n.gov[xj] in funcDic ? JSON.stringify(funcDic[n.gov[xj]]) : "") :	n.gov[xj];
						xgovsl.push(xj+":"+func);
					}
					xgovs=xgovsl.join("|");
					if (xgovs.length==0) xgovs="_";
				}
				$.each(ngovs, function(ind, j){ // loop over array of gov keys:
					var t=n.features.t;
					var cat=n.features.cat;
					var func = $('#styleconllcheck').prop('checked') ? n.gov[j]+"::"+(n.gov[j] in funcDic ? JSON.stringify(funcDic[n.gov[j]]) : "") :	n.gov[j];
					c+=1;
					if (el == 4)	{	
								if (c>1) {t="_";cat="_"}
								ar = [t,cat,j,func]
							}
					else if (el == 10) 	ar = [n.index,t,n.features.lemma,n.features.cat,n.features.xpos,n.features.morph,j,func,xgovs,( (("NoSpaceAfter" in n.features) && n.features["NoSpaceAfter"]==true) ? "SpaceAfter=No" : n.features.gloss)]
					else if (el == 14) 	ar = [n.index,t,"_",n.features.lemma,"_",n.features.cat,"_","_",j,j,func,func,"_","_"]
					thisconll+=ar.join("\t")+"\n"
				});
			}
			if (i in uextra) thisconll+=uextra[i].join("\n")+"\n";
		};
	return thisconll;
}


// overriding the arborator.draw function to add conll stuff
drawalldeps = function() 
	{
	currentnr = $(currentsvg).parent().attr("nr");
	var thisconll=wordsToConll(currentsvg.words);
	conlltrees[currentnr]=thisconll;
	for (var i in currentsvg.words)
		{
			var n = currentsvg.words[i];
			for (var j in n.svgdep) 
			{
				n.svgdep[j].remove();
				delete n.svgdep[j];
			}
			n.svgdep={};
			var c=0;
			
			var distarray = $.map(n.gov, function(value, index) {return [[Math.abs(index-i),index]];}).sort(); // order drawing of multiple governors by increasing distance
			for (var jj in distarray) 
			{
				var j=distarray[jj][1];
				drawDep(n.index,j,n.gov[j],c);
				c+=1;
			};
			
		};
		
// 	deptreeexperiment();
		
	if (inDrawTrees) return; // if i got here by reading the conll text content, no need to again write it back into the conll textarea
	
	
	// making new conlltext
	var conlltext = "";
	$.each(conlltrees, function(i, conlltree){ // just modifies the changed tree, keeps the other conll strings
			if (i==currentnr) conlltext+=thisconll+"\n";
			else conlltext+=conlltrees[i]+"\n"
		})
	
// 	if (autostart) 
	conllarea.val(conlltext);
			
	
// 	console.log("autostart",autostart)

	
// 	console.log(window.location.href.slice(-13) != "?autostart=no", 88888, window.opener)
	};


// overriding the changeCat function to add conll stuff

function changeCat(){ // called by onclick on the menu or return

	var cc=$('#catform');
	if (cc.is(":hidden")) return false;
	var cat=$("#catchoice")[0].options[$("#catchoice")[0].selectedIndex].value;
	if (cat==null) cat=defaultcategory;
	var id = cc.data("index");
	establishCat(id,cat);
	cc.hide();
	
	currentnr = $(currentsvg).parent().attr("nr");
	var thisconll=wordsToConll(currentsvg.words);
	conlltrees[currentnr]=thisconll;
// 	console.log(currentnr);
	var conlltext = "";
	$.each(conlltrees, function(i, conlltree){ // just modifies the changed tree, keeps the other conll strings
			if (i==currentnr) conlltext+=thisconll+"\n";
			else conlltext+=conlltrees[i]+"\n"
		})
	conllarea.val(conlltext);
		
}	
	
	
	
deptreeexperiment = function(){ // unfinished experiment of creating an unordered tree representation
		
	var roots=[];
	var leaves=[];
	for (var i in currentsvg.words)
		{
			var n = currentsvg.words[i];
			var k = Object.keys(n.gov);
			if (k.length==0||k.length==1 && k[0]==0)
				roots.push(n);
			n.kids=n.kids||[];
			n.levels=n.levels||{};
			n.levels[0]=n.width;
			for (var j in n.gov) 
			{
				if (j==0) continue;
				var nn = currentsvg.words[j];
				nn.kids=nn.kids||[];
				nn.kids.push(n);
			};
		};
// 	console.log(roots);
	for (var i in roots) console.log("$$$",walkdown(roots[i],0,0,[]));
// 	for (var i in currentsvg.words)
// 		{
// 			var n = currentsvg.words[i];
// 			var k = Object.keys(n.gov);
// 			if (k.length==0)
// 				leaves.push(n);
// 		}
// 	for (var i in leaves)
// 		{
// 			var n = currentsvg.words[i];
// 			
// 		}
	console.log("end deptree",currentsvg.words);
		
}
	
walkdown = function(n,level,maxi,already){
	console.log("walkingdown",n.index,n.features.t,n,level,maxi,already);
	
	if (level < n.level) n.level=level;
	n.level=n.level||level
	
	console.log("***",already.indexOf(n.index));
	if (already.indexOf(n.index)>-1) return maxi;
	already.push(n.index);
	if (level>maxi) maxi=level;
	for (var i in n.kids) {
		m=walkdown(n.kids[i], level+1,maxi,already );
		if (m>maxi) maxi=m;
	}
	
	
	console.log("***walkingdown",n.index,n,already);
	
	for (var i in n.kids) 
	{
		var kid=n.kids[i];
		for (var j in kid.levels) 
		{
			var j=parseInt(j);
			console.log("i'm in",n.index,"kid",kid.index,"kid level",j);
			n.levels[j+1]=(n.levels[j+1]||0)+kid.levels[j];
			
		}
	}
	
	
	console.log("___walkingdown",n.index,n.level,"==",n.levels,n,already);
	return maxi	
}
	
	
exportTree = function () {
	
	nr=$("#ex").attr("nr");
	
	var v=$("#exptype")[0].options[$("#exptype")[0].selectedIndex].value;

	$("svg").attr("xmlns","http://www.w3.org/2000/svg");
	$("svg").attr("xmlns:xlink","http://www.w3.org/1999/xlink");
	
// 			$('#source').attr("value",header+$('#holder'+nr).html());
	$('#source').attr( "value", svgheader+$('#holder'+nr+' >svg').clone().wrap('<p>').parent().html() );
	
	if(v=="xxxsvg")	// TODO: no need to go via the server to show svg content
	{
		var x=window.open();
		x.document.open();
		x.document.write(svgheader+$('#holder'+nr+' >svg').clone().wrap('<p>'));
		x.document.close();	
	}
	else $('#ex').submit();
		
// 		}
}

openFeatureTable = function() {
	console.log("no feature table in the quick mode.")
}


	
	
function dirt() { 
	var nr=currentsvg.id.substr(3);
	if (currentsvg.undo.undo_available)
	{
		var ind=dirty.indexOf(currentsvg.id);
		$("#save"+nr).css({ visibility: 'visible' });
		$("#undo"+nr).css({ visibility: 'visible' }).attr("title","undo: "+currentsvg.undo.undo_names[currentsvg.undo.undo_available - 1]);
		if (ind!=-1) dirty.splice(ind, 1);
		dirty.push(currentsvg.id);
	}
	else
	{	
		var ind=dirty.indexOf(currentsvg.id);
		$("#save"+nr).css({ visibility: 'hidden' });
		$("#undo"+nr).css({ visibility: 'hidden' });
		if (ind!=-1) dirty.splice(ind, 1);
	}
	if (currentsvg.undo.redo_available)
	{
		$("#redo"+nr).css({ visibility: 'visible' }).attr("title","redo: "+currentsvg.undo.redo_names[currentsvg.undo.redo_available - 1]);
	}	
	else
	{	
		$("#redo"+nr).css({ visibility: 'hidden' });
	}	
	if (dirty.length==0)	$("#sav").attr(attrclean).addClass( "ui-state-disabled " );
	else			$("#sav").attr(attrdirty).removeClass( "ui-state-disabled " );
	
}

function drawAnnodoc() {
	// bug in annodoc: tabs are not accepted as separator for conll!!
	readConll();
	$.each(conlltrees, function(i, conlltree){
			$( '<div class="annodoc" id="annodoc'+i+'">\n<pre><code class="language-conllu">\n'+ conlltree.replace( /\t/g, "  ")+ '\n</code></pre></div>').insertAfter( '#holder'+i );
// 			$( '<xspan class="annodoc"><img id="export'+i+'" class="exportannodoc" border="0" style="visibility: visible;" src="images/export.bw.png" nr="'+i+'" title="export the Annodoc svg graph"></xspan>').insertAfter( '#export'+i );

		})
	
	
	Annodoc.activate(Config.bratCollData, Collections.listing);
	
// 	$(".exportannodoc").click(function()
// 	{
// 			console.log($(this).attr("nr"))
// 			console.log( $("#annodoc"+$(this).attr("nr")+" svg" ).attr("xmlns:xlink","http://www.w3.org/1999/xlink").attr("xmlns","http://www.w3.org/1999/xlink").prop("outerHTML") );
// 			
// 			
// 	
// // 			$('#source').attr("value",header+$('#holder'+nr).html());
// // 	$('#source').attr( "value", svgheader+$('#holder'+nr+' >svg').clone().wrap('<p>').parent().html() );
// 	
// 			
// 			
// // 		$("#ex").show();
// // 		$("#ex").offset($(this).offset()).attr("nr",$(this).attr("nr"));
// 	});
	
	
}
