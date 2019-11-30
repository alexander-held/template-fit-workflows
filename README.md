# Template fit toy examples
Examples for template profile likelihood fits.

## Minimal example
The minimal example consists of two processes, a signal and a background process.
It also includes a pseudodataset.

### Input creation
The ntuples are built with `build_minimal_example_ntuples.py`.
The processes "signal" and "background" are used to build the pseudodataset, and the signal contribution is scaled by a factor 1.2.

### Common fit approach
A fit of the predicted distributions to the pseudodataset can be performed with TRExFitter, a tool used in the [ATLAS Collaboration](https://atlas.cern/) to steer profile likelihood fits.
The configuration is provided in `TRExFitter/minimal_example.config`.
It also produces a [RooFit](https://root.cern.ch/roofit) workspace.

The fit performed with TRExFitter determines the signal normalization to be `1.19 ± 0.03`, and also uses a luminosity uncertainty of 2% that is slightly pulled and significantly constrained (to `0.10 ± 0.23`).

### Using pyhf to fit the workspace
The notebook `pyhf_from_xml.ipynb` shows how to convert the workspace to python and subsequently determine the best fit configuration with [iminuit](https://github.com/scikit-hep/iminuit).
The resulting measured signal normalization is `1.19 ± 0.04`.

### Processing ntuples with FAST-HEP
The [FAST-HEP](http://fast-hep.web.cern.ch/fast-hep/public/) package can be used to build template histograms.

## Expressions for normalization factors
The script `build_inputs_expression.py` creates predicted distributions for three processes, as well as the distribution of a fictitious measurement. The figure below visualizes the events created.

<img src="figures/stacked.png" alt="distribution of simulated processes and pseudodata" width="640"/>

The pseudodatata is not an Asimov dataset, but corresponds to a dataset where a normalization factor of 1.05 is applied to the background, and normalization factors 0.7 and 1.3 to the two signal processes.