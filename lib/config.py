#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, codecs, json, colorsys, random, sys
from configobj import ConfigObj

try:	
	projects = [f.decode('utf-8') for f in os.listdir("projects")]
	projectsfolder=os.path.realpath("projects")
except:
	try:
		projects = [f.decode('utf-8') for f in os.listdir("../projects")]
		projectsfolder =  os.path.realpath("../projects")
	except:
		print "can't find projects folder"
		sys.exit()
verbose=False
#verbose=True



def configProject(projectName):
	""" read in config file"""
	if projectName==None:return
	filename=os.path.join(projectsfolder,unicode(projectName),u"project.cfg" ).encode("utf-8")
	if projectName not in projects: 
		print 'Content-type: text/plain\n\n',"error in projects:",type(projectName),"projectName:",[projectName]
		print projects
		return
		
	if os.path.exists(filename):
		try:
			config = ConfigObj(filename,encoding="UTF-8")
			#config.BOM=True
			if verbose : print "read", filename
						
		except Exception, e:
			if verbose : print "can't read config file:",filename,e
			return
	return readinContent(config,projectName)		

def readinContent(config,projectName, tmp=""):
	
	config.shownfeatures=[config["shown features"][i] for i in sorted(config["shown features"])]
	config.shownsentencefeatures=[config["shown sentencefeatures"][i] for i in sorted(config["shown sentencefeatures"])]
	
	config.functions=[]
	config.funcDic={}
	#try:
	#(os.getcwd(),"projects",projectName.encode("utf-8"),config["configuration"]["functionsfilename"].encode("utf-8") ) 
	fn=os.path.join(projectsfolder,projectName.encode("utf-8"),(config["configuration"]["functionsfilename"]+tmp).encode("utf-8") ) 
	f=codecs.open(fn ,"r","utf-8")
	for li in f: 
		if li.strip(): 
			if li[0]=='\ufeff':li=li[1:] # TODO: find out why this anti BOM shit is needed...
			par=li.strip().split("\t")
			if par[0][0]=="#":continue
			atts={}
			if len(par)==2: 
				a=par[1].strip().split(" #")[0] # not ideal: only removes comments that are preceded by space (to avoid confusion with hex values for colors)
				try:atts=json.loads(a)
				except:pass
			config.funcDic[par[0]]=atts
			config.functions+=[par[0]]
			#config.functions+=[li.strip()]
	f.close()
	#except Exception, e:
		#if verbose : print "can't read file:",fn,e
	#print type(config.functions)
	config.funcDic[config["configuration"]["erase"]]={}
	config.functions+=[config["configuration"]["erase"]]
	attStroke(config.funcDic)
	
	
	config.categories=[]
	config.catDic={}
	#config.categories={}
	#try:
	fn=os.path.join(projectsfolder,projectName.encode("utf-8"),(config["configuration"]["categoriesfilename"]+tmp).encode("utf-8") )  
	f=codecs.open(fn,"r","utf-8")
	for li in f:
		if li.strip(): 
			if li.strip()[0]==u'\ufeff':li=li[1:] # TODO: find out why this anti BOM shit is needed...
			par=li.strip().split("\t")
			if par[0][0]=="#":continue
			atts={}
			if len(par)==2:
				a=par[1].strip().split(" #")[0]
				atts=json.loads(a)
			#if len(par)==2: atts=par[1]
			config.catDic[par[0]]=atts
			config.categories+=[par[0]]
	f.close()
	#except Exception, e:
		#if verbose : print "_____can't read file:",fn,e

	attFill(config.catDic)
	
	return config

def checkConfigProject(projectName, filename=u"project.cfg",readin=True,tmp=""):	
	filename=unicode(os.path.join(projectsfolder,projectName,filename )).encode("utf-8")
	config = ConfigObj(filename,encoding="UTF-8")
	if readin:return readinContent(config,projectName, tmp)	
	else: return config
	
	
	
	
	

def simpleJsDefPrinter(functions, categories, shownfeatures=["t","tag","lemma"]):
	"""
	
	for viewer
	
	"""
	print """
	<script type="text/javascript">"""
	
	print ("shownfeatures = ['" + "','".join( shownfeatures ) +"'];").encode("utf-8")
	print "shownsentencefeatures=[];"
	functions+=["erase"]
	print ("functions = "+json.dumps(functions) +";").encode("utf-8")
	funcDic={}
	for f in functions:	funcDic[f]=None
	attStroke(funcDic)
	print ("funcDic = "+json.dumps(funcDic)+";").encode("utf-8")	
	print ("defaultfunction = '"+functions[0]+"';").encode("utf-8")
	print "categories = ",json.dumps(categories),";"
	catDic={}
	for c in categories:	catDic[c]=None
	attFill(catDic)
	print "catDic = ",json.dumps(catDic),";"
	print ("defaultcategory = '"+categories[0]+"';").encode("utf-8")
	print "categoryindex = '1';"
	print ("erase = 'erase';").encode("utf-8")
	print ("root = 'root';").encode("utf-8")
	print '</script>'	
	return functions,funcDic,categories,catDic
	
	
