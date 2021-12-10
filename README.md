[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
![](https://github.com/kipoi/kipoi-veff2/actions/workflows/nightly-ci.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Description

This is an Ensembl Variant Effect Predictor (VEP) like tool with a subset of kipoi models. Models in Kipoi can be broadly classified into two groups -

- Models that are capable of inferring from any part of the genome. These models will use variant centered effect prediction. The chosen model groups use `kipoiseq.datalaoders.SeqIntervalDl` as their default dataloader. The algorithm is as follows:
	- For every variant a sequence centred on said variant is generated.
	- That sequence is then mutated by modifying the central base twice - once with reference and once with alternative allele - generating two sets of sequences.
	- Infer twice with each model, once each with the above two sequences.
	- Perform scoring with the above two predictions with scoring functions like diff, logit, etc.
- ![alt text](misc/variantcentered.png?raw=true "variant centered")

- Models that are capable of Inferring from only selected parts of the genome. For example, splicing models like MMSplice that are capable of inferring only near the splice site as it has been trained on such sites. We denote them as interval based effect predicttion and it utilizes the model specific dataloaders directly.
- ![alt text](misc/intervalbased.png?raw=true "interval based")


## Available models

We currently support following model/ model groups.

| Model group                  | Type             |
|------------------------------|------------------|
| Basset                       | Variant centered |
| DeepSEA                      | Variant centered |
| DeepBind                     | Variant centered |
| MPRA-DragoNN                 | Variant centered |
| pwm_HOCOMOCO                 | Variant centered |
| Basenji                      | Variant centered |
| MMSplice                     | Interval based   |

## Installation

The installation operates in two stages - first a conda environment is created with necessary dependencies and after that kipoi-veff2 is installed in that environment.

1. ### Install the conda environment appropriate to your operating system

	Currently the provided conda environment(s) resolve in Ubuntu, MacOS and CentOS.

	#### Ubuntu

	```bash
	conda env create -f environment.ubuntu.yml
	```

	#### MacOS

	```bash
	conda env create -f environment.osx.yml
	```

	#### General purpose environment

	A more abridged version with minimal sets of dependencies is avaiable in environment.minimal.yml. This has been tested on CentOS Linux with conda 4.7.10. This environment intentionally does not contain snakemake in order to keep it minimal. Please be sure to install snakemake before
	using the Snakefile inside examples.

2. ### Install kipoi-veff2

	```bash
	conda activate kipoi-veff2
	python -m pip uninstall -y enum34 && python -m pip install .
	```

	Note: For older version of conda (4.7.10), pinning cyvcf2 to 0.11 seems to work in CentOS Linux

## Tests

### Package

```bash
pytest -k "not workflow"  tests
```

### Workflow

```bash
cd examples && snakemake -j4 && cd ../ && pytest -k "workflow" tests
```

## Usage

### Variant centered

```bash
kipoi_veff2_predict <input-vcf> <input-fasta> <output-tsv> -m "DeepSEA/predict" 
```

or

```python
from kipoi_veff2 import variant_centered

model_group = model_name.split("/")[0]
model_group_config_dict = (
	variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
        model_group, {}
    )
)

model_config = variant_centered.get_model_config(model_name, **model_group_config_dict)

variant_centered.score_variants(
    model_config=model_config,
    vcf_file=vcf_file,
    fasta_file=fasta_file,
    output_file=output_file,
)
```

You can specify a list of scoring functions defined in kipoi_veff2.scores like so -

```bash
kipoi_veff2_predict  <input-vcf> <input-fasta> <output-tsv> -m "DeepSEA/predict" -s "diff" -s "logit"
```

or

```python
from kipoi_veff2 import scores, variant_centered

model_group = model_name.split("/")[0]
model_group_config_dict = (
	variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
        model_group, {}
    )
)

model_config = variant_centered.get_model_config(model_name, **model_group_config_dict)

variant_centered.score_variants(
    model_config=model_config,
    vcf_file=vcf_file,
    fasta_file=fasta_file,
    output_file=output_file,
	scoring_functions=[
            {"name": "diff", "func": scores.diff},
            {"name": "logit", "func": scores.logit},
        ]
)
```

### Sequence length

Currently, there are three ways to define the required sequence length of a model in this category.

1. Through cli using -l flag. This option has the highest priority and will over ride any default in the source code.

2. Through variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.
See the entry for pwm_HOCOMOCO as an example.
Currently this feature is only available per model group.

3. Otherwise, sequence length is inferred from ```auto_resize_len``` key of the respective dataloader description.

### Scoring function

Currently, the scoring functions must be defined in kipoi_veff2.scores. By default, each model in this category has "diff" as a default scoring funciton.  The only exception is Basenji which has "basenji_effect" as default. There are two ways to indicate which scoring function to use.

1. Through cli using -s flag. This option has the highest priority and will over ride any default. Just specify the name of the function and it will infer which function to call.

2. Through variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS. See the entry for Basenji as an example. Currently this feature is only available per model group.

### Batch size

- Basenji can only accept a pair of inputs as a batch whereas the rest of the models can accept an arbitrary number of inputs. To handle this special case, we introduced a ```batch_size``` parameter to ModelConfig class.```batch_size``` can be altered via variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS. See the entry for Basenji as an example.

- For the rest of the models in this category we use a batch size of 1000 by default. We make two batches out of a list of 1000 reference sequences and alternative sequences for each of 1000 variants. In order to accomodate Basenji's unique needs, we concatenate a pair of inputs - the first one reference sequence and the second one alternative sequence to form a batch.

## Interval based

```bash
kipoi_veff2_predict <input-vcf> <input-fasta> -g <input-gtf> <output-tsv> -m "MMSplice/mtsplice"
```

or

```python
from kipoi_veff2 import interval_based

model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[model_name]
interval_based.score_variants(
	model_config=model_config,
	vcf_file=vcf_file,
	fasta_file=fasta_file,
	gtf_file=gtf_file,
	output_file=output_file,
)
```

## Optional merge functionality

For model groups who have a large number of models (Example: DeepBind), it is more convenient to output a single file by merging all the scored effect predictions across all the models in the group. For this, we provide a merge cli as described below.

```bash
kipoi_veff2_merge output1.tsv output2.tsv ... output.10.tsv merged.tsv
```

## Running multiple models and/or vcf/fasta pairs

### Preparing the vcf and fasta files

- Variant centered effect prediction will only work with one allele at a time. Split multiple alternative alleles into separate lines.
- Chromosome names in the fasta file have to be compatible with the VCF file. For example, if chromosome 1 is denoted by ' chr1' in the vcf file, then the reference genome also has to have `chr1` chromosome and not `1`.
- Fasta files can not contain lower cases.
- ’N’ is the only allowed neutral alphabet (e.g. sequence should only contain A,C,G,T,N)

### Snakemake workflow

- We use [snakemake](https://snakemake.readthedocs.io/en/stable/index.html) for running a full workflow with multiple models and/or vcf/fasta files. An example workflow with multiple models and a single set of vcf and fasta file is in `examples/Snakefile` which you can execute by

	```bash
	cd examples && snakemake -j4
	```

	In this workflow, one job is submitted per model for a total of 2 jobs. The output will be available in examples/output.merged.tsv.

- A more complicated workflow is available in `examples/multimodelmultiinput/Snakefile`. Here all files with an extension .vcf.gz and corresponding fasta files were picked from a user specified directory. One job is submitted per model per vcf/fasta file pair - a total of 1217 jobs per vcf/fasta pair. Finally, the outputs were merged across models in a group producing a single output file for each model group and each vcf/fasta pair.

### General recommendations

- I recommend sharding large vcf files into smaller vcfs before running this workflow. Since this code is single threaded overall runtime will benefit from running as many simultaneous jobs as possible.
- For all models except Basenji, a larger batch_size (1000 by default) may make execution time smaller.
- DeepSEA models may benefit from using a gpu.
- I highly recommend using cluster architecture specific [snakemake profiles](https://github.com/Snakemake-Profiles) in hpc clusters.
- In hpc clusters, make sure `model_sources.kipoi.auto_update` is `False` in `~/.kipoi/config.yaml`. Due to a race condition in kipoi sometimes jobs get stuck otherwise.
