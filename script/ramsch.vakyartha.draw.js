/*!
 * vakyartha dependency script 1.0
 * http://arborator.ilpga.fr/
 *
 * Copyright 2010-2011, Kim Gerdes
 *
 * This program is free software: 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License. 
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
 * See the License for the specific language governing permissions and limitations under the License. 
 *
 */


///////////////////////// parameters ////////////////
////////////////////////////////////////////////////


tab=8; 			// space between tokens
line=25 		// line height
dependencyspace=180; 	// y-space for dependency representation
xoff=8; 		// placement of the start of a depdency link in relation to the center of the word
linedeps=15; 		// y distance between two arrows arriving at the same token (rare case)
pois=4; 		// size of arrow pointer
tokdepdist=15; 		// distance between tokens and depdendency relation
funccurvedist=8;	// distance between the function name and the curves highest point
depminh = 20; 		// minimum height for dependency
worddistancefactor = 8; // distant words get higher curves. this factor fixes how much higher.

rootTriggerSquare = 50; // distance from top of svg above which root connections are created and minimum width of this zone (from 0 to 50 par example the connection jumps to the middle)

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
colored={"dependency":null,"cat":null}; //object of elements to be colored. the colors have to be defined in config.py. just leave the object empty {} if you don't want colors

extraspace=50 // extends the width of the svg in order to fit larger categories

//  "dragdeptext":	{"font": '12px "Times"', "font-style":'italic', "fill": '#999'}, #C54664 , "stroke":'#999999',"stroke-width": '.5 , "font-style":'italic'



////////////////////////////////////////// end parameters //////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
//////////////////don't touch below if you don't know what you're doing ////////////////



///////////////////////// node object and functions //////////////// 
////////////////////////////////////////////////////////////////////


var currentsvg=false;
var isSelected=false;
var isDrag=false;
var dirty=false;
var lastSelected;
var keyediting=false;

function Pnode(index,token)
	{
		index=parseInt(index,10);
		this.index=index;
		this.govs={};
		if ("govs" in token) 
		{
// 			this.govs=token["govs"];
			for (var i in token["govs"])
			{
// 				alert(i+" "+parseInt(i)+token["govs"][i])
				this.govs[parseInt(i,10)]=token["govs"][i]
			}
		}	
		this.width=0;
		this.texts=new Object(); // contains for each shownfeature the corresponding text
		this.svgs=new Object(); // contains for each shownfeature the corresponding svg object
		var currenty=dependencyspace;
		for (var i in shownfeatures) 
			{	
			var f = shownfeatures[i]; // f= eg. "cat"
			this.texts[f]=token[f];
			var t = paper.text(currentx, currenty, token[f]);
			t.attr(defaultattris);
			if (f in token) t.attr(attris[f]);
			if ("attris" in token) t.attr(token["attris"][f]);
			var wi=t.getBBox().width;
			t.width=wi;
			t.index=index;
		
			t.node.setAttribute("class",f);
			if (f in colored && token[f] in ccolors) t.attr({fill: "#"+ccolors[token[f]]});
			this.svgs[f]=t;
			if (wi>this.width) this.width=wi;
			currenty=currenty+line;
			};
// 					$("#sentinfo").html("openFunctionMenu"+ "---- " +shownfeatures);
		if (editable) activate(this.svgs[shownfeatures[0]], this.svgs[shownfeatures[categoryindex]]);

		svgwi=svgwi+this.width+tab;
		this.x=0;
		this.y=0;
		this.svgdep={};		// the svg dependency (the arrow and the function name): gives the svgobject for each govind
		this.deplineattris={},t.deptextattris={};
		if ("attris" in token && "depline" in token["attris"]) this.deplineattris=token["attris"]["depline"];
		if ("attris" in token && "deptext" in token["attris"]) this.deptextattris=token["attris"]["deptext"];
	};


	
	
//////////////////////////// only used for editing:
//////////////////////////////////////////////////////// 


