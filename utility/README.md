# Utility
## MC XSec calculation (getXSec.sh)

This is script which can **roughly** calculate the Xsec for given MC based on CMSSW. However, since the calculation depends on the MC configuration setting (LO, NLO), if there is any high order QCD (NNLO, NNLL) or EW (NLO) calculation involved in the MC process (for example, Higgs production), you need to follow it.


### usage
```
./getXSec.sh -d <dataset name in DAS> -n <number of event>

```
### example
```
./getXSec.sh -d /GluGluHToGG_M126_13TeV_amcatnloFXFX_pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM -n 10000

```
**Output**
```
------------------------------------
GenXsecAnalyzer:
------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Overall cross-section summary 
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Process		xsec_before [pb]		passed	nposw	nnegw	tried	nposw	nnegw 	xsec_match [pb]			accepted [%]	 event_eff [%]
0		2.896e+01 +/- 4.742e-02		3510	3323	187	6080	5752	328	1.674e+01 +/- 2.075e-01		57.8 +/- 0.7	57.7 +/- 0.6
1		2.972e+01 +/- 1.013e-01		4236	3163	1073	14523	10125	4398	1.084e+01 +/- 2.903e-01		36.5 +/- 1.0	29.2 +/- 0.4
2		2.118e+01 +/- 1.129e-01		3193	2145	1048	15411	9683	5728	5.875e+00 +/- 2.753e-01		27.7 +/- 1.3	20.7 +/- 0.3
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Total		7.986e+01 +/- 1.589e-01		10939	8631	2308	36014	25560	10454	3.343e+01 +/- 4.802e-01		41.9 +/- 0.6	30.4 +/- 0.2
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Before matching: total cross section = 7.986e+01 +- 1.589e-01 pb
After matching: total cross section = 3.343e+01 +- 4.802e-01 pb
Matching efficiency = 0.3 +/- 0.0   [TO BE USED IN MCM]
Filter efficiency (taking into account weights)= (1.20011e+06) / (1.20011e+06) = 1.000e+00 +- 0.000e+00
Filter efficiency (event-level)= (10939) / (10939) = 1.000e+00 +- 0.000e+00    [TO BE USED IN MCM]

After filter: final cross section = 3.343e+01 +- 4.802e-01 pb
After filter: final fraction of events with negative weights = 2.110e-01 +- 8.231e-04
After filter: final equivalent lumi for 1M events (1/fb) = 9.995e+00 +- 1.544e+00
```