#!/usr/bin/python
# -*- coding: utf-8 -*-

#important functions:
	#conll2trees
	#trees2conll10

####
# Copyright (C) 2009-2012 Kim Gerdes
# kim AT gerdes. fr
# http://arborator.ilpga.fr/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public License (the "License")
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of of version 3 of the GNU Affero General Public License
# from http://www.gnu.org/licenses/agpl-3.0.html 
# For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####

import sys, json, codecs, copy, collections, re, hashlib, os, glob
#import config, xmlsqlite, traceback

debug=True

def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def tree2nodedic(tree, correctiondic={}, rhaps=False):
	""" 
	takes the conll string (or malt) representation of a single tree and creates a dictionary for it
	correctiondic of the form {"tag":"cat"} (old to new) corrects feature names
	"""
	
	nodedic={}
	nr=1
	for line in tree.split('\n'):
		#print line
		if line.strip():
			cells = line.split('\t')
			nrCells = len(cells)
			if not rhaps and nrCells in [4,10,13,14]:
				if nrCells == 4: # malt!
					t, tag, head, rel = cells

					if head=="_":head=-1
					else:head = int(head)
					
					newf={'id':nr,'t': t, 'tag': tag,'gov':{head: rel}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)

					nodedic[nr]=update(nodedic.get(nr,{}),newf )
					nr+=1
				elif nrCells == 10:
					nr, t, lemma , tag, tag2, _, head, rel, _, gloss = cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}, 'gloss':gloss}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)

					nodedic[nr]=update(nodedic.get(nr,{}),newf )
				elif nrCells == 13: # stupid orfeo format with extra column
					nr, t, lemma , tag, tag2, _, head, rel, _, _, _, _, _ = cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)

					nodedic[nr]=update(nodedic.get(nr,{}),newf )
				elif nrCells == 14:
					#mate:
					#6, inscriptions, _, inscription, _, N, _, pl|masc, -1, 4, _, dep, _, _
					nr, t, lemma, lemma2, tag, tag2, morph, morph2, head, head2, rel, rel2, _, _ = cells
					#nr, t, lemma, lemma2, _, tag, morph, _, head, _, rel, _, _, _ = cells
					nr = int(nr)
					if head=="_":head=-1
					else:head = int(head)
					if head2=="_":head2=-1
					else:head2 = int(head2)
					
					
					if lemma=="_" and lemma2!="_":lemma=lemma2
					if tag=="_" and tag2!="_":tag=tag2
					if morph=="_" and morph2!="_":morph=morph2
					if rel=="_" and rel2!="_":
						rel=rel2
						head=head2
					
					newf={'id':nr,'t': t,'lemma': lemma,'lemma2': lemma2, 'tag': tag, 'tag2': tag2, 'morph': morph, 'morph2': morph2, 'gov':{head: rel}, 'gov2':{head2: rel2} }
					
										
					
					#if rel2!="_":
						#newf={'id':nr,'t': t,'lemma': lemma2, 'tag': tag2, 'morph': morph2, 'gov':{head2: rel2} }
					#elif morph and morph != "_":
						#newf={'id':nr,'t': t,'lemma': lemma,'lemma2': lemma2, 'tag': tag2, 'morph': morph, 'gov':{head: rel} }
					#else:
						#newf={'id':nr,'t': t,'lemma': lemma,'lemma2': lemma2, 'tag': tag2, 'gov':{head: rel} }
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)

					nodedic[nr]=update(nodedic.get(nr,{}),newf )
					
					
			elif rhaps and nrCells in [3,5,15]:
				if nrCells == 3: continue
				elif nrCells == 5 : continue
					#and cells[-1]=="I": # inside a multi token word
					#textID,treeID,tokenID,token,wordspan=cells
					#nodedic[lasttokennr]
					
				else:
					textID,treeID,tokenID,token,wordspan,wordform,lemma,pos,mood,tense,person,number,gender,iddep,typedep=cells
					nr = int(tokenID)
					#if head.strip()=="_":head=-1
					head = int(iddep)
					newf={'id':nr,'t': wordform,'lemma': lemma, 'tag': pos, 'gov':{head: typedep}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					nodedic[nr]=update(nodedic.get(nr,{}),newf )
					
			elif rhaps=="orfeo": # conll 10 with extra columns
				
				nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells[:10]
				nr = int(nr)
				if head.strip()=="_":head=-1
				else:head = int(head)
				newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}}
				for k in correctiondic:
					if k in newf: newf[correctiondic[k]] = newf.pop(k)
				
				# orfeo correction. TODO: remove!
				if newf["cat"][0]=='V':
					if newf["cat"]=='VRB': newf["mode"]="finite"
					elif newf["cat"]=='VPP': newf["mode"]="participle"
					elif newf["cat"]=='VPR': newf["mode"]="participle"
					elif newf["cat"]=='VNF': newf["mode"]="infinitive"
					else: 
						print newf["cat"]
						qsdf
					newf["cat"]='V'
				elif newf["cat"]=='PRE':	newf["cat"]='Pre'
				elif newf["cat"]=='PRQ':	newf["cat"]='Qu'
				elif newf["cat"]=='PRO':	newf["cat"]='Pro'
				elif newf["cat"]=='ADV':	newf["cat"]='Adv'
				elif newf["cat"]=='CLS':	newf["cat"]='Cl'
				elif newf["cat"]=='CLI':	newf["cat"]='Cl'
				elif newf["cat"]=='CLN':	newf["cat"]='Cl'
				
				elif newf["cat"]=='INT':	newf["cat"]='I'
				elif newf["cat"]=='COO':	newf["cat"]='J'
				elif newf["cat"]=='ADN':	newf["cat"]='Adv'
				elif newf["cat"]=='NOM':	newf["cat"]='N'
				elif newf["cat"]=='ADJ':	newf["cat"]='Adj'
				elif newf["cat"]=='DET':	newf["cat"]='D'
				elif newf["cat"]=='CSU':	newf["cat"]='CS'
				
				else:
					print newf["cat"]
					qsfd
				######	
					
				nodedic[nr]=update(nodedic.get(nr,{}),newf )
					
			elif debug:
				print "strange conll:",nrCells,"columns!",rhaps
	#print nodedic
	return nodedic
		
	