activate = function (t,cat) /*makes word node t interactive  */
{
	t.attr({cursor:"move"}).mousedown(dragger).mouseover(function () {
		if (t==isDrag || keyediting) return;	
		isSelected=t;
		if (isDrag) 
			{
				for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris["t"]);	
				t.attr(attris["target"]);
				isDrag.attr(attris["source"]);
			}
	}).mouseout(function () {
		if (t==isDrag  || keyediting) return;				
		isSelected=null;
		for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris["t"]);

	}).dblclick(function () {
		openFeatureTable(this.index,currentsvg.words)
	})
	cat.click(function (e) {openCatMenu(this);})
}


newchangeDrag = function (govs, funcs, dep, addDep) /* reaction if good connection was created, gov and dep are indeces */
{
	// adding a depdendency from gov to dep. if add is true, add the link to existing dependencies pointing to dep
	if (dep)
	{
		var depn=currentsvg.words[dep];
		for (i in depn.svgdep) { depn.svgdep[i].remove(); }
		var func = null;
		if (!funcs) for (i in depn.govs) { func = depn.govs[i]; break;} // get any (the first) of the existing func name
		if (func==null) func = defaultfunction;
		if (!addDep) {
			oldgovs = depn.govs;
			delete depn.govs;
			depn.govs={}
			}			
		if (!govs) // case: dragging straight up
		{
			gov=0;
			func=root;
		}
		func="root";
		for (i in govs) { depn.govs[i]=func; alert(i) }
// 		depn.govs[gov]=func;
		drawalldeps();
		
		currentsvg.undo.undoable('changeDrag ' + (typeof govs) + ' ' + oldgovs + ' !', changeDrag, [oldgovs,dep]);  
// 		alert(oldgovs[0]);
		if (!dirty) dirt()
// 			alert(govs+" "+govs[0]);
			gov=govs[0];
		if (govs.length==1) openFunctionMenu(depn.svgdep[gov][0]); // sending the svg text node of the dependency link to openFunctionMenu
		
	}
	
};

oldchangeDrag = function (govs, funcs, dep, addDep) /* reaction if good connection was created, gov and dep are indeces */
{
	// adding a depdendency from gov to dep. if add is true, add the link to existing dependencies pointing to dep
	if (dep)
	{
		var depn=currentsvg.words[dep];
		for (i in depn.svgdep) { depn.svgdep[i].remove(); }
		
		
// 		oldgovs=new Object();
		oldgovs=[];
		oldfuncs=[];
		info="remove"
		
		for (var i in govs)
		{
			alert(i+" " + (i in currentsvg.words))
			alert(currentsvg.words[i].texts.t);
			if (i in currentsvg.words) info=info+" link "+ currentsvg.words[i].texts.t + " ↷ "+depn.texts.t + " ";
			else info=info+" link root ↷ "+depn.texts.t;
		}
		
		info=info + " and reestablish"
		for (var i in depn.govs)
		{
			oldgovs.push(i);
			oldfuncs.push(depn.govs[i]);
			if (i in currentsvg.words) info=info+" link "+ currentsvg.words[i].texts.t + " ↷ "+depn.texts.t + " ";
			else info=info+"link root ↷ "+depn.texts.t;
		}
		
		var func = null;
		for (i in depn.govs) { func = depn.govs[i]; break;} // get any (the first) of the existing func name
		if (func==null) func = defaultfunction;
		
		if (!addDep) {
			delete depn.govs;
			depn.govs={}
			}			
		if (govs==null || govs==[]) // case: dragging straight up
		{
			govs=[0]
			func=root
		}
		depn.govs[govs[0]]=func;
		drawalldeps();
		
		currentsvg.undo.undoable(info, changeDrag, [oldgovs, oldfuncs, dep, addDep]);  
// 		alert(oldgovs[0]);
		if (!dirty) dirt()
		openFunctionMenu(depn.svgdep[govs[0]][0]); // sending the svg text node of the dependency link to openFunctionMenu
		
	}
	
};


changeDrag = function (govs, funcs, dep, addDep) /* reaction if good connection was created, gov and dep are indeces */
{
	
	
}

