 
conlls = {	10: 	{"id": 0, "t":1, "lemma": 2, "cat": 3, "xpos":4, "morph":5, "gov":6, "func":7, "xgov":8, "gloss":9}, 
		14: 	{"id": 0, "t":1, "lemma": 3, "cat": 5, "gov":8, "func":11}, 
		4: 	{"t":0, "lemma": 0, "cat": 1, "gov":2, "func":3} 
	}
 
 
function conllNodesToTree(treeline)
	// reads a conll representation of a single tree
	{
		var nodes = treeline.split('\n');
		var tree={};
		var uextra={};
		var words=[]
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
			lastid=id;
			});
		
		sentence="";
		$.each(words, function(jj,word){ // making the sentence with correct spacing:
			sentence+=word;
			if (!(("NoSpaceAfter" in tree[jj+1]) && tree[jj+1]["NoSpaceAfter"]==true)) sentence+=" ";
		});
		
		return {tree:tree, uextra:uextra, words:words, sentence:sentence};
	}



