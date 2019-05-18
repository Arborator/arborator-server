/*!
 * arborator script for dependency drawing
 * version 1.0
 * http://arborator.ilpga.fr/
 *
 * Copyright 2010-2018, Kim Gerdes
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



attrdirty = {"value":"save all modified trees",'disabled':false,"cursor":"pointer"};
attrclean = {"value":"all trees are saved",'disabled':true,"cursor":"default"};

noshowtokens = {'misc':{"SpaceAfter=No":"_"}}

///////////////////////// node object and functions ////////////////
////////////////////////////////////////////////////////////////////


var currentsvg=false;
var isSelected=false;
var isDrag=false;
var dirty=[]; // list of dirty svgs
var lastSelected;
var keyediting=false;
var nokeys=false;
var numbersent=0;

function Pnode(index,token)
	{
		index=parseInt(index,10);
		this.index=index;
		this.gov={};
		if ("gov" in token)
		{
			for (var i in token["gov"])
			{
				this.gov[parseInt(i,10)]=token["gov"][i]
			}
		}
		this.width=0;
		this.features=new Object(); // contains for each shownfeature the corresponding text
		this.svgs=new Object(); // contains for each shownfeature the corresponding svg object
		var currenty=dependencyspace;

// 		console.log("________________________",index);


		for (var i in shownfeatures)
			{
			var f = shownfeatures[i]; // f= eg. "cat"
			if (token[f]===undefined) {token[f] = "_";} // 😐
			this.features[f]=token[f];

			if ( (token[f] instanceof Object) ) // mode compare!!!
			{

				var user0=token[f][0][1][0];
				if (user0=="ok")
				{
					c=token[f][0][0]
					var t = paper.text(currentx, currenty, c);
					t.attr(defaultattris);
					t.attr({fill: "#"+compacolors[user0],title:"All annotators agree."});
				}
				else
				{
					c=""
					ti=""
					for (i in token[f])
					{
						c=c+" "+token[f][i][0];
						ti=ti+" "+token[f][i][0]+" ("+token[f][i][1]+")";
					}
					var t = paper.text(currentx, currenty, c);
					t.attr(defaultattris);
					t.attr({fill: "red",title:ti});

				}


			}
			else // normal mode
			{
				if (f in noshowtokens && token[f] in noshowtokens[f])
					{tokenf=noshowtokens[f][token[f]];  }
				else 	{tokenf=token[f];}
				var t = paper.text(currentx, currenty, tokenf);
				t.attr(defaultattris);
				if (f in token) t.attr(attris[f]);
			}
			t.attr("index",index);
			var wi=t.getBBox().width;
			t.width=wi;
			t.index=index;

			t.node.setAttribute("class",f);
			if (f in colored && token[f] in catDic) t.attr(catDic[token[f]]);
			this.svgs[f]=t;
			if (wi>this.width) this.width=wi;

			currenty=currenty+line;

			};

		for (var a in token) // remaining features
			{
				v=token[a]
				if (a in this.features || a=="gov") continue;
				this.features[a]=v;
			}

		if (editable) activate(this.svgs[shownfeatures[0]], this.svgs[shownfeatures[categoryindex]]);

		//svgwi=svgwi+this.width+tab;
		this.x=0;
		this.y=0;
		this.svgdep={};		// the svg dependency (the arrow and the function name): gives the svgobject for each govind

	};

	// add-on 1 by Luigi : adjust the current token width in fonction of the label width
	tokenWidthDetection = function(node)
	{
		// node.width defines the common width of each of
		// feature texts related to a token
		var index = node.index;
		var new_width = node.width;
		for (var gov_index in node.gov) {

			if (gov_index - index == 1) {
				// as left-adjacent dependent of its governor, this token
				// adapt its width in fonction of arc label width
				var label = node.gov[gov_index];
				var min_width = label.length * _FONTSIZE * .75;
				if (new_width < min_width) {
					new_width = min_width;
					needRespace = true;
				}
			}

			if (index + 1 in tokens) {
				for (var i in tokens[index + 1].gov) {
					if (i == index) {
						// as left-adjacent governor of one of its dependent, this token
						// adapt its width in fonction of arc label width
						var label = tokens[index + 1].gov[i];
						var min_width = label.length * _FONTSIZE * .85;
						// then adapt its width to the width of this label
						if (new_width < min_width) {
							new_width = min_width;
							needRespace = true;
						}
						//console.log(label,tokens[index].t,tokens[index+1].t,this.width,min_width);
					}
				}
			}
		}
		return new_width;

	} // end of tokenWidthDetection





//////////////////////////// only used for editing:
////////////////////////////////////////////////////////




createConnection = function () {

	$(currentsvg).mousemove(function(e)
	{
// 		console.log("ddd",currentsvg.id,$(currentsvg));
		if (currentsvg!=this)
		{
			reset()
			$(".toggler").removeClass("currentsentence"); // remove it from all togglers
			currentsvg=this;
			currentsvgchanged();
			$(".toggler:eq("+(parseInt(currentsvg.id.slice(3))-1)+")").addClass("currentsentence");
		}
		if ( isDrag && !keyediting )
		{

			moveConnection(e.pageX - $(document).scrollLeft() - $(currentsvg).offset().left +3, e.pageY - $(currentsvg).offset().top - 10);

			isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
			isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
		}
	}).mouseup(function(e)
	{
// 		console.log(e,"mouseup, isSelected:",isSelected , "yyyyyy",isDrag  ,isDrag.svg,"uuuuuuuuuuuuu",currentsvg ,isDrag.svg==currentsvg ,lastSelected)
// 		if (isSelected) console.log(isSelected.index);

		emptyclick=true;
		if (isSelected && isDrag && isSelected!=isDrag && isDrag.svg==currentsvg && isSelected.index!=lastSelected)
			{ changeDrag(isDrag.index,isSelected.index);emptyclick=false;};
		if (isDrag && isDrag.rooting)
			{ changeDrag(0,isDrag.index);emptyclick=false;}
		setTimeout("isDrag = false;",500);

		for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris[shownfeatures[0]]);

		if (emptyclick)
			{
// 				console.log("emptyclick")
				$('#funcform').hide(); $('#catform').hide(); $('#ex').hide(); $('#compbox').hide(); $('#checkbox').hide();
// 				currentsvg.dragConnection.hide();

				if (isDrag)
				{
					lastSelected=isDrag.index;
					gov=null;
					for (gov in currentsvg.words[lastSelected].gov) break; // get first (any) gov

					if (gov!=null) keyConnection(gov);
				}

			}
		else {$("#catchoice").focus();}
		isDrag = false;
		currentsvgchanged();
// 		console.log(3)
	});


// 	  attris["dragdepline"], attris["deptext"],
	return drawsvgDep(1,2,50,60,150,150,"", "",false,0); // arbitrary points

}


activate = function (t,cat) /*makes word node t (t=token, cat=cat) interactive  */
{
	t.attr({cursor:"move"}).mousedown(dragger).mouseover(function () {
// 		console.log("mouseover",t,isDrag,t==isDrag,keyediting,isSelected)
		if (t==isDrag || keyediting) return;
		isSelected=t;

// 		console.log("isSelected:",isSelected)
		if (isDrag)
			{
				for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris[shownfeatures[0]]);
				t.attr(attris["target"]);
				isDrag.attr(attris["source"]);
			}
	}).mouseout(function () {
		if (t==isDrag  || keyediting) return;
// 		console.log("mouseout",t,isDrag,t==isDrag,keyediting,isSelected)
		isSelected=null;
		for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris[shownfeatures[0]]);
		currentsvgchanged();

	}).dblclick(function () {
		openFeatureTable(this.index,currentsvg.words)
	})
	cat.click(function (e) {openCatMenu(this);})
}


