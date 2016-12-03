#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2016 Kim Gerdes
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
####

import sys, json, codecs, copy, collections, re, os, glob
debug=False
debug=True


class Tree(dict):
	"""
	just a dictionary that maps nodenumber->{"t":"qsdf", ...}
	moreover: 
	sentencefeatures is a dictionary with sentence wide information, eg "comments":"comment line content"
	words is a list of tokens
	"""
	def __init__(self, *args, **kwargs):
		self.update(*args, **kwargs)
		self.sentencefeatures={}
		self.words=[]

	def __getitem__(self, key):
		val = dict.__getitem__(self, key)
		#print 'GET', key
		return val

	def __setitem__(self, key, val):
		#print 'SET', key, val
		dict.__setitem__(self, key, val)

	def __repr__(self):
		#dictrepr = dict.__repr__(self)
		#return '%s(%s)' % (type(self).__name__, dictrepr)
		return u"\n".join([u"Tree: "+self.sentence()]+[f+": "+v for f,v in self.sentencefeatures.iteritems()]+[str(i)+u": "+self[i].get("t",u"")+"\t"+str(self[i]) for i in self]).encode("utf-8")

	def update(self, *args, **kwargs):
		#print 'update', args, kwargs
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v
	
	def sentence(self):
		if self.words==[]:
			self.words = [self[i].get("t","") for i in sorted(self)]
		return u" ".join(self.words)

def update(d, u):
	for k, v in u.iteritems():
		if isinstance(v, collections.Mapping):
			r = update(d.get(k, {}), v)
			d[k] = r
		else:
			d[k] = u[k]
	return d


