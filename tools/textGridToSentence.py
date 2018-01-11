#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2014 Kim Gerdes
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

import sys, json, codecs, copy, collections, re, hashlib, os, glob, subprocess, fnmatch
from datetime import datetime
#import config, xmlsqlite, traceback
from parseSentences import textToSentences
debug=True

#print codecs.open("textgrids/Chloe Guyard_23953_assignsubmission_file_guyard2411.TextGrid","r","utf-16").read()






requotes=re.compile(ur'\"(.*)\"$',re.U)
#reinvers=re.compile('(-je|-tu|-t-il|-il|-elle|-t-elle|-nous|-vous|-t-ils|-ils)',re.U)

incompleteTextLine=re.compile(ur'^ *text \= \"\s*\r?\n?',re.U+re.M)
lonelyQuote=re.compile(ur'\s*\"\s*$',re.U+re.M)

            


verbose=False
verbose=True

def textgridToSentences(filter="*", keepEndSent=True, maxlength=100, writeProblemBeforeSentence=False, skipBefore=None):
	
	
	skipnext=False
	skiptier=False
	#for infilename in glob.glob(os.path.join("textgrids", filter)):
	for root, dirnames, filenames in os.walk('textgrids'):
		for filename in fnmatch.filter(filenames, filter):
			infilename=os.path.join(root, filename)
			
			
			#print datetime.fromtimestamp(os.path.getmtime(infilename)) 
			if skipBefore and str( datetime.fromtimestamp(os.path.getmtime(infilename))) < skipBefore: 
				print infilename,"too old"
				continue
			
			print  "\n\n",infilename,root, dirnames, filenames
			simplename = infilename.split("/")[1].split("_")[0].replace(" ","_") 
			print "-->",simplename
			
			problem=True
			for enc in ["utf-8","utf-16","iso-8859-1"]:
				try:
					alltext=codecs.open(infilename,"r",enc).read()
					#print enc
					problem=False
					break
				except Exception,e: 
					pass
					#print str(e)
			
			if problem:
				print "can't decode",infilename
				break
			else:
				nbtiers=alltext.count('class = "IntervalTier"')
				if nbtiers!=1:
					print "the file",infilename,"has",nbtiers,"tiers!"
			with codecs.open(infilename,"r",enc) as infile:
				#c=infile.read()
				#print c
				#continue
				first=infile.readline().strip()
				if first and ord(first[0])==65279: first=first[1:] # fucking boms!
				text=""
				if first.startswith("File type") or '"IntervalTier"' in alltext:
					print "reading textgrid",infilename
					
					intext=infile.read()
					
					intext = incompleteTextLine.sub('  text = "', intext) # remove new line after incompleteTextLine
					intext = lonelyQuote.sub('"', intext) # move lonelyQuote to previous line
					
					
					#print intext
					for line in intext.split("\n"):
						line=line.strip()
						if skipnext:
							if line==u'"phonèmes"' or line==u'"Fonctions"':
								skiptier=line
							skipnext=False
							continue
						
						if line=='"IntervalTier"' or line=='"TextTier"':
							skipnext=True
							skiptier=False
							continue
						else: skipnext= False
						
						if skiptier:
							continue
						if line.startswith("class =") or line.startswith("File type =") or line.startswith("Object class =") or line.startswith("name ="): continue
						
						m = requotes.search(line)
						if m:
							text+=m.group(1)+" "
							if verbose:print m.group(1)
						else:
							pass
							if verbose:print "no",line
						
				else:
					print "textfile",infilename
					text+=first
					for line in infile:
						line=line.strip()
						line=line.replace('"',' ')
						text+=line+" "
				text=text.replace("...",".")
				text=text.replace("/","~")
				if verbose:
					print "___",text,"___"
				
			textToSentences(text, outname="sentences/"+simplename, problemout="longsentences/"+simplename, keepEndSent=keepEndSent, maxlength=maxlength, writeProblemBeforeSentence=writeProblemBeforeSentence)	
				
			#outfile=codecs.open(outfolder+"/"+infile.split("/")[-1],"w","utf-8")