def conll2trees(path, correctiondic={}, rhaps=False):
	"""
	important function!
	
	called from enterConll and uploadConll in treebankfiles.cgi
	
	"""
	trees=[]
	with codecs.open(path,"r","utf-8") as f:
		tree=""
		if rhaps==True :next(f) # skip first line
		for li in f:
			
			li=li.strip()
			if rhaps:
				if len(li)>5: tree+=li+"\n" # 5 characters for the empty lines in rhapsodie holding only the sample code
				else:
					nd=tree2nodedic(tree,correctiondic, rhaps)
					if nd!={}: trees+=[nd]
					del nd
					tree=""
			else:
				if li: 	tree+=li+"\n"
				else: # emptyline, sentence is finished copy.deepcopy(nodedic)
					nd=tree2nodedic(tree,correctiondic)
					trees+=[nd]
					del nd
					tree=""
		f.close()
		if tree.strip(): # last tree may not be followed by empty line
			nd=tree2nodedic(tree,correctiondic)
			trees+=[nd]
		return trees




	
def conlltext2trees(conlltext, correctiondic={}):
	"""
	called from quickedit
	"""
	tree=""
	trees,sentences=[],[]
	functions,categories={},{}
	conlltype=None
	renl=re.compile("[\n\r][\n\r][\n\r]+",re.U+re.M)	
	conlltext=renl.sub(u"\n\n",conlltext.strip()+u"\n") # normalize double new lines
	
	for li in conlltext.split(u"\n"):
		li=li.strip()
		#print li.encode("utf-8")+"xxx<br>"
		if li: 	tree+=li+u"\n"
		else: # emptyline, sentence is finished copy.deepcopy(nodedic)
			#print "yyyyyyyyyy",tree.encode("utf-8")
			nd=tree2nodedic(tree,correctiondic)
			#print nd
			trees+=[nd]
			sentence=[]
			for i in nd:
				#print "_____________",nd[i]
				for h in nd[i]["gov"]:	
					functions[nd[i]["gov"][h]]=None
				categories[nd[i]["tag"]]=None
				sentence+=[nd[i]["t"]]
				#print text,"<br>"
			sentences+= [" ".join(sentence)]	
			
			del nd
			tree=""
	if trees: # determine conll type by checking the last conlltext:
		for li in conlltext.split("\n"):
			li=li.strip()
			if li: 	#, correctiondic={"tag":"cat"}
				conlltype=len(li.split("\t"))
				break
	return conlltext.strip()+"\n",trees,sentences,conlltype,list(functions),list(categories)

	
