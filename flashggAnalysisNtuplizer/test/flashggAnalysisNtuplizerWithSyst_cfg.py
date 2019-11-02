import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.ParameterSet.VarParsing as opts

import os, sys
import json

options = opts.VarParsing ('analysis')

options.register('year',
                 '2017',
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'year'
                 )

options.register('runMiniAOD',
                 False,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'runMiniAOD'
                 )

options.register('processType',
                 "sig",
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'processType'
                 )

options.register('filename',
                 "",
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.string,
                 'filename'
                 )

options.register('isZeroVtx',
                 True,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'isZeroVtx'
                 )

options.register('doHTXS',
                 False,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'doHTXS'
                 )

options.register('doSystematics',
                 False,
                 opts.VarParsing.multiplicity.singleton,
                 opts.VarParsing.varType.bool,
                 'doSystematics'
                 )

options.parseArguments()

metaConditionVersion = ''
triggerkey = ''

if options.year == '2016':
    metaConditionVersion = 'Era2016_RR-17Jul2018_v1.json'
    triggerkey = '.*DoubleEG.*'
elif options.year == '2017':
    metaConditionVersion = 'Era2017_RR-31Mar2018_v1.json'
    triggerkey = '.*DoubleEG.*'
elif options.year == '2018ABC':
    metaConditionVersion = 'Era2018_RR-17Sep2018_v1.json'
    triggerkey = '.*EGamma.*2018.*'
elif options.year == '2018D':
    metaConditionVersion = 'Era2018_Prompt_v1.json'
    triggerkey = '.*EGamma.*2018.*'
else:
    print '[ERROR] : Please input 2016, 2017, 2018ABC or 2018 D'
    sys.exit(0)

condition_dict = {}
with open( os.path.expandvars('$CMSSW_BASE/src/flashgg/MetaData/data/MetaConditions/' + metaConditionVersion) ) as json_condition:
    condition_dict = json.load(json_condition)

process = cms.Process("flashggAnalysisNtuplizerStd")

# geometry and global tag:
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

from Configuration.AlCa.GlobalTag import GlobalTag

if options.processType == 'data':
    process.GlobalTag = GlobalTag(process.GlobalTag, condition_dict['globalTags']['data'])
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, condition_dict['globalTags']['MC'])

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(300) )

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32( 1 )
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

process.source = cms.Source ("PoolSource",
        fileNames = cms.untracked.vstring(
#'/store/mc/RunIIFall17MiniAODv2/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/044F95FB-A342-E811-907F-5065F3816251.root'
#'/store/group/phys_higgs/cmshgg/spigazzi/flashgg/RunIIFall17-3_2_0/RunIIFall17-3_2_0/DoubleEG/RunIIFall17-3_2_0-RunIIFall17-3_2_0-v0-Run2017F-09May2018-v1/181008_110542/0000/myMicroAODOutputFile_572.root'
#'/store/data/Run2017D/DoubleEG/MINIAOD/31Mar2018-v1/00000/002F7CD1-9D37-E811-A03E-B499BAABCF1A.root'
#'/store/group/phys_higgs/cmshgg/sethzenz/flashgg/RunIIFall17-3_1_0/3_1_0/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8_PSWeights/RunIIFall17-3_1_0-3_1_0-v0-RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/180605_202241/0000/myMicroAODOutputFile_3.root'
#'root://maite.iihe.ac.be:/pnfs/iihe/cms/store/user/kskovpen/tHGG/MicroAOD/2017_v20190402/RunIIFall18-4_0_0-44-g36175afd/ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8/2017_v20190402-RunIIFall18-4_0_0-44-g36175afd-v0-RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3/190402_221745/0000/myMicroAODOutputFile_97.root'
'/store/user/spigazzi/flashgg/Era2017_RR-31Mar2018_v2/legacyRun2FullV1/VBFHToGG_M125_13TeV_amcatnlo_pythia8/Era2017_RR-31Mar2018_v2-legacyRun2FullV1-v0-RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/190703_112047/0000/myMicroAODOutputFile_37.root'
#'/store/mc/RunIIFall17MiniAODv2/TT_FCNC-TtoHJ_aThadronic_HToaa_eta_hct-MadGraph5-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/80000/BC014599-986D-E811-9493-1866DA85D72E.root'
#'/store/mc/RunIIFall17MiniAODv2/TT_FCNC-aTtoHJ_Thadronic_HToaa_eta_hut-MadGraph5-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/50000/FA62F95C-CAAB-E811-BF6F-001E67E713A4.root'
#'/store/mc/RunIIFall17MiniAODv2/GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/EEC90FD7-A242-E811-AA78-EC0D9A8225FE.root'
#'/store/group/phys_higgs/cmshgg/sethzenz/flashgg/RunIIFall17-3_1_0/3_1_0/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17-3_1_0-3_1_0-v0-RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/180609_083905/0002/myMicroAODOutputFile_2040.root'
#'/store/group/phys_higgs/cmshgg/sethzenz/flashgg/RunIIFall17-3_1_0/3_1_0/DoubleEG/RunIIFall17-3_1_0-3_1_0-v0-Run2017C-31Mar2018-v1/180606_155753/0000/myMicroAODOutputFile_217.root'
        )
)

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("DiPhotonNtuple.root")
)

