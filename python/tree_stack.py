#!/usr/bin/env python
from samplesclass import sample
from printcolor import printc
import pickle
import ROOT 
from array import array
from BetterConfigParser import BetterConfigParser
import sys, os
from mvainfos import mvainfo
#from gethistofromtree import getHistoFromTree, orderandadd
from optparse import OptionParser
from HistoMaker import HistoMaker, orderandadd
from copy import copy,deepcopy
from StackMaker import StackMaker
from math import sqrt

#CONFIGURE
argv = sys.argv
parser = OptionParser()
parser.add_option("-P", "--path", dest="path", default="",
                      help="path to samples")
parser.add_option("-R", "--reg", dest="region", default="",
                      help="region to plot")
parser.add_option("-C", "--config", dest="config", default=[], action="append",
                      help="configuration file")
(opts, args) = parser.parse_args(argv)
if opts.config =="":
        opts.config = "config"
print opts.config
config = BetterConfigParser()
config.read(opts.config)

path = opts.path
region = opts.region


#get locations:
Wdir=config.get('Directories','Wdir')
samplesinfo=config.get('Directories','samplesinfo')
#limitpath=config.get('Directories','limits')
limitpath=path
section='Plot:%s'%region

infofile = open(samplesinfo,'r')
info = pickle.load(infofile)
infofile.close()