openFunctionMenu = function(funcnode)  // funcnode=svg text node of the dependency link
	{
		var ff=$('#funcform');
		funcnum=functions.indexOf(funcnode.attr("text"));
		if (funcnum==null) funcnum=0;
		svgpos=$(currentsvg).position();
		var os=$("#funchoice")[0].options;
		if (funcnum in os) os[funcnum].selected = true;
		ff.css({ top: svgpos.top+funcnode.attr("y")-7, left: svgpos.left+funcnode.attr("x")-20 });// TODO: make the position of the function menu parametrizable
		ff.show();
		$("#funchoice").focus()
		ff.data("index", funcnode.index);
		ff.data("govind", funcnode.govind);
		lastSelected = funcnode.index;
		
	}

openCatMenu = function(catnode)  // funcnode=svg text node of the dependency link
	{
		var cc=$('#catform');
		catnum=categories.indexOf(catnode.attr("text"));
		if (catnum<0) catnum=0;
		svgpos=$(currentsvg).position();
		var os=$("#catchoice")[0].options;
		if (catnum in os) os[catnum].selected = true;
// 		$("#catchoice")[0].options[catnum].selected = true;
// 		$("#sentinfo").html("openCatMenu"+catnum+ "---- ");
		cc.css({ top: svgpos.top, left: svgpos.left+catnode.attr("x")+catnode.width});
		cc.show();
		$("#catchoice").focus();
		cc.data("index",catnode.index);
		lastSelected = catnode.index;
	}

function dirt() { 
	
	if (currentsvg.undo.undo_available)
	{
		$("#save"+currentsvg.id.substr(3)).css({ visibility: 'visible' });
		$("#undo"+currentsvg.id.substr(3)).css({ visibility: 'visible' }).attr("title",currentsvg.undo.undo_names[currentsvg.undo.undo_available - 1]);
	}
	else
	{
		$("#save"+currentsvg.id.substr(3)).css({ visibility: 'hidden' });
		$("#undo"+currentsvg.id.substr(3)).css({ visibility: 'hidden' });
		
	}
	if (currentsvg.undo.redo_available)
	{
		$("#redo"+currentsvg.id.substr(3)).css({ visibility: 'visible' });
	}	
	else
	{	
		$("#redo"+currentsvg.id.substr(3)).css({ visibility: 'hidden' });
	}	
	
	
	dirty=true; $("#sav").attr(attrdirty).text("save tree").removeClass( "ui-state-disabled " );
// 	alert("#save"+currentsvg.id.substr(3));
	
	
}


checkUndo = function () 
{
	
	; // The amount of undos possible  
	undo.redo_available; // The amount of undos possible  
	undo.undo_names; // The names of the undo objects (eg: "Set title")  
	undo.redo_names; // The names of the redo objects  
	undo.undo_names[undo.undo_available - 1]; // The next object on the queue  
	undo.redo_names[undo.redo_available - 1]; // The next object on the queue 

}

function changeFunc(){ // called by onclick on the menu or return

	var ff=$('#funcform');
	if (ff.is(":hidden")) return false;
	
	var func=$("#funchoice")[0].options[$("#funchoice")[0].selectedIndex].value;
	
	var id = ff.data("index");
	var govid = ff.data("govind");
	var node=currentsvg.words[id];
	if (func==null) func=defaultfunction;
	node.govs[govid]=func;
	if (func==erase)
		{
			node.svgdep[govid].remove();
			delete node.svgdep[govid];
			delete node.govs[govid];
		}
	else if (func==root) 
		{
			delete node.govs;
			node.govs={}
			node.govs[0]=func;
		}
	drawalldeps();
	if (!dirty) dirt()
	ff.hide();
	
}	
	

function changeCat(){ // called by onclick on the menu or return

	var cc=$('#catform');
	if (cc.is(":hidden")) return false;
	
	var cat=$("#catchoice")[0].options[$("#catchoice")[0].selectedIndex].value;
	
	var id = cc.data("index");
	var node=currentsvg.words[id];
	if (cat==null) cat=defaultcategory;
	node.texts["cat"]=cat;
	node.svgs["cat"].attr("text",cat);
	if (!dirty) dirt()
	cc.hide();
	
}	

