/*!
 * arborator script for tree handling 
 * version 1.0
 * http://arborator.ilpga.fr/
 *
 * Copyright 2010-2017, Kim Gerdes
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


saveCGI="save.cgi";
eraseTreeCGI="eraseTree.cgi";
statusChangeCGI="statusChange.cgi";
getTreeCGI="getTree.cgi";
exportCGI="export.cgi";
connectCGI="connect.cgi";

treeid=0;
commentid=0;
erasetreeid=0;
compacolors={};
tokensChanged=[];
teacher=0 // this variable is set to 1 in some types of exercices. then saving a (teacher) tree is impossible.

if (typeof tokenModifyable == 'undefined') tokenModifyable=0;

//////////////////////////////////////////////
/////// initialisation ///////////////////////
//////////////////////////////////////////////



$(document).ready(function(){
		

	$('#loader')
	.hide()  // hide it initially
	.ajaxStart(function() {
		$(this).show();
		})
	.ajaxStop(function() {
		$(this).hide();
		});
	
	$(".toggler").click(function()
		{
			toggleOpen($(this), $(this).attr("nr"), $(this).attr("treeid"));	
		})
	$(".othertree").click(function()
		{
			toggleOpen($(this).parent().prev(),  $(this).attr("nr"), $(this).attr("treeid"));	
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
			currentsvg.undo.undo();
		});
	$(".redoimg").click(function()
		{
			var nr=$(this).parent().attr("nr");
			var sid=$(this).parent().attr("sid");
			currentsvg=$('#svg'+nr)[0];
			currentsvg.undo.redo();
		});
	
	$(".connectRight").click(function(evt)
		{
			var nr=$(this).parent().attr("nr");
			var sid=$(this).parent().attr("sid");
			if (evt.ctrlKey)
				splitRight(project,nr,sid);
			else
				connectRight(project,nr,sid);
		});
	$(".check").click(function(evt)
		{
			var nr=$(this).parent().attr("nr");
			var sid=$(this).parent().attr("sid");
			check(project,nr,sid, $(this).attr("graphical"));
			
		});

		
	onkey();
	settings();
	if (editable) $('.toggler[nr="'+opensentence+'"]').click();
	else openAllTrees();

	/////////////////// navigateAway initialisation:
	
	window.onbeforeunload = function(){ if (dirty.length>0){ return "useless message"} }
	
	
	
	
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
				width:600,
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
		
	
// 	makeSplitter();
	
});




// end initialisation ///////////////////////



toggleOpen = function(the, nr, tid) {
	treeid=tid
 
// 	console.log("!!!",the,nr);
	if (the.hasClass("expanded") ) // case: tree already open, closing
	{
		currentsvg=$('#svg'+nr)[0];
		if (dirty.indexOf(currentsvg.id)==-1)
		{
			$("#redo"+nr).css({ visibility: 'hidden' });
			$("#undo"+nr).css({ visibility: 'hidden' });
			$("#export"+nr).css({ visibility: 'hidden' });
			$("#holder"+nr).remove();
			$("#edit"+nr).remove();
			reset();
			$(".toggler").removeClass("currentsentence");
			currentsvg=false;
			the.toggleClass('expanded');
		}
		else
		{
			the.parent().after('<div id="savewarning" style="margin:0 20;" class="ui-state-error ui-corner-all">The tree is unsaved. Save before closing.</div>')
			$("#savewarning").delay(2000).fadeOut('slow'); ;
		}
		
	}
	else // case: no tree showing for this sentence, opening sentence
	{
		
		if (editable) 
		{
// 			treeid=the.attr("treeid");
			$("#holder"+nr).remove();
			the.parent().after('<div id="holder'+nr+'" class="svgholder"> </div>');
			getTree(nr,treeid);
			initialOtherTree(nr);
		}
		the.toggleClass('expanded');
	}
  
  
}

openAllTrees = function() {
	
	
	$( ".toggler:not(.expanded)'" ).each(function( i ) {
		console.log( i + ": " +$(this).attr("nr") );
		var nr = $(this).attr("nr");
// 		if (nr!=1) return(1);
		var treeid = $(this).attr("treeid");
		$("#holder"+nr).remove();
		$(this).parent().after('<div id="holder'+nr+'" class="svgholder"> </div>');
		getTree(nr,treeid);
		initialOtherTree(nr);
		
		$(this).toggleClass('expanded');
		
		
	});

// 	
}


initialOtherTree = function(nr) {
// 	console.log("initialOtherTree",nr);
	$("#othertrees"+nr+" > a").off("click").click(function()
	{
		if (dirty.indexOf(currentsvg.id)==-1) // the currentsvg is not dirty
		{
			treeid=$(this).attr("treeid");
			nr=$(this).parent().parent().attr("nr");
			sid=$(this).parent().parent().attr("sid");
			$("#holder"+nr).remove();
			$(this).parent().parent().after('<div id="holder'+nr+'" class="svgholder"> </div>');
			getTree(nr,treeid);
		}
		else
		{
			$(this).parent().parent().after('<div id="savewarning" style="margin:0 20;" class="ui-state-error ui-corner-all">The tree is unsaved. Save before closing.</div>')
			$("#savewarning").delay(2000).fadeOut('slow'); ;
		}
				
	});
	
	$("#export"+nr).show().click(function()
	{
// 		console.log("export clicked",$(this).offset(),$("#ex").attr("nr"));
		$("#ex").show();
		$("#ex").offset($(this).offset()).attr("nr",$(this).attr("nr"));
// 		console.log("export clicked",$(this).offset(),$("#ex"),$("#ex").attr("nr"),$("#ex").css("visibility"))

	});
	
}


getJSON = function (nr, treeid) {
	
	$('#sentencediv'+nr).append($("#loader"));
	delete tokens;
	tokens=new Object();
	
	$.getJSON(
		getTreeCGI,
		{
				project: project,
				treeid: treeid,
				filename: filename,
				filetype: filetype,
				nr: nr			
		},
		function(data)
				{
					startTree(nr,data)
				}
			
	);
	initialOtherTree(nr);	
	
}

var allData=new Object();
var allGoodData=new Object();
var tokens=new Object();



getTree = function(nr, treeid) {
	if (editable)
	{
// 			console.log("getTree",nr,treeid);
		$("#othertrees"+nr+" > .thistree").removeClass("thistree").addClass("othertree");
		$('a.othertree[treeid=' + treeid + ']').removeClass("othertree").addClass("thistree");
		getJSON(nr, treeid)
		
	}
	else
	{
		$.get('svg/contentSnippet.html', function (response) {
// 			console.log("cool",response);
			$("#holder"+nr).html(response);
		}).fail( function() {
			console.log("oh non!"+nr+"-"+"treeid");
			getJSON(nr, treeid);
			
			
		})
		;
// 		$("#holder"+nr).load('svg/contentSnippet.html');
		
	}
}


startTree = function (nr, data) {
	delete redata;
	redata = new Object();

	$("html, body").animate({scrollTop: $("#loader").offset().top-50}, 1000,'easeInOutCubic');
	
	$.each(data, function(key, val) 
		{
			redata[key]=val;
		});
	if ("tree" in redata)
		{
			allData[nr]=new Object();
			$.each(redata.tree, function(key, val) 
			{
				tokens[key]=val;
				allData[nr][key]=val; // todo: only use allData, forget about tokens!
				
			});
			start("holder"+nr, nr); // call to function from arborator.draw.js
			$("#sentencediv"+nr).attr("treeid",treeid);
		}
	if ("goodtree" in redata)
		{
			allGoodData[nr]=new Object();
			$.each(redata.goodtree, function(key, val) 
			{
				allGoodData[nr][key]=val; 
				
			});
		}
	
	if ("teacher" in redata)
		{
			teacher = redata["teacher"];
		}
		else
		{
			teacher = 0;
		}
	
	currentsvg.sentencefeatures={}
	for (a in redata)
	{
		if (!(["tree","goodtree","teacher"].includes(a)))
		{
			if (shownsentencefeatures.includes(a))
			{
				$('#holder'+nr).append('<p>'+redata[a]+'</p>');
			}
		}
	}
	if (!editable)
	{

		var svg = $('#svg'+nr)[0].paper.toSVG();
	}

	$("#save"+nr).css({ visibility: 'hidden' });
	$("#undo"+nr).css({ visibility: 'hidden' });
	$("#redo"+nr).css({ visibility: 'hidden' });
	
}


writeSvg = function(treeid,svg) {
	
	console.log("writeSvg")
	$.ajax({
		type: "POST",
		url: "writeSvg.cgi",
		data: {	"project":project,	"treeid":treeid,
			"svg":svg
		},
		success: function(answer){
				console.log("cool:saved:"+answer)				
			},
		error: function(XMLHttpRequest, textStatus, errorThrown){
			console.log("uncool:notsaved:"+errorThrown)
			}
		});	
	
	
}



getCompareTree = function(project, treeids, nr) {
	
	$("#othertrees"+nr+" > .thistree").removeClass("thistree").addClass("othertree");

	$('#sentencediv'+nr).append($("#loader"));
        delete tokens;
        tokens=new Object();
// 	delete redata;
// 	redata = new Object();
	treeid=0;
        $.getJSON(
	      getTreeCGI,
	      {
			"project": project,
			"treeids":treeids,
			"compare":true
	      },
	      function(data)
			{
				startTree(nr,data);
			}

        );
}


function countChecked() {
	var n = $("input:checked").length;
	if (n>1) $("#compasubmit").show();
	else $("#compasubmit").hide();
	  
}


compare = function (data,snr,colors) {	
	var formhtml="";
	compacolors=colors;
	$.each(data, function(k, v) {
// 		console.log(k,v)
		if (k=="guest") formhtml=formhtml+'<input type="checkbox" name="'+k+'" value="'+v+'" >'+k+'<span style="color:#'+colors[k]+'">◼</span><br>'
		else formhtml=formhtml+'<input type="checkbox" name="'+k+'" value="'+v+'" checked>'+k+'<span style="color:#'+colors[k]+'">◼</span><br>'
		});
	$("#complist").html(formhtml);
	$(":checkbox").click(countChecked);
	countChecked();
	
// 	$("#compbox").offset($("#compa"+snr).offset()).attr("nr",snr);
	$("#compbox").css({ top: $("#compa"+snr).offset().top, left: $("#compa"+snr).offset().left }).attr("nr",snr);
	$("#compbox").show();
	
}

compareSubmit = function () {	
	treeidname={};
	$.each($("input:checked"), function(k, v) {
// 		console.log(k,v.value,v.name);
		treeidname[v.value]=v.name
// 		console.log(treeidname);
	});
	var nr = $("#compbox").attr("nr");
	$("#holder"+nr).remove();
// 	console.log("yyyyyyyyyyy",$("#sentencediv"+nr));
	$("#sentencediv"+nr).after('<div id="holder'+nr+'" class="svgholder"> </div>');
	getCompareTree(project, treeidname, nr);
	
}
	
exportTree = function () {
	
	nr=$("#ex").attr("nr");
	treeid = $("#sentencediv"+nr).attr("treeid");
// 	console.log("exportTree",nr,treeid);
	
	var v=$("#exptype")[0].options[$("#exptype")[0].selectedIndex].value;
	
	if(v=="conll" || v=="xml") 
		{
			var currentsvg=$('#svg'+nr)[0];			
			$('#source').attr("value",stringify(currentsvg));
// 			$('#cat').attr("value",shownfeatures[categoryindex]);
			$('#ex').attr("action",exportCGI).submit();			
		}
	else 	{
			$("svg").attr("xmlns","http://www.w3.org/2000/svg");
			$("svg").attr("xmlns:xlink","http://www.w3.org/1999/xlink");
			var header = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
			$('#source').attr( "value", header+$('#holder'+nr+' >svg').clone().wrap('<p>').parent().html() );			
			$('#ex').submit();
		
		}
}

	
function dirt() { 
	
	var nr=currentsvg.id.substr(3);
	
	if (teacher) 
	{
		return;
	}
// 	console.log("dirt starts",nr,dirty,currentsvg.id,dirty.indexOf(currentsvg.id))
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
// 	console.log("end dirt",dirty)
	
}
	
	
	

openFeatureTable = function (index,words) {
	// called from draw.js: openFeatureTable(this.index,currentsvg.words)
	
	var tbody='<tbody id="featabody">'
	var fs = words[index].features;
	
	// 	console.log("openFeatureTable", index,words[index])
	
	tbody+='<tr><input size=8 type="hidden" name="wordid" value='+index+'></tr>';

	for (a in fs) 
		{
		ivstyle="";
		iastyle="";
		if (shownfeatures.indexOf(a)==0 && tokenModifyable==0) {iastyle="readonly='readonly'";ivstyle="readonly='readonly'";}
		else if (shownfeatures.indexOf(a)>=0) iastyle="readonly='readonly'";
		tbody+='<tr><td style="padding:0;"><input size=8 type="text" name="att-'+a+'" value="'+a+'" '+iastyle+' ></td><td style="padding:0;"><input size=8 type="text" name="val-'+a+'" value="'+fs[a]+'"  '+ivstyle+' ></td></tr>';
		}
	tbody+='<tr><td style="padding:0;"><input size=8 type="text"  name="att-new" value=""></td><td style="padding:0;"><input size=8 type="text"  name="val-new" value=""></td></tr>';
	tbody+='</tbody>'
	$('#featabody').before(tbody).remove();
	$('#fdialog').attr("index",index);
	$('#ui-dialog-title-fdialog').text("Features of Node "+index);
	$("input").focus(function () {nokeys=true;}).blur(function () {nokeys=false;});
	$('#fdialog').dialog('open');
}	
	
	

featureChanged = function (ind) {
	
	newfeatures={};
	$("#featab input").each(function (i) 
		{
			if (this.name.substr(0,4)=="att-") 
			{
				var a=this.name.substr(4,this.name.length);
				var v=$("input[name='val-" +a+ "']").attr("value");
				if (v) newfeatures[this.value]=v;			
			}
		})
	setFeatures(ind,newfeatures);
	}
	
	
setFeatures = function (nodenumber,features) {
	
	// 	console.log("setting",nodenumber,features);
	
	var n = currentsvg.words[nodenumber];
	var oldfeatures = n.features;
	
	n.features=features;	
	
	sdiv=$(currentsvg).parent().prev()
	var nr = sdiv.attr("nr");
	delete tokens;
	tokens=new Object();
	
// 	svgws=$.extend(true, {}, currentsvg.words);
	
	for (i in currentsvg.words)
	{
		tokens[i]={"gov":currentsvg.words[i]["gov"]};
		for (j in currentsvg.words[i]["features"])
		{
// 			console.log(j,currentsvg.words[i]["features"][j])
			tokens[i][j]=currentsvg.words[i]["features"][j];			
		}
	}
	paper.clear();
	
	draw();
// 	currentsvg.words=svgws
	currentsvg.undo.undoable("reestablish manually changed features", setFeatures, [nodenumber, oldfeatures]);
	if (tokenModifyable>0) tokensChanged.push([nodenumber,0]);
}
	




	
createNode = function(ind) {
	createindex=ind;
		
	$("#question").html("Are you sure that you want to duplicate this node? <br>This change will immediately apply to <b>all annotations</b> of this sentence and <b>cannot</b> be undone.")
	$("#dialog").dialog({	
			height: 450,
			width:500,
			buttons: {
			
				Cancel: function() {
					$(this).dialog('close');
					return false;
					},
				"Duplicate the node": function() {
					$(this).dialog('close');
					reallyCreateNode();
					return true;
					}
				}
		});
	$('#ui-dialog-title-dialog').text("Please confirm");
	$('#dialog').dialog('open');
		
		}	
	
reallyCreateNode = function() {
	var thenr=currentsvg.id.substr(3);
	var thesid=$("#sentencediv"+thenr).attr("sid");
	
	if (tokenModifyable>0) tokensChanged.push([createindex,1]);
	console.log(project,thenr,thesid,userid,username,tokensChanged);
	
	saveTree(project,thenr,thesid,userid,username);
	
}



	
eraseNode = function(ind) {
	eraseindex=ind;
		
		$("#question").html("Are you sure that you want to erase this node? <br>This change will immediately apply to <b>all annotations</b> of this sentence and <b>cannot</b> be undone. You and the other users will lose the changes they have done on this node.")
		$("#dialog").dialog({	height: 450,
				buttons: {
				
					Cancel: function() {
						$(this).dialog('close');
						return false;
						},
					"Erase the node": function() {
						$(this).dialog('close');
						reallyEraseNode();
						return true;
						}
					}
			});
		$('#ui-dialog-title-dialog').text("Please confirm");
		$('#dialog').dialog('open');
		
		}	
	
reallyEraseNode = function() {
	var thenr=currentsvg.id.substr(3);
	var thesid=$("#sentencediv"+thenr).attr("sid");
	
	if (tokenModifyable>0) tokensChanged.push([eraseindex,-1]);
	console.log(project,thenr,thesid,userid,username,tokensChanged);
	
	saveTree(project,thenr,thesid,userid,username);
	
}

///////////////////////// connecting/splitting //////////////////////
////////////////////////////////////////////////////////////////////


connectRight = function(project,nr, sid) {

	// TODO: kick this out:
	// 	reallyconnectRight(project,nr, sid);
	// 	return;
	
	$("#question").html("Are you sure that you want to join this sentence with the following sentence? This <b>cannot</b> be undone and will affect all the users.")
	$("#dialog").dialog({height: 450,
			buttons: {
			
				Cancel: function() {
					$(this).dialog('close');
					return false;
					},
				"Connect the sentence": function() {
					$(this).dialog('close');
					reallyconnectRight(project,nr, sid);
					return true;
					}
				}
		});
	$('#ui-dialog-title-dialog').text("Please confirm");
	$('#dialog').dialog('open');
	}

splitRight = function(project,nr, sid) {

	// TODO: kick this out:
	// 	reallyconnectRight(project,nr, sid);
	// 	return;
	if (lastSelected && currentsvg.id.substr(3)==nr) // word selected and clicked the connect button on the last modified svg
		{
			console.log(lastSelected,currentsvg.words[lastSelected],currentsvg.words[lastSelected].features.t,treeid)
			$("#question").html("Are you sure that you want to split this sentence after the word '"+currentsvg.words[lastSelected].features.t +"'?<br/> This <blink>cannot</blink> be undone and will affect all the users.")
			$("#dialog").dialog({height: 450,
					buttons: {
					
						Cancel: function() {
							$(this).dialog('close');
							return false;
							},
						"Split the sentence": function() {
							$(this).dialog('close');
							reallysplitRight(project,nr, sid,currentsvg.words[lastSelected].index);
							return true;
							}
						}
				});
			$('#ui-dialog-title-dialog').text("Please confirm");
			$('#dialog').dialog('open');
		}
	}
	
	
reallyconnectRight = function(project,nr, sid) {

	$.ajax({
		type: "POST",
		url: connectCGI,
		data: {"project":project,"nr":nr,"sid":sid,"connectsplit":"connect"}, 
		success: function(answer){
				console.log("sentence nr "+nr+" connected!\n"+answer);
				location.reload(); 
			},
		error: function(XMLHttpRequest, textStatus, errorThrown){
			console.log("error connecting",project,nr,sid)
			alert("error connecting"+XMLHttpRequest+ "\n"+textStatus+ "\n"+errorThrown);
			}
		});
	}

reallysplitRight = function(project,nr, sid, toknr) {

	$.ajax({
		type: "POST",
		url: connectCGI,
		data: {"project":project,"nr":nr,"sid":sid,"toknr":toknr,"connectsplit":"split"}, 
		success: function(answer){
				console.log("sentence nr "+nr+" split!\n"+answer);
				location.reload(); 
			},
		error: function(XMLHttpRequest, textStatus, errorThrown){
			console.log("error connecting",project,nr,sid)
			alert("error connecting"+XMLHttpRequest+ "\n"+textStatus+ "\n"+errorThrown);
			}
		});
	}

///////////////////////// check ///////////////////////////////
////////////////////////////////////////////////////////////////////	
	

check = function(project,snr, sid, graphical) {	
	
	prepareData(snr); // useful to be able to compare even before saving
// 	console.log(allData, allGoodData, snr);

	var goodcat=[],badcat=[],gooddep=[],baddep=[];
	if (!(snr in allGoodData)) return;
	$.each(allGoodData[snr], function(toknr, nodedic) 
	{
		console.log(toknr,allData[snr][toknr]);
		if (nodedic.tag == allData[snr][toknr].tag) goodcat.push(toknr);	
		else badcat.push(toknr);
		if ($.isEmptyObject( nodedic.gov )) return;
		$.each(nodedic.gov, function(govnum, func) 
		{
			if ((func == allData[snr][toknr].gov[govnum] || allData[snr][toknr].gov[govnum]==null && govnum==-1)) gooddep.push(toknr);
			else baddep.push(toknr);
		})
	});
	if (badcat.length==1) 	html="1 category error: "
	else 		html=badcat.length+" category errors: "
	html += (goodcat.length/(goodcat.length+badcat.length)*100).toFixed(1)+"% correct.<br/>"
	if (baddep.length==1) 	html+="1 dependency error: "
	else		html+=baddep.length+" dependency errors: "
	html += (gooddep.length/(gooddep.length+baddep.length)*100).toFixed(1)+"% correct.<br/>"
	$("#checklist").html(html);
	$("#checkbox").css({ top: $("#check"+snr).offset().top, left: $("#check"+snr).offset().left })
	$("#checkbox").show();
	if (graphical==1)
	{
		for (var i in currentsvg.words)
		{
			var n = currentsvg.words[i];
			if(badcat.indexOf(i)==-1) n.svgs.tag.attr({"fill":"black"});
			else n.svgs.tag.attr("fill","red");
			if(baddep.indexOf(i)==-1) n.svgs.t.attr({"fill":"black"});
			else n.svgs.t.attr("fill","red");
		}
	}
	
}

///////////////////////// saving etc ///////////////////////////////
////////////////////////////////////////////////////////////////////

prepareData = function (nr) {
	var currentsvg=$('#svg'+nr)[0];	
	tree=stringify(currentsvg);
	allData[nr]=new Object();
	$.each(nsimple, function(toknr, strangedic) 
	{
		allData[nr][toknr]=new Object();
		allData[nr][toknr].tag = strangedic.features.tag;
		allData[nr][toknr].gov = strangedic.gov;
	});
}
saveAllTrees = function () {
	
		oldcsvg=currentsvg;		
		for (i in dirty.slice())
		{
			var thenr=dirty[i].substr(3);
			var thesid=$("#sentencediv"+thenr).attr("sid")
			saveTree(project,thenr,thesid,userid,username);
		}
		currentsvg=oldcsvg;
	
	}

	
simpleFeatStruc = function (svg) {
	nsimple={}
	var good={index:0,gov:0,features:0};
	for (var i in svg.words)
		{ 
			nsimple[i]={}
			for (j in svg.words[i]["gov"]) // correct compare governors before saving
			{
				if (svg.words[i]["gov"][j] instanceof Object) svg.words[i]["gov"][j] = svg.words[i]["gov"][j][0][0];
			}
			if (svg.words[i]["features"][shownfeatures[categoryindex]] instanceof Object)  // correct compare cats before saving
			{
				svg.words[i]["features"][shownfeatures[categoryindex]]=svg.words[i]["features"][shownfeatures[categoryindex]][0][0]
			}
			
			
			for (feat in good) nsimple[i][feat]=svg.words[i][feat]; // copy the good features into nsimple before saving
// 			console.log("vvv",currentsvg.words[i]["gov"])
		}
	return {"tree":nsimple,"sentencefeatures":svg.sentencefeatures};
	
	}
	
stringify = function (currentsvg) {
	return JSON.stringify(simpleFeatStruc(currentsvg), "")
	}
	
saveTree = function (project,nr,sid,uid,username) {
	prepareData(nr);
	$("#save"+nr).addClass( "ui-state-disabled " );
	
	$.ajax({
		type: "POST",
		url: saveCGI,
		data: {	"project":project,	"tree":tree,
			"sentenceid":sid,	"sentencenr":nr,
			"userid":uid,		"username":username,	"todo":todo, 
			"addEmptyUser":addEmptyUser, "validvalid":validvalid,
			"validator":validator,	"tokensChanged":JSON.stringify(tokensChanged, "")
		},
		success: function(answer){
				if ( !(answer instanceof Object) || !("treeid" in answer) ) 
				{
					alert("Problem saving the tree. Please check the javascript console for more information.");
// 					console.log(answer);
					$("#save"+nr).removeClass( "ui-state-disabled " );
					return;
				
				}
				
// 				console.log(tokensChanged,tokensChanged.length, tokensChanged != []);
				if (tokensChanged.length>0) // special stuff for duplicating and erasing nodes
				{
					tokens=new Object();
					$("#holder"+nr).remove();
					$("#sentencediv"+nr).after('<div id="holder'+nr+'" class="svgholder"> </div>');
					startTree(nr,answer);
					$("#toggler"+nr).html(nr+": "+answer.sentence);
					initialOtherTree(nr);
					tokensChanged=[];
						
				}
							
				dirty.splice(dirty.indexOf(currentsvg.id), 1);
				if (dirty.length==0)	$("#sav").attr(attrclean).addClass( "ui-state-disabled " );
				else		$("#sav").attr(attrdirty).removeClass( "ui-state-disabled " );
				$("#save"+nr).css({ visibility: 'hidden' });
				$("#othertrees"+nr).html(answer.treelinks);
				
				treeid=answer.treeid;
				$('a.othertree[treeid=' + treeid + ']').removeClass("othertree").addClass("thistree");
				initialOtherTree(nr);
				$("#save"+nr).removeClass( "ui-state-disabled " );
				
				
			},
		error: function(XMLHttpRequest, textStatus, errorThrown){
			console.log("error",project,nr,sid,uid,username)
			alert("error saving"+XMLHttpRequest+ "\n"+textStatus+ "\n"+errorThrown);
			$("#save"+nr).removeClass( "ui-state-disabled " );	
			}
		});
	// 	console.log("saved",project,nr,sid,uid,username)
	}

	
	
eraseSentenceNumber=0;
	
eraseTree = function(nr, treeid, treecreator) {
	
	eraseSentenceNumber=nr;
	erasetreeid=treeid;
	$("#question").html("<span style='font-size:.7em;'>Are you sure that you want to completely erase from the database the beautiful analysis made by "+treecreator+"?</span>")
	$('#dialog').dialog('open');
	
	}	
	
reallyEraseTree = function() {
	$.ajax({
		type: "POST",
		url: eraseTreeCGI,
		data: {"project":project,"treeid":erasetreeid,"sentencenr":nr,"username":username}, 
		success: function(answer){
				
				$("#othertrees"+eraseSentenceNumber).html(answer);
				initialOtherTree(eraseSentenceNumber);
				console.log(nr+"erased!"+answer);
				
			},
		error: function(XMLHttpRequest, textStatus, errorThrown){
			console.log("error",project,erasetreeid)
			alert("error erasing"+XMLHttpRequest+ "\n"+textStatus+ "\n"+errorThrown);
			}
		});
	
}


nexttreestatus =  function(sid,snr) {

	treeid = $("#toggler"+snr).attr("treeid");
	
// 	console.log("nexttreestatus. treeid:",treeid)	
	if (treeid!=null)
		$.ajax({
			type: "POST",
			url: statusChangeCGI,
			data: {"project":project,"treeid":treeid,"snr":snr,"userid":userid,"username":username,"sid":sid, "textid":textid}, 
			success: function(answer){
	// 				var nr=currentsvg.id.substr(3);
					$("#status"+snr).html(answer.status);
					$("#othertrees"+snr).html(answer.links);
	// 				initialOtherTree(nr);
					console.log("changed!",answer);
					
				},
			error: function(XMLHttpRequest, textStatus, errorThrown){
				console.log("error",project,treeid)
				alert("error erasing"+XMLHttpRequest+ "\n"+textStatus+ "\n"+errorThrown);
				}
			});
		
}








	
	
	
	
	/*
saveComment = function (answerto) {
// 	alert("saveComment");

	var comment = $('#txtDefaultHtmlArea').htmlarea('toHtmlString');
	$.ajax({
		type: "POST",
		url: saveCGI,
		data: {		"comment":comment,
				"sentenceid":sentenceid,
				"userid":userid,
				"answerto":answerto
			},
		success: function(x){
				$("#comments").prepend('<div class="comment"><div class="commentitle"><cite style="float: left;"><img title="comment" src="images/commentNano.png"/>'+username+'</cite><em style="float: right;">now</em></div><br/>'+comment+'</div>');
			},
		error: function(XMLHttpRequest, textStatus, errorThrown){
				alert("error saving comment"+XMLHttpRequest+ textStatus+ errorThrown);
			}
		});
		
	$("#wysiwyg").hide();
		
	}*/





