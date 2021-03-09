FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y build-essential libz-dev libcurl3-dev wget git gcc
    
RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python=3 \
    && apt-get -qq -y remove curl bzip2 \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

ENV PATH /usr/local/condabin:$PATH


RUN mkdir -p /app

ADD environment.yml /app/environment.yml

RUN conda env create -f /app/environment.yml

RUN echo "source activate kipoi-veff2" > ~/.bashrc
ENV PATH /usr/local/envs/kipoi-veff2/bin:$PATH

SHELL ["conda", "run", "-n", "kipoi-veff2", "/bin/bash", "-c"]