if 'vhbb_TH_BDT' in region:
#-----------Histo from TH File------------------------------------
    if 'Zee' in region: d='Zee'
    elif 'Zmm' in region: d='Zmm'
    if 'LowPt' in region:
        var='BDT8_RMed'
        newregion='LowPt_%s'%d
    elif 'HighPtLooseBTag' in region:
        var='BDT8_RTightLooseBTag'
        newregion='HighPtLooseBTag_%s'%d
    elif 'HighPt' in region:
        var='BDT8_RTight'
        newregion='HighPt_%s'%d

    blind = eval(config.get('Plot:%s'%newregion,'blind'))
    Stack=StackMaker(config,var,newregion,True)

    log = eval(config.get('Plot:%s'%newregion,'log'))

    if log:
        setup = config.get('Plot_general','setupLog').split(',')
    else:
        setup = config.get('Plot_general','setup').split(',')
    Dict = eval(config.get('LimitGeneral','Dict'))

    setup.remove('DYc')

    sys_BDT= eval(config.get('LimitGeneral','sys_BDT'))
    systematicsnaming8TeV = eval(config.get('LimitGeneral','systematicsnaming8TeV'))
    systs=[systematicsnaming8TeV[s] for s in sys_BDT]
    if eval(config.get('LimitGeneral','weightF_sys')): systs.append('UEPS')
    input = ROOT.TFile.Open(limitpath+'/'+region+'.root','read')

    lumi=0
    for job in info:
        if job.name == d:
            lumi=job.lumi
            break
        else: pass

    histos = []
    typs = []

    #systs=[] 

    setup2=copy(setup)
    setup2.remove('ZH')

    shapesUp = [[] for _ in range(0,len(setup2))]
    shapesDown = [[] for _ in range(0,len(setup2))]
    for s in setup:
        if 'ZH' == s:
            Overlay=copy(input.Get(Dict[s]))
        else:
            histos.append(input.Get(Dict[s]))
            typs.append(s)
            print s
            for syst in systs:
                print 'syst %s'%syst
                shapesUp[setup2.index(s)].append(input.Get(Dict[s]+syst+'Up'))
                shapesDown[setup2.index(s)].append(input.Get(Dict[s]+syst+'Down'))

    #print shapesUp

    ##calculate the Errors
    #counter = 0
    #total=[]
    #errUp=[]
    #errDown=[]
    #print 'total bins %s'%histos[0].GetNbinsX()
    #for h in range(0,len(histos)):
    #    if counter == 0:
    #        Error = ROOT.TGraphAsymmErrors(histos[h])
    #    for bin in range(1,histos[h].GetNbinsX()+1):
    #        if counter == 0 and h == 0:
    #            total.append(0)
    #            errUp.append(0)
    #            errDown.append(0)
    #        point=histos[h].GetXaxis().GetBinCenter(bin)
    #        total[bin-1]+=histos[h].GetBinContent(bin)
    #        for i in range(0,len(shapesUp[h])):
    #            errUp[bin-1]+=(shapesUp[h][i].GetBinContent(bin)-histos[h].GetBinContent(bin))**2
    #            #print 'down = %s'%((shapesUp[h][i].GetBinContent(bin)-histos[h].GetBinContent(bin))/histos[h].GetBinContent(bin))
    #            errDown[bin-1]+=(shapesDown[h][i].GetBinContent(bin)-histos[h].GetBinContent(bin))**2
    #        #errUp[bin-1]+=(histos[h].GetBinError(bin))**2
    #        #errDown[bin-1]+=(histos[h].GetBinError(bin))**2
    #        
    #        Error.SetPoint(bin-1,point,1)
    #    counter += 1
    #    
    #for bin in range(0,len(total)):
    #    if not total[bin] == 0: 
    #        Error.SetPointEYlow(bin,sqrt(errDown[bin])/total[bin])
    #        print 'down %s'%(sqrt(errDown[bin])/total[bin])
    #        Error.SetPointEYhigh(bin,sqrt(errUp[bin])/total[bin])
    #        print 'up   %s'%(sqrt(errUp[bin])/total[bin])

    #-------------
    counter = 0
    errUp=[]
    total=[]
    errDown=[]
    print 'total bins %s'%histos[0].GetNbinsX()
    for h in range(0,len(histos)):
        if counter == 0:
            Error = ROOT.TGraphAsymmErrors(histos[h])
        for bin in range(1,histos[h].GetNbinsX()+1):
            if counter == 0 and h == 0:
                total.append(0)
                errUp.append([])
                errDown.append([])
            point=histos[h].GetXaxis().GetBinCenter(bin)
            total[bin-1]+=histos[h].GetBinContent(bin)
            Error.SetPoint(bin-1,point,1)
        counter += 1



    for bin in range(1,histos[0].GetNbinsX()+1):
        for i in range(0,len(shapesUp[h])):
            totUp=0
            totDown=0
            for h in range(0,len(histos)):
                if histos[h].GetBinContent(bin)>0:
                    totUp+=(shapesUp[h][i].GetBinContent(bin)-histos[h].GetBinContent(bin))#/histos[h].GetBinContent(bin)
                    totDown+=(shapesDown[h][i].GetBinContent(bin)-histos[h].GetBinContent(bin))#/histos[h].GetBinContent(bin)
            errUp[bin-1].append(totUp)
            errDown[bin-1].append(totDown)
        for h in range(0,len(histos)):
            if histos[h].GetBinContent(bin)>0:
                errUp[bin-1].append(histos[h].GetBinError(bin))#/histos[h].GetBinContent(bin))
                errDown[bin-1].append(histos[h].GetBinError(bin))#/histos[h].GetBinContent(bin))
            else:
                errUp[bin-1].append(0)
                errDown[bin-1].append(0)

    totErrUp=[sqrt(sum([x**2 for x in bin])) for bin in errUp]
    totErrDown=[sqrt(sum([x**2 for x in bin])) for bin in errDown]

    

    for bin in range(0,histos[0].GetNbinsX()):
        if not total[bin] == 0: 
            Error.SetPointEYlow(bin,totErrDown[bin]/total[bin])
            print 'down %s'%(totErrDown[bin]/total[bin])
            Error.SetPointEYhigh(bin,totErrUp[bin]/total[bin])
            print 'up   %s'%(totErrUp[bin]/total[bin])




    #-----------------------


    datas=[input.Get('data_obs')]
    datatyps = [None]
    datanames=[d] 


    if blind:
        #for 15 Bin DCs: 
        for bin in range(10,datas[0].GetNbinsX()+1):
            datas[0].SetBinContent(bin,0)
        #for bin in range(1+datas[0].GetNbinsX()/2,datas[0].GetNbinsX()+1):
        #    datas[0].SetBinContent(bin,0)


    histos.append(copy(Overlay))
    typs.append('ZH')
    #histos.append(copy(Overlay))
    #typs.append('ZH')

    Stack.histos = histos
    Stack.typs = typs
    Stack.datas = datas
    Stack.datatyps = datatyps
    Stack.datanames= datanames
    Stack.overlay = Overlay
    Stack.AddErrors=Error
    Stack.lumi = lumi
    Stack.doPlot()

    print 'i am done!\n'