var dragger = function (e) {

// 	console.log("____",currentsvg);
	if(e.ctrlKey) return true; // to allow dbl click if nothing else works. ugly hack!
	reset();
	isDrag = this;
	lastSelected=this.index;
	isDrag.rooting=false;
	isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
	isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
// 	moveConnection(e.pageX,e.pageY);
	moveConnection(e.pageX - $(document).scrollLeft() - $(currentsvg).offset().left +3, e.pageY - $(currentsvg).offset().top - 10);

	currentsvg.dragConnection.show();
	currentsvg.dragConnection.toFront();
	isDrag.svg=currentsvg;
	e.preventDefault && e.preventDefault();
    };




changeDrag = function (gov, dep) /* reaction if good connection was created, gov and dep are indeces */
{
// 	console.log("changedrag",gov,dep)
	var depn=currentsvg.words[dep];
	var func = null;
	for (i in depn.gov) { func = depn.gov[i]; break;}
	var c=currentsvg.dragConnection[1];
	a=c.getPointAtLength(c.getTotalLength()/2);
	svgpos=$(currentsvg).offset();
	openFunctionMenu(dep,gov,func,  svgpos.left+a.x, svgpos.top+a.y-funccurvedist);

}

clickOpenFunctionMenu = function(funcnode)  // funcnode=svg text node of the dependency link
	{
// 		console.log("clickOpenFunctionMenu",funcnode,$(currentsvg).position())
// 		svgpos=$(currentsvg).position();
// 		console.log("jjjj",$(currentsvg),currentsvg.id);
		svgpos=$(currentsvg).offset()
		openFunctionMenu(funcnode.index, funcnode.govind, funcnode.attr("text"), svgpos.left+funcnode.attr("x")-20, svgpos.top+funcnode.attr("y")-7 );   // TODO: make the position of the function menu parametrizable
	}