def conll2tree(conllstring, correctiondic={}, rhaps=False):
	""" 
	takes the conll string (or malt) representation of a single tree and creates a tree dictionary for it
	correctiondic of the form {"tag":"cat"} (old to new) corrects feature names
	rhaps: special rhapsodie formats
	former name: tree2nodedic
	"""
	tree=Tree()
	nr=1
	conv={}
	skipuntil=0
	for line in conllstring.split('\n'):
		#print line
		if line.strip():
			if line.strip()[0]=="#": # comment of conllu
				tree.sentencefeatures["comments"]=tree.sentencefeatures.get("comments","")+line
				continue
			
			cells = line.split('\t')
			nrCells = len(cells)
			
			if not rhaps and nrCells in [4,10,11,12,13,14,19]:
				
				if nrCells == 4: # malt!
					t, tag, head, rel = cells
					if head=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t, 'tag': tag,'gov':{head: rel}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )
					nr+=1

				elif nrCells == 10: # standard conll 10 or conllu
					nr, t, lemma , tag, tag2, features, head, rel, _, _ = cells
					if "-" in nr: 
						skipuntil=int(nr.split("-")[-1])
						tree.words+=[t]
						continue
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}}
					if "=" in features:
						mf=dict([(av.split("=")[0],av.split("=")[-1]) for av in features.split("|")])
						newf=update(mf,newf)
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )
					if nr>skipuntil: tree.words+=[t]
					
				elif nrCells == 11:
					nr, t, lemma , tag, f1, f2, f3, f4, f5 ,head, rel = cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					#else:head = int(head)
					fs=[f for f in [f1, f2, f3, f4, f5] if f not in ["_"," "]]
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'features': ":".join(fs), 'gov':{int(h): r for h,r in zip(head.split("|"),rel.split("|"))}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )

				elif nrCells == 12: #Used for written corpus Orfeo
					nr, t, lemma, tag, tag2, morph, head, rel, _, _, rel2, head2 = cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}, 'morph':morph, 'gov2':{head2:rel2}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )

				elif nrCells == 13: # stupid orfeo format with extra column
					nr, t, lemma , tag, tag2, _, head, rel, _, _, _, _, _ = cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )
					
				elif nrCells == 14:
					#mate:
					#6, inscriptions, _, inscription, _, N, _, pl|masc, -1, 4, _, dep, _, _
					nr, t, lemma, lemma2, tag, tag2, morph, morph2, head, head2, rel, rel2, _, _ = cells
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
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )
				
				elif nrCells == 19: # format macaon / decoda
					_, _, nr, t, disf, tag, _, _, rel, head, _, lemma, morph, loc, beg, end, coupure,_,_ = cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'gov':{head: rel}, 'loc':loc, 'beg':beg, 'end':end}
					if coupure == "//":
						newf['coupure'] = True
					if "DISF" in disf:
						newf['disf'] = True
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )
						
			elif rhaps==True and nrCells in [3,5,12,15]:
				if nrCells == 3: continue
				elif nrCells == 5 : continue
					#and cells[-1]=="I": # inside a multi token word
					#textID,treeID,tokenID,token,wordspan=cells
					#tree[lasttokennr]
				
				elif nrCells==12:
					nr, t, lemma , tag, tag2, _, head, rel, _, _, _, _= cells
					nr = int(nr)
					if head.strip()=="_":head=-1
					else:head = int(head)
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)

				else:
					textID,treeID,tokenID,token,wordspan,wordform,lemma,pos,mood,tense,person,number,gender,iddep,typedep=cells
					nr = int(tokenID)
					#if head.strip()=="_":head=-1
					head = int(iddep)
					newf={'id':nr,'t': wordform,'lemma': lemma, 'tag': pos, 'gov':{head: typedep}}
					for k in correctiondic:
						if k in newf: newf[correctiondic[k]] = newf.pop(k)
					tree[nr]=update(tree.get(nr,{}),newf )
					
			elif rhaps=='six3col': 
				if nrCells > 11:
					token_id, t = cells[2:4]
					word_span, wordform, lemme, tag = cells[5:9]
					id_dep, type_dep = cells[14:16]
					if id_dep != '':
						#iu, nucleus, prenucleus, gov_nucleus, innucleus, gov_innucleus, postnucleus, gov_postnucleus, iu_parenthesis, iu_graft
						if nrCells > 58:
							iu, nucleus, prenucleus, gov_nucleus, innucleus, gov_innucleus, postnucleus, gov_postnucleus, iu_parenthesis, iu_graft = cells[27:37]
							associative_nucleus = cells[38]
						else:
							iu = " "
							nucleus = " "
							prenucleus = " "
							gov_nucleus = " "
							innucleus = " " 
							gov_innucleus = " "
							postnucleus = " "
							gov_postnucleus = " "
							iu_parenthesis = " "
							iu_graft = " "
							associative_nucleus = " "
						conv[int(token_id)] = nr
						newf={'id': nr,'t': wordform, 'lemma': lemme, 'tag': tag, 'id_dep':int(id_dep), 'type_dep': type_dep, 'iu': iu, 'nucleus': nucleus, 'prenucleus':prenucleus, 'gov_nucleus': gov_nucleus, 'innucleus': innucleus, 'gov_innucleus': gov_innucleus, 'postnucleus':postnucleus,'gov_postnucleus':gov_postnucleus, 'iu_parenthesis': iu_parenthesis, 'iu_graft': iu_graft, 'associative_nucleus': associative_nucleus}
						for k in correctiondic:
							if k in newf: newf[correctiondic[k]] = newf.pop(k)
						tree[nr]=update(tree.get(nr,{}),newf )
						nr+=1
			
			elif rhaps=="orfeo": # conll 10 with extra columns
				nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells[:10]
				nr = int(nr)
				if head.strip()=="_":head=-1
				else:head = int(head)
				newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'tag2': tag2, 'gov':{head: rel}}
				for k in correctiondic:
					if k in newf: newf[correctiondic[k]] = newf.pop(k)
				tree[nr]=update(tree.get(nr,{}),newf )
			
			elif debug:
				print "strange conll:",nrCells,"columns!",rhaps
	
	if rhaps == "six3col":
		###### alignement micro_macro_pros #######
		for e in tree:
			if tree[e]["id_dep"] in conv.keys():
				tree[e]["gov"] = {conv[tree[e]["id_dep"]]: tree[e]["type_dep"]}
				del tree[e]["id_dep"]
				del tree[e]["type_dep"]
			else:
				tree[e]["gov"] = {tree[e]["id_dep"]:tree[e]["type_dep"]}
				del tree[e]["id_dep"]
				del tree[e]["type_dep"]
	return tree


