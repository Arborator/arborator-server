#!/usr/bin/python
# -*- coding: utf-8 -*-


from xml.dom import minidom
from xml.dom.ext import PrettyPrint
from random import choice, shuffle
import subprocess,re
from config import *
#functions=["suj","objd","obji","objloc","attrmesu","épi","appos","mod","prép","dét","attrsuj","attrobj","racine"]

punct=u",;:!?./§*+=(){}[]"

debug=False
#debug==True

#sentence=u"L'île de Bermeja est une ancienne île inhabitée du golfe du Mexique, portée disparue en 1997.".strip()
#outfilename="sentence.xml"



def makexmls(text, randomdep, split=True):
	filelist=[]
	#print"oooooooooooo",split
	if split:
		text=insertAtSentenceBorders(text,"(([\?\!](?![\?\!])|((?<!\s[A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜÃÑÕÆÅÐÇØ])\.\s)|\s\|)\s*)", 
		r"\1\n","Mr Ph Dr Mme Ms".split())
		for sentence in text.split("\n") :
			#print "sentence",sentence.encode('utf-8')
			sentence=sentence.strip()
			if not sentence or sentence=="":continue
			f = ("cache/"+sentence[:50]+".xml").encode("utf-8")
			filelist+=[f]
			makexml(sentence,f,randomdep)
	else: # only one sentence (text is presplit)
		#print "*************"
		f = ("cache/"+text[:50]+".xml").encode("utf-8")
		filelist+=[f]
		makexml(text,f,randomdep)
	return filelist
		
		
		


def makexml(sentence,outfilename,randomdep):
	
	outfile=open(outfilename,"w")

	doc=minidom.Document()

	sentEl=doc.createElement("sentence")
	text=doc.createElement("text")
	text.appendChild(doc.createTextNode(sentence))
	sentEl.appendChild(text)
	doc.appendChild(sentEl)

	wordtier=doc.createElement("tier")
	wordtier.setAttribute("type","words")
	sentEl.appendChild(wordtier)

	token=""
	start,id=0,0

	def makeTokenNode(token,start,end,id):
		#print "***"+token.encode("utf-8")
		if token.lower()=="des":
			id=makeTokenNode("de",start,end,id)
			token="les"
		if token.lower()=="du":
			id=makeTokenNode("de",start,end,id)
			token="le"
		if token.lower()=="au":
			id=makeTokenNode(u"à",start,end,id)
			token="le"
		if token.lower()=="aux":
			id=makeTokenNode(u"à",start,end,id)
			token="les"
		if token.lower()=="duquel":
			id=makeTokenNode(u"de",start,end,id)
			token="lequel"
		if token.lower()=="auquel":
			id=makeTokenNode(u"à",start,end,id)
			token="lequel"
		if token.lower()=="auxquels":
			id=makeTokenNode(u"à",start,end,id)
			token="lesquels"
		if token.lower()=="auxquelles":
			id=makeTokenNode(u"à",start,end,id)
			token="lesquelles"
		#print token,punct
		try:
			if token in punct:  #.decode("utf-8")
				tokenEl=doc.createElement("punct")
				tokenEl.appendChild(doc.createTextNode(token))
				tokenEl.setAttribute("start",str(start))
				tokenEl.setAttribute("end",str(end))
				#tokenEl.setAttribute("id",str(id))
				wordtier.appendChild(tokenEl)
				return id
			else:
				tokenEl=doc.createElement("word")
				tokenEl.appendChild(doc.createTextNode(token))
				tokenEl.setAttribute("start",str(start))
				tokenEl.setAttribute("end",str(end))
				tokenEl.setAttribute("id",str(id))
				#lemma=doc.createElement("lemma")
				#lemma.appendChild(doc.createTextNode(token))
				#tokenEl.appendChild(lemma)
				wordtier.appendChild(tokenEl)
				id+=1
				return id
		except:
			print "problem",token
		

	for i,ll in enumerate(sentence+" "):
		if (ll==" " or ll=="'" or ll=="," or ll=="."):
			ii=i
		
			if token=="":
				start=ii+1
				continue
			
			if ll=="'" :
				token+=ll
				ii+=1
			
			id = makeTokenNode(token,start,ii-1,id)
			
			
			if ll in punct: id = makeTokenNode(ll,ii,ii,id)
			
			token=""
			if ll=="'" :ii-=1
			start=ii+1
			
		else:	token+=ll

	ids=[]
	for n in doc.getElementsByTagName("word"):
		ids+=[n.getAttribute("id")]

	if debug:	print ids
	shuffle(ids)

	for i,n in enumerate(doc.getElementsByTagName("word")):
		if randomdep:
			govel=doc.createElement("gov")
			govel.setAttribute("id",ids[i])
			govel.setAttribute("func",choice(syntfunctions))
			n.appendChild(govel)
		#n.setAttribute("govid",ids[i])
		#n.setAttribute("func",choice(functions))
		#print unicode(n.childNodes[0].nodeValue).encode("utf-8"),"===",
		
		#s=unicode(n.childNodes[0].nodeValue).encode("utf-8")
		s=n.childNodes[0].nodeValue #).encode("utf-8")
		
		args=["./buildlexicon -d . -p lemmm consult"]
		p = subprocess.Popen(args ,stdout=subprocess.PIPE, shell=True,stdin=subprocess.PIPE, stderr=subprocess.PIPE)
		(stdoutdata, stderrdata) = p.communicate(s.encode("utf-8")+"\n")
		#print s,(stdoutdata, stderrdata),p
		if stdoutdata.strip()!="":le = stdoutdata.decode("utf-8").strip().split()[0]
		if le=="?":le=s
		#lemma=doc.createElement("lemma")
		#lemma.appendChild(doc.createTextNode(le))
		#n.appendChild(lemma)
		
		features=doc.createElement("features")
		features.setAttribute("cat","nom")
		features.setAttribute("lemma",le)
		n.appendChild(features)
		

		
	#print "_____________"	
		
		

	outfile.write(doc.toprettyxml())
	outfile.close()

