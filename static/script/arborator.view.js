/*!
 * arborator script for dependency viewing 
 * version 1.0
 * http://arborator.ilpga.fr/
 *
 * Copyright 2010-2016, Kim Gerdes
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


///////////////////////// settings //////////////// 
////////////////////////////////////////////////////////////////////


shownfeatures = ['t','cat','lemma'];
shownsentencefeatures = ['markupIU'];
functions = [];
funcDic = {};
categoryindex = '1';
root = 'ROOT';
catDic =  {} ;


tab=8; 		// space between tokens
line=25 		// line height
dependencyspace=320; 	// y-space for dependency representation
xoff=8; 		// placement of the start of a depdency link in relation to the center of the word
linedeps=6; 		// y distance between two arrows arriving at the same token (rare case)
pois=4; 		// size of arrow pointer
tokdepdist=15; 		// distance between tokens and depdendency relation
funccurvedist=8;	// distance between the function name and the curves highest point
depminh = 15; 		// minimum height for dependency
worddistancefactor = 2; 	// distant words get higher curves. this factor fixes how much higher.
extraspace=50 		// extends the width of the svg in order to fit larger categories
defaultattris={"font": '14px "Arial"', "text-anchor":'start'};
attris = {	"t":	{"font": '18px "Arial"', "text-anchor":'start',"fill": '#000',"stroke-width": '0'}, 
	"cat":	{"font": '12px "Times"', "text-anchor":'start',"fill": '#000'},
	"lemma":	{"font": '14px "Times"', "text-anchor":'start',"fill": '#000'},
	"depline":	{"stroke": '#000',"stroke-width":'1',"stroke-dasharray": ''},
	"deptext":	{"font": '12px "Times"', "font-style":'italic', "fill": '#000'},
	"form":	{"font-style":'italic'}
	  };

colored={"dependency":null}; //object of elements to be colored. just leave the object empty {} if you don't want colors
attris[shownfeatures[categoryindex]]=attris["cat"]
colored[shownfeatures[categoryindex]]=null;
	
	




///////////////////////// node object and functions //////////////// 
////////////////////////////////////////////////////////////////////


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
				
		
		for (var i in shownfeatures) 
			{	
			var f = shownfeatures[i]; // f= eg. "cat"
			
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
				var t = paper.text(currentx, currenty, token[f]);
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
		
			

		svgwi=svgwi+this.width+tab;
		this.x=0;
		this.y=0;
		this.svgdep={};		// the svg dependency (the arrow and the function name): gives the svgobject for each govind

	};



	

////////////////////////////////////////////////////////////////
/////////////////////essential drawing stuff////////////////////
////////////////////////////////////////////////////////////////



drawsvgDep = function(ind,govind,x1,y1,x2,y2,func,tooltip, color, funcposi)
	{
		// ind: word index
// 		govind: index of governor
// 		x1,y1: start coordinates
// 		x2,y2: target coordinates
// 		func: function name
// 		tooltip, color, funcposi: only for compare mode
		
		var set=currentsvg.paper.set();
		var x1x2=Math.abs(x1-x2)/2;
		var yy = Math.max(y1-x1x2-worddistancefactor*Math.abs(ind-govind),-tokdepdist);
		yy = Math.min(yy,y1-depminh);

		var cstr="M"+x1+","+y1+"C"+x1+","+yy+" "+x2+","+yy+" "+x2+","+y2;
		var c = currentsvg.paper.path(cstr).attr(attris["depline"]).attr({"x":x1,"y":y1});

		var poi = currentsvg.paper.pointer(x2,y2,pois,0).attr(attris["depline"]);

		a=c.getPointAtLength(c.getTotalLength()/2);
		t = currentsvg.paper.text(a.x, a.y-funccurvedist-funcposi*10, func);
		t.attr(attris["deptext"]);
		t.index=ind;
		t.govind=govind;
		
		if (govind==0) { // case: head of sentence (root): the function name needs special treetment
			var newx=a.x+t.getBBox().width/2+funccurvedist/2;
			if (newx+t.getBBox().width/2 > svgwi) newx=a.x-t.getBBox().width/2-funccurvedist/2;
			if (newx-t.getBBox().width/2 < 0) newx=a.x;
			t.attr("x",newx);
		}
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
			poi.attr({stroke: att["stroke"]});
			t.attr({fill: att["stroke"]});
		      };
		
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
			if (node1==null) {delete node2.gov[govind];return;}
			if (ind<govind) var x1=node1.svgs[shownfeatures[0]].attr("x")+node1.svgs[shownfeatures[0]].width/2-xoff;
			else var x1=node1.svgs[shownfeatures[0]].attr("x")+node1.svgs[shownfeatures[0]].width/2+xoff;
			var x2=node2.svgs[shownfeatures[0]].attr("x")+node2.svgs[shownfeatures[0]].width/2;
			var y1=node1.svgs[shownfeatures[0]].attr("y")+pois-tokdepdist;
			var y2=node2.svgs[shownfeatures[0]].attr("y")-tokdepdist-c*linedeps;
		};
		
		if ( (func instanceof Object) ) // mode compare!!!
		{
			var user0=func[0][1][0];

			if (user0=="ok")
			{
				func=func[0][0]
				node2.svgdep[govind]=drawsvgDep(ind,govind,x1,y1,x2,y2,func,  "All annotators agree.", "#"+compacolors[user0],0);
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
						var newset=drawsvgDep(ind,govind, x1+j*2,y1, parseInt(x2,10)+j*2, y2, funcusers[0], funcusers[0]+" ("+u+") ", "#"+compacolors[u], i+j);
						if (lastset) lastset.push(newset);
						else lastset=newset;
						node2.svgdep[govind]=lastset;
						
					}
					
				}
				
			}
			
		
		}
		else node2.svgdep[govind]=drawsvgDep(ind,govind,x1,y1,x2,y2,func, "click to change", false, 0);
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
			for (var i in n.gov) 
			{
				drawDep(n.index,i,n.gov[i],c);
				c+=1;
			};
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
					}
				};	
			
		};
	
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
			for (var i in n.gov) 
			{
				drawDep(n.index,i,n.gov[i],c);
				c+=1;
			};
		};
	};
	
////////////////////////// initialisation ///////////////////////////
/////////////////////////////////////////////////////////////////////




makewords = function(tokens) 
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


draw = function (holder, tokens) {
	paper = Raphael(holder, window.innerWidth-100,100);
	currentsvg=paper.canvas;
	currentsvg.paper=paper;
	

	currentsvg.words = makewords(tokens);
	currentsvg.setAttribute("width",svgwi+extraspace);
	currentsvg.setAttribute("height",dependencyspace+shownfeatures.length*line);	
	drawalldeps();	
	
}



//////////////////////////////////////////////////////////////////////

Raphael.fn.pointer = function (x,y, size, angle) {
	var startpoint = x+","+(y+size);
	var lefttop = "0,0" +(-size/2)+","+(-size*1.5)+" "+(-size/2)+","+(-size*1.5);
	var righttop = (size/2)+"," +(size/2)+" "+(size/2)+"," +(size/2)+ " "+(size)+",0";
	var arrowPath = this.path("M"+ startpoint+"c"+lefttop+ "c"+righttop+ "z");
	arrowPath.rotate(angle);
	return arrowPath;
}