def mate(outfolder="parses", lang="fr", memory="12G", sentenceFolder=u"sentences", filter="*",depparse=True):
	
	for sentencefile in glob.glob(os.path.join(sentenceFolder, filter)):
		sentencefile=unicode(sentencefile)
		if outfolder[-1]!="/":outfolder=outfolder+"/"

		filebase=outfolder+os.path.basename(sentencefile)
		print "java -Dfile.encoding=UTF-8 -cp anna-3.6.jar is2.util.Split "+sentencefile+" > "+filebase+"-one-word-per-line.txt"
		p1 = subprocess.Popen(["java -Dfile.encoding=UTF-8 -cp anna-3.6.jar is2.util.Split "+sentencefile+" > "+filebase+"-one-word-per-line.txt"],shell=True, stdout=subprocess.PIPE)
		print p1.stdout.read()
		print "ooo",sentencefile
		########### français
		if lang=="fr":

			p1 = subprocess.Popen(["java -Xmx"+memory+" -cp anna-3.6.jar is2.lemmatizer.Lemmatizer -model lemModelAll -test  "+filebase+"-one-word-per-line.txt -out   "+filebase+"-lemmatized.txt"],shell=True)
			out, err = p1.communicate()
			print out, err
			p1 = subprocess.Popen(["java -Xmx"+memory+" -cp anna-3.6.jar is2.tag.Tagger  -model tagModelAll -test  "+filebase+"-lemmatized.txt -out   "+filebase+"-tagged.txt"],shell=True,  stdout=subprocess.PIPE) # is2.tag3.Tagger or is2.tag.Tagger ???
			out, err = p1.communicate()
			print out, err
			p1 = subprocess.Popen(["java -Xmx"+memory+" -cp anna-3.6.jar is2.mtag.Tagger  -model morphModelAll -test  "+filebase+"-tagged.txt -out   "+filebase+"-mtagged.txt"],shell=True,  stdout=subprocess.PIPE) # is2.tag3.Tagger or is2.tag.Tagger ???
			out, err = p1.communicate()
			print out, err
			p1 = subprocess.Popen(["java -Xmx"+memory+" -classpath anna-3.6.jar is2.parser.Parser -model faaModelAll -test  "+filebase+"-mtagged.txt -out  "+filebase+".trees.conll14"],shell=True,  stdout=subprocess.PIPE)
			print p1.stdout.read()


#print glob.glob(os.path.join("textgrids", 'Alexia*.*'))

#lis=""
#with codecs.open("textgrids/Alexia Murano_23945_assignsubmission_file_Text_gridmuranoalexia","r","utf-8") as infile:
	#for line in infile:
		#if line and line[0]=='"':lis+=line
#with codecs.open("textgrids/Alexia Murano_23945_assignsubmission_file_Text_gridmuranoalexia","w","utf-8") as outfile:
	#outfile.write(lis)





def rename():
	for fil in glob.glob(os.path.join(u"parses", '*-dependanaly.txt')):
		os.rename(fil, fil[:-16]+".trees.conll14")






if __name__ == "__main__":
	pass
	
	#rename()
	#textgridToSentences("*", keepEndSent=True)
	#textgridToSentences("*", keepEndSent=False, writeProblemFile=True)
	#textgridToSentences("*", keepEndSent=False, writeProblemFile=False)
	#textgridToSentences("*Lipo*")
	
	#mate(sentenceFolder="rafael")
	
	#textgridToSentences("*")
	textgridToSentences("*", keepEndSent=True, maxlength=100, writeProblemBeforeSentence=False, skipBefore="2017-11-16")
	#mate(filter="*Fum*")
	
	#for fil in glob.glob(os.path.join(u"sentences", '*')):
		#if "?" in codecs.open(fil,"r","utf-8").read():
			#print fil
