import codecs,random,os,glob,conll, shutil

def rhapsToStandardConll():
	with codecs.open("Rhapsodie.tok.simpl","r","utf-8") as infile, codecs.open("Rhapsodie.tok.simpl.conll","w","utf-8") as outfile:
		for line in infile:
			line=line.strip()
			lili = line.split("\t")
			print len(lili)
			if len(lili)==1: outfile.write("\n")
			elif len(lili)==8:
				outfile.write(lili[0]+"\t"+lili[1]+"\t"+lili[2]+"\t"+lili[2]+"\t"+lili[3]+"\t"+lili[3]+"\t"+"_\t_\t"+lili[6]+"\t"+lili[6]+"\t"+lili[7]+"\t"+lili[7]+"\t"+"_\t_\t"+"\n")
			else:
				outfile.write(line+"\n")

def treeToConll14Text(tree):
	outtext=""
	for i in sorted(tree.keys()):
		node = tree[i]
		gov = node.get("gov",{}).items()
		govid = -1
		func = "_"
		
		if gov:
			for govid,func in gov:
				if govid!=-1:
					outtext+="\t".join([str(i),node.get("t","_"), node.get("lemma",""), node.get("lemma",""), node.get("tag","_"), node.get("tag","_"), "_","_", str(govid), str(govid),func,func,"_","_"])+"\n"
		else:
			outtext+="\t".join([str(i),node.get("t","_"), node.get("lemma",""), node.get("lemma",""), node.get("tag","_"), node.get("tag","_"), "_","_", str(govid), str(govid),func,func,"_","_"])+"\n"
	return outtext

def treeToEmptyConll14Text(tree, lemma=True):
	outtext=""
	for i in sorted(tree.keys()):
		node = tree[i]
		lem="_"
		if not lemma: lem=node.get("t","_")
		outtext+="\t".join([str(i),node.get("t","_"), node.get("t","_"), lem]+["_"]*10)+"\n"
	return outtext


def makeTrainTestSets(infolder,pattern="*conll",train="train",test="test",empty="emptytest",testsize=10, lemma=True):
	tottec,tottrc,toks=0,0,0
	with codecs.open(os.path.join(infolder, test),"w","utf-8") as testf, codecs.open(os.path.join(infolder, empty),"w","utf-8") as emptyf, codecs.open(os.path.join(infolder, train),"w","utf-8") as trainf:
		for infilename in glob.glob(os.path.join(infolder, pattern)):
			print "newconvert: looking at",infilename
			
			tec,trc=0,0
			allsentences=conll.conllFile2trees(infilename)
			print len(allsentences),"sentences"
			testselection=random.sample(range(len(allsentences)),len(allsentences)*testsize/100)
			
			for i,s in enumerate(allsentences):
				toks+=len(s)
				if i in testselection:
					testf.write(treeToConll14Text(s)+"\n")
					emptyf.write(treeToEmptyConll14Text(s,lemma)+"\n")
					tec+=1
				else:
					trainf.write(treeToConll14Text(s)+"\n")
					trc+=1
						
			print "testing with",tec,"sentences. training with",trc,"sentences"
			tottec+=tec
			tottrc+=trc
			if not lemma: shutil.copyfile(os.path.join(infolder, empty), os.path.join(infolder, empty)+"_lem")
	print "tottec,tottrc,toks=",tottec,tottrc,toks
				
def tagFuncConfig(infolder,pattern="*conll"):
	tags,funcs={},{}
	for infilename in glob.glob(os.path.join(infolder, pattern)):
		print infilename
		allsentences=conll.conllFile2trees(infilename)
		for tree in allsentences:
			for i in tree.keys():
				node = tree[i]
				gov = node.get("gov",{}).items()
				tag=node.get("tag",None)
				if tag: tags[tag]=None
				for govid,func in gov:
					 funcs[func]=None
	for tag in sorted(tags):
		print tag, '{"fill": "#69399d"}'
	for func in sorted(funcs):
		print func, '{"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}'
		
		
#makeTrainTestSets("canons")	
#tagFuncConfig("canons")
#makeTrainTestSets("newcanons/punct_prev_clause")
#makeTrainTestSets("newcanons/punct_root_p0")

"""
AD {"fill": "#69399d"}
AS {"fill": "#69399d"}
BA {"fill": "#69399d"}
CC {"fill": "#69399d"}
CD {"fill": "#69399d"}
CS {"fill": "#69399d"}
DEC {"fill": "#69399d"}
DEG {"fill": "#69399d"}
DT {"fill": "#69399d"}
ETC {"fill": "#69399d"}
IJ {"fill": "#69399d"}
JJ {"fill": "#69399d"}
LB {"fill": "#69399d"}
LC {"fill": "#69399d"}
M {"fill": "#69399d"}
MSP {"fill": "#69399d"}
NN {"fill": "#69399d"}
NR {"fill": "#69399d"}
NT {"fill": "#69399d"}
OD {"fill": "#69399d"}
P {"fill": "#69399d"}
PN {"fill": "#69399d"}
PU {"fill": "#69399d"}
SB {"fill": "#69399d"}
SP {"fill": "#69399d"}
VA {"fill": "#69399d"}
VC {"fill": "#69399d"}
VE {"fill": "#69399d"}
VV {"fill": "#69399d"}
det {"fill": "#69399d"}
CJTN {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
_ {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
advmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
amod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
asp {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
assm {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
assmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
attr {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
ba {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
cc {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
ccomp {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
clf {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
conj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
cpm {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
csubj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
dep {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
det {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
dobj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
etc {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
exd {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
iobj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
lccomp {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
lmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
lobj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
loc {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
mmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
neg {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
nn {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
npadvmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
nsubj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
nsubjpass {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
nummod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
obl {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
ordmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
pass {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
pccomp {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
plmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
pobj {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
prep {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
prtmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
range {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
rcmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
rcomp {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
root {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
tmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
top {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
vmod {"stroke": "#000000","stroke-width":"1","stroke-dasharray": ""}
"""

if __name__ == "__main__":
	path="mate/fr/"
	try:
		os.mkdir(path)
	except OSError:
		pass

	makeTrainTestSets(path,pattern="trainingSet.2016-07-05.conll14",train="train",test="test",empty="emptytest",testsize=10)