#-------------------------------------------------


else:
#----------Histo from trees------------
    vars = (config.get(section, 'vars')).split(',')

    if 'ZLight' in region or 'TTbar' in region or 'Zbb' in region: SignalRegion = False
    else:
        SignalRegion = True
        print 'You are in the Signal Region!'

    data = config.get(section,'Datas')

    samples=config.get('Plot_general','samples')
    samples=samples.split(',')

    weightF=config.get('Weights','weightF')
    Group = eval(config.get('Plot_general','Group'))

    #GETALL AT ONCE
    options = []
    Stacks = []
    for i in range(len(vars)):
        Stacks.append(StackMaker(config,vars[i],region,SignalRegion))
        options.append(Stacks[i].options)

    Plotter=HistoMaker(path,config,region,options)

    #print '\nProducing Plot of %s\n'%vars[v]
    Lhistos = [[] for _ in range(0,len(vars))]
    Ltyps = [[] for _ in range(0,len(vars))]
    Ldatas = [[] for _ in range(0,len(vars))]
    Ldatatyps = [[] for _ in range(0,len(vars))]
    Ldatanames = [[] for _ in range(0,len(vars))]

    #Find out Lumi:
    lumicounter=0.
    lumi=0.
    for job in info:
        if job.name in data:
            lumi+=float(job.lumi)
            lumicounter+=1.

    if lumicounter > 0:
        lumi=lumi/lumicounter

    Plotter.lumi=lumi
    mass = Stacks[0].mass

    for job in info:
        if eval(job.active):
            if job.subsamples:
                for subsample in range(0,len(job.subnames)):
                    
                    if job.subnames[subsample] in samples:
                        hTempList, typList = Plotter.getHistoFromTree(job,subsample)
                        for v in range(0,len(vars)):
                            Lhistos[v].append(hTempList[v])
                            Ltyps[v].append(Group[job.subnames[subsample]])
                            print job.subnames[subsample]

            else:
                if job.name in samples:
                    if job.name == mass:
                        print job.name
                        hTempList, typList = Plotter.getHistoFromTree(job)
                        for v in range(0,len(vars)):
                            if SignalRegion:
                                Lhistos[v].append(hTempList[v])
                                Ltyps[v].append(Group[job.name])
                            Overlaylist= deepcopy(hTempList)
                                                                                                                                 
                    else:
                        print job.name
                        hTempList, typList = Plotter.getHistoFromTree(job)
                        for v in range(0,len(vars)):
                            Lhistos[v].append(hTempList[v])
                            Ltyps[v].append(Group[job.name])

                elif job.name in data:
                    #print 'DATA'
                    hTemp, typ = Plotter.getHistoFromTree(job)
                    for v in range(0,len(vars)):
                        Ldatas[v].append(hTemp[v])
                        Ldatatyps[v].append(typ[v])
                        Ldatanames[v].append(job.name)

    for v in range(0,len(vars)):

        histos = Lhistos[v]
        typs = Ltyps[v]
        Stacks[v].histos = Lhistos[v]
        Stacks[v].typs = Ltyps[v]
        Stacks[v].datas = Ldatas[v]
        Stacks[v].datatyps = Ldatatyps[v]
        Stacks[v].datanames= Ldatanames[v]
        Stacks[v].overlay = Overlaylist[v]
        Stacks[v].lumi = lumi
        Stacks[v].doPlot()
        print 'i am done!\n'
#----------------------------------------------------
sys.exit(0)