# Modules builder
#**************************************************************
process.stdDiPhotonSeq = cms.Sequence()

#---------------------------------------------------------------------------------------------
# Dump ntuples from MiniAOD not microAOD. Very Slow!  Default is False
#---------------------------------------------------------------------------------------------
if options.runMiniAOD:
    process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
    process.RandomNumberGeneratorService.flashggRandomizedPhotons = cms.PSet(
              initialSeed = cms.untracked.uint32(16253245)
            )

    from flashggPlugins.flashggAnalysisNtuplizer.prepareflashggMicroAODTask import prepareflashggMicroAODTask
    MicroAODTask = prepareflashggMicroAODTask(process, options.processType, options.filename, options.doHTXS, options.year)
    process.stdDiPhotonSeq.associate( MicroAODTask )

#---------------------------------------------------------------------------------------------
# Diphoton Trigger setting
# Data : Directly filter during processing 
# MC   : Store in Ntuple
#---------------------------------------------------------------------------------------------
hlt_paths = []
for hlt in condition_dict["TriggerPaths"][triggerkey]:
    hlt_paths.append(str(hlt))

if options.processType == 'data':
    from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel
    process.hltHighLevel = hltHighLevel.clone(HLTPaths = cms.vstring(hlt_paths))
    process.stdDiPhotonSeq += process.hltHighLevel

#---------------------------------------------------------------------------------------------
# Use Zeroth vertex for diphoton
#---------------------------------------------------------------------------------------------
if options.isZeroVtx:
    process.load("flashgg.MicroAOD.flashggDiPhotons_cfi")
    process.flashggDiPhotons.whichVertex = cms.uint32(0)
    process.flashggDiPhotons.useZerothVertexFromMicro = cms.bool(True)
    process.flashggDiPhotons.vertexIdMVAweightfile = cms.FileInPath("flashgg/MicroAOD/data/TMVAClassification_BDTVtxId_SL_2016.xml")
    process.flashggDiPhotons.vertexProbMVAweightfile = cms.FileInPath("flashgg/MicroAOD/data/TMVAClassification_BDTVtxProb_SL_2016.xml")
    process.stdDiPhotonSeq += process.flashggDiPhotons

#---------------------------------------------------------------------------------------------
# DiPhoton preselection and MVA setting
#---------------------------------------------------------------------------------------------
from flashgg.Taggers.flashggDifferentialPhoIdInputsCorrection_cfi import setup_flashggDifferentialPhoIdInputsCorrection
setup_flashggDifferentialPhoIdInputsCorrection(process, condition_dict)

if options.runMiniAOD:
    process.RandomNumberGeneratorService.flashggRandomizedPhotons = cms.PSet(
              initialSeed = cms.untracked.uint32(16253245)
            )

process.load("flashgg.Taggers.flashggPreselectedDiPhotons_cfi")
process.load("flashgg.Taggers.flashggDiPhotonMVA_cfi")

#---------------------------------------------------------------------------------------------
# Jets unpack setting
#---------------------------------------------------------------------------------------------
from flashggPlugins.flashggAnalysisNtuplizer.flashggJets_cfi import maxJetCollections

if options.runMiniAOD:
    for label in range(maxJetCollections):
        setattr( process.RandomNumberGeneratorService, 'flashggRandomizedPFCHSJets%d' % label, cms.PSet(initialSeed = cms.untracked.uint32(36423784 + int(label))))

flashggUnpackedJets = cms.EDProducer("FlashggVectorVectorJetUnpacker",
                                     JetsTag = cms.InputTag("flashggFinalJets"),
                                     NCollections = cms.uint32(maxJetCollections)
                                    )

