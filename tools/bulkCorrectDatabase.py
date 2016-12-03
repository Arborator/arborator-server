#!/usr/bin/python
# -*- coding: utf-8 -*-

#######################################################################################
# this file allows to systematically correct a complete annotation project, 
# directly in the database
#######################################################################################


debug=False
debug=True
#debug=5



import traceback, copy
from time	import mktime, time, asctime, localtime
from copy 	import deepcopy
sys.path.insert(0, '../lib')
from database 	import SQL

	
def splice(sentencedic,nodenum,intdic,copiedfeatures=['t','token','lemma','cat']):
		"""
		integrates the intdic into sentencedic at position nodenum
		an empty intdic kicks out the node in a proper manner (other dependencies are still ok)
		
		format of intdic:
			indices start with 'i', for example 'i44'
			last node that carries 'child' feature will receive the children of the former nodenum node
			last node that has governor i0 will receive the governors of the former nodenum node
			if no node has a 'i0' governor, the first node will receive the governors
			
			example:
			{	
				'i1':{ u'person': u'3', u'number': u'sg', u'cat': u'V', u'lemma': u'\xeatre', u'token': u'est', u'tense': u'present', u'mode': u'indicative', 'gov': {'i0':'root'}, u't': u'A'},
				'i2':{u'cat': u'Cl', u'lemma': u'c', u'token': u'-ce', u't': u'B', 'gov': {'i1': u'sub'}, 'child':None}
			}
		
		gives back new sentencedic
		
		"""
		intgov,intchi=None,None
		newsentencetree={}
		if debug>2: 
			print "================== integrating"
			for i in sorted(intdic):
				print i,intdic[i]
			print "into ((((((((((((("
			for i in sorted(sentencedic):
				print i,sentencedic[i].get("t","-"),sentencedic[i]
			print ")))))))))))))))"
		#try:
		l = [0]+sorted(sentencedic)[:nodenum-1]+sorted(intdic)+sorted(sentencedic)[nodenum:]
		if debug>2: print "lllll",l
		
		
		for i in sorted(intdic):
		
			sentencedic[i]=sentencedic[nodenum].copy()
			for at in copiedfeatures:
				if at in intdic[i]:
					sentencedic[i][at]=intdic[i][at]
			sentencedic[i]['gov']=intdic[i].get('gov',{})
			
			if 'i0' in intdic[i].get('gov',{}).keys(): # found the gov: the one that has a root link
				sentencedic[i]['gov']=sentencedic[nodenum]['gov']
				intgov=i
			if "child" in intdic[i]: # found the child bearer
				intchi = i
				del intdic[i]['child']
		if not intgov:# if no governor is indicated, i guess it's the first word
			intgov="i1"
			if intgov in sentencedic: sentencedic[intgov]['gov']=sentencedic[nodenum]['gov']
		if not intchi: intchi=intgov
		
		# correct wrong gov links
		for i in sorted(sentencedic):
			if nodenum in sentencedic[i]['gov'].keys():
				sentencedic[i]['gov'][intchi]=sentencedic[i]['gov'][nodenum]
				del sentencedic[i]['gov'][nodenum]		
		
		
		#print 'lllll',l
		# bring all in a new list with new indeces based on l
		newsentencedic={}
		for newi,oldi in enumerate(l):
			if newi:# not 0
				newsentencedic[newi]=sentencedic[oldi]
				govdic={}
				for govi,dep in sentencedic[oldi]['gov'].iteritems():
					if govi>=0 and govi in l:govdic[l.index(govi)]=dep
				newsentencedic[newi]['gov']=govdic
		#except Exception, err:
			#print traceback.format_exc()
			#print "oldoldold((((((((((((("
			#for i in sorted(sentencedic):
				#print i,sentencedic[i]
			#print ")))))))))))))))"
			#print "newnewnew((((((((((((("
			#for i in sorted(newsentencedic):
				#print i,newsentencedic[i]
			#print ")))))))))))))))"
			#print "intdic((((((((((((("
			#for i in sorted(intdic):
				#print i,intdic[i]
			#print ")))))))))))))))"
			#print nodenum
			#print intdic
			
			#if logfile:
				#f=codecs.open(logfile,"a","utf-8")
				#f.write(traceback.format_exc()+"\n\n\n"+unicode(sentencedic)+"\n\n\n"+unicode(newsentencedic)+"\n\n\n")
				#f.close()

			#raise ShitError
		#del sentencedic[nodenum]

		if debug>2:
			print "result:((((((((((((("
			for i in sorted(newsentencedic):
				print i,newsentencedic[i].get("t",""),newsentencedic[i]
			print ")))))))))))))))"
			
		return newsentencedic

##################################### bulkcorrection directly in the database ####################
		