var dragger = function (e) {
	
	if(e.ctrlKey) return true; // to allow dbl click if nothing else works. ugly hack!
	reset();
	isDrag = this;
	isDrag.rooting=false;
	isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
	isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
	moveConnection(e.pageX,e.pageY);
	currentsvg.dragConnection.show();
	currentsvg.dragConnection.toFront();
	isDrag.svg=currentsvg;
        e.preventDefault && e.preventDefault();
    };



moveConnection = function(x,y) // moves the connection so that it links the isDrag to the x,y position
	{	
		
		if (!isDrag || !currentsvg) return;
		
		var p = $(currentsvg).position();
		var wi = isDrag.width/2;
		var wix = Math.max(wi,rootTriggerSquare/2);
		x2=x-p.left;
		y2=y-p.top-tokdepdist;
				
		if (x2<=isDrag.attr("x")+wi) var x1=isDrag.attr("x")+wi-xoff; // 1st case: cursor to the right of the word
		else var x1=isDrag.attr("x")+wi+xoff; // 2nd case: cursor to the left of the word
		if (y2<rootTriggerSquare && x2>isDrag.attr("x")+wi-wix && x2<isDrag.attr("x")+wi+wix) // 3rd case: cursor rooting above
			{
				isDrag.rooting=true;
				lineattris=attris["dragdeplineroot"]
				x1=isDrag.attr("x")+wi;
			}
		else 	// not rooting, normal
			{
				isDrag.rooting=false;
				lineattris=attris["dragdepline"];
			}
		var y1 = isDrag.attr("y")+pois-tokdepdist;
		applyPath(x1,y1,x2,y2,lineattris);
	}
  
applyPath = function(x1,y1,x2,y2,lineattris) // 
	{
		var x1x2=Math.abs(x1-x2)/2;
		var yy = Math.max(y1-x1x2-worddistancefactor,-tokdepdist);
		yy = Math.min(yy,y1-depminh);

		var path="M"+x1+","+y1+"C"+x1+","+yy+" "+x2+","+yy+" "+x2+","+y2;
	
		currentsvg.dragConnection[1].attr({path:path}).attr(lineattris);;// curve        
		currentsvg.dragConnection[2].translate(x2-isDrag.ox,y2-isDrag.oy).attr(lineattris);; // pointer
	}	

createConnection = function () {
	
	$(currentsvg).mousemove(function(e) 
	{
		if (currentsvg!=this) 
		{
			reset()
			$(".toggler").removeClass("currentsentence");
			currentsvg=this;
			$(".toggler:eq("+parseInt(currentsvg.id.slice(3))+")").addClass("currentsentence");			
		}
		if ( isDrag && !keyediting ) 
		{
			moveConnection(e.pageX,e.pageY);
			isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
			isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
		}
	}).mouseup(function(e) 
	{
		currentsvg.dragConnection.hide();
		emptyclick=true;
		if (isSelected && isDrag && isSelected!=isDrag && isDrag.svg==currentsvg) 
			{changeDrag([isDrag.index],null,isSelected.index,e.shiftKey );emptyclick=false;};
		if (isDrag && isDrag.rooting) 
			{changeDrag(null,null,isDrag.index,e.shiftKey );emptyclick=false;}
		setTimeout("isDrag = false;",500);
		
		for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris["t"]);

		if (emptyclick) {$('#funcform').hide();$('#catform').hide();}
		else {$("#catchoice").focus();}
		isDrag = false;
	});
	
	$(document).mouseup(function()
	{
		if(isDrag)
		{
			currentsvg.dragConnection.hide();
			isDrag = false;
		}
	}); 
	  
	return drawsvgDep(1,2,50,60,150,150,"", attris["dragdepline"], attris["deptext"]); // arbitrary points
	
}
   

//////////////////////////////////////// keystuff ///////////////////////////////
////////////////////////////////////////////////////////////////////////////////


