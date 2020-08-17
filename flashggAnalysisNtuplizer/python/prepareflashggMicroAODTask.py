import os
import FWCore.ParameterSet.Config as cms

def includeflashggDiphoton(process, condition_dict):
    from flashgg.MicroAOD.flashggTkVtxMap_cfi import flashggVertexMapUnique,flashggVertexMapNonUnique
    setattr(process, 'flashggVertexMapUnique', flashggVertexMapUnique)
    setattr(process, 'flashggVertexMapNonUnique', flashggVertexMapNonUnique)

    process.load("flashgg.MicroAOD.flashggPhotons_cfi")
    process.load("flashgg.MicroAOD.flashggRandomizedPhotonProducer_cff")
    process.load("flashgg.MicroAOD.flashggDiPhotons_cfi")

    process.flashggPhotons.photonIdMVAweightfile_EB = cms.FileInPath(str(condition_dict["flashggPhotons"]["photonIdMVAweightfile_EB"]))
    process.flashggPhotons.photonIdMVAweightfile_EE = cms.FileInPath(str(condition_dict["flashggPhotons"]["photonIdMVAweightfile_EE"]))
    process.flashggPhotons.effAreasConfigFile = cms.FileInPath(str(condition_dict["flashggPhotons"]["effAreasConfigFile"]))
    process.flashggPhotons.is2017 = cms.bool(condition_dict["flashggPhotons"]["is2017"])

    process.flashggDiPhotons.vertexIdMVAweightfile = cms.FileInPath(str(condition_dict["flashggDiPhotons"]["vertexIdMVAweightfile"]))
    process.flashggDiPhotons.vertexProbMVAweightfile = cms.FileInPath(str(condition_dict["flashggDiPhotons"]["vertexProbMVAweightfile"]))

def includeflashggLepton(process):
    process.load("flashgg.MicroAOD.flashggElectrons_cfi")
    process.load("flashgg.MicroAOD.flashggMuons_cfi")
    process.load("flashgg.MicroAOD.flashggLeptonSelectors_cff")

def includeflashggJet(process, isMC):
    from flashgg.MicroAOD.flashggTkVtxMap_cfi import flashggVertexMapForCHS
    from flashggPlugins.flashggAnalysisNtuplizer.flashggJets_cfi import addFlashggPFCHSJets, maxJetCollections

    JetCollectionVInputTag = cms.VInputTag()
    for ivtx in range(0,maxJetCollections):
        addFlashggPFCHSJets (process       = process,
                             isData        = (not isMC),
                             vertexIndex   = ivtx,
                             useZeroVertex = False,
                             label         = '' + str(ivtx))
        JetCollectionVInputTag.append(cms.InputTag('flashggSelectedPFCHSJets' + str(ivtx)))
    flashggFinalJets = cms.EDProducer("FlashggVectorVectorJetCollector",
                                      inputTagJets = JetCollectionVInputTag
    )
    setattr(process, 'flashggVertexMapForCHS', flashggVertexMapForCHS)
    setattr(process, 'flashggFinalJets', flashggFinalJets)

def includePFMET(process, isMC, year):

    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
    runMetCorAndUncFromMiniAOD(process,
                         isData = (not isMC),
                         fixEE2017 = True,
                         fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold': 3.139},
                         # will produce new MET collection: slimmedMETsModifiedMET
                         postfix = "ModifiedMET",
                         )

    met_tag = 'slimmedMETs'
    if year == '2017':
        met_tag = 'slimmedMETsModifiedMET'

    if year == '2017' or year == '2018':
        baddetEcallist = cms.vuint32(
            [872439604,872422825,872420274,872423218,
            872423215,872416066,872435036,872439336,
            872420273,872436907,872420147,872439731,
            872436657,872420397,872439732,872439339,
            872439603,872422436,872439861,872437051,
            872437052,872420649,872422436,872421950,
            872437185,872422564,872421566,872421695,
            872421955,872421567,872437184,872421951,
            872421694,872437056,872437057,872437313])
        ecalBadCalibReducedMINIAODFilter = cms.EDFilter(
            "EcalBadCalibFilter",
            EcalRecHitSource = cms.InputTag("reducedEgamma:reducedEERecHits"),
            ecalMinEt        = cms.double(50.),
            baddetEcal       = baddetEcallist,
            taggingMode      = cms.bool(True),
            debug            = cms.bool(False)
        )
        setattr( process, 'ecalBadCalibReducedMINIAODFilter', ecalBadCalibReducedMINIAODFilter )

    process.flashggMets = cms.EDProducer('FlashggMetProducer',
                                          verbose = cms.untracked.bool(False),
                                          metTag  = cms.InputTag(met_tag),
                                          )