def conllFile2trees(path, correctiondic={}, rhaps=False, encoding="utf-8"):
	"""
	important function!
	
	called from enterConll and uploadConll in treebankfiles.cgi
	
	"""
	trees=[]
	with codecs.open(path,"r",encoding) as f:
		conlltext=""
		if rhaps==True or rhaps=="six3col":next(f) # skip first line
		for li in f:
			li=li.strip()
			if rhaps:
				if len(li)>5: conlltext+=li+"\n" # 5 characters for the empty lines in rhapsodie holding only the sample code
				else:
					tree=conll2tree(conlltext,correctiondic, rhaps)
					if tree!={}: trees+=[tree]
					del tree
					conlltext=""
			else:
				if li: 	conlltext+=li+"\n"
				else: # emptyline, sentence is finished
					tree=conll2tree(conlltext,correctiondic)
					trees+=[tree]
					del tree
					conlltext=""
		f.close()
		if conlltext.strip(): # last tree may not be followed by empty line
			tree=conll2tree(conlltext,correctiondic,rhaps)
			trees+=[tree]
		return trees


def extractTreeFromConllFile(path,number):
	"""
	currently not used
	"""
	f=codecs.open(path.encode("utf-8"),"r","utf-8")
	conlltext=""
	sentencecount=0
	tree={}
	for li in f:
		li=li.strip()
		if number==sentencecount:
			if li: 	conlltext+=li+"\n"
			else:
				tree=conll2tree(conlltext)
				sentencecount+=1
		else:
			if not li: sentencecount+=1
			if sentencecount>number: break
	if not tree and conlltext.strip():tree=conll2tree(conlltext)
	f.close()
	return tree


def extractJsonTreeFromConllFile(path,number):
	"""
	currently not used
	"""
	tree = extractTreeFromConllFile(path,number)
	print '{"tree":',json.dumps(tree),'}'


def conllFile2functioncolordico(path):
	"""
	currently not used
	creates something like fcolors={"suj":"06713e","objd":"0ce27c","compnom":"1353ba","prép":"19c4f8","dét":"203636","épi":"d14c47"} 

	"""
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
	
	fcolors=[str(hex(i*fcolorstep))[2:].rjust(6,"0") for i in range(1,len(functions)+1)]
	functions = dict(zip(sorted(functions),fcolors))
	print json.dumps(functions)	


