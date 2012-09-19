#!/usr/bin/env python
from copytree import copytree
from printcolor import printc
from samplesclass import sample
import pickle
import sys
from optparse import OptionParser
from BetterConfigParser import BetterConfigParser
import ROOT


#get files info from config
parser = OptionParser()
parser.add_option("-I", "--inPath", dest="pathIn", default="",
                      help="path to the input files")
parser.add_option("-O", "--outPath", dest="pathOut", default="",
                      help="path to the output files")
parser.add_option("-C", "--config", dest="config", default="",
                      help="configuration defining the plots to make")
argv=sys.argv
(opts, args) = parser.parse_args(argv)

pathIN=opts.pathIn
pathOUT=opts.pathOut

if opts.config =="":
        opts.config = "7TeVsamples_ZZ.cfg"
print "Config is: %s" %(opts.config)
config = BetterConfigParser()
config.read(opts.config)

prefix=config.get('General','prefix')
newprefix=config.get('General','newprefix')
lumi=float(config.get('General','lumi'))
weightexpression=config.get('General','weightexpression')
#this is only to speed it up, remove for final trees!
Precut=''
info = []

for Sample in config.sections():
    if not config.has_option(Sample,'infile'): continue
    infile = config.get(Sample,'infile')
    if not ROOT.TFile.Open(pathIN+prefix+infile+'.root',"READ"):
        print 'WARNING: No file ' + pathIN+prefix+infile+ ' found! '
        continue
    #this need exception handle    
    #if type(eval(config.get(Sample,'sampleName'))) != list: 
    
    
    #Initialize samplecalss element
    sampleName = config.get(Sample,'sampleName')
    sampleType = config.get(Sample,'sampleType')
    cut = config.get(Sample, 'cut')
    info.append(sample(sampleName,sampleType))

    info[-1].addtreecut(cut)
    info[-1].path=pathOUT
    info[-1].identifier=infile
    info[-1].weightexpression=weightexpression
    info[-1].lumi=lumi
    info[-1].prefix=newprefix
    
    if eval(config.get(Sample,'subsamples')):
        info[-1].subsamples=True
        info[-1].group = eval((config.get(Sample,'sampleGroup')))
        info[-1].subcuts = eval((config.get(Sample, 'subcuts')))
        info[-1].subnames = eval((config.get(Sample, 'subnames')))
        if sampleType != 'DATA':
            info[-1].sf = eval((config.get(Sample, 'SF')))
            info[-1].xsec = eval((config.get(Sample,'xSec')))    
    else:
        info[-1].group = config.get(Sample,'sampleGroup')
        if sampleType != 'DATA':
            info[-1].sf = config.get(Sample, 'SF')
            info[-1].xsec = config.get(Sample,'xSec')
        
    copytree(pathIN,pathOUT,prefix,newprefix,infile,'',cut+Precut)

#dump info   
infofile = open(pathOUT+'/samples.info','w')
pickle.dump(info,infofile)
infofile.close()