def includeRunIIEleID(process):

    from PhysicsTools.SelectorUtils.tools.vid_id_tools import DataFormat,switchOnVIDElectronIdProducer,setupAllVIDIdsInModule,setupVIDElectronSelection
    dataFormat = DataFormat.MiniAOD
    switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
    my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
                     'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
                     'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff']
    for idmod in my_id_modules:
        setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)
    process.flashggElectrons.eleVetoIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-veto")
    process.flashggElectrons.eleLooseIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-loose")
    process.flashggElectrons.eleMediumIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-medium")
    process.flashggElectrons.eleTightIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-tight")
    process.flashggElectrons.eleMVALooseIdMap = cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wpLoose")
    process.flashggElectrons.eleMVAMediumIdMap = cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp90")
    process.flashggElectrons.eleMVATightIdMap = cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp80")
    process.flashggElectrons.mvaValuesMap = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17IsoV2Values")
    process.flashggElectrons.effAreasConfigFile = cms.FileInPath("RecoEgamma/ElectronIdentification/data/Fall17/effAreaElectrons_cone03_pfNeuHadronsAndPhotons_94X.txt")

def includeRunIIEGMPhoID(process):
    from PhysicsTools.SelectorUtils.tools.vid_id_tools import DataFormat,switchOnVIDPhotonIdProducer,setupAllVIDIdsInModule,setupVIDPhotonSelection
    dataFormat = DataFormat.MiniAOD
    switchOnVIDPhotonIdProducer(process, DataFormat.MiniAOD)
    my_id_modules = ['RecoEgamma.PhotonIdentification.Identification.mvaPhotonID_Fall17_94X_V2_cff']
    for idmod in my_id_modules:
        setupAllVIDIdsInModule(process,idmod,setupVIDPhotonSelection)
    process.flashggPhotons.effAreasConfigFile = cms.FileInPath("RecoEgamma/PhotonIdentification/data/Fall17/effAreaPhotons_cone03_pfPhotons_90percentBased_TrueVtx.txt")
    process.flashggPhotons.egmMvaValuesMap = cms.InputTag("photonMVAValueMapProducer:PhotonMVAEstimatorRunIIFall17v2Values")

def includeflashggGenInfo(process):
    process.load("flashgg.MicroAOD.flashggMicroAODGenSequence_cff")

def includeflashggPDFs(process):
    process.load("flashgg.MicroAOD.flashggPDFWeightObject_cfi")

# signal specific setting
def prepareSignal(process, filename, year, condition_dict):

    includeflashggDiphoton(process, condition_dict)
    includeflashggLepton(process)
    includeflashggJet(process, isMC = True)
    includePFMET(process, True, year)
    includeRunIIEleID(process)
    includeRunIIEGMPhoID(process)
    includeflashggGenInfo(process)

    #if filename.find("THQ") != -1 or filename.find("THW") != -1:
    #    process.flashggPDFWeightObject.isStandardSample = False
    #    process.flashggPDFWeightObject.isThqSample = True

    process.flashggGenPhotonsExtra.defaultType = 1

# background specific setting
def prepareBackground(process, filename, year, condition_dict):

    includeflashggDiphoton(process, condition_dict)
    includeflashggLepton(process)
    includeflashggJet(process, isMC = True)
    includePFMET(process, True, year)
    includeRunIIEleID(process)
    includeRunIIEGMPhoID(process)
    includeflashggGenInfo(process)

    if filename.find("Sherpa") != -1:
        process.flashggGenPhotonsExtra.defaultType = 1

# data specific setting
def prepareData(process, year, condition_dict):

    includeflashggDiphoton(process, condition_dict)
    includeflashggLepton(process)
    includeflashggJet(process, isMC = False)
    includePFMET(process, False, year)
    includeRunIIEleID(process)
    includeRunIIEGMPhoID(process)

    from flashggPlugins.flashggAnalysisNtuplizer.flashggJets_cfi import maxJetCollections
    for vtx in range(0, maxJetCollections):
        delattr(process, "patJetGenJetMatchAK4PFCHSLeg%i"%vtx)
        delattr(process, "patJetFlavourAssociationAK4PFCHSLeg%i"%vtx)
        delattr(process, "patJetPartons%i"%vtx)
        delattr(process, "patJetPartonMatchAK4PFCHSLeg%i"%vtx)

def prepareflashggMicroAODTask(process, processType, filename, year = '2017', condition_dict):

    if processType == 'sig':
        prepareSignal(process, filename, year, condition_dict)
    elif processType == 'bkg':
        prepareBackground(process, filename, year, condition_dict)
    elif processType == 'data':
        prepareData(process, year, condition_dict)
    else:
        raise Exception, "Please specify 'sig', 'bkg', 'data'"

    setattr( process, 'MicroAODTask', cms.Task() )
    getattr( process, 'MicroAODTask', cms.Task() ).add(*[getattr(process,prod) for prod in process.producers_()])
    getattr( process, 'MicroAODTask', cms.Task() ).add(*[getattr(process,filt) for filt in process.filters_()])
    return process.MicroAODTask