def tempsaveconll(conlltext,text,conlltype,temppath="corpus/temp/"):
	"""
	called from quickedit
	"""
	renolet=re.compile("\W",re.U+re.I)
	basefilename=renolet.sub("_",text[:20].strip().replace(" ","_").replace("?","")).encode("utf-8")
	md5hex = hashlib.md5(conlltext.encode("utf-8")).hexdigest()
	filename=basefilename+"."+md5hex+".conll"+str(conlltype)
	f=codecs.open(temppath+filename , "w", "utf-8")
	f.write(conlltext)
	f.close()
	return filename.decode("utf-8")
	
	
	
def conll2tree(path,number):

	f=codecs.open(path.encode("utf-8"),"r","utf-8")
	tree=""
	sentencecount=0
	nodedic={}
	for li in f:
		li=li.strip()
		if number==sentencecount:
			#print "___",li.encode("utf-8")
			if li: 	tree+=li+"\n"
			else:
				nodedic=tree2nodedic(tree)
				sentencecount+=1
				#print "====",nodedic
		else:
			if not li: sentencecount+=1
			if sentencecount>number: break
	if not nodedic and tree.strip():nodedic=tree2nodedic(tree)

	f.close()
	return nodedic





def conll2jsonTree(path,number):
	"""
	called from getTree
	"""
	nodedic = conll2tree(path,number)
	
	print '{"tree":',json.dumps(nodedic),'}'

	
	
	
	
	


def conll2functioncolordico(path):

	f=codecs.open(path,"r","utf-8")
	functions={}
	for li in f:
		li=li.strip()

		if li:
			cells = li.split('\t')
			nrCells = len(cells)

			if nrCells == 14:
				nr, t, _, _, _, tag, _, _, head, _, rel, _, _, _ = cells
				functions[rel]=None

	f.close()
	fcolorstep=(256*256*256-2000000)/len(functions)
	
	#for f in sorted(functions):
		#functions[f]=
	fcolors=[str(hex(i*fcolorstep))[2:].rjust(6,"0") for i in range(1,len(functions)+1)]
	functions = dict(zip(sorted(functions),fcolors))
	print json.dumps(functions)
	#return 

	
#fcolors={"suj":"06713e","objd":"0ce27c","compnom":"1353ba","prép":"19c4f8","dét":"203636","épi":"d14c47"} // you can define default colors for syntactic functions



def trees2conll10(trees, outfile, colons=10):
	"""
	can export a list of treedics into outfile
	used after tree transformations...
	"""
        f=codecs.open(outfile,"w","utf-8")
        for tree in trees:
                for i in sorted(tree.keys()):
                        node = tree[i]
                        gov = node.get("gov",{}).items()
                        govid = -1
                        func = "_"
                        if gov:
				for govid,func in gov:
					if govid!=-1:
						if colons==10:
							f.write("\t".join([str(i),node.get("t","_"), node.get("lemma",""), node.get("tag","_"), node.get("tag2","_"),"_", str(govid),func,"_","_"])+"\n")
						elif colons==14:
							f.write("\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("lemma",""), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n")
			else:
				if colons==10:
					f.write("\t".join([str(i), node.get("t","_"), node.get("lemma",""),node.get("tag","_"), node.get("tag2","_"), "_", str(govid),func,"_","_"])+"\n")
				elif colons==14:
					f.write("\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("lemma",""), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n")
##                        nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells
                f.write("\n")
        f.close()


