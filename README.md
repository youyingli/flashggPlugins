# flashggPlugins

Various plugins to analyze flashgg MicroAOD

## flashggAnalysisNtuplizer

Produce flat TTrees from MicroAOD

### Installation

```
cmsrel CMSSW_10_5_0
cd CMSSW_10_5_0/src/
cmsenv
git cms-init
cd $CMSSW_BASE/src
git clone -b dev_legacy_runII https://github.com/cms-analysis/flashgg 
cd $CMSSW_BASE/src
scram b -j4

git clone https://github.com/ntuhep/flashggPlugins
scram b -j4
```

### Run

```
cmsRun flashggAnalysisNtuplizerWithSyst_cfg.py doSystematics=1 year=2017
```
