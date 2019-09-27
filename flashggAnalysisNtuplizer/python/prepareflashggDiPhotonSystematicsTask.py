import FWCore.ParameterSet.Config as cms
import importlib

def getDiPhotonSystematicsList():

    phosystlabels = []
    for direction in ["Up","Down"]:
        phosystlabels.append("MvaShift%s01sigma" % direction)
        phosystlabels.append("SigmaEOverEShift%s01sigma" % direction)
        phosystlabels.append("MaterialCentralBarrel%s01sigma" % direction)
        phosystlabels.append("MaterialOuterBarrel%s01sigma" % direction)
        phosystlabels.append("MaterialForward%s01sigma" % direction)
        phosystlabels.append("FNUFEB%s01sigma" % direction)
        phosystlabels.append("FNUFEE%s01sigma" % direction)
        phosystlabels.append("MCScaleGain6EB%s01sigma" % direction)
        phosystlabels.append("MCScaleGain1EB%s01sigma" % direction)
        for r9 in ["HighR9","LowR9"]:
            for region in ["EB","EE"]:
                phosystlabels.append("ShowerShape%s%s%s01sigma"%(r9,region,direction))
                phosystlabels.append("MCScale%s%s%s01sigma" % (r9,region,direction))
                for var in ["Rho","Phi"]:
                    phosystlabels.append("MCSmear%s%s%s%s01sigma" % (r9,region,var,direction))

        #variablesToUse.append("MvaLinearSyst%s01sigma[1,-999999.,999999.] := weight(\"MvaLinearSyst%s01sigma\")" % (direction,direction))
        #variablesToUse.append("LooseMvaSF%s01sigma[1,-999999.,999999.] := weight(\"LooseMvaSF%s01sigma\")" % (direction,direction))
        #variablesToUse.append("PreselSF%s01sigma[1,-999999.,999999.] := weight(\"PreselSF%s01sigma\")" % (direction,direction))
        #variablesToUse.append("electronVetoSF%s01sigma[1,-999999.,999999.] := weight(\"electronVetoSF%s01sigma\")" % (direction,direction))
        #variablesToUse.append("TriggerWeight%s01sigma[1,-999999.,999999.] := weight(\"TriggerWeight%s01sigma\")" % (direction,direction))
        #variablesToUse.append("FracRVWeight%s01sigma[1,-999999.,999999.] := weight(\"FracRVWeight%s01sigma\")" % (direction,direction))
        #variablesToUse.append("FracRVNvtxWeight%s01sigma[1,-999999.,999999.] := weight(\"FracRVNvtxWeight%s01sigma\")" % (direction,direction))

    return phosystlabels

def customizeSystematicsForMC(process):
    photonSmearBins = getattr(process,'photonSmearBins',None)
    photonScaleUncertBins = getattr(process,'photonScaleUncertBins',None)
    for pset in process.flashggDiPhotonSystematics.SystMethods:
        if photonSmearBins and pset.Label.value().startswith("MCSmear"):
            pset.BinList = photonSmearBins
        elif photonScaleUncertBins and pset.Label.value().count("Scale"):
            pset.BinList = photonScaleUncertBins

def customizeVPSetForData(systs, phScaleBins):
    newvpset = cms.VPSet()
    for pset in systs:
        if (pset.Label.value().count("Scale") or pset.Label.value().count("SigmaEOverESmearing")) and not pset.Label.value().count("Gain"):
            pset.ApplyCentralValue = cms.bool(True) # Turn on central shift for data (it is off for MC)
            if type(pset.NSigmas) == type(cms.vint32()):
                pset.NSigmas = cms.vint32() # Do not perform shift
            else:
                pset.NSigmas = cms.PSet( firstVar = cms.vint32(), secondVar = cms.vint32() ) # Do not perform shift - 2D case
            if pset.Label.value().count("Scale") and phScaleBins != None: 
                pset.BinList = phScaleBins
            newvpset += [pset]
    return newvpset

def includeScale_Central_Systematics(process):
    customizeSystematicsForMC(process)