def text2conll10(infile, outfile):
	"""
	transforms a list of sentences into conll format without trees
	"""
	inf=codecs.open(infile,"r","utf-8")
	outf=codecs.open(outfile,"w","utf-8")
	counter=0
	for line in inf:
		line=line.strip()
		if line:
			for i,word in enumerate(line.split()):
				outf.write("\t".join([str(i+1),word,word,"_","_","_","-1","","_","_"])+"\n")
		##                        nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells
			outf.write("\n")
			counter+=1
	inf.close()
	outf.close()
	print counter, "sentences"



def text2conll(infolder, outfolder):
	#rebalise=re.compile("<.*?>",re.U)
	#retokenize=re.compile("([\.\;\!\?\,\(\]\"\'])",re.U+re.I)
	sentenceSplit=re.compile(ur"(\s*\n+\s*|(?<!\s[A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜÃÑÕÆÅÐÇØ])[\?\!？\!\.。！……]+\s+|\s+\|\s+|[？。！……]+)(?!\d)", re.M+re.U)
	resentence=re.compile(ur"[\?\!？\!\.。！……]+", re.M+re.U)
	
	retokenize=re.compile("(\W)",re.U+re.I)
	redoublespace=re.compile("(\s+)",re.U+re.I)
	renumber=re.compile("(\d) \. (\d)",re.U+re.I)
	
	rewhite=re.compile("\w",re.U+re.I)
	
	#repostspace=re.compile("(\]\))",re.U+re.I)
	try:os.mkdir(outfolder)
	except:print "folder exists"
	
	for infile in glob.glob(os.path.join(infolder, '*.*')):
		print  infile
		outfile=codecs.open(outfolder+"/"+infile.split("/")[-1],"w","utf-8")
		for line in codecs.open(infile,"r","utf-8"):
			
			#if line and line[0]=='\ufeff':line=line[1:] # TODO: find out why this anti BOM shit is needed...
			line=line.strip()
			#print "line",line
			for s in sentenceSplit.split(line):
				s=s.strip()
				#print "s",s
				
				
				if resentence.match(s):
					#print "match"
					outfile.write(str(count)+"\t"+s+"\n")
					outfile.write("\n")
				else:
					#print "no"
				
					count=1
				
					s = retokenize.sub(r" \1 ",s)
					s = redoublespace.sub(r" ",s)
					s = renumber.sub(r"\1.\2",s)
					
					
					for token in s.split():
						#print "---"+token+"---",[token]
						if token.strip()==u'\ufeff':continue # TODO: find out why this anti BOM shit is needed...
						outfile.write(str(count)+"\t"+token+"\n")
						count +=1
					
				
	print "finished"
						
	


def eraseFunctions(infile, outfile):
	"""
	erases the functions of a conll analysis
	"""
	cats={}
	trees=conll2trees(infile)
	print len(trees),"sentences"
	for tree in trees:
		for index in tree:
			#print tree[index]
			#print tree[index]["gov"]
			tree[index]["gov"]={}
			cats[tree[index]["tag"]]=None
			tree[index]["tag"]="_"
	for c in sorted(cats): print c
	print
	trees2conll10(trees,outfile)	


def splitForTraining(infilename="Rhapsodie.micro_simple.conll.oldnum"):
	"""
	+ splitting for parsing
	"""
	count=0
	try:
		outfile = codecs.open("bonne.Rhapsodie1000","w","utf-8")
		testfile = codecs.open("bonne.Rhapsodie600","w","utf-8")
		emptyfile = codecs.open("bonne.Rhapsodie600empty","w","utf-8")
		
		for tree in conll2trees(infilename):
			count+=1
			treecorrdic={0:0}
			for i,tokenid in enumerate(sorted(tree)):
				treecorrdic[tokenid]=i+1
			print treecorrdic
			for i,tokenid in enumerate(sorted(tree)):
				node=tree[tokenid]
				gov = node.get("gov",{}).items()
				govid,func= gov[0]
				#govid
				print "____",i+1,tokenid,node,govid,func,treecorrdic,treecorrdic[tokenid],treecorrdic[govid]
				
				if count<=1000:
					outfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(treecorrdic[govid]),str(treecorrdic[govid]),func,func,"_","_"])+"\n")
				else:
				
					testfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(treecorrdic[govid]),str(treecorrdic[govid]),func,func,"_","_"])+"\n")
					emptyfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), "_", "_", "_", "_", "_", "_", "_","_","_","_","_","_"])+"\n")
			if count<=1000:outfile.write("\n")
			else:
				testfile.write("\n")
				emptyfile.write("\n")
	finally:
		outfile.close()
		emptyfile.close()
		testfile.close()

		
	

