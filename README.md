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
| CpGenie                      | Variant centered |
| DeepSEA/predict              | Variant centered |
| DeepSEA/beluga               | Variant centered |
| DeepSEA/variantEffects       | Variant centered |
| DeepBind                     | Variant centered |
| Divergent421                 | Variant centered |
| MMSplice/mtsplice            | Interval based   |
| MMSplice/deltaLogitPSI       | Interval based   |
| MMSplice/modularPredictions  | Interval based   |
| MMSplice/pathogenicity       | Interval based   |
| MMSplice/splicingEfficiency  | Interval based   |


# Install the conda environment 

Here is a table of which model/model groups are compatible with which conda environment file(s).

| Model/ Model group           | Compatible conda environment                                                      |             
|------------------------------|-----------------------------------------------------------------------------------|
| Basset                       | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| CpGenie                      | environment.minimal.linux.keras1.yml                                              |
| DeepSEA/predict              | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| DeepSEA/beluga               | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| DeepSEA/variantEffects       | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| DeepBind                     | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| Divergent421                 | environment.minimal.linux.keras1.yml                                              |
| MMSplice/mtsplice            | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| MMSplice/deltaLogitPSI       | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| MMSplice/modularPredictions  | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| MMSplice/pathogenicity       | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |
| MMSplice/splicingEfficiency  | environment.ubuntu.yml, environment.osx.yml, environment.minimal.linux.yml        |


## CI and development uses the following setup
```
Ubuntu: 20.04
MacOS: 10.15
Conda distribution: Miniconda 4.9.2
```

## General instructions for different environments

If you are using CpGenie and/or Divergent421, a different environment needs to be resolved for using the rest of the available model groups and vice versa. Due to a different keras version requirement, all of the model groups can not be used under the same environment.

## Ubuntu

```
conda env create -f environment.ubuntu.yml
conda activate kipoi-veff2
python -m pip uninstall -y enum34 && python -m pip install . (Note: I am not sure yet why or how enum34 get installed)
```
If you would like to use CpGenie and/or Divergent421 please create a separate environment like so
```
conda env create -f environment.minimal.linux.keras1.yml
conda activate kipoi-veff2-keras1
python -m pip uninstall -y enum34 && python -m pip install . (Note: I am not sure yet why or how enum34 get installed)
```

## MacOS
```
conda env create -f environment.osx.yml
conda activate kipoi-veff2
python -m pip uninstall -y enum34 && python -m pip install . (Note: I am not sure yet why or how enum34 get installed)
```
Note: environment.minimal.linux.keras1.yml does not resolve under macos. This will be resolved soon.


## General purpose environment

A more abridged version of the above environments is avaiable in environment.minimal.linux.yml and environment.minimal.linux.keras1.yml. 
Both have been tested on CentOS Linux with conda 4.7.10. These environments intentionally do
not contain snakemake in order to keep them minimal. Please be sure to install snakemake before
using the Snakefile inside examples. 

Note: For older version of conda (4.7.10), pinning cyvcf2 to 0.11 seems to work in CentOS Linux


## Docker container


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

We use snakemake for running a full workflow. Snakemake is installed in the conda environment provided by the environment files.
```
cd examples && snakemake -j4
```
The output will be available in examples/output.merged.tsv 

# TODO: Add instruction for working with big vcf files 


### pre-commit hooks - black and flake8

For the first time,
```
pip install pre-commit 
pre-commit install
pre-commit run --all-files
```
