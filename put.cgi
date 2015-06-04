#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi,sys
from os       import environ
import conll, config
#import database,json
#sys.path.append('modules')
#from logintools import isloggedin

#test = isloggedin("users/")
#if not test:sys.exit()
#admin = int(test[0]["admin"])





def printmenues(functions,funcDic,categories,catDic):
	
	# form for functions and form for categories
	print """	
	<div id="funcform" style="display:none;position:absolute;z-index:444;">
		<form  method="post" id="func" name="func" >
			<select id="funchoice" class='funcmenu' onClick="changeFunc(event);"  size=""" +str( len(functions))+""" style="height:"""+str( len(functions)*13.5+10)+"""px; width:80px;"  >"""
	for f in functions:
		print "<option style='color: "+funcDic[f]["stroke"]+";'>"+f+"</option>"	
	print """
			</select>
		</form>
	</div>
	
	<div id="catform" style="display:none;position:absolute;z-index:444;">
		<form  method="post" id="cat" name="cat" >
			<select id="catchoice" class='funcmenu' onClick="changeCat();"  size=""" +str( len(categories))+""" style="height:"""+str( len(categories)*13.5+10)+"""px; " >"""

	for i,c in enumerate(categories): 
		print "<option style='color: "+catDic[c]["fill"]+";'>"+c+"</option>"	
	
	print """
			</select>
		</form>
	</div>
	<div style="border-top:1px solid #EEE;">&nbsp;</div>	
	"""
	
	# form for compare
	print """
		<div class="ui-widget ui-widget-content ui-corner-all" style="position: absolute; padding: 5px;z-index:20;display:none;" id="compbox">
			<form id="compform" name="compform" method="POST">
				<div id="complist">
				</div><br>
				<div align="center" id="compasubmit">
					<img class="compare" src="images/compare.png" border="0" align="bottom" onclick='compareSubmit()'>
				</div>
			</form>
		</div>
		"""


method = environ.get( 'REQUEST_METHOD' )
if method == "POST" : #or True
	data = cgi.FieldStorage()
	
	conllstr = data.getvalue("conll",None).decode("utf-8")
	addfuncsstr = data.getvalue("addfuncs","").decode("utf-8")
	if addfuncsstr:addfuncs = addfuncsstr.strip().split()
	else: addfuncs=[]
	addcatsstr = data.getvalue("addcats",None)
	if addcatsstr:addcats = addcatsstr.strip().split()
	else: addcats=[]
	print "Content-Type: text/html\r\n\r\n"
	#print conllstr
	
	if conllstr:
		#print "vvvvvvvvvv"
		conlltext, trees, sentences, conlltype, functions, categories = conll.conlltext2trees(conllstr) # , correctiondic={"tag":"cat"}
		functions=list(set(functions+addfuncs))
		categories=list(set(categories+addcats))
		if conlltype==4: functions,funcDic,categories,catDic = config.simpleJsDefPrinter(functions, categories, ["t","tag"])
		else: 		functions,funcDic,categories,catDic = config.simpleJsDefPrinter(functions, categories)
		#print "uuuuuuuuuu"
		filename = conll.tempsaveconll(conlltext," ".join(sentences),conlltype)
		#print "<br><br>",sentences,filename
		#try:
			#projectconfig = config.configProject("quickie") # read in the settings of the current project
			#config.jsDefPrinter(projectconfig)
			#xfunctions,xfuncDic,categories,catDic = projectconfig.functions,projectconfig.funcDic,projectconfig.categories,projectconfig.catDic
		#except:
			#functions,funcDic,categories,catDic = config.simpleJsDefPrinter(functions, categories)
		#print "<br><br>"," ".join(sentences), filename
		#print filename.encode("utf-8")
		print u"""
		<script type="text/javascript">
		filename = 'corpus/temp/{filename}';
		filetype = 'conll{conlltype}';
		
		</script>
		""".format(filename=filename,conlltype=conlltype).encode("utf-8")
		#printmenues(functions,funcDic,categories,catDic)
		#//$(document).ready(function(){
			#//makeSplitter();
			#//$('#CentralSplitter').trigger('dock');
			#//}
		
		for i,s in enumerate(sentences):########### essential loop: all the sentences:

			#print '''<div style="margin:10px"><a class="toggler" nr="{nr}">{nr}: {sentence} </a></div>'''.format(sentence=s.encode("utf-8"),nr=i)
			
			
		
			print '''<div id='sentencediv{nr}' class='sentencediv' style="margin:10px;"  nr={nr}>
				<a class="toggler" nr="{nr}" >
					{nr}: {sentence} &nbsp;
				</a> 
				
				<img class="saveimg" src="images/save.png" border="0" align="bottom" id='save{nr}' title="save">
				<img class="undoimg" src="images/undo.png" border="0" align="bottom" id='undo{nr}'>
				<img class="redoimg" src="images/redo.png" border="0" align="bottom" id='redo{nr}'> 
			
				<img class="exportimg" src="images/export.png" border="0" align="bottom" id='export{nr}' nr='{nr}' title="export"> 
				
			</div>'''.format(sentence=s.encode("utf-8"),nr=i, project="quickie")


			
			
		printmenues(functions,funcDic,categories,catDic)
	
	
	
	#project = data.getlist("project")
	#tree = data.getvalue("tree",None)
	
	#if tree:
		#snode=json.loads(tree)
		
		#sentenceid = int(data.getvalue("sentenceid",0))
		#sentencenr = int(data.getvalue("sentencenr",0))
		#userid = int(data.getvalue("userid",0))
		#username = data.getvalue("username","unknown")
		#validator = int(data.getvalue("validator",0))
		#tokensChanged = eval(data.getvalue("tokensChanged","[]"))
		
		##print "Content-Type: application/json\r\n\r\n"
		##print sentenceid
		
		##sql=database.SQL(project)
		
		##treeid, newtree, sent =sql.saveTree(sentenceid,userid,snode,tokensChanged)
		##treelinks, firsttreeid=sql.links2AllTrees(sentenceid,sentencenr,username,admin,validator)
		
		#print "Content-Type: application/json\r\n\r\n"
		##print sentenceid
		#if newtree:
			##print newtree
			#newtree.update({"treeid":treeid, "treelinks":treelinks, "firsttreeid":firsttreeid, "sentence":sent})
			#print json.dumps(newtree, sort_keys=True)
		#else: print json.dumps({"treeid":treeid, "treelinks":treelinks, "firsttreeid":firsttreeid})
