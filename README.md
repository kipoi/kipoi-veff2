# Install the environment for development

Currently the conda environment provided in this repo resolves in Ubuntu and MacOS with conda. Our specific test specs are -
```
Ubuntu: 20.04
MacOS: 10.15
conda: Miniconda 4.9.2
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

We are also providing a docker containers for development purposes as well. The use is follows

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

```
pytest -k "not workflow" -s --disable-warnings tests
cd examples && snakemake -j4 && cd ../ && pytest -k "workflow" -s --disable-warnings tests
```

# Use

## Variant centered
```
kipoi_veff2_predict kipoi-veff2/tests/data/general/singlevariant.vcf kipoi-veff2/tests/data/general/hg38_chr22.fa out_vc.tsv -m "DeepSEA/predict" -s "diff" -s "logit"
```

## Interval based

```
kipoi_veff2_predict kipoi-veff2/tests/data/interval-based/test.vcf kipoi-veff2/tests/data/interval-based/test.fa -g kipoi-veff2/tests/data/interval-based/test.gtf out_i.tsv -m "MMSplice/mtsplice"
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
