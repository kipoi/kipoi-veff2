FROM continuumio/miniconda3:latest

RUN apt-get update && apt-get install --no-install-recommends -y build-essential libz-dev libcurl3-dev libarchive-dev gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN conda update -n base conda && \
    conda install -y -c conda-forge conda-libmamba-solver && \
    conda env create -f /app/environment.ubuntu.yml --experimental-solver=libmamba && \
    conda clean -afy

RUN echo "source activate kipoi-veff2" > ~/.bashrc

RUN pip install .

ENV PATH /opt/conda/envs/kipoi-veff2/bin:$PATH