def attStroke(dic):
	for fu,co in list2colors([ f for f,c in dic.iteritems() if not c]).iteritems():
		dic[fu]=json.loads('{"stroke": "#'+co+'","stroke-width":"1"}')
	
def attFill(dic):
	for fu,co in list2colors([ f for f,c in dic.iteritems() if not c]).iteritems():
		dic[fu]=json.loads('{"fill": "#'+co+'"}')
	
#def firstProject():
	


#syntfunctions=[f.replace(","," ") for f in syntfunctionstext.split()]
#["suj","objd","obji","objloc","attrmesu","aux","comp","épi","appos","mod","prép","dét","attrsuj","attrobj","conj","coord","racine"]
#categories=["nom","nomp","conjsub","conjcoo","prép","pro","prori","adj","adv","parti","verbe","dét","num","interj","xxx"]
#categories=["nc","pnoun","conjsub","coo","prep","pro","prel","adj","adv","parti","verb","det","num","interj","xxx"]
#syntfunctionstext="""
 #suj, objd, compnom,
 #prép, comp, aux, coord, conj, 
 #dét, épi, épi-par, 
 #attr-suj, attr-obj,  comp-mesu, qsuj, qobj, obji, objobl, objloc, comp-man,
 #aj-attr, aj-loc, aj-temp, aj-man, aj,
  #app, app-par,
 #suj-disl, objd-disl, obji-disl, loc-disl, temp-disl, disl,
 #racine
#"""
#syntfunctionstext="""rac rég arg suj comp attr obj obl aj aux dét asso intro para"""
#syntfunctionstext="""root arg      subj  comp       pred     obj   iobj          mod   asso    aux det"""

##################################### functions: TODO: make work even for variable color scheme!!!

def jsDefPrinter(config):
	
	print """
	<script type="text/javascript">"""
	
	print ("shownfeatures = ['" + "','".join( config.shownfeatures ) +"'];").encode("utf-8")
	print ("shownsentencefeatures = ['" + "','".join( config.shownsentencefeatures ) +"'];").encode("utf-8")
	print ("functions = "+json.dumps(config.functions+[config["configuration"]["erase"]] ) +";").encode("utf-8")
	print ("funcDic = "+json.dumps(config.funcDic)+";").encode("utf-8")	
	
	print ("defaultcategory = '"+config["configuration"]["defaultcategory"]+"';").encode("utf-8")
	print "categoryindex = '"+config["configuration"]["categoryindex"]+"';"
	print ("erase = '"+config["configuration"]["erase"]+"';").encode("utf-8")
	print ("defaultfunction = '"+config["configuration"]["defaultfunction"]+"';").encode("utf-8")
	print ("root = '"+config["configuration"]["root"]+"';").encode("utf-8")

	print "categories = ",json.dumps(config.categories),";"
	print "catDic = ",json.dumps(config.catDic),";"
	print '</script>'
	#return fcolors,ccolors

def jsDef(config):
	
	txt += """
	<script type="text/javascript">"""
	
	txt += ("shownfeatures = ['" + "','".join( config.shownfeatures ) +"'];").encode("utf-8")
	txt += ("shownsentencefeatures = ['" + "','".join( config.shownsentencefeatures ) +"'];").encode("utf-8")
	txt += ("functions = "+json.dumps(config.functions+[config["configuration"]["erase"]] ) +";").encode("utf-8")
	txt += ("funcDic = "+json.dumps(config.funcDic)+";").encode("utf-8")	
	
	txt += ("defaultcategory = '"+config["configuration"]["defaultcategory"]+"';").encode("utf-8")
	txt += "categoryindex = '"+config["configuration"]["categoryindex"]+"';"
	txt += ("erase = '"+config["configuration"]["erase"]+"';").encode("utf-8")
	txt += ("defaultfunction = '"+config["configuration"]["defaultfunction"]+"';").encode("utf-8")
	txt += ("root = '"+config["configuration"]["root"]+"';").encode("utf-8")

	txt += "categories = ",json.dumps(config.categories),";"
	txt += "catDic = ",json.dumps(config.catDic),";"
	txt += '</script>'

	return txt

def oldlist2colors(lis):
	
	if len(lis)>0:
		#colorstep=(256*256*256-200000)/len(lis)
		colorstep=(256*256*256)/(len(lis)+1)
		colors=[str(hex(i*colorstep))[2:].rjust(6,"0") for i in range(1,len(lis)+1)]
		fus = dict(zip(lis,colors))
		#fat = dict(zip(lis,[json.loads('{"stroke": "#'+c+'","stroke-width":"1"}') for c in colors])) 
		return fus
		#,fat
	return {}

def list2colors(lis):
	
	if len(lis)>0:
		colorstep=1.0/(len(lis))
		colors=[ '%02x%02x%02x' % tuple(255*c for c in colorsys.hls_to_rgb(i*colorstep, random.uniform(.3, .6),random.uniform(.4, 1.0))) for i in range(0,len(lis))]
		fus = dict(zip(lis,colors))
		return fus
	return {}
	
	
if __name__ == "__main__":	
	#c = configProject(projects[0])
	#c = configProject("Rhapsodie")
	#jsDefPrinter(c)
	print list2colors(["a","b","c"])

	
