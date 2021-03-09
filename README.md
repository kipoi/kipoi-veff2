# Install the environment for development
Currently the conda environment resolves only in Ubuntu. If you are using Ubuntu 
```
conda env create -f environment.yml
conda activate kipoi-veff2
```

We are providing a docker containers for development purposes as well. The use is follows

# Build
```
docker build --no-cache -t kipoi-veff2-docker -f Dockerfile .
```

# Run 
```
docker run -v $PWD:/app/ -it kipoi-veff2-docker
```

This will return a bash shell with the conda environment already activated

# Test

## Ubuntu:
```
pytest
```

## Docker container: 
```
cd /app
pytest
```

# Use
```
python kipoi_veff2/cli.py in.vcf out.vcf -m "Basenji" -m "Basset"
```

### pre-commit hooks - black and flake8

For the first time,
```
pip install pre-commit 
pre-commit install
pre-commit run --all-files
```