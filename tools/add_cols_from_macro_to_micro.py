#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import sys, listdir, makedirs, path
import argparse
import datetime

# --------------------------------
# options and arguments

parser = argparse.ArgumentParser(description=sys.argv[0])

parser.add_argument('--micro','-micro', help=u"Folder containing microsyntactic tabular files", action='store', dest='dos_in', metavar=('MICRO'), required=True)
parser.add_argument('--all','-all', help=u"Folder containing aligned tabular files", action='store', dest='dos_add', metavar=('ALL'), required=True)

args = parser.parse_args()  

dos_in = args.dos_in
if dos_in[-1]=="/": dos_in = dos_in[:-1]

dos_add = args.dos_add
if dos_add[-1]=="/": dos_add = dos_add[:-1]


# columns in aligned files (here speaker (in column 4) and layer (in column 26)
speaker_col = 4 # when it has already been moved!!
layer_col = 26


for fic in (listdir(dos_in)):

#    base_dos = dos_add.rsplit("/", 1)[0]
    base_name = fic.rsplit(".", 2)[0]
    print "\nProcessing "+base_name
    if "~" in fic or "Rhapsodie" in fic: continue #skip global file (done after)

    pt=open(dos_in+"/"+fic, "r")
    contents=pt.readlines()
    pt.close()

    pt=open(dos_add+"/"+base_name+".micro_macro_prosody.tabular", "r")
    contents_add=pt.readlines()
    pt.close()

    all_pt = (dos_add+"/"+fic)

    pt=open(dos_in+"/"+fic, "w")  

    for i, line in enumerate(contents):

        line = line.strip("\n")
        line = line.split("\t")

        #print "length = ", len(line)  #check length

        contents[i] = line

        # get info to be added
        speaker = contents_add[i].split("\t")[speaker_col]
        layer = contents_add[i].split("\t")[layer_col]

        # print directly by putting speaker in column 4 (so the same as in the
        # original aligned files and layer at the end)
        print>>pt, "\t".join(line[:speaker_col]) + "\t" + speaker + "\t" + "\t".join(line[speaker_col:])+ layer

    pt.close()

# do global file
ncols = 27
pt=open(dos_add+"/Rhapsodie.micro_macro_prosody.tabular", "r") 
contents = pt.readlines()
pt.close()

pt=open(dos_in+"/Rhapsodie.micro.tabular", "w")  

for i, line in enumerate(contents):

    line = line.strip("\n")
    line = line.split("\t")

    #print "length = ", len(line)  #check length

    contents[i] = line

    print>>pt, "\t".join(line[:27])


pt.close()




        
    


