# Install the environment for development
Currently the conda environment resolves only in Ubuntu. 

```
conda env create -f environment.ubuntu.yml
conda activate kipoi-veff2
```

We are providing a docker containers for development purposes as well. The use is follows

# Build
```
docker build --no-cache -t kipoi-veff2-docker:latest -f Dockerfile .

```

# Run 
```
docker run -v $PWD:/app/ -it kipoi-veff2-docker:latest

```

This will return a bash shell with the conda environment already activated

# Test CI

## Ubuntu:
```
pytest -s --disable-warnings
```

## Docker container: 
```
cd /app
pytest  -s --disable-warnings
```
# Use

## Install the package

```
pip uninstall -y enum34 && pip install . (Note: I am not sure yet why or how enum34 get installed)
```
## Variant centered
```
kipoi_veff2 kipoi-veff2/tests/data/general/singlevariant.vcf kipoi-veff2/tests/data/general/hg38_chr22.fa out_vc.tsv -m "DeepSEA/predict" -s "diff" -s "logit"
```

## Interval based

```
kipoi_veff2 kipoi-veff2/tests/data/interval-based/test.vcf kipoi-veff2/tests/data/interval-based/test.fa -g kipoi-veff2/tests/data/interval-based/test.gtf out_i.tsv -m "MMSplice/mtsplice"

```

# Run the full workflow

```
snakemake -j4
```

### pre-commit hooks - black and flake8

For the first time,
```
pip install pre-commit 
pre-commit install
pre-commit run --all-files
```

### Building the conda package 

All dependencies are available via conda channels except mmsplice. So, we will first build a conda package for mmsplice followed by kipoi_veff2. The steps are as follows - 

```
conda install conda-build
conda create -n kipoiveff2pkg python=3.6
conda activate kipoiveff2pkg
cd conda-recipe
conda build -c bioconda -c conda-forge  ./mmsplice python=3.6 
conda install --use-local mmsplice python=3.6
conda build -c bioconda -c conda-forge -c pytorch ./kipoi-veff2 python=3.6
conda install -c pytorch  -c conda-forge -c bioconda  --use-local kipoi_veff2 python=3.6
```

TODO: 
- Add CI for building and testing package
- Can/Should we get rid of python 3.6 requirement?
- Possibility for a pypi release? 

#### Testing the package

```
cd kipoi_veff2
conda activate kipoiveff2pkg
conda install mamba
mambla install snakemake
pytest
```