setattr(process, 'flashggUnpackedJets', flashggUnpackedJets)

UnpackedJetCollectionVInputTag = cms.VInputTag()
for i in range(0,maxJetCollections):
    UnpackedJetCollectionVInputTag.append(cms.InputTag('flashggUnpackedJets',str(i)))

#---------------------------------------------------------------------------------------------
# Merge DiPhoton and Jets modules
#---------------------------------------------------------------------------------------------
process.basicSeq = cms.Sequence(process.flashggDifferentialPhoIdInputsCorrection
                               *process.flashggPreselectedDiPhotons
                               *process.flashggDiPhotonMVA
                               *process.flashggUnpackedJets
                                )

process.stdDiPhotonSeq *= process.basicSeq

#---------------------------------------------------------------------------------------------
# Systematics setting
#---------------------------------------------------------------------------------------------
from flashggPlugins.flashggAnalysisNtuplizer.prepareflashggDiPhotonSystematicsTask import prepareflashggDiPhotonSystematicsTask, getDiPhotonSystematicsList
diphotonSystematicsTask = prepareflashggDiPhotonSystematicsTask(process, options.processType, condition_dict, options.doSystematics)
diphosystname = ['']
diphoton = [cms.InputTag('flashggPreselectedDiPhotons')]
diphotonMVA = [cms.InputTag('flashggDiPhotonMVA')]

if options.doSystematics:
    for syst in getDiPhotonSystematicsList():
        diphosystname.append(syst)
        diphoton.append(cms.InputTag('flashggPreselectedDiPhotons' + syst))
        diphotonMVA.append(cms.InputTag('flashggDiPhotonMVA' + syst))

#---------------------------------------------------------------------------------------------
# Customize your own settings based on exist modules
#---------------------------------------------------------------------------------------------
from flashggPlugins.flashggAnalysisNtuplizer.myflashggCustomize import myflashggCustomize
myflashggCustomize(process, options.runMiniAOD)

#---------------------------------------------------------------------------------------------
# Main Ntuplizer
#---------------------------------------------------------------------------------------------
from flashgg.Taggers.flashggTags_cff import HTXSInputTags
process.flashggNtuples = cms.EDAnalyzer('flashggAnaTreeMerge',
                                       diphosystnames  = cms.vstring(diphosystname),
                                       diphotons       = cms.VInputTag(diphoton),
                                       diphotonMVAs    = cms.VInputTag(diphotonMVA),
                                       nondiphosetting = cms.PSet(
                                           inputTagJets            = UnpackedJetCollectionVInputTag,
                                           ElectronTag             = cms.InputTag('flashggSelectedElectrons'),
                                           MuonTag                 = cms.InputTag('flashggSelectedMuons'),
                                           MetTag                  = cms.InputTag('flashggMets'),
                                           VertexTag               = cms.InputTag('offlineSlimmedPrimaryVertices'),
                                           BeamSpotTag             = cms.InputTag('offlineBeamSpot'),
                                           RhoTag                  = cms.InputTag('fixedGridRhoAll'),
                                           GenParticleTag          = cms.InputTag('flashggPrunedGenParticles'),
                                           GenEventInfo            = cms.InputTag('generator'),
                                           PileUpTag               = cms.InputTag('slimmedAddPileupInfo'),
                                           TriggerTag              = cms.InputTag('TriggerResults::HLT'),
                                           MetTriggerTag           = cms.InputTag('TriggerResults::PAT'),
                                           pathNames               = cms.vstring(hlt_paths),
                                           isMiniAOD               = cms.bool(options.runMiniAOD),
                                           storeSyst               = cms.bool(options.doSystematics),
                                           doHTXS                  = cms.bool(options.doHTXS),
                                           HTXSTags                = HTXSInputTags
                                       )
)

process.stdDiPhotonSeq *= process.flashggNtuples

#---------------------------------------------------------------------------------------------
# MetFilter For Data is "RECO" lebal
#---------------------------------------------------------------------------------------------
if options.processType == 'data':
    process.flashggNtuples.nondiphosetting.MetTriggerTag = cms.InputTag('TriggerResults::RECO')

#---------------------------------------------------------------------------------------------
# Final Path to run
#---------------------------------------------------------------------------------------------
process.p = cms.Path(process.stdDiPhotonSeq,diphotonSystematicsTask)