onkey = function () {
	$(document).keypress(function(e) {
		var code = (e.keyCode ? e.keyCode : e.which);
		
		switch(code)
		{
		case 8: // backspace
			if(currentsvg) {nextword(0)}
			return false;
		case 9: // tab
			if(currentsvg) {nextsentence()}
			else $(".toggler:first").click().focus();
			return false;
		case 13: // return
			if(currentsvg && $('#funcform').is(":visible"))
			{
				changeFunc();
				if (keyediting) nextword(1);
			}
			else if (currentsvg && $('#catform').is(":visible"))
			{ 
				changeCat();
				if (keyediting) nextword(1);
			}
			else if (currentsvg && keyediting)
			{ 
				changeDrag([isDrag.index],null,lastSelected,e.shiftKey )
			}
			return false;
		case 27: //esc 
			reset();
// 			$("#sentinfo").html("escaping");
			return false;
		case 32: // space
			if(currentsvg) {nextword(1)}
			else $(".toggler:first").click().focus();
			return false;
		case 37: // left
			if(currentsvg && keyediting && $('#funcform').is(":hidden") && $('#catform').is(":hidden")) moveGov(-1);
			break;
		case 38: // up
			if(currentsvg && keyediting && $('#funcform').is(":hidden") && $('#catform').is(":hidden")) keyOpenMenu(e.shiftKey || e.ctrlKey);
			break;
		case 39: // right
			if(currentsvg && keyediting && $('#funcform').is(":hidden") && $('#catform').is(":hidden")) moveGov(1);
			break;
		case 40: // down
			if(currentsvg && keyediting && $('#funcform').is(":hidden") && $('#catform').is(":hidden")) keyOpenMenu(e.shiftKey || e.ctrlKey);
			break;
		case 99: // "c"
			if(currentsvg && keyediting && $('#funcform').is(":hidden") && $('#catform').is(":hidden")) keyOpenMenu(true);
			break;
		case 102: // "f"
			if(currentsvg && keyediting && $('#funcform').is(":hidden") && $('#catform').is(":hidden")) keyOpenMenu(false);
			break;
		case 115: // "s"
			
			if(e.ctrlKey && dirty) saveTree(false);
			
			return false; 
		default:
		return true;
		}
		
	}); 

}

keyOpenMenu = function (cat) {

	
// 	$("#sentinfo").html(" lastSelected "+" "+cat)

	if (cat) openCatMenu(currentsvg.words[lastSelected].svgs["cat"]);
	else 
	{
		i = (isDrag.index==lastSelected ? 0 : isDrag.index);
		openFunctionMenu(currentsvg.words[lastSelected].svgdep[i][0]);
	}
}


nextword = function (forward) {
	
	if (!currentsvg) return;
	$('#funcform').hide();
	$('#catform').hide();
	
	if (forward) lastSelected++;
	else  lastSelected--;
	if (lastSelected > Object.keys(currentsvg.words).length) lastSelected=1;
	else if (lastSelected<=0) lastSelected=Object.keys(currentsvg.words).length;
	for (gov in currentsvg.words[lastSelected].govs) break; // get first (any) gov

	keyConnection(gov);

}


keyConnection = function (gov) {
	
	var p = $(currentsvg).position();
	for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris["t"]);
	keyediting=true;
// 	$("#sentinfo").html(" keyConnection "+gov)
	if (gov==0 || gov==lastSelected) //root
	{
		isDrag = currentsvg.words[lastSelected].svgs.t;
		isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
		isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
		moveConnection(isDrag.attr("x")+p.left+isDrag.width/2,p.top);
	}
	else
	{
		isDrag = currentsvg.words[gov].svgs.t; // gov node
		isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
		isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
		depn = currentsvg.words[lastSelected].svgs.t
		moveConnection(depn.attr("x")+p.left+depn.width/2,depn.attr("y")+p.top);
		depn.attr(attris["target"]);
	}
	currentsvg.dragConnection.show();
	currentsvg.dragConnection.toFront();
	isDrag.attr(attris["source"]);
	return false;
}

reset = function () {
	if (currentsvg) 
	{
		currentsvg.dragConnection.hide();
		for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris["t"]);
	}
	keyediting=false;
	isDrag = false;
	$('#funcform').hide();
	$('#catform').hide();
	lastSelected=0;
	
}


