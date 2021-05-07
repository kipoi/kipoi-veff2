# Install the environment for development
Currently the conda environment resolves only in Ubuntu and OSX. 

If you are using Ubuntu 
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

## Variant centered models

```
cd workflow/variantcentered
snakemake -j4
```

## Interval based models

```
cd workflow/intervalbased
snakemake -j4
```

# Test the full workflow 

## Variant centered models

```
cd workflow/variantcentered
pytest -s --disable-warnings .tests
```

## Interval based models

```
cd workflow/intervalbased
pytest -s --disable-warnings .tests
```

### pre-commit hooks - black and flake8

For the first time,
```
pip install pre-commit 
pre-commit install
pre-commit run --all-files
```