/*
commentstuff = function () {
	$("#newcomment").click(function () { 
// 		$(this).hide(); comments
		$('#wysiwyg').show();
// 		$("#txtDefaultHtmlArea").htmlarea();
		$("#txtDefaultHtmlArea").htmlarea({



                // Do something once the editor has finished loading
                loaded: function() {
                    //// 'this' is equal to the jHtmlArea object
                    //alert("jHtmlArea has loaded!");
//                     this.showHTMLView(); // show the HTML view once the editor has finished loading
		    		document.getElementById("wysiwyg").scrollIntoView(true);
				$("#wysiwyg").focus();

                }
            });

		
		
// 		$("#txtDefaultHtmlArea").htmlarea(); // Initialize jHtmlArea's with all default values
	});*/
	

	/*
	$("#tabledialog").dialog({
			bgiframe: true,
			autoOpen: false,
			height: 444,
 			width:window.innerWidth-50,
// 			modal: true,
			buttons: {
				
				Cancel: function() {
					$(this).dialog('close');
				},
				"OK": function() {
					$(this).dialog('close');
					//alert(treeid);
					$("#eraseCommentNumber").attr("value",commentid);
					$("#erasecomment").submit();
				}
				}
			});
	
	$("#confirmdialog").dialog({
			bgiframe: true,
			autoOpen: false,
			height: 350,
 			width:400,
// 			modal: true,
			buttons: {
				
				Cancel: function() {
					$(this).dialog('close');
				},
				"OK": function() {
					$(this).dialog('close');
					//alert(treeid);
// 					$("#eraseCommentNumber").attr("value",commentid);
// 					$("#erasecomment").submit();
				}
				}
			});
	$('#corrdialog').dialog({
			bgiframe: true,
			autoOpen: true,
			height: 350,
 			width:window.innerWidth-50,
			position: 'bottom',
// 			modal: true,
			buttons: {
				
				Cancel: function() {
					$(this).dialog('close');
				},
				"OK": function() {
					$(this).dialog('close');
					
				}
				}
			});
	
// $('#wysiwyg').show();
// $("#txtDefaultHtmlArea").htmlarea(); // Initialize jHtmlArea's with all default values
	
  
  	
	};*/