def insertAtSentenceBorders(text,border,insert,abreviationList):

	abreviationsregex = re.compile("("+ "|".join(abreviationList) +")\.",re.UNICODE+re.M+re.IGNORECASE)
	borderRegex=re.compile(border,re.UNICODE+re.M+re.IGNORECASE)
	#replaceRegex=re.compile(replace,re.UNICODE+re.M+re.IGNORECASE)

	text = abreviationsregex.sub(r"\1__ABR__",text) # substitute abreviation+period => abreviation+__ABR__
	text = borderRegex.sub(insert,text) # substitute period ==> period + new line symbol
	text = re.sub("__ABR__",".",text) # substitute __ABR__ ==> period
	text = re.sub(r"[  \t\r\f\v\n]*\n+[  \t\r\f\v\n]*","\n",text,re.UNICODE+re.M) # strange: different spaces???
	return text

	#print "test"
	#doc = minidom.parse(outfilename)
	#for n in doc.getElementsByTagName("word"):print unicode(n.childNodes[0].nodeValue).encode("utf-8")
	#print doc.getElementsByTagName("ponct")
	#print doc.getElementsByTagName("text")[0].childNodes[0].nodeValue
	#PrettyPrint(doc.getElementsByTagName("text")[0])





if __name__ == "__main__":
	print "bonjour"	
	
	makexml("Nous mangions qsdf","qsdf.xml",False)
	
	#text=u"""
	#L'île de Bermeja est une ancienne île inhabitée du golfe du Mexique, portée disparue en 1997. Diverses cartes et documents historiques la situaient à plus de 100 kilomètres au nord de l'État de Yucatan, sous dépendance mexicaine.

	#Sa localisation est actuellement indéterminée, tout comme son existence. Elle est donnée pour disparue, situation qui affecte la souveraineté du Mexique en faveur des États-Unis, dans une région stratégique du Golfe du même nom, dans laquelle on présume l'existence de réserves pétrolières.
	#Histoire [modifier]

	#Bermeja est apparue pour la première fois sur les cartes comme un simple point dans la mer. Son existence fut attestée dès 1864 sur la Carta Etnográfica de México (carte ethnographique du Mexique), ainsi que par l'ouvrage Islas mexicanas, publié par le secrétariat à l'Éducation publique, qui la situait (p. 110) à 22°33′N 91°22′W / 22.55, -91.367

	#Plusieurs agences fédérales des États-Unis, dont la CIA, ont rapporté son existence [1].

	#Sa présence géographique s'est maintenue jusqu'en 1946 dans un ouvrage édité par le gouvernement mexicain. Mais à la fin des années 1990, aux environs de ce récif corallien, les compagnies pétrolières découvrent un gisement pétrolier qui serait l'un des plus important au monde. Et alors que le Mexique négociait avec les États-Unis un accord pour délimiter la frontière maritime entre les deux pays, Bermeja cessa d'être visible.

	#En 1997 le ministère mexicain de la Marine dépêcha un navire océanographique pour vérifier l'existence de cette île, mais Nestor Yee Amador, le capitaine (promu depuis amiral) du navire, chargé de la recherche rapporta qu'il n'avait rien trouvé. L'inspection, réalisée le 5 septembre à 7 h, aux coordonnées indiquées plus haut par balayage hydroacoustique dans un cadre de recherche d'une superficie de 322,5 milles nautiques carrés donna des résultats négatifs.

	#Le 9 juin 2000, l'accord Clinton-Zedillo ne la mentionne pas; ce qui donne aux États-Unis 40% de la zone pétrolière découverte précédemment dans cette zone.

	#En 2008, des sénateurs du Parti d'action nationale ont demandé au gouvernement des « explications » sur la disparition de l'île. Selon l'un d'eux, Alberto Coppola, cette disparition aurait été provoquée (L'île aurait tout simplement été dynamitée[2]), et l'île serait toujours présente à quarante ou cinquante mètres sous la surface de la mer[3].
	#Importance stratégique [modifier]

	#L'existence de l'île de Bermeja attribuait au Mexique un plus grand espace maritime, étendu sur environ cent milles vers le nord, que celui qui résulta du traité Clinton-Zedillo, par lequel le Mexique et les États-Unis définirent la frontière maritime dans le golfe du Mexique lors d'une cérémonie célébrée à Washington le 9 juin 2000.
	#Notes, sources et références [modifier]

	#1. En se basant sur les ouvrages mexicains.
	#2. (fr) Mexique - A la recherche de l'île perdue, Le Point, 11 décembre 2008, p. 24. [archive]
	#3. (fr) Bermeja, l'île disparue au large du Mexique, Le Figaro, 2 décembre 2008, p. 7. [archive]


	#"""

	#paragraphs=text.split("\n")
	#c=0
	#for p in paragraphs:
		#if p.strip()=="" or p.strip()[-1] not in ".!?)" : continue
		#for s in p.split("."):
			#s=s.strip()
			#if s!="":
				#sentence=s+"."
				##outfilename="xml/sentence."+sentence[:30].decode("utf-8").encode('ascii', 'ignore')+".xml"
				#outfilename="xml/sentence."+str(c)+".xml"
				#c+=1
				#print "______________________________\n\n"
				#print sentence.encode("utf-8"),outfilename
				#print "______________________________\n\n"
				#makexml(sentence,outfilename)