nextsentence = function () {

	reset();
	nr = parseInt(currentsvg.id.slice(3));
	$(".toggler").removeClass("currentsentence");	
	nr++;
	if (nr > numbersent) nr=0;
	else if (nr<0) nr=numbersent	;
	nexttog = $(".toggler:eq("+nr+")");
	
// 	$("#sentinfo").html(nexttog.hasClass("expanded")+"nr "+nr);
	if ( nexttog.hasClass("expanded") ) 
	{
		currentsvg=$("#svg"+(nr))[0];
	}
	else nexttog.click();
	
	$("html,body").animate({scrollTop: $(currentsvg).offset().top-[50]},700); // scroll to -50 speed .7 seconds

	nexttog.addClass("currentsentence");

}

moveGov = function (dir) {
	var n = Object.keys(currentsvg.words).length;
	keyConnection((((parseInt(isDrag.index)+dir-1)%n)+n)%n + 1 ) // javascript modulo bug for negative numbers workaround :-s
}

/////////////////// end key stuff


///////////// end editing


////////////////////////////////////////////////////////////////
/////////////////////essential drawing stuff////////////////////
////////////////////////////////////////////////////////////////
    
    
drawsvgDep = function(ind,govind,x1,y1,x2,y2,func,lineattris,textattris)
	{
		var set=currentsvg.paper.set();
		var x1x2=Math.abs(x1-x2)/2;
		var yy = Math.max(y1-x1x2-worddistancefactor*Math.abs(ind-govind),-tokdepdist);
		yy = Math.min(yy,y1-depminh);

		var cstr="M"+x1+","+y1+"C"+x1+","+yy+" "+x2+","+yy+" "+x2+","+y2;
		var c = currentsvg.paper.path(cstr).attr(attris["depline"]).attr({"x":x1,"y":y1});

		var poi = currentsvg.paper.pointer(x2,y2,pois,0).attr(attris["depline"]);

		a=c.getPointAtLength(c.getTotalLength()/2);
		t = currentsvg.paper.text(a.x, a.y-funccurvedist, func);
		t.attr(attris["deptext"]);
		t.attr(textattris);
		t.index=ind;
		t.govind=govind;
		
		if (editable) t.click(function (e) {
				openFunctionMenu(this);
			})
		
		if (govind==0) { // case: head of sentence (root): the function name needs special treetment
			var newx=a.x+t.getBBox().width/2+funccurvedist/2;
			if (newx+t.getBBox().width/2 > svgwi) newx=a.x-t.getBBox().width/2-funccurvedist/2;
			if (newx-t.getBBox().width/2 < 0) newx=a.x;
			t.attr("x",newx);
		}
			
		if ("dependency" in colored && func in fcolors)
		      {
			var color = "#"+fcolors[func];
			c.attr({stroke: color});
			poi.attr({stroke: color});
			t.attr({fill: color});
		      };
		c.attr(lineattris);
		poi.attr(lineattris);
		
		set.push(t); // text
		set.push(c); // curve
		set.push(poi); // pointer
		
		return set;
	};
	

drawDep = function(ind,govind,func,c)	// draw dependency of type func from govind to ind (c is usually 0, only for multiple heads)
	{

		if (govind==0 ) // head of sentence
		{
			node2=currentsvg.words[ind];
			var x2=node2.svgs[shownfeatures[0]].attr("x")+node2.svgs[shownfeatures[0]].width/2;
			var y2=node2.svgs[shownfeatures[0]].attr("y")-tokdepdist;
			var x1=x2;
			var y1=0;
		}
		else // normal dependency
		{
			var node1=currentsvg.words[govind];
			var node2=currentsvg.words[ind];
			if (node1==null) {delete node2.govs[govind];return;}
			if (ind<govind) var x1=node1.svgs[shownfeatures[0]].attr("x")+node1.svgs[shownfeatures[0]].width/2-xoff;
			else var x1=node1.svgs[shownfeatures[0]].attr("x")+node1.svgs[shownfeatures[0]].width/2+xoff;
			var x2=node2.svgs[shownfeatures[0]].attr("x")+node2.svgs[shownfeatures[0]].width/2;
			var y1=node1.svgs[shownfeatures[0]].attr("y")+pois-tokdepdist;
			var y2=node2.svgs[shownfeatures[0]].attr("y")-tokdepdist-c*linedeps;
		};
		node2.svgdep[govind]=drawsvgDep(ind,govind,x1,y1,x2,y2,func, node2.deplineattris, node2.deptextattris);
	};