openFunctionMenu = function(ind,govind,func,x,y)  // called from clickOpenFunctionMenu and from changeDrag, changeFunc closes the menu
	{
// 		currentnr = $(currentsvg).parent().attr("nr");
// 		console.log("kkkk",$(currentsvg),currentsvg.id);
		var ff=$('#funcform');
		var os=$("#funchoice")[0].options;
		funcnum=functions.indexOf(func);
		if (funcnum==null) funcnum=0;
		if (funcnum in os) os[funcnum].selected = true;
		ff.css({ top: y, left: x });
		ff.show();
		$("#funchoice").focus()
		ff.data("index", ind);
		ff.data("govind", govind);
		lastSelected = ind;
	}

openCatMenu = function(catnode)  // funcnode=svg text node of the dependency link
	{
		var cc=$('#catform');
		catnum=categories.indexOf(catnode.attr("text"));
		if (catnum<0) catnum=0;
		svgpos=$(currentsvg).position();
		var os=$("#catchoice")[0].options;
		if (catnum in os) os[catnum].selected = true;
// 		console.log(svgpos)
		cc.css({ top: svgpos.top+catnode.attr("y")-7, left: svgpos.left+catnode.attr("x")-7});
// 		+catnode.width
		cc.show();
		$("#catchoice").focus();
		cc.data("index",catnode.index);
		lastSelected = catnode.index;
	}




function changeFunc(event){ // called by onclick on the func menu or return

	var addDep=event.shiftKey;
	var ff=$('#funcform');
	if (ff.is(":hidden")) return false;
	var func=$("#funchoice")[0].options[$("#funchoice")[0].selectedIndex].value;
	var id = ff.data("index");
	var govid = ff.data("govind");
	if (id==govid) govid=0;
	if (func==null) func=defaultfunction;
	gi2f = new Object(); // governor index to function
	gi2f[govid]=func;
	if (func==erase) eraseRelation(id, gi2f)
	else if (addDep) addRelations(id, gi2f);
	else establishRelations(id,gi2f );
	ff.hide();
	currentsvg.dragConnection.hide();


}




function establishRelations(depind,gi2f)
{
	var depn=currentsvg.words[depind];
	for (i in depn.svgdep) { depn.svgdep[i].remove(); }
	oldgi2f={};
	info="removing"
	for (var i in depn.gov)
	{
		oldgi2f[i]=depn.gov[i]
		if (i in currentsvg.words) info=info+" link "+ currentsvg.words[i].features.t + " ―"+ depn.gov[i]+ "→ "+depn.features.t + " ";
		else info=info+" link ―"+depn.gov[i]+ "→ "+depn.features.t;
	}

	depn.gov={}

	info = info + " and replacing by"

	for (var i in gi2f)
	{
		depn.gov[i]=gi2f[i]
		tokens[depind].gov[i]=gi2f[i] // Luiig : sync tokens[depind] with depn
		if (i in currentsvg.words) info=info+" link "+ currentsvg.words[i].features.t + "―" + gi2f[i] + "→ "+depn.features.t + " ";//normal link
		else info=info+" link ―" + gi2f[i] + "→ "+depn.features.t;//root link

	}

	if (_TOKEN_WIDTH_RESIZING){
		// redrawing tokens before redraw relations
		currentsvg.paper.clear();
		currentsvg.words = makewords();
	}
	drawalldeps(); //

	currentsvg.undo.undoable(info, establishRelations, [depind, oldgi2f]);

}


function eraseRelation(depind,gi2f)
{
	var depn=currentsvg.words[depind];
	for (i in depn.svgdep) { depn.svgdep[i].remove(); }
	info="removing"
	oldgi2f={};
	for (var i in depn.gov)
	{
		oldgi2f[i]=depn.gov[i]
		if (i in gi2f)
		{
			delete depn.gov[i];
			if (i in currentsvg.words) info=info+" link "+ currentsvg.words[i].features.t + " ―"+ depn.gov[i]+ "→ "+depn.features.t + " ";
			else info=info+" link ―"+depn.gov[i]+ "→ "+depn.features.t;
		}
	}

	if (_TOKEN_WIDTH_RESIZING){
		// redrawing tokens before redraw relations
		currentsvg.paper.clear();
		currentsvg.words = makewords();
	}
	//drawalldeps(); //

	currentsvg.undo.undoable(info, establishRelations, [depind,oldgi2f]);



}

function addRelations(depind,gi2f)
{
	var depn=currentsvg.words[depind];

	for (i in depn.svgdep) { depn.svgdep[i].remove(); }

	oldgi2f={};

	for (var i in depn.gov) oldgi2f[i]=depn.gov[i]

	info = "adding"

	for (var i in gi2f)
	{
		depn.gov[i]=gi2f[i]

		if (i in currentsvg.words) info=info+" link "+ currentsvg.words[i].features.t + "―" + gi2f[i] + "→ "+depn.features.t + " ";//normal link
		else info=info+" link ―" + gi2f[i] + "→ "+depn.features.t;//root link

	}

	if (_TOKEN_WIDTH_RESIZING){
		// redrawing tokens before redraw relations
		currentsvg.paper.clear();
		currentsvg.words = makewords();
	}
	drawalldeps();
	currentsvg.undo.undoable(info, establishRelations, [depind, oldgi2f]);

}


