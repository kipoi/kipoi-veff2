# Description

  

This is an Ensembl Variant Effect Predictor (VEP) like tool with a subset of kipoi models. Models in Kipoi can be broadly classified into two groups -

- Models that are capable of inferring from any part of the genome. These models will use variant centered effect prediction. The algorithm is as follows - 

	- For every variant a sequence centred on said variant is generated.
	- That sequence is then mutated by modifying the central base twice - once with reference and once with alternative allele - generating two sets of sequences.- Infer twice with each model, once each with the above two sequences.
	- Perform scoring with the above two predictions with scoring functions like diff, logit, etc.


- Models that are capable of Inferring from only selected parts of the genome. For example, splicing models like MMSplice that are capable of inferring only near the splice site as it has been trained on such sites. These models will use interval based effect prediction. We are utilizing the model specific dataloaders. 

# Available models

We currently support following model/ model groups.

| Model/ Model group           | Type             |
|------------------------------|------------------|
| Basset                       | Variant centered |
| DeepSEA/predict              | Variant centered |
| DeepSEA/beluga               | Variant centered |
| DeepSEA/variantEffects       | Variant centered |
| DeepBind                     | Variant centered |
| MMSplice/mtsplice            | Interval based   |
| MMSplice/deltaLogitPSI       | Interval based   |
| MMSplice/modularPredictions  | Interval based   |
| MMSplice/pathogenicity       | Interval based   |
| MMSplice/splicingEfficiency  | Interval based   |


# Install the conda environment 

Currently the conda environment provided in this repo resolves in Ubuntu and MacOS. Our test specs are
```
Ubuntu: 20.04
MacOS: 10.15
Conda distribution: Miniconda 4.9.2
```

## Ubuntu

```
conda env create -f environment.ubuntu.yml
conda activate kipoi-veff2
python -m pip uninstall -y enum34 && python -m pip install . (Note: I am not sure yet why or how enum34 get installed)
```

## MacOS
```
conda env create -f environment.osx.yml
conda activate kipoi-veff2
python -m pip uninstall -y enum34 && python -m pip install . (Note: I am not sure yet why or how enum34 get installed)
```

## General purpose environment

A more abridged version of the above environments is avaiable in environment.minimal.yml. 
This has been tested on CentOS Linux with conda 4.7.10. This environment intentionally does
not contain snakemake in order to keep it minimal. Please be sure to install snakemake before
using the Snakefile inside examples. 

Note: For older version of conda (4.7.10), pinning cyvcf2 to 0.11 seems to work in CentOS Linux

We are also providing a docker containers for development purposes as well. The use is follows

### Build docker container

```
docker build --no-cache -t kipoi-veff2-docker:latest -f Dockerfile .
```

### Run the docker container

```
docker run -v $PWD:/app/ -it kipoi-veff2-docker:latest
```
This will return a bash shell with the conda environment already activated

# Test CI

```
pytest -k "not workflow" -s --disable-warnings tests
cd examples && snakemake -j4 && cd ../ && pytest -k "workflow" -s --disable-warnings tests
```

# Usage

## Variant centered
```
kipoi_veff2_predict kipoi-veff2/tests/data/general/singlevariant.vcf kipoi-veff2/tests/data/general/hg38_chr22.fa out_vc.tsv -m "DeepSEA/predict" -s "diff" -s "logit"
```

## Interval based

```
kipoi_veff2_predict kipoi-veff2/tests/data/interval-based/test.vcf kipoi-veff2/tests/data/interval-based/test.fa -g kipoi-veff2/tests/data/interval-based/test.gtf out_i.tsv -m "MMSplice/mtsplice"
```

# Run the full workflow

We use snakemake for running a full workflow. Snakemake is installed in the conda environment provided by the environment file environment.ubuntu.yml and environment.macos.yml
```
cd examples && snakemake -j4
```
The output will be available in examples/output.merged.tsv 

For model groups which has a large number of models (Example: DeepBind), it is recommended to use the above workflow. The list of 
models are generated from the variable modelsorgroups. Updated modelsorgroups variable in examples/Snakefile according to your need. 
This variable can accept a model name (MMSplice/mtsplice), a model group (DeepSEA) or a sub model group (DeepBind/Homo_sapiens/RBP)
provided they are available in kipoi. Please note - names are case sensitive

# TODO: Add instruction for working with big vcf files 


### pre-commit hooks - black and flake8

For the first time,
```
pip install pre-commit 
pre-commit install
pre-commit run --all-files
```