def trees2conllFile(trees, outfile, columns=10):
	"""
	exports a list of treedics into outfile
	used after tree transformations...
	in conll14 format, the lemma position is occupied by the t position if lemma is not available
	"""
        f=codecs.open(outfile,"w","utf-8")
        for tree in trees:
                for i in sorted(tree.keys()):
                        node = tree[i]                        
                        if columns=="u": # conllu format
				govs=node.get("gov",{})
				govk = sorted(govs.keys())
				if govk:
					gk,gv = str(govk[0]),govs.get(govk[0],"_")
				else:
					gk,gv = "_","_"
				f.write("\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("tag","_"), node.get("tag2","_"), "|".join( [ a+":"+v for a,v in node.get("features",{}).iteritems() ]), gk,gv, "|".join( [ str(g)+":"+govs.get(g,"_") for g in govk[1:] ]),"_"])+"\n")
                        
                        else:
				gov = node.get("gov",{}).items()
				govid = -1
				func = "_"
				if gov:
					for govid,func in gov:
						#if govid==-1:
						#else:
						if columns==10:
							f.write("\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("tag","_"), node.get("tag2","_"), "_", str(govid),func,"_","_"])+"\n")
						elif columns==14:
							lemma = node.get("lemma","_")
							if lemma == "_": lemma = node.get("t","_")
							f.write("\t".join([str(i), node.get("t","_"), lemma, lemma or node.get("t","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n")
				else:
					if columns==10:
						f.write("\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("tag","_"), node.get("tag2","_"), "_", str(govid),func,"_","_"])+"\n")
						
					elif columns==14:
						lemma = node.get("lemma","_")
						if lemma == "_": lemma = node.get("t","_")
						f.write("\t".join([str(i), node.get("t","_"), lemma, lemma, node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n")
##                        nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells
                f.write("\n")
        f.close()


def sentences2emptyConllFile(infile, outfile):
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
				## nr, t, lemma , tag, tag2, _, head, rel, _, _ = cells
			outf.write("\n")
			counter+=1
	inf.close()
	outf.close()
	print counter, "sentences"


def textFiles2emptyConllFiles(infolder, outfolder):
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


def eraseFunctions(infile, outfile):
	"""
	erases the functions of a conll analysis
	"""
	cats={}
	trees=conllFile2trees(infile)
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
	trees2conllFile(trees,outfile)	


def makeEmpty(infilename,removeHash=True, outfolder="", lemma=True):
	"""
	takes a conll file and gives back an empty (pre-analysis file)
	removeHash removes the hash that is used for empty spaces in tokens 
	lemma = True: lemma will be empty, too 
	lemma = False: lemma not empty but equal to the token (useful when no model for lemmatizing like in chinese)
	"""
	if outfolder[-1]!="/": outfolder=outfolder+"/"
	count=0
	if infilename.endswith(".trs.lif.w+p.orfeo"):
		emptyname=outfolder+os.path.basename(infilename)[:-len(".trs.lif.w+p.orfeo")]+"-one-word-per-line.conll14"
	elif infilename.endswith(".w+p.orfeo"):
		emptyname=outfolder+os.path.basename(infilename)[:-len(".w+p.orfeo")]+"-one-word-per-line.conll14"
	elif infilename.endswith(".trs.lif.w+p_anon.orfeo"):
		emptyname=outfolder+os.path.basename(infilename)[:-len(".trs.lif.w+p_anon.orfeo")]+"-one-word-per-line.conll14"
	elif infilename.endswith(".most.recent.trees.conll10"):
		emptyname=outfolder+os.path.basename(infilename)[:-len(".most.recent.trees.conll10")]+"-one-word-per-line.conll14"
	elif infilename.endswith("-one-word-per-line.conll14_parse_retok"):
		emptyname=outfolder+os.path.basename(infilename)[:-len("-one-word-per-line.conll14_parse_retok")]
	else:
		emptyname=outfolder+os.path.basename(infilename)+"-one-word-per-line.conll14"
	with codecs.open(emptyname,"w","utf-8") as emptyfile:
		for tree in conllFile2trees(infilename):
			for i in sorted(tree.keys()):
				node = tree[i]
				t=node.get("t","_")
				if removeHash and "#" in t: t=t.replace("#"," ")
				if lemma:lem="_"
				else: lem=t
				emptyfile.write("\t".join([str(node["id"]),t, lem, lem] + ["_"]*10)+"\n")
			emptyfile.write("\n")
	return emptyname

def folderMakeEmpty(foldername):
	for infile in glob.glob(os.path.join(foldername, '*.orfeo')):
		print "making empty",infile
		makeEmpty(infile,outfolder=foldername)


def rhapsodie2standardConll(infilename="Rhapsodie.micro_simple", outfilename="Rhapsodie.micro_simple.conll.oldnum"):
	# orféo double line format --> conll 14
	with codecs.open(infilename,"r","utf-8") as infile, codecs.open(outfilename,"w","utf-8")  as outfile:
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
				head=lili[13]
				func=lili[14]
				outfile.write("\t".join([lili[2],lili[5],lili[6],lili[6],lili[7],lili[7], morph,morph,head,head,func,func,"_","_" ] )+"\n")
			elif len(line.strip())==5:
				outfile.write("\n")
				
def standardNodeNumbering(infilename="Rhapsodie.micro_simple.conll.oldnum",outfilename="Rhapsodie.conll"):
	"""
	put file to standard numbers
	"""
	count=0
	with codecs.open(outfilename,"w","utf-8") as outfile:
		
		for tree in conllFile2trees(infilename):
			count+=1
			treecorrdic={0:0}
			for i,tokenid in enumerate(sorted(tree)):
				treecorrdic[tokenid]=i+1
			for i,tokenid in enumerate(sorted(tree)):
				node=tree[tokenid]
				gov = node.get("gov",{}).items()
				govid,func= gov[0]
				outfile.write("\t".join([str(treecorrdic[tokenid]),node.get("t","_"), node.get("lemma","_"), node.get("lemma","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(treecorrdic[govid]),str(treecorrdic[govid]),func,func,"_","_"])+"\n")
			outfile.write("\n")
	#test:
	for tree in conllFile2trees(outfilename):
		print len(tree)

if __name__ == "__main__":
	pass
	#sentences2emptyConllFile("corpus/xytest.txt.seg","corpus/xytest.txt.seg.conll10")
	#eraseFunctions("corpus/conll/englishSentences.txt-dependanaly.conll10","corpus/conll/englishSentences.noFunctions.conll10")
	#text2conll(u"corpus/学习者语料库--宋晓爽",u"corpus/学习者语料库--宋晓爽-conll")
	#rhapsodie2standardConll()
	#standardNodeNumbering()
	#folderMakeEmpty("tcof")
	ts = conllFile2trees("test.conll")
	print len(ts)
	print ts[1]
	
