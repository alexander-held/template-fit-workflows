# Template fit workflows

- [Example 1: Minimal example](#example-1-minimal-example)
    - [Input creation](#input-creation)
    - [Subsequent processing and statistical analysis](#subsequent-processing-and-statistical-analysis)
        - [1. Traditional approach](#1-traditional-approach)
        - [2. Using pyhf to fit the workspace](#2-using-pyhf-to-fit-the-workspace)
        - [3. Alternative approach within the python ecosystem](#3-alternative-approach-within-the-python-ecosystem)
            - [3.a Template histogram production with FAST-HEP](#3a-template-histogram-production-with-fast-hep)
            - [3.b Building a pyhf workspace from FAST-HEP dataframes](#3b-building-a-pyhf-workspace-from-fast-hep-dataframes)
    - [Further comments and comparison](#further-comments-and-comparison)
- [Example 2: Expressions for normalization factors](#example-2-expressions-for-normalization-factors)


## Example 1: Minimal example
The minimal example consists of two processes, a signal and a background process.
It also includes a pseudodataset.

### Input creation
The ntuples are built with `build_minimal_example_ntuples.py`.
The processes "signal" and "background" are used to build the pseudodataset, and the signal contribution is scaled by a factor 1.2.

### Subsequent processing and statistical analysis
This repository shows three different workflows shown in this repository, which start with the ntuples and end with statistical inference.

#### 1. Traditional approach
A fit of the predicted distributions to the pseudodataset can be performed with TRExFitter, a tool used in the [ATLAS Collaboration](https://atlas.cern/) to steer profile likelihood fits.
The configuration is provided in `TRExFitter/minimal_example.config`.
It also produces a [RooFit](https://root.cern.ch/roofit) workspace.

The fit performed with TRExFitter determines the signal normalization to be `1.19 ± 0.03`, and also uses a luminosity uncertainty of 2% that is slightly pulled and significantly constrained (to `0.10 ± 0.23`).

The workflow in this approach can be summarized as:
```
ntuples -> TRExFitter -> inference
```

#### 2. Using pyhf to fit the workspace
The notebook `pyhf_from_xml.ipynb` shows how to convert the workspace created with TRExFitter to python and subsequently determine the best fit configuration with [iminuit](https://github.com/scikit-hep/iminuit).
The resulting measured signal normalization is `1.19 ± 0.04`.

This workflow is:
```
ntuples -> TRExFitter -> workspace -> pyhf -> inference
```

#### 3. Alternative approach within the python ecosystem
This approach makes no use of TRExFitter and operates fully with python-based tools.

The workflow in this approach is:
```
ntuples -> FAST-HEP -> dataframes -> custom conversion -> workspace -> pyhf -> inference
```

##### 3.a Template histogram production with FAST-HEP
The [FAST-HEP](http://fast-hep.web.cern.ch/fast-hep/public/) package can be used to build template histograms.
The full workflow, including the output visualization, can be run via `make plotter`.
There are three steps to this workflow:
- `fast_curator` reads the produced ntuples and extracts metadata, saved to `output/file_list.yml`.
- `fast_carpenter` is steered by the configuration file in `config/sequence.yml`, it has two stages:
    - Event selection: applies cuts, the cutflow is a `.csv` file found in `output/`.
    - Dataframe creation: creates histograms, saved as `.csv` in `output/`.
- `fast_plotter` visualizes the histograms, configured by `config/plot.yml`, with output `.png` files saved in `output/`.

##### 3.b Building a pyhf workspace from FAST-HEP dataframes
The notebook `pyhf_from_dataframe.ipynb` shows how to read the FAST-HEP output and turn it into a JSON workspace that can be read by pyhf.
The resulting output, `workspace_from_dataframe.json` should be consistent with the workspace obtained in approach 2.
The statistical inference can then be performed analogous to approach 2 with pyhf, consequently leading to the same measured signal normalization.

### Further comments and comparison

In the third approach, there is significant overlap in the information needed to produce the histograms with FAST-HEP, and in the construction of the workspace.
The first approach solves this with a monolithic framework that operates from a single configuration file, included in `TRExFitter/minimal_example.config`.
This third workflow will evolve gradually towards also being steered by a central configuration file that can be used in all steps, with automated handover between the different software frameworks in use.
Another example with some aspects of how such a file may look like is shown in [lukasheinrich/pyhfinput](https://github.com/lukasheinrich/pyhfinput).

The first and second approaches show that it is possible to factorize the workflow into multiple independent tasks, where pyhf can be substitute to build a likelihood from a workspace and perform statistical inference.
The third workflow takes this one step further, also factoring out the production of template histograms.
There are further steps that can be factorized.
One example is post-processing of the template histograms, applying operations like smoothing or symmetrization.
These aspects are not yet included.

ROOT appears in this approach only as the file format for the initial inputs, which are processed with [uproot](https://github.com/scikit-hep/uproot) and could easily be provided in another format.

---

## Example 2: Expressions for normalization factors
The script `build_inputs_expression.py` creates predicted distributions for three processes, as well as the distribution of a fictitious measurement. The figure below visualizes the events created.

<img src="figures/stacked.png" alt="distribution of simulated processes and pseudodata" width="640"/>

The pseudodatata is not an Asimov dataset, but corresponds to a dataset where a normalization factor of 1.05 is applied to the background, and normalization factors 0.7 and 1.3 to the two signal processes.