#include "DataFormats/Common/interface/Ptr.h"
#include "FWCore/Utilities/interface/RegexMatch.h"

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"

#include "flashggPlugins/flashggAnalysisNtuplizer/interface/flashggAnaTreeMakerWithSyst.h"
#include "flashggPlugins/flashggAnalysisNtuplizer/interface/JetSystematics.h"
#include "flashggPlugins/flashggAnalysisNtuplizer/interface/PDFWeightsProducer.h"

using namespace std;
using namespace edm;
using namespace flashgg;

flashggAnaTreeMakerWithSyst::flashggAnaTreeMakerWithSyst( const edm::InputTag &diphoton, const edm::InputTag &diphotonMVA,
                                                          const edm::ParameterSet &iConfig, edm::ConsumesCollector&& iC):
    diphotonToken_        ( iC.consumes< View<flashgg::DiPhotonCandidate> >     ( diphoton                                            ) ),
    diphotonMVAToken_     ( iC.consumes< View<flashgg::DiPhotonMVAResult> >     ( diphotonMVA                                         ) ),
    inputTagJets_         ( iConfig.getParameter<vector<edm::InputTag> >        ( "inputTagJets"                                      ) ),
    electronToken_        ( iC.consumes< View<flashgg::Electron> >              ( iConfig.getParameter<InputTag> ( "ElectronTag"    ) ) ),
    muonToken_            ( iC.consumes< View<flashgg::Muon> >                  ( iConfig.getParameter<InputTag> ( "MuonTag"        ) ) ),
    metToken_             ( iC.consumes< View<flashgg::Met> >                   ( iConfig.getParameter<InputTag> ( "MetTag"         ) ) ),
    vertexToken_          ( iC.consumes< View<reco::Vertex> >                   ( iConfig.getParameter<InputTag> ( "VertexTag"      ) ) ),
    beamSpotToken_        ( iC.consumes< reco::BeamSpot >                       ( iConfig.getParameter<InputTag> ( "BeamSpotTag"    ) ) ),
    rhoTaken_             ( iC.consumes< double >                               ( iConfig.getParameter<InputTag> ( "RhoTag"         ) ) ),
    genParticleToken_     ( iC.consumes< View<reco::GenParticle> >              ( iConfig.getParameter<InputTag> ( "GenParticleTag" ) ) ),
    genEventInfoToken_    ( iC.consumes< GenEventInfoProduct >                  ( iConfig.getParameter<InputTag> ( "GenEventInfo"   ) ) ),
    pileUpToken_          ( iC.consumes< View<PileupSummaryInfo > >             ( iConfig.getParameter<InputTag> ( "PileUpTag"      ) ) ),
    triggerToken_         ( iC.consumes< edm::TriggerResults >                  ( iConfig.getParameter<InputTag> ( "TriggerTag"     ) ) ),
    mettriggerToken_      ( iC.consumes< edm::TriggerResults >                  ( iConfig.getParameter<InputTag> ( "MetTriggerTag"  ) ) ),
    pdfWeightToken_       ( iC.consumes< vector<flashgg::PDFWeightObject> >     ( iConfig.getParameter<InputTag> ( "PDFWeightTag"   ) ) )
{
    pathNames_  = iConfig.getParameter<vector<string>>( "pathNames" ) ;
    isMiniAOD_  = iConfig.getParameter<bool>( "isMiniAOD" ) ;
    storeSyst_  = iConfig.getParameter<bool>( "storeSyst" ) ;

    for (unsigned i = 0 ; i < inputTagJets_.size() ; i++) {
        auto token = iC.consumes<View<flashgg::Jet> >(inputTagJets_[i]);
        tokenJets_.push_back(token);
    }

}

flashggAnaTreeMakerWithSyst::~flashggAnaTreeMakerWithSyst()
{
}

void
flashggAnaTreeMakerWithSyst::RegisterTree( TTree* tree )
{
    dataformat.RegisterTree( tree );
}

const reco::GenParticle*
flashggAnaTreeMakerWithSyst::getMother( const reco::GenParticle &part )
{
    const reco::GenParticle *mom = &part;

    while( mom->numberOfMothers() > 0 ) {
        for( unsigned int j=0;j<mom->numberOfMothers();++j ) {
            mom = dynamic_cast<const reco::GenParticle*>(mom->mother(j));
            if( mom->pdgId() != part.pdgId() ) return mom;
        }
    }

    return mom;
}

void
flashggAnaTreeMakerWithSyst::Analyze( const edm::Event &iEvent, const edm::EventSetup &iSetup, bool isDiphoSystTree = false )
{

    // Access edm objects
    // ---------------------------------------------------------------------------------------------------------
    JetCollectionVector Jets( inputTagJets_.size() );

    iEvent.getByToken( diphotonToken_     ,     diphotons           );
    iEvent.getByToken( diphotonMVAToken_  ,     diphotonMVAs        );
    for( size_t j = 0; j < inputTagJets_.size(); ++j ) 
        iEvent.getByToken( tokenJets_[j], Jets[j] );
    iEvent.getByToken( electronToken_     ,     electrons           );
    iEvent.getByToken( muonToken_         ,     muons               );
    iEvent.getByToken( metToken_          ,     met                 );
    iEvent.getByToken( vertexToken_       ,     primaryVertices     );
    iEvent.getByToken( beamSpotToken_     ,     recoBeamSpotHandle  );
    iEvent.getByToken( rhoTaken_          ,     rho                 );
    iEvent.getByToken( genParticleToken_  ,     genParticles        );
    iEvent.getByToken( genEventInfoToken_ ,     genEventInfo        );
    iEvent.getByToken( pileUpToken_       ,     pileupInfo          );
    iEvent.getByToken( triggerToken_      ,     triggerHandle       );
    iEvent.getByToken( mettriggerToken_   ,     mettriggerHandle    );
    iEvent.getByToken( pdfWeightToken_    ,     pdfWeightHandle     );

    // dataformat Initialzation
    // ---------------------------------------------------------------------------------------------------------
    dataformat.Initialzation();

    // Global information
    // ---------------------------------------------------------------------------------------------------------
    dataformat.Rho     = *rho;
    dataformat.PVz     = primaryVertices->ptrAt(0)->z();
    dataformat.NVtx    = primaryVertices->size();
    dataformat.EvtNo   = iEvent.id().event();
    if( recoBeamSpotHandle.isValid() ) {
        dataformat.BSsigmaz = recoBeamSpotHandle->sigmaZ();
    }

    if (iEvent.isRealData()) {
        dataformat.passTrigger = true;
    } else {
        const edm::TriggerNames &triggerNames = iEvent.triggerNames( *triggerHandle );

        for (const auto& i_pathName : pathNames_) {
            std::regex path_pattern (edm::glob2reg(i_pathName));

            for( unsigned int i = 0; i < triggerNames.triggerNames().size(); i++ ) {
                string triggerName = triggerNames.triggerName( i );
                int triggerIndex   = triggerNames.triggerIndex( triggerName );
                if (triggerHandle->accept(triggerIndex)) {
                    if (std::regex_match(triggerName, path_pattern)) {dataformat.passTrigger = true; break;}
                }
            }
        }
    }

    const edm::TriggerNames& mettriggername = iEvent.triggerNames( *mettriggerHandle );
    auto passMETFilter = [ this, &mettriggername ] ( const std::string& triggername ) {
         const unsigned index = mettriggername.triggerIndex( triggername );
         return    this->mettriggerHandle->accept( index ) 
                && this->mettriggerHandle->wasrun( index ) 
                && !this->mettriggerHandle->error( index );
    };

    dataformat.Flag_HBHENoiseFilter                    = passMETFilter("Flag_HBHENoiseFilter");
    dataformat.Flag_HBHENoiseIsoFilter                 = passMETFilter("Flag_HBHENoiseIsoFilter");
    dataformat.Flag_EcalDeadCellTriggerPrimitiveFilter = passMETFilter("Flag_EcalDeadCellTriggerPrimitiveFilter");
    dataformat.Flag_goodVertices                       = passMETFilter("Flag_goodVertices");
    dataformat.Flag_globalSuperTightHalo2016Filter     = passMETFilter("Flag_globalSuperTightHalo2016Filter");
    dataformat.Flag_BadPFMuonFilter                    = passMETFilter("Flag_BadPFMuonFilter");
    dataformat.Flag_eeBadScFilter                      = iEvent.isRealData() ? passMETFilter("Flag_eeBadScFilter") : true;

    // Gen information
    if (!iEvent.isRealData()) {
        float NPu = -999.;
        for( unsigned int PVI = 0; PVI < pileupInfo->size(); ++PVI ) {
            int pu_bunchcrossing = pileupInfo->ptrAt( PVI )->getBunchCrossing();
            if( pu_bunchcrossing == 0 ) { NPu = pileupInfo->ptrAt( PVI )->getTrueNumInteractions(); break; }
        }

        dataformat.NPu = (NPu >= -0.5 && NPu <= 200.5) ? NPu : 0.;
        dataformat.genweight     = genEventInfo->weight();

        if ( !isDiphoSystTree ) {
            int NGenParticles = 0;
            const std::vector<edm::Ptr<reco::GenParticle> > genParticlesPtrs = genParticles->ptrs();
            for (const auto& it_gen : genParticles->ptrs()) {
                if ( abs(it_gen->pdgId()) > 25 ) continue;
                if ( it_gen->status() > 30 ) continue;

                dataformat.GenParticles_Pt     .emplace_back( it_gen->pt() );
                dataformat.GenParticles_Eta    .emplace_back( it_gen->eta() );
                dataformat.GenParticles_Phi    .emplace_back( it_gen->phi() );
                dataformat.GenParticles_Mass   .emplace_back( it_gen->mass() );
                dataformat.GenParticles_PdgID  .emplace_back( it_gen->pdgId() );
                dataformat.GenParticles_Status .emplace_back( it_gen->status() );
                dataformat.GenParticles_nMo    .emplace_back( it_gen->numberOfMothers() );
                dataformat.GenParticles_nDa    .emplace_back( it_gen->numberOfDaughters() );
	       
                dataformat.GenParticles_isHardProcess                              .emplace_back( it_gen->isHardProcess() );
                dataformat.GenParticles_fromHardProcessFinalState                  .emplace_back( it_gen->fromHardProcessFinalState() );
                dataformat.GenParticles_isPromptFinalState                         .emplace_back( it_gen->isPromptFinalState() );
                dataformat.GenParticles_isDirectPromptTauDecayProductFinalState    .emplace_back( it_gen->isDirectPromptTauDecayProductFinalState() );

                const reco::GenParticle* mom = getMother(*it_gen);

                dataformat.GenParticles_MomPdgID    .emplace_back( mom->pdgId() );
                dataformat.GenParticles_MomStatus   .emplace_back( mom->status() );
                dataformat.GenParticles_MomPt       .emplace_back( mom->pt() );
                dataformat.GenParticles_MomEta      .emplace_back( mom->eta() );
                dataformat.GenParticles_MomPhi      .emplace_back( mom->phi() );
                dataformat.GenParticles_MomMass     .emplace_back( mom->mass() );

                NGenParticles++;

            }

            dataformat.GenParticles_size = NGenParticles;

            //Store PDF uncertainties
            if (pdfWeightHandle.isValid() && storeSyst_)
                flashggAnalysisNtuplizer::PDFWeightsProducer ( *pdfWeightHandle, dataformat, dataformat.genweight );

        }
    }

    // Choose leading diphoton information and store them and associated ones
    const std::vector<edm::Ptr<flashgg::DiPhotonCandidate> > diphotonPtrs = diphotons->ptrs();
    const std::vector<edm::Ptr<flashgg::DiPhotonMVAResult> > diphotonMVAPtrs = diphotonMVAs->ptrs();
    if (diphotonPtrs.size() > 0) {

        // DiPhoton information 
        // ---------------------------------------------------------------------------------------------------------
        const Ptr<flashgg::DiPhotonCandidate> diphoPtr    = diphotonPtrs[0];
        const Ptr<flashgg::DiPhotonMVAResult> diphoMVAPtr = diphotonMVAPtrs[0];
        dataformat.dipho_mass                 = diphoPtr->mass();
        dataformat.dipho_pt                   = diphoPtr->pt();
        dataformat.dipho_leadPt               = diphoPtr->leadingPhoton()->pt();
        dataformat.dipho_leadEta              = diphoPtr->leadingPhoton()->eta();
        dataformat.dipho_leadPhi              = diphoPtr->leadingPhoton()->phi();
        dataformat.dipho_leadE                = diphoPtr->leadingPhoton()->energy();
        dataformat.dipho_leadEtaSC            = diphoPtr->leadingPhoton()->superCluster()->eta();
        dataformat.dipho_leadPhiSC            = diphoPtr->leadingPhoton()->superCluster()->phi();
        dataformat.dipho_leadsigEOverE        = diphoPtr->leadingPhoton()->sigEOverE();
        dataformat.dipho_leadR9               = diphoPtr->leadingPhoton()->full5x5_r9();
        dataformat.dipho_leadsieie            = diphoPtr->leadingPhoton()->full5x5_sigmaIetaIeta();
        dataformat.dipho_leadhoe              = diphoPtr->leadingPhoton()->hadronicOverEm();
        dataformat.dipho_leadIDMVA            = diphoPtr->leadingView()->phoIdMvaWrtChosenVtx();
        dataformat.dipho_leadIsEB             = diphoPtr->leadingPhoton()->isEB();
        dataformat.dipho_leadIsEE             = diphoPtr->leadingPhoton()->isEE();
        dataformat.dipho_leadhasPixelSeed     = diphoPtr->leadingPhoton()->hasPixelSeed();
        dataformat.dipho_leadGenMatch         = diphoPtr->leadingPhoton()->hasMatchedGenPhoton();
        dataformat.dipho_leadGenMatchType     = diphoPtr->leadingPhoton()->genMatchType();//enum mcMatch_t { kUnkown = 0, kPrompt, kFake  };
        dataformat.dipho_subleadPt            = diphoPtr->subLeadingPhoton()->pt();
        dataformat.dipho_subleadEta           = diphoPtr->subLeadingPhoton()->eta();
        dataformat.dipho_subleadPhi           = diphoPtr->subLeadingPhoton()->phi();
        dataformat.dipho_subleadE             = diphoPtr->subLeadingPhoton()->energy();
        dataformat.dipho_subleadEtaSC         = diphoPtr->subLeadingPhoton()->superCluster()->eta();
        dataformat.dipho_subleadPhiSC         = diphoPtr->subLeadingPhoton()->superCluster()->phi();
        dataformat.dipho_subleadsigEOverE     = diphoPtr->subLeadingPhoton()->sigEOverE();
        dataformat.dipho_subleadR9            = diphoPtr->subLeadingPhoton()->full5x5_r9();
        dataformat.dipho_subleadsieie         = diphoPtr->subLeadingPhoton()->full5x5_sigmaIetaIeta();
        dataformat.dipho_subleadhoe           = diphoPtr->subLeadingPhoton()->hadronicOverEm();
        dataformat.dipho_subleadIDMVA         = diphoPtr->subLeadingView()->phoIdMvaWrtChosenVtx();
        dataformat.dipho_subleadIsEB          = diphoPtr->subLeadingPhoton()->isEB();
        dataformat.dipho_subleadIsEE          = diphoPtr->subLeadingPhoton()->isEE();
        dataformat.dipho_subleadhasPixelSeed  = diphoPtr->subLeadingPhoton()->hasPixelSeed();
        dataformat.dipho_subleadGenMatch      = diphoPtr->subLeadingPhoton()->hasMatchedGenPhoton();
        dataformat.dipho_subleadGenMatchType  = diphoPtr->subLeadingPhoton()->genMatchType();
        dataformat.dipho_diphotonMVA          = diphoMVAPtr->result;
        dataformat.dipho_SelectedVz           = diphoPtr->vtx()->position().z();
        dataformat.dipho_GenVz                = diphoPtr->genPV().z();

        dataformat.dipho_centralWeight        = diphoPtr->centralWeight();
        if ( storeSyst_ && !isDiphoSystTree ) {
            dataformat.dipho_LooseMvaSFUp         = diphoPtr->weight("LooseMvaSFUp01sigma");
            dataformat.dipho_LooseMvaSFDown       = diphoPtr->weight("LooseMvaSFDown01sigma");
            dataformat.dipho_PreselSFUp           = diphoPtr->weight("PreselSFUp01sigma");
            dataformat.dipho_PreselSFDown         = diphoPtr->weight("PreselSFDown01sigma");
            dataformat.dipho_electronVetoSFUp     = diphoPtr->weight("electronVetoSFUp01sigma");
            dataformat.dipho_electronVetoSFDown   = diphoPtr->weight("electronVetoSFDown01sigma");
            dataformat.dipho_TriggerWeightUp      = diphoPtr->weight("TriggerWeightUp01sigma");
            dataformat.dipho_TriggerWeightDown    = diphoPtr->weight("TriggerWeightDown01sigma");
            //dataformat.dipho_FracRVWeightUp       = diphoPtr->weight("FracRVWeightUp01sigma");
            //dataformat.dipho_FracRVWeightDown     = diphoPtr->weight("FracRVWeightDown01sigma");
        }

        // Electron information
        // ---------------------------------------------------------------------------------------------------------
        int Nelecs = 0;
        for ( const auto& it_elec : electrons->ptrs() ) {

            dataformat.elecs_Charge                    .emplace_back( it_elec->charge() );
            dataformat.elecs_Pt                        .emplace_back( it_elec->pt() );
            dataformat.elecs_Eta                       .emplace_back( it_elec->eta() );
            dataformat.elecs_Phi                       .emplace_back( it_elec->phi() );
            dataformat.elecs_Energy                    .emplace_back( it_elec->energy() );
            dataformat.elecs_EtaSC                     .emplace_back( it_elec->superCluster()->eta() );
            dataformat.elecs_PhiSC                     .emplace_back( it_elec->superCluster()->phi() );
            dataformat.elecs_EGMCutBasedIDVeto         .emplace_back( it_elec->passVetoId() );
            dataformat.elecs_EGMCutBasedIDLoose        .emplace_back( it_elec->passLooseId() );
            dataformat.elecs_EGMCutBasedIDMedium       .emplace_back( it_elec->passMediumId() );
            dataformat.elecs_EGMCutBasedIDTight        .emplace_back( it_elec->passTightId() );
            dataformat.elecs_EGMMVAIDMedium            .emplace_back( it_elec->passMVAMediumId() );
            dataformat.elecs_EGMMVAIDTight             .emplace_back( it_elec->passMVATightId() );
            dataformat.elecs_passConvVeto              .emplace_back( it_elec->passConversionVeto() );

            if ( it_elec->hasUserFloat("ecalTrkEnergyPostCorr") ) {
                dataformat.elecs_EnergyCorrFactor          .emplace_back( it_elec->userFloat("ecalTrkEnergyPostCorr") / it_elec->energy() );
                dataformat.elecs_EnergyPostCorrErr         .emplace_back( it_elec->userFloat("ecalTrkEnergyErrPostCorr") );
                dataformat.elecs_EnergyPostCorrScaleUp     .emplace_back( it_elec->userFloat("energyScaleUp") );
                dataformat.elecs_EnergyPostCorrScaleDown   .emplace_back( it_elec->userFloat("energyScaleDown") );
                dataformat.elecs_EnergyPostCorrSmearUp     .emplace_back( it_elec->userFloat("energySigmaUp") );
                dataformat.elecs_EnergyPostCorrSmearDown   .emplace_back( it_elec->userFloat("energySigmaDown") );
            }

            if ( isMiniAOD_ ) {
                dataformat.elecs_GsfTrackDz     .emplace_back( it_elec->gsfTrack()->dz( diphoPtr->vtx()->position() ) );
                dataformat.elecs_GsfTrackDxy    .emplace_back( it_elec->gsfTrack()->dxy( diphoPtr->vtx()->position() ) );
                if ( !iEvent.isRealData() && !isDiphoSystTree ) {
                    const reco::GenParticle* gen = it_elec->genLepton();
                    if ( gen != nullptr ) {
                        dataformat.elecs_GenMatch .emplace_back( true );
                        dataformat.elecs_GenPdgID .emplace_back( gen->pdgId() );
                        dataformat.elecs_GenPt    .emplace_back( gen->pt() );
                        dataformat.elecs_GenEta   .emplace_back( gen->eta() );
                        dataformat.elecs_GenPhi   .emplace_back( gen->phi() );
                    } else {
                        dataformat.elecs_GenMatch .emplace_back( false );
                        dataformat.elecs_GenPdgID .emplace_back( 0 );
                        dataformat.elecs_GenPt    .emplace_back( -999. );
                        dataformat.elecs_GenEta   .emplace_back( -999. );
                        dataformat.elecs_GenPhi   .emplace_back( -999. );
                    }
                }
            }
            
            Nelecs++;
        }
        dataformat.elecs_size = Nelecs;

        // Muon information
        // ---------------------------------------------------------------------------------------------------------
        int Nmuons = 0;
        for ( const auto& it_muon : muons->ptrs() ) {
            if ( !it_muon->passed(reco::Muon::CutBasedIdLoose) ) continue;
            if ( fabs( it_muon->eta() ) > 2.4 ) continue;

            int vtxInd = 0;
            float dzmin = 999.;
            const std::vector<edm::Ptr<reco::Vertex> > vertexPointers = primaryVertices->ptrs();
            for( unsigned int ivtx = 0; ivtx < vertexPointers.size(); ivtx++ ) {
                edm::Ptr<reco::Vertex> vtx = vertexPointers[ivtx];
                if( !it_muon->innerTrack() ) continue; 
                if( fabs( it_muon->innerTrack()->vz() - vtx->position().z() ) < dzmin ) {                    
                    dzmin = fabs( it_muon->innerTrack()->vz() - vtx->position().z() );
                    vtxInd = ivtx;
                }
            }

            dataformat.muons_Charge                  .emplace_back( it_muon->charge() );
            dataformat.muons_MuonType                .emplace_back( it_muon->type() );
            dataformat.muons_Pt                      .emplace_back( it_muon->pt() );
            dataformat.muons_Eta                     .emplace_back( it_muon->eta() );
            dataformat.muons_Phi                     .emplace_back( it_muon->phi() );
            dataformat.muons_Energy                  .emplace_back( it_muon->energy() );
            dataformat.muons_BestTrackDz             .emplace_back( it_muon->muonBestTrack()->dz( diphoPtr->vtx()->position() ) );
            dataformat.muons_BestTrackDxy            .emplace_back( it_muon->muonBestTrack()->dxy( diphoPtr->vtx()->position() ) );
            dataformat.muons_CutBasedIdMedium        .emplace_back( it_muon->passed(reco::Muon::CutBasedIdMedium) );
            dataformat.muons_CutBasedIdTight         .emplace_back( muon::isTightMuon( *it_muon, *(diphoPtr->vtx()) ) );
            dataformat.muons_CutBasedIdTight_bestVtx .emplace_back( muon::isTightMuon( *it_muon, *(vertexPointers[vtxInd]) ) );
            dataformat.muons_PFIsoDeltaBetaCorrR04   .emplace_back( it_muon->fggPFIsoSumRelR04() );
            dataformat.muons_TrackerBasedIsoR03      .emplace_back( it_muon->fggTrkIsoSumRelR03() );

            if ( isMiniAOD_ ) {
                if ( !iEvent.isRealData() && !isDiphoSystTree ) {
                    const reco::GenParticle* gen = it_muon->genLepton();
                    if ( gen != nullptr ) {
                        dataformat.muons_GenMatch .emplace_back( true );
                        dataformat.muons_GenPdgID .emplace_back( gen->pdgId() );
                        dataformat.muons_GenPt    .emplace_back( gen->pt() );
                        dataformat.muons_GenEta   .emplace_back( gen->eta() );
                        dataformat.muons_GenPhi   .emplace_back( gen->phi() );
                    } else {
                        dataformat.muons_GenMatch .emplace_back( false );
                        dataformat.muons_GenPdgID .emplace_back( 0 );
                        dataformat.muons_GenPt    .emplace_back( -999. );
                        dataformat.muons_GenEta   .emplace_back( -999. );
                        dataformat.muons_GenPhi   .emplace_back( -999. );
                    }
                }
            }

            Nmuons++;
        }
        dataformat.muons_size = Nmuons;

        // Jet information
        // ---------------------------------------------------------------------------------------------------------
        int Njets = 0;
        unsigned int jetCollectionIndex = diphoPtr->jetCollectionIndex();
        for ( const auto& it_jet : Jets[jetCollectionIndex]->ptrs() ) {
            if ( !it_jet->passesJetID(flashgg::Tight2017) ) continue;
            if ( fabs( it_jet->eta() ) > 4.7 ) { continue; }

            dataformat.jets_Pt                            .emplace_back( it_jet->pt() );
            dataformat.jets_Eta                           .emplace_back( it_jet->eta() );
            dataformat.jets_Phi                           .emplace_back( it_jet->phi() );
            dataformat.jets_Mass                          .emplace_back( it_jet->mass() );
            dataformat.jets_Energy                        .emplace_back( it_jet->energy() );
            dataformat.jets_PtRaw                         .emplace_back( it_jet->correctedJet( "Uncorrected" ).pt() );
            dataformat.jets_QGL                           .emplace_back( it_jet->QGL() );
            dataformat.jets_RMS                           .emplace_back( it_jet->rms() );
            dataformat.jets_puJetIdMVA                    .emplace_back( it_jet->puJetIdMVA() );
            dataformat.jets_passesPuJetIdLoose            .emplace_back( it_jet->passesPuJetId( diphotonPtrs[0], PileupJetIdentifier::kLoose ) );
            dataformat.jets_passesPuJetIdMedium           .emplace_back( it_jet->passesPuJetId( diphotonPtrs[0], PileupJetIdentifier::kMedium ) );
            dataformat.jets_passesPuJetIdTight            .emplace_back( it_jet->passesPuJetId( diphotonPtrs[0], PileupJetIdentifier::kTight ) );
            dataformat.jets_GenJetMatch                   .emplace_back( it_jet->hasGenMatch() );
            dataformat.jets_pfDeepCSVJetTags_probb        .emplace_back( it_jet->bDiscriminator( "pfDeepCSVJetTags:probb" ) );
            dataformat.jets_pfDeepCSVJetTags_probbb       .emplace_back( it_jet->bDiscriminator( "pfDeepCSVJetTags:probbb" ) );
            dataformat.jets_pfDeepCSVJetTags_probc        .emplace_back( it_jet->bDiscriminator( "pfDeepCSVJetTags:probc" ) );
            dataformat.jets_pfDeepCSVJetTags_probudsg     .emplace_back( it_jet->bDiscriminator( "pfDeepCSVJetTags:probudsg" ) );
            dataformat.jets_pfDeepFlavourJetTags_probb    .emplace_back( it_jet->bDiscriminator( "mini_pfDeepFlavourJetTags:probb" ) );
            dataformat.jets_pfDeepFlavourJetTags_probbb   .emplace_back( it_jet->bDiscriminator( "mini_pfDeepFlavourJetTags:probbb" ) );
            dataformat.jets_pfDeepFlavourJetTags_probc    .emplace_back( it_jet->bDiscriminator( "mini_pfDeepFlavourJetTags:probc" ) );
            dataformat.jets_pfDeepFlavourJetTags_probuds  .emplace_back( it_jet->bDiscriminator( "mini_pfDeepFlavourJetTags:probuds" ) );
            dataformat.jets_pfDeepFlavourJetTags_probg    .emplace_back( it_jet->bDiscriminator( "mini_pfDeepFlavourJetTags:probg" ) );
            dataformat.jets_pfDeepFlavourJetTags_problepb .emplace_back( it_jet->bDiscriminator( "mini_pfDeepFlavourJetTags:problepb" ) );
	   
            auto jer = flashggAnalysisNtuplizer::JERUncertainty( *it_jet, *rho, iSetup );
            dataformat.jets_JECScale                      .emplace_back( it_jet->pt() / it_jet->correctedJet( "Uncorrected" ).pt() );
            dataformat.jets_JERScale                      .emplace_back( std::get<0>(jer) );

            if ( storeSyst_ && !isDiphoSystTree ) {
                dataformat.jets_JECUnc                    .emplace_back( flashggAnalysisNtuplizer::JECUncertainty( *it_jet, iSetup ) );
                dataformat.jets_JERUp                     .emplace_back( std::get<1>(jer) );
                dataformat.jets_JERDown                   .emplace_back( std::get<2>(jer) );
            }

            dataformat.jets_GenFlavor         .emplace_back( it_jet->partonFlavour() );
            dataformat.jets_GenHadronFlavor   .emplace_back( it_jet->hadronFlavour() );

            if ( isMiniAOD_ && !iEvent.isRealData() && !isDiphoSystTree ) {
                const reco::GenParticle* parton = it_jet->genParton();
                if ( parton != nullptr ) {
                    dataformat.jets_GenPartonMatch    .emplace_back( true );
                    dataformat.jets_GenPt             .emplace_back( parton->pt() );
                    dataformat.jets_GenEta            .emplace_back( parton->eta() );
                    dataformat.jets_GenPhi            .emplace_back( parton->phi() );
                    dataformat.jets_GenPdgID          .emplace_back( parton->pdgId() );
                } else {
                    dataformat.jets_GenPartonMatch    .emplace_back( false );
                    dataformat.jets_GenPt             .emplace_back( -999. );
                    dataformat.jets_GenEta            .emplace_back( -999. );
                    dataformat.jets_GenPhi            .emplace_back( -999. );
                    dataformat.jets_GenPdgID          .emplace_back( 0 );
                }
            }

            Njets++;
        } //jet loop
        dataformat.jets_size = Njets;

        // Met information
        // ---------------------------------------------------------------------------------------------------------
        edm::Ptr<flashgg::Met> theMet = met->ptrAt( 0 );
        dataformat.met_Pt                           = theMet->pt();
        dataformat.met_Phi                          = theMet->phi();
        dataformat.met_Px                           = theMet->px();
        dataformat.met_Py                           = theMet->py();
        dataformat.met_SumET                        = theMet->sumEt();
        dataformat.met_Significance                 = theMet->significance();
        dataformat.ecalBadCalibReducedMINIAODFilter = theMet->getPassEcalBadCalibFilter();

        if ( storeSyst_ && !isDiphoSystTree ) {
            dataformat.met_CorrPtShiftJetEnUp           = theMet->shiftedPt  ( pat::MET::JetEnUp           );
            dataformat.met_CorrPtShiftJetEnDown         = theMet->shiftedPt  ( pat::MET::JetEnDown         );
            dataformat.met_CorrPtShiftJetResUp          = theMet->shiftedPt  ( pat::MET::JetResUp          );
            dataformat.met_CorrPtShiftJetResDown        = theMet->shiftedPt  ( pat::MET::JetResDown        );
            dataformat.met_CorrPtShiftUncEnUp           = theMet->shiftedPt  ( pat::MET::UnclusteredEnUp   );
            dataformat.met_CorrPtShiftUncEnDown         = theMet->shiftedPt  ( pat::MET::UnclusteredEnDown );
            dataformat.met_CorrPtShiftPhoEnUp           = theMet->shiftedPt  ( pat::MET::PhotonEnUp        );
            dataformat.met_CorrPtShiftPhoEnDown         = theMet->shiftedPt  ( pat::MET::PhotonEnDown      );
            dataformat.met_CorrPhiShiftJetEnUp          = theMet->shiftedPhi ( pat::MET::JetEnUp           );
            dataformat.met_CorrPhiShiftJetEnDown        = theMet->shiftedPhi ( pat::MET::JetEnDown         );
            dataformat.met_CorrPhiShiftJetResUp         = theMet->shiftedPhi ( pat::MET::JetResUp          );
            dataformat.met_CorrPhiShiftJetResDown       = theMet->shiftedPhi ( pat::MET::JetResDown        );
            dataformat.met_CorrPhiShiftUncEnUp          = theMet->shiftedPhi ( pat::MET::UnclusteredEnUp   );
            dataformat.met_CorrPhiShiftUncEnDown        = theMet->shiftedPhi ( pat::MET::UnclusteredEnDown );
            dataformat.met_CorrPhiShiftPhoEnUp          = theMet->shiftedPhi ( pat::MET::PhotonEnUp        );
            dataformat.met_CorrPhiShiftPhoEnDown        = theMet->shiftedPhi ( pat::MET::PhotonEnDown      );
        }
    
        //Only store the first diphoton candidate which passes diphoton preselection with mass > 100 GeV
        if(diphoPtr->mass() > 100.) dataformat.TreeFill();

    }//diphoton candidate > 0
}

// Local Variables:
// mode:c++
// indent-tabs-mode:nil
// tab-width:4
// c-basic-offset:4
// End:
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