def complexbulkcorrectdic(dic):
	changed,newdic=False,False
	
	for i,node in dic.iteritems():
		print i, node["t"],node
		
		if node.get("t"," ") in ["$","L1","L2","L3"]:
			print i, node["t"],node
			print "found false token"
			newdic=integrate(dic,i,{}) # kicking out the token
			newdic, newchanged = complexbulkcorrectdic(newdic)
			changed = True
		
	if newdic:return newdic, changed
	else:return dic,changed
	
def simplebulkcorrectdic(dic):
	changed,newdic=False,False
	
	for i,node in dic.iteritems():
		print i, node["t"],node
		
		continue
	
	
		if node["cat"]=="Cl":		node["lemma"]=node["t"]
		
		if node["lemma"]=="ils":	node["lemma"]="il"
		elif node["lemma"]=="elles":	node["lemma"]="elle"
		elif node["lemma"]=="l'":	node["lemma"]="le"
		elif node["lemma"]=="la":	node["lemma"]="le"
		elif node["lemma"]=="les":	node["lemma"]="le"
		elif node["lemma"]=="c'":	node["lemma"]="ce"
		elif node["lemma"]=="m'":	node["lemma"]="me"
		elif node["lemma"]=="t'":	node["lemma"]="te"
		elif node["lemma"]=="s'":	node["lemma"]="se"
		elif node["lemma"]=="j'":	node["lemma"]="je"
		elif node["lemma"]=="n'":	node["lemma"]="ne"
		
	return dic,True	

	
	
	

def correctfeatures(sentencetree, enterNr=None,enterDic=None):
	"""
	takes a dictionary structure: node number => feature structure
	applies changes
	gives back the new dictionary and the comparison to the old structure
	"""
	
	newsentencetree=deepcopy(sentencetree)
	
	
	if enterNr:
		newsentencetree=splice(newsentencetree,enterNr,enterDic)
	
	
	#return None,None
	
	govcats={}
	for i, node in sentencetree.iteritems():
		govcats[i]=[sentencetree[j].get("cat") for j in node.get("gov",{}) if j in sentencetree and "cat" in sentencetree[j] ]
	
	for i, node in newsentencetree.iteritems():
	
		#get short forms:
		cat = node.get("cat",None)
		t = node.get("t", None)
		token = node.get("token",None) # 
		lemma = node.get("lemma")
		mode = node.get("mode", None)
		
		
		
		#ajouter mode="indicative" et tense="present" pour tous les V qui n'ont pas de trait mode instancié
		if cat=="V" and not "mode" in node:
			node["mode"]="indicative"
			node["tense"]="present"
			
		#faire mode="infinitive" pour tous les V dont la forme se termine par er, ir, oir
		if cat=="V" and t[-2:]=="er" or t[-2:]=="ir" or t[-3:]=="oir" or t==u"répondre" or t=="dire" or t=="reprendre" or t=="prendre" or t=="conduire" :
			node["mode"]="infinitive"
		
		#faire mode="infinitive" pour tous les V dont le lemme et la forme sont identique et se termine par re
		if cat=="V" and lemma==t and lemma[-2:]=="re":
			node["mode"]="infinitive"
		#changer mode= "gerundive" en mode="present_participle"
		if cat=="V" and mode=="gerundive":
			node["mode"]="present_participle"
		
		# faire mode="past_participle" et supprimer le trait tense pour tous les V qui dépendent d'un lemme="avoir" ou lemme="être" par une relation pred
		# kim: changé en : si verbe et dépend d'un verbe par pred
		if cat=="V" and "V" in govcats[i] and "pred" in node["gov"].values():
			if "tense" in node : del node["tense"]
			node["mode"]="present_participle"
		
		#faire mode="past_participle" et supprimer le trait tense pour tous les V dont la forme se termine par é, i, u, ée, és, ées (on fait pas ie, ies, is parce que ca peut étre d'autres formes)
		if cat=="V" and (t[-1:]==u"é" or t[-1:]==u"i" or t[-1:]==u"u" or t[-2:]==u"ée" or t[-2:]==u"és" or t[-3:]==u"ées"):
			if "tense" in node : del node["tense"]
			node["mode"]="past_participle"
		
		#faire mode="present_participle" et supprimer le trait tense pour tous les V dont la forme se termine par ant
		if cat=="V" and (t[-3:]==u"ant"):
			if "tense" in node : del node["tense"]
			node["mode"]="present_participle"
		
		
		#2) il y a aussi qq lemmes à changer
		#faire lemme="ça" quand forme="ça"
		if t==u"ça":
			node["lemma"]=u"ça"
			
		#et faire forme="n'" quand token="n'" (IMPORTANT)
		if token=="n' " or token=="n'":  # TODO: regarder si c'est utile (et si on veut l'espace
			node["t"]=u"n' "
		
		
		#faire forme="qu' " quand token="qu' "
		if token=="qu' " or token=="qu'":
			node["t"]=u"qu' "
			
		
		
		
		if cat=="V" and mode=="conditional":
			node["mode"]="indicative"
			node["tense"]="conditional"
		
		
		#Pour les V il faudrait le faire une fois maintenant et une fois que tout aura été corrigé (avant l'export) ????
		

		#3) supprimer les traits qui servent à rien :
		dumbfeatures="""
		token
		que
		aux
		aux_req
		attention
		attentionFeature
		Vadj
		countable
		def
		dem
		det
		poss
		numberposs
		index
		wh
		control
		extraction
		neg
		sat
		enum
		hum
		nb
		sat
		time
		inv
		width
		features
		pcas
		real
		position""".strip().split()
		for df in dumbfeatures:
			if df in node: del node[df]
			#node.hasAttribute(df) : node.removeAttribute(df)
			
		#si cat≠V supprimer trait mode
		if cat!="V" :
			if mode : del node["mode"]
		#pour les V
		else:
			#si mode≠past_particple|present_participle supprimer trait gender
			if mode!="past_particple":
				if "gender" in node : del node["gender"]
			#si mode≠ indicative supprimer trait tense, person
			if mode!="indicative":
				if "tense" in node :del node["tense"]
				if "person" in node :del node["person"]
			#si mode= infinitive supprimer trait numberposs
			if mode=="infinitive":
				if "numberposs" in node : del node["numberposs"]
		

		if cat=="CS" or cat=="I":
			if "gender" in node : del node["gender"]
			if "number" in node : del node["number"]
			if "person" in node : del node["person"]
			if "tense" in node : del node["tense"]
			
		if cat!="V":
			if "tense" in node : del node["tense"]
			
		if lemma and lemma[0]=="-": lemma=lemma[1:]
		if cat=="Adj" and not "gender" in node  : node["gender"]="masc/fem"
		
		#test:
		#lemma="xxx_"+lemma
		#lemma=lemma[4:]
		
		
		#rewrite values into the node
		if cat: node["cat"]=cat
		if t: node["t"]=t
		if token: node["token"]=token
		if lemma: node["lemma"]=lemma
		if mode: node["mode"]=mode
		

	return newsentencetree,(newsentencetree!=sentencetree or enterNr)