def includeScale_Central(process):
    # Keep default MC central value behavior, remove all up/down shifts
    customizeSystematicsForMC(process)
    vpsetlist = [process.flashggDiPhotonSystematics.SystMethods]
    vpsetlist += [process.flashggDiPhotonSystematics.SystMethods2D]
    for vpset in vpsetlist:
        for pset in vpset:
            if type(pset.NSigmas) == type(cms.vint32()):
                pset.NSigmas = cms.vint32() # Do not perform shift
            else:
                pset.NSigmas = cms.PSet( firstVar = cms.vint32(), secondVar = cms.vint32() ) # Do not perform shift - 2D case

def includeScale(process):
    # By default remove the systematic entirely (central value and shifts)
    # For scale: put in central value, but omit shifts
    # TODO: this is wrong for sigE/E and possibly others - check!

    photonScaleBinsData = getattr(process,'photonScaleBinsData',None)
    if hasattr(process,'photonScaleBinsData'):
        print photonScaleBinsData, process.photonScaleBinsData
    process.flashggDiPhotonSystematics.SystMethods = customizeVPSetForData(process.flashggDiPhotonSystematics.SystMethods, photonScaleBinsData)
    process.flashggDiPhotonSystematics.SystMethods2D = customizeVPSetForData(process.flashggDiPhotonSystematics.SystMethods2D, photonScaleBinsData)

def prepareflashggDiPhotonSystematicsTask(process, processType, condition_dict, doSystematics = False):

    from flashgg.Systematics.SystematicsCustomize import useEGMTools
    process.load("flashgg.Systematics.flashggDiPhotonSystematics_cfi")
    process.flashggPreselectedDiPhotons.src = cms.InputTag('flashggDiPhotonSystematics')

    process.load("flashgg.Systematics." + condition_dict['flashggDiPhotonSystematics'])
    sysmodule = importlib.import_module("flashgg.Systematics." + condition_dict['flashggDiPhotonSystematics'])

    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCScaleHighR9EB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCScaleLowR9EB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCScaleHighR9EE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCScaleLowR9EE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCScaleGain6EB_EGM)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCScaleGain1EB_EGM)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MaterialCentralBarrel)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MaterialOuterBarrel)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MaterialForward)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.ShowerShapeHighR9EB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.ShowerShapeHighR9EE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.ShowerShapeLowR9EB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.ShowerShapeLowR9EE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.FNUFEB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.FNUFEE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCSmearHighR9EE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCSmearLowR9EE)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCSmearHighR9EB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MCSmearLowR9EB)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.MvaShift)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.PreselSF)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.electronVetoSF)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.TriggerWeight)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.LooseMvaSF)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.SigmaEOverEShift)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.SigmaEOverESmearing)
    process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.FracRVWeight)
    #process.flashggDiPhotonSystematics.SystMethods.append(sysmodule.FracRVNvtxWeight)

#    print 'point1'
#    for pset in process.flashggDiPhotonSystematics.SystMethods:
#        print "=== 1D syst method pset ==="
#        print pset
#        print
#    print 'point2'

    SystTask = cms.Task(process.flashggDiPhotonSystematics)

    useEGMTools(process)

    if processType == 'sig':
        if doSystematics:
            includeScale_Central_Systematics(process)
        else:
            includeScale_Central(process)
    elif processType == 'bkg':
        includeScale_Central(process)
    elif processType == 'data':
        includeScale(process)
    else:
        print "Please choose processType which is 'sig', 'bkg', 'data' in prepareflashggDiPhotonSystematicsTask(..., processType, ...) "

    if doSystematics:
        for phosystlabel in getDiPhotonSystematicsList():
            setattr( process, 'flashggPreselectedDiPhotons' + phosystlabel,
                            process.flashggPreselectedDiPhotons.clone(
                                src = cms.InputTag('flashggDiPhotonSystematics', phosystlabel)
                            )
            )
            setattr( process, 'flashggDiPhotonMVA' + phosystlabel,
                            process.flashggDiPhotonMVA.clone(
                                DiPhotonTag = cms.InputTag('flashggPreselectedDiPhotons' + phosystlabel)
                            )
            )

            SystTask.add( getattr( process, 'flashggPreselectedDiPhotons' + phosystlabel ) )
            SystTask.add( getattr( process, 'flashggDiPhotonMVA' + phosystlabel ) )

    return SystTask