def rhapsodie2standardConll(infilename="Rhapsodie.micro_simple", outfilename="Rhapsodie.micro_simple.conll.oldnum"):
	try:
		infile = codecs.open(infilename,"r","utf-8")
		outfile = codecs.open(outfilename,"w","utf-8")
		print infile.readline() # first header line
		for line in infile:
			print line
			lili=line.strip().split("\t")
			#i got:
			#M0009	4	1	au	B	à+le	à+le	Pre+D				sg	masc	9	ad
			# sample, sentence, tokid, begintok, chunk, tok, lemma, tag, Mood	Tense	Person	Number	Gender	ID dep	Type dep
			#  0     				     5				10				14
			#i want to obtain:
			# nr, t, lemma, lemma2, tag, tag, morph,morph, head, head, rel, rel, _, _ 
			if len(lili)>3 and lili[4][0]=="B":
				morph = "|".join([morp for morp in lili[8:13] if morp ]) or "_"
				#if not ( lili[11] or lili[13] or lili[15] or lili[17] ):
					#print "errrrrrrror 1/0"
					#1/0
				#head=lili[11] or lili[13] or lili[15] or lili[17] or "0"
				head=lili[13]
				func=lili[14]
				#head=head.split(",")[0]
				outfile.write("\t".join([lili[2],lili[5],lili[6],lili[6],lili[7],lili[7], morph,morph,head,head,func,func,"_","_" ] )+"\n")
			elif len(line.strip())==5:
				outfile.write("\n")
	finally:
		infile.close()
		outfile.close()



def standardNodeNumbering(infilename="Rhapsodie.micro_simple.conll.oldnum",outfilename="Rhapsodie.conll"):
	"""
	put file to standard numbers
	"""
	count=0
	try:
		outfile = codecs.open(outfilename,"w","utf-8")
		
		for tree in conll2trees(infilename):
			count+=1
			treecorrdic={0:0}
			for i,tokenid in enumerate(sorted(tree)):
				treecorrdic[tokenid]=i+1
			#print treecorrdic
			for i,tokenid in enumerate(sorted(tree)):
				node=tree[tokenid]
				gov = node.get("gov",{}).items()
				#print gov
				govid,func= gov[0]
				#govid
				#print "____",i+1,tokenid,node,govid,func,treecorrdic,treecorrdic[tokenid],treecorrdic[govid]
				
				outfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(treecorrdic[govid]),str(treecorrdic[govid]),func,func,"_","_"])+"\n")
				
			outfile.write("\n")
	finally:
		outfile.close()
			

	#test:
	for tree in conll2trees(outfilename):
		print len(tree)

if __name__ == "__main__":
	#conll2json("corpus/temp/faut_que_tu_me_les_d.efc1023153706bed4f641266e1c4420c.conll10",1)
	#text2conll10("corpus/xytest.txt.seg","corpus/xytest.txt.seg.conll10")
	#eraseFunctions("corpus/conll/chineseSentences.txt-dependanaly.conll10","corpus/conll/chineseSentences.noFunctions.conll10")
	#eraseFunctions("corpus/conll/englishSentences.txt-dependanaly.conll10","corpus/conll/englishSentences.noFunctions.conll10")
	#text2conll("corpus/profTickleExpertText","corpus/profTickleExpertText-conll")
	#text2conll(u"corpus/学习者语料库--宋晓爽",u"corpus/学习者语料库--宋晓爽-conll")
	
	#rhapsodie2standardConll()
	#standardNodeNumbering()
	#print sorted([len(tree) for tree in conll2trees("Rhapsodie.conll")])
	print conll2trees("corpus/conll/ouest1a.conll10")[1]
		#print len(tree)