drawalldeps = function() 
	{
		
	for (var i in currentsvg.words)
		{
			var n = currentsvg.words[i];
			for (var i in n.svgdep) 
				{
				n.svgdep[i].remove();
				delete n.svgdep[i];
				}
			n.svgdep={};
			var c=0;
			for (var i in n.govs) 
			{
				drawDep(n.index,i,n.govs[i],c);
				c+=1;
			};
		  };
	};

////////////////////////// initialisation ///////////////////////////
/////////////////////////////////////////////////////////////////////



makewords = function() 
	{
		var words = new Object();
		svgwi=0;
		currentx=tab;
		for (var i in tokens) 
			{
			var node = new Pnode( i, tokens[i]);
			words[i]=node;
			currentx=currentx+node.width+tab;
			};
		
		return words;
	};


	
start = function (holder, nr) {

	paper = Raphael(holder, window.innerWidth-100,100);
	currentsvg=paper.canvas;
	currentsvg.paper=paper;
	currentsvg.id="svg"+nr;
	currentsvg.words = makewords();
	if (editable) 
	{
		currentsvg.dragConnection = createConnection().hide();
		lastSelected=0;
	}
	currentsvg.setAttribute("width",svgwi+extraspace);
	currentsvg.setAttribute("height",dependencyspace+shownfeatures.length*line);
	drawalldeps();
	$("html,body").animate({scrollTop: $(currentsvg).offset().top-[50]},700);
	$(".toggler").removeClass("currentsentence");
	$(".toggler:eq("+nr+")").addClass("currentsentence");
	currentsvg.undo = new UndoManager();  
	
};

//////////////////////////////////////////////////////////////////////

Raphael.fn.pointer = function (x,y, size, angle) {
	var startpoint = x+","+(y+size);
	var lefttop = "0,0" +(-size/2)+","+(-size*1.5)+" "+(-size/2)+","+(-size*1.5);
	var righttop = (size/2)+"," +(size/2)+" "+(size/2)+"," +(size/2)+ " "+(size)+",0";
	var arrowPath = this.path("M"+ startpoint+"c"+lefttop+ "c"+righttop+ "z");
	arrowPath.rotate(angle);
	return arrowPath;
}

$(document).ready(function(){

	$(".toggler").click(function()
		{
		if (!$(this).hasClass("expanded"))
		{
			if (editable) 
			{
				var nr=$(this).attr("nr");
				var treeid=$(this).attr("treeid");
				$(this).parent().after('<div id="holder'+nr+'" class="svgholder"> </div>');
				getTree(project,treeid, nr);
			}
			else if (conllview)
			{
				var nr=$(this).attr("nr")
				$(this).parent().after('<div id="holder'+nr+'" class="svgholder"> </div>');
				getTreeFromConllFile(filename,nr,filetype);
			}
		}
		else
		{
			$("#holder"+$(this).attr("nr")).remove();
			$("#edit"+$(this).attr("nr")).remove();
			reset();
			$(".toggler").removeClass("currentsentence");
			currentsvg=false;
		}
		$(this).toggleClass('expanded');
		})
	onkey();
});



var tokens=new Object();

getTree = function(project, treeid, nr) {
        delete tokens;
        tokens=new Object();
        $.getJSON(
	      "getTree.cgi",
	      {
		    project: project,
		    treeid: treeid,
// 		    number: nr,
// 		    uid: uid,
// 		    sid: sid
	      },
	      function(data)
			{
				$.each(data, function(key, val) 
				{
					tokens[key]=val;
				});
				start("holder"+nr, nr);
			}
        );
}

getTreeFromConllFile = function(id, nr, type) {
        delete tokens;
        tokens=new Object();
        $.getJSON(
	      "getTreeFromConllFile.cgi",
	      {
		    id: id,
		    nr: nr,
		    type: type
	      },
	      function(data)
		    {
				$.each(data, function(key, val) 
				{
				        tokens[key]=val;
				});
			  start("holder"+nr, nr);
		    }
        );
}