def bulkcorrectDB(project, treeids=[]):
	"""
	bulk correction of a whole project! very slow!
	
	better to do directly in sql, for example:
	#change all functions:
		#update links set function='dep' where function='det';

	"""
	
	sql = SQL(project)
	db,cursor=sql.open()
	
	if treeids:	a,v=["rowid"],treeids
	else:		a,v=[],[]
	
	allt=sql.getall(cursor, "trees",a,v)
	
	ti = time()
	
	for nr, (treeid,sid,uid,annotype,status,comment,timestamp) in enumerate(allt):
		
		print "_____ treeid",treeid,"nr",nr+1,"/",len(allt),"---",float(nr+1)/(time()-ti),"trees per second",float(len(allt)-nr+1)/(float(nr+1)/(time()-ti)),"seconds to go",float(len(allt)-nr+1)/(float(nr+1)/(time()-ti))/60,"minutes to go"
		
		dic=sql.gettree(None,None,treeid, indb=db,incursor=cursor)
		if dic:
			sentencetree=dic["tree"]
			
			#newdic, changed = complexbulkcorrectdic(sentencetree)
			#newdic, changed = simplebulkcorrectdic(sentencetree)
			#newdic, changed = correctfeatures(sentencetree)
			#newdic, changed = correctfeatures(sentencetree,4,{})
			newdic, changed = correctfeatures(sentencetree,4,{	
				'i1':{ u'person': u'3', u'number': u'sg', u'cat': u'V', u'lemma': u'\xeatre', u'token': u'est', u'tense': u'present', u'mode': u'indicative', 'gov': {'i0':'root'}, u't': u'A'},
				'i2':{u'cat': u'Cl', u'lemma': u'c', u'token': u'-ce', u't': u'B', 'gov': {'i1': u'sub'}, 'child':None}
			})
			
	
			
			#break
			if changed:
				print "________________________________\n"
				#for i,node in newdic.iteritems():
					#print i, node["t"], node
				#1/0
				tokensChanged=True
				ws,sentence,_ = sql.enterTree(cursor, newdic, sid, uid,tokensChanged=tokensChanged)
				print sentence
				print "changed"
				db.commit()
	#db.commit()
	db.close()
	
	
	
if __name__ == "__main__":
	print "bonjour"
	
	#bulkcorrectDB("Rhapsodie")
	bulkcorrectDB("Rhapsodie", [9795])
	
	