function changeCat(){ // called by onclick on the menu or return

	var cc=$('#catform');
	if (cc.is(":hidden")) return false;
	var cat=$("#catchoice")[0].options[$("#catchoice")[0].selectedIndex].value;
	if (cat==null) cat=defaultcategory;
	var id = cc.data("index");
	establishCat(id,cat);
	cc.hide();

}

function establishCat(ind,cat)
{
	var node=currentsvg.words[ind];
	var oldcat=node.features[shownfeatures[categoryindex]];
	var info="replacing the category "+oldcat+"of the node "+currentsvg.words[ind].features.t+" by "+cat
	node.features[shownfeatures[categoryindex]]=cat;
	node.svgs[shownfeatures[categoryindex]].attr("text",cat);

	// added by Luigi
	if (_TOKEN_WIDTH_RESIZING){
		currentsvg.paper.clear();
		tokens[ind][shownfeatures[categoryindex]] = cat // sync tokens[ind]'s feature with the new one
		currentsvg.words = makewords();
		drawalldeps(); //
	}
	currentsvg.undo.undoable(info, establishCat, [ind, oldcat]);


}

moveConnection = function(x2,y2) // moves the connection so that it links the isDrag-element -------> to the x2,y2 position
	{

		if (!isDrag || !currentsvg) return;
		var wi = isDrag.width/2;
		var wix = Math.max(wi,rootTriggerSquare/2);
		if (x2<=isDrag.attr("x")+wi) var x1=isDrag.attr("x")+wi-xoff; // 1st case: cursor to the right of the word
		else var x1=isDrag.attr("x")+wi+xoff; // 2nd case: cursor to the left of the word

// 		console.log(y2,rootTriggerSquare, y2<rootTriggerSquare,x2>isDrag.attr("x")+wi-wix ,x2<isDrag.attr("x")+wi+wix);
		if (y2<rootTriggerSquare && x2>isDrag.attr("x")+wi-wix && x2<isDrag.attr("x")+wi+wix) // 3rd case: cursor rooting above
			{
// 				console.log("iiiiiiiiiiiii")
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
// 		console.log(x1,y1,x2,y2,lineattris);

		/*
		var x1x2=Math.abs(x1-x2)/2;
		var yy = Math.max(y1-x1x2-worddistancefactor*3,-tokdepdist);// 3 is adhoc: curve looks like link between tokens that are 3 words apart. original: worddistancefactor*Math.abs(ind-govind) TODO: think about this...
		yy = Math.min(yy,y1-depminh);

		var path="M"+x1+","+y1+"C"+x1+","+yy+" "+x2+","+yy+" "+x2+","+y2;
		*/

		// add-on 4 by Luigi
		var toknum = Object.keys(currentsvg.words).length; // number of tokens
		var dict = {};
		for (i in currentsvg.words)
			for (j in currentsvg.words[i].gov)
			{
				var d = Math.abs(i-j);
				if (j == 0) d = toknum - 1; // root
				dict[i + ' ' + j] = d;
			}
		// sort the dictionary'keys by their associated values
		var tokenid_govind = Object.keys(dict).sort(function(a,b){return dict[a]-dict[b]});

		var arcnum = tokenid_govind.length;
		var gov_cnt = {}
		var heights = Array(toknum).fill(1);
		for (var i = 0; i < arcnum; i++)
		{
			// unpack tokenid_govind to token id and governor id
			tidgid = tokenid_govind[i].split(" ");
			var tid = parseInt(tidgid[0],10);
			var gid = parseInt(tidgid[1],10);
			var n = currentsvg.words[tid];
			if (!(tid in gov_cnt)) gov_cnt[tid] = 0;
			var c = gov_cnt[tid];
			gov_cnt[tid] += 1; // count num of governor
			var height = 1;
			var start = Math.min(tid, gid), end = Math.max(tid, gid);
			if (gid == 0) {start = 0; end = toknum - 1;}

			// get height for current arc
			for (var j = start + 1; j < end; j++) if (heights[j] > height) height = heights[j];
			if (gid != 0) for (var j = start; j <= end; j++) heights[j] = height + 1;

		};
		//
		var height = 1;
		for (var j = 0; j < toknum; j++) if (heights[j] > height) height = heights[j];


		var start_x = Math.min(x1,x2);
		var end_x   = Math.max(x1,x2);

		var heigh_pts = _ARC_HEIGHT_UNIT * Math.abs(height); // height in pxl
		var radius    = heigh_pts / (1 - Math.cos(_ANGLE));
		var length    = radius * Math.sin(_ANGLE) / 2;
		var yy        = Math.min(y1 - heigh_pts, y1 - depminh);

			// arc of other relations
			var cstr ="M" + start_x + "," + y1;
			cstr +="A" + radius + "," + radius + " 0 0 1 "+ (start_x + length / 2) + "," + yy;
			cstr +="L"+ (end_x - length / 2)   + "," + yy;
			cstr +="A" + radius + "," + radius + " 0 0 1 "+ end_x   + "," + y2;

			if (!_YANDEX_STYLE_EN) { // original arc drawing style
				//var x1x2=Math.abs(x1-x2)/2;
				//var yy = Math.max(y1-x1x2-worddistancefactor*Math.abs(ind-govind),-tokdepdist);
				//yy = Math.min(yy,y1-depminh);
				yy        = Math.min(y1 - worddistancefactor*heigh_pts, y1 - depminh);
				cstr="M"+x1+","+y1+"C"+x1+","+yy+" "+x2+","+yy+" "+(x2+.01)+","+y2;

			}

		var path = cstr;

		currentsvg.dragConnection[1].attr({path:path}).attr(lineattris);;// curve
		currentsvg.dragConnection[2].translate(x2-isDrag.ox,y2-isDrag.oy).attr(lineattris);; // pointer

// 		console.log(";;;",currentsvg.dragConnection[1],lineattris)

// 		if (currentsvg.dragConnection[1].getAttribute('stroke-dasharray')==0) // firefox/raphael bug!
// 		{
// 			currentsvg.dragConnection[1].removeAttribute('stroke-dasharray')
// 			currentsvg.dragConnection[2].removeAttribute('stroke-dasharray')
// 		}

	}





//////////////////////////////////////// keystuff ///////////////////////////////
////////////////////////////////////////////////////////////////////////////////


onkey = function () {
	$(document).keypress(function(e) {
		if (nokeys) return true;
		e.stopImmediatePropagation();
		var code = (e.keyCode ? e.keyCode : e.which);

		switch(code)
		{
		case 8: // backspace
			if(currentsvg) {nextword(0)}
			return true;
		case 9: // tab
			if(currentsvg) {nextsentence()}
			else $(".toggler:first").click().focus();
			return false;
		case 13: // return
			if(currentsvg && $('#funcform').is(":visible"))
			{
				changeFunc(e);
				if (keyediting) nextword(1);
			}
			else if (currentsvg && $('#catform').is(":visible"))
			{
				changeCat();
				if (keyediting) nextword(1);
			}
			else if (currentsvg && keyediting)
			{
				changeDrag(isDrag.index,lastSelected )
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
			if(e.ctrlKey && dirty!=[] && currentsvg.words) saveAllTrees();
			return false;
		default:
			return true;
		}

	});

}

keyOpenMenu = function (cat) {
// 	console.log("keyOpenMenu",cat);

// 	$("#sentinfo").html(" lastSelected "+" "+cat)

	if (cat) openCatMenu(currentsvg.words[lastSelected].svgs["cat"]);
	else
	{
		i = (isDrag.index==lastSelected ? 0 : isDrag.index);
		clickOpenFunctionMenu(currentsvg.words[lastSelected].svgdep[i][0]);
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
	gov=0; // in case a node has no governor
	for (gov in currentsvg.words[lastSelected].gov) break; // get first (any) gov
	keyConnection(gov);

}


keyConnection = function (gov) {

// 	var p = $(currentsvg).position();
	for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris[shownfeatures[0]]);
	keyediting=true;
	if (gov==0 || gov==lastSelected) //root
	{
		isDrag = currentsvg.words[lastSelected].svgs[shownfeatures[0]];
		isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
		isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
// 		moveConnection(isDrag.attr("x")+p.left+isDrag.width/2-10,p.top);
		moveConnection(isDrag.attr("x")+isDrag.width/2,0);
	}
	else
	{
		isDrag = currentsvg.words[gov].svgs[shownfeatures[0]]; // gov node
		isDrag.ox=currentsvg.dragConnection[2].getPointAtLength(0).x;
		isDrag.oy=currentsvg.dragConnection[2].getPointAtLength(0).y;
		depn = currentsvg.words[lastSelected].svgs[shownfeatures[0]];
// 		moveConnection(depn.attr("x")+p.left+depn.width/2,depn.attr("y")+p.top);
		moveConnection(depn.attr("x")+depn.width/2,depn.attr("y")-10);
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
// 		currentsvg.dragConnection.hide();
		for (var i in currentsvg.words) currentsvg.words[i].svgs[shownfeatures[0]].attr(attris[shownfeatures[0]]);
	}
	keyediting=false;
	isDrag = false;
	$('#funcform').hide();
	$('#catform').hide();
	$('#ex').hide();
// 	lastSelected=0;

}


nextsentence = function () {

	reset();
	nr = parseInt(currentsvg.id.slice(3));
	$(".toggler").removeClass("currentsentence");
	if (nr >= numbersent) nr=0;
	else if (nr<0) nr=numbersent	;
	nexttog = $(".toggler:eq("+(nr)+")");
	if ( nexttog.hasClass("expanded") )
	{
		currentsvg=$("#svg"+(nr+1))[0];
	}
	else nexttog.click();

	$("html,body").animate({scrollTop: $(currentsvg).offset().top-[100]},500); // scroll to -100 speed .7 seconds

	nexttog.addClass("currentsentence");

}

moveGov = function (dir) {
	var n = Object.keys(currentsvg.words).length;
// 	console.log("isDrag",isDrag,isDrag.index);
	keyConnection((((parseInt(isDrag.index)+dir-1)%n)+n)%n + 1 ) // javascript modulo bug for negative numbers workaround :-s
}

/////////////////// end key stuff


///////////// end editing


////////////////////////////////////////////////////////////////
/////////////////////essential drawing stuff////////////////////
////////////////////////////////////////////////////////////////
var _FONTSIZE        = 12;
var _ARC_HEIGHT_UNIT = _FONTSIZE * 1.2;
var _ANGLE           = Math.PI / 3;
var _YANDEX_STYLE_EN      = true;  // Yandex or Arborator style
var _TOKEN_WIDTH_RESIZING = true; // auto adapt token width to associated label widths

drawsvgDep = function(ind,govind,x1,y1,x2,y2,func,tooltip, color, funcposi,height = 1)
	{
		// ind: word index
// 		govind: index of governor
// 		x1,y1: start coordinates
// 		x2,y2: target coordinates
// 		func: function name
// 		tooltip, color, funcposi: only for compare mode
// 		console.log("drawsvgDep",ind,govind,func);
		var set=currentsvg.paper.set();

		// add-on 3 by Luigi
		// Yandex-style tree layout
		// code inspired from https://github.com/vieenrose/dep_tregex/blob/master/dep_tregex/tree_to_html.py


			var start_x = Math.min(x1,x2);
			var end_x   = Math.max(x1,x2);

			var heigh_pts = _ARC_HEIGHT_UNIT * Math.abs(height); // height in pxl
			var radius    = heigh_pts / (1 - Math.cos(_ANGLE));
			var length    = radius * Math.sin(_ANGLE) / 2;
			var yy        = Math.min(y1 - heigh_pts, y1 - depminh);

			if (govind == 0) {
				// vertical line for root
				ytop = y2 - heigh_pts;
				var cstr ="M" + start_x + "," + ytop ;
				cstr +="L"+ end_x  + "," + y2;

			}
			else {
				// arc of other relations
				var cstr ="M" + start_x + "," + y1;
				cstr +="A" + radius + "," + radius + " 0 0 1 "+ (start_x + length / 2) + "," + yy;
				cstr +="L"+ (end_x - length / 2)   + "," + yy;
				cstr +="A" + radius + "," + radius + " 0 0 1 "+ end_x   + "," + y2;

				if (!_YANDEX_STYLE_EN) { // original arc drawing style
					//var x1x2=Math.abs(x1-x2)/2;
					//var yy = Math.max(y1-x1x2-worddistancefactor*Math.abs(ind-govind),-tokdepdist);
					//yy = Math.min(yy,y1-depminh);
					var yy        = Math.min(y1 - worddistancefactor*heigh_pts, y1 - depminh);
					var cstr="M"+x1+","+y1+"C"+x1+","+yy+" "+x2+","+yy+" "+(x2+.01)+","+y2;

				}
			}





		var c = currentsvg.paper.path(cstr).attr(attris["depline"]).attr({"x":x1,"y":y1,"smooth":true});
// 		console.log("'''",c.getTotalLength());
		var poi = currentsvg.paper.pointer(x2,y2,pois,0).attr(attris["depline"]);
// 		.data("xfunc",func);

		a=c.getPointAtLength(c.getTotalLength()/2); // put text in the middle of arc
		if (govind == 0) a=c.getPointAtLength(0); // Luigi : root style ajustement : put text on the top of a root
		t = currentsvg.paper.text(a.x, a.y-funccurvedist-funcposi*10, func);
		t.attr(attris["deptext"]);
		t.index=ind;
		t.govind=govind;
		if (editable) t.click(function (e) {
// 				console.log(e);
				clickOpenFunctionMenu(this);
			})

		/*
		if (govind==0 && !_YANDEX_STYLE_EN) { // case: head of sentence (root): the function name needs special treetment

				var newx=a.x+t.getBBox().width/2+funccurvedist/2;
				if (newx+t.getBBox().width/2 > svgwi) newx=a.x-t.getBBox().width/2-funccurvedist/2;
				if (newx-t.getBBox().width/2 < 0) newx=a.x;
// 			console.log("--",c.getPointAtLength(100),c.getTotalLength(),t,a.y-funccurvedist-funcposi*10,a.y,funccurvedist,funcposi*10)
				t.attr("x",newx);
		}
		*/
// 		console.log(color,colored,functions)
		if (color) // case compare: colors depend on users
		{
			c.attr({stroke: color});
			poi.attr({stroke: color});
			t.attr({fill: color,title:tooltip});
		}
		else if ("dependency" in colored && func in funcDic) // normal graph: color depends on function
		      {
			var att = funcDic[func];
			c.attr(att);
			poi.attr({"stroke": att["stroke"]});
			t.attr({fill: att["stroke"]});
		      };
		if (c.node.getAttribute('stroke-dasharray')==0) // firefox/raphael bug!
			c.node.removeAttribute('stroke-dasharray');
		if (poi.node.getAttribute('stroke-dasharray')==0)
			poi.node.removeAttribute('stroke-dasharray');

		set.push(t); // text
		set.push(c); // curve
		set.push(poi); // pointer
		return set;
	};


drawDep = function(ind,govind,func,c, height)	// draw dependency of type func from govind to ind (c is usually 0, only for multiple heads)
	{
		if (govind==0 ) // head of sentence
		{
			node2=currentsvg.words[ind];
			var x2=node2.svgs[shownfeatures[0]].attr("x")+node2.svgs[shownfeatures[0]].width/2;
			var y2=node2.svgs[shownfeatures[0]].attr("y")-tokdepdist-c*linedeps;
			var x1=x2;
			var y1=0;
		}
		else // normal dependency
		{
			var node1=currentsvg.words[govind];	// from node
			var node2=currentsvg.words[ind];	// to node
			if (node1==null) {delete node2.gov[govind];return;}
			if (ind<govind) var x1=node1.svgs[shownfeatures[0]].attr("x")+node1.svgs[shownfeatures[0]].width/2-xoff;
			else var x1=node1.svgs[shownfeatures[0]].attr("x")+node1.svgs[shownfeatures[0]].width/2+xoff;
			var x2=node2.svgs[shownfeatures[0]].attr("x")+node2.svgs[shownfeatures[0]].width/2;
			var y1=node1.svgs[shownfeatures[0]].attr("y")+pois-tokdepdist;
			var y2=node2.svgs[shownfeatures[0]].attr("y")-tokdepdist-c*linedeps;
		};

		if ( (func instanceof Object) ) // mode compare!!!
		{
// 			console.log("start",ind,govind,func);
			var user0=func[0][1][0];

			if (user0=="ok")
			{
				func=func[0][0]
				node2.svgdep[govind]=drawsvgDep(ind,govind,x1,y1,x2,y2,func, "All annotators agree.", "#"+compacolors[user0],0, height);
// 				node2.deplineattris, node2.deptextattris,
			}
			else
			{
				var lastset=false;
				for (i in func)
				{
					var funcusers=func[i];
					i=parseInt(i,10);
					for (j in funcusers[1])
					{
						var u=funcusers[1][j];
						j=parseInt(j,10);
// 						console.log(node2.svgdep[govind]);
// 						if (node2.svgdep[govind]) alert("yyy");  node2.deplineattris, node2.deptextattris,
						var newset=drawsvgDep(ind,govind, x1+j*2,y1, parseInt(x2,10)+j*2, y2, funcusers[0], funcusers[0]+" ("+u+") ", "#"+compacolors[u], i+j, height);
// 						if (node2.svgdep[govind]) alert(newset);
						if (lastset) lastset.push(newset);
						else lastset=newset;
						node2.svgdep[govind]=lastset;
// 						console.log(node2.svgdep[govind]);

					}

// 					nfunc = nfunc +funcusers[0]+ " ";
// 					txt = txt+
				}
// 				func=nfunc

			}
// 			console.log(user0,func)  node2.deplineattris, node2.deptextattris,


		}
		// normal dependency:
		else node2.svgdep[govind]=drawsvgDep(ind,govind,x1,y1,x2,y2,func, "click to change", false, 0, height);
// 		console.log(":::",ind,govind,node2,node2.svgdep[govind])
//
	};

drawalldeps = function()
{

	// add-on 2 by Luigi : allocation of arc height
	// code inspired from https://github.com/vieenrose/dep_tregex/blob/master/dep_tregex/tree_to_html.py

	// get a list of token id and governor id pair sorted by distance
	// because shorter arc will occupy lower level of height
	var toknum = Object.keys(currentsvg.words).length; // number of tokens
	var dict = {};
	for (i in currentsvg.words)
		for (j in currentsvg.words[i].gov)
		{
			var d = Math.abs(i-j);
			if (j == 0) d = toknum - 1; // root
			dict[i + ' ' + j] = d;
		}
	// sort the dictionary'keys by their associated values
	var tokenid_govind = Object.keys(dict).sort(function(a,b){return dict[a]-dict[b]});

	var arcnum = tokenid_govind.length;
	var gov_cnt = {}
	var heights = Array(toknum).fill(1);
	for (var i = 0; i < arcnum; i++)
	{
		// unpack tokenid_govind to token id and governor id
		tidgid = tokenid_govind[i].split(" ");
		var tid = parseInt(tidgid[0],10);
		var gid = parseInt(tidgid[1],10);
		var n = currentsvg.words[tid];
		if (!(tid in gov_cnt)) gov_cnt[tid] = 0;
		var c = gov_cnt[tid];
		gov_cnt[tid] += 1; // count num of governor
		var height = 1;
		var start = Math.min(tid, gid), end = Math.max(tid, gid);
		if (gid == 0) {start = 0; end = toknum - 1;}

		// get height for current arc
		for (var j = start + 1; j < end; j++) if (heights[j] > height) height = heights[j];

		// clear
		for (var j in n.svgdep)
		{
			n.svgdep[j].remove();
			delete n.svgdep[j];
		};
		n.svgdep={};

		// draw this arc
		drawDep(tid,gid,n.gov[gid],c,height);

		// update heights
		if (gid != 0) for (var j = start; j <= end; j++) heights[j] = height + 1;

	};
};


drawalldeps2 = function()
	{

	var distdic = new Object();

	for (var i in currentsvg.words)
		{
			var n = currentsvg.words[i];
			for (var i in n.gov)
				{
					i=parseInt(i,10)
					if (i != 0)
					{
						dis=Math.abs(n.index-i)

						if (dis in distdic) distdic[dis].push([n.index,i])//
						else distdic[dis]=[ [n.index,i] ]
// 						console.log(n.index,i,dis,distdic,distdic[dis],n.gov)
					}
				};

		};

  drawalldeps();
	};

////////////////////////// initialisation ///////////////////////////
/////////////////////////////////////////////////////////////////////


function keys(obj)
	{
		var ks = [];

		for(var key in obj)
		{
			if (obj.hasOwnProperty(key)) ks.push(key);
		}

		return ks;
	}


makewordsxx = function()
	{
		var words = new Object();
		svgwi=0;
		currentx=tab;
// 		console.log("ttt",tokens)
// 		ks=keys(tokens);

// 		ks.sort();
// 		console.log("kkkk",ks)

		for (var i in ks)
			{
// 				console.log("iii",i, tokens[ks[i]]);
			var node = new Pnode(i, tokens[i]);
			if (_TOKEN_WIDTH_RESIZING) node.width = tokenWidthDetection(node);
			words[i]=node;
			currentx=currentx+node.width+tab;
			svgwi=svgwi+node.width+tab; // moved from inside Pnode to here
			};
			// adjust drawing paper width
			currentsvg.setAttribute("width",svgwi+extraspace);

		return words;
	};


makewords = function()
	{
		var words = new Object();
		// gloabl variable assignment
		svgwi=0;
		currentx=tab;
		for (var i in tokens)
		{
				var node = new Pnode(i, tokens[i]);
				if (_TOKEN_WIDTH_RESIZING) node.width = tokenWidthDetection(node);
				words[i]=node;
				currentx=currentx+node.width+tab;
				svgwi=svgwi+node.width+tab; // moved from inside Pnode to here
		};
		// adjust drawing paper width
		currentsvg.setAttribute("width",svgwi+extraspace);

		return words;
	};





start = function (holder, nr) {
// 	console.log("start",nr);
// 	settings();
	paper = Raphael(holder, window.innerWidth-100,100);
	currentsvg=paper.canvas;
	currentsvg.paper=paper;
	currentsvg.id="svg"+nr;

	draw();

// 	$("html,body").animate({scrollTop: $(currentsvg).offset().top-[100]},500);
	$(".toggler").removeClass("currentsentence");
	$(".toggler:eq("+(nr-1)+")").addClass("currentsentence");
	$("#export"+nr).css({ visibility: 'visible' });
	currentsvg.undo = new UndoManager({
				undoChange: function() { dirt(); },
				redoChange: function() { dirt(); }
					})




};


draw = function() {

	currentsvg.paper.clear();
	currentsvg.words = makewords();


	if (editable)
	{
		if(currentsvg.dragConnection) currentsvg.dragConnection = drawsvgDep(1,2,50,60,150,150,"", "",false,0).hide();
		else currentsvg.dragConnection = createConnection().hide();
		lastSelected=0;
	}
	currentsvg.setAttribute("width",svgwi+extraspace);
	currentsvg.setAttribute("height",dependencyspace+shownfeatures.length*line);

// 	TODO:work on the difference between drawalldeps and drawalldeps2
	drawalldeps();

}


currentsvgchanged = function () { } // to be overridden in q.js


// 	console.log(attris[shownfeatures[categoryindex]]);
// 	console.log(shownfeatures[categoryindex]);

//////////////////////////////////////////////////////////////////////

Raphael.fn.pointer = function (x,y, size, angle) {
	var startpoint = x+","+(y+size);
	var lefttop = "0,0" +(-size/2)+","+(-size*1.5)+" "+(-size/2)+","+(-size*1.5);
	var righttop = (size/2)+"," +(size/2)+" "+(size/2)+"," +(size/2)+ " "+(size)+",0";
	var arrowPath = this.path("M"+ startpoint+"c"+lefttop+ "c"+righttop+ "z");
	arrowPath.rotate(angle);
	return arrowPath;
}
