FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu18.04 AS base_system

ARG PYTHON_VERSION=3.7.11

SHELL ["/bin/bash", "-c"]

RUN apt-get update --fix-missing \
    && apt-get install -y wget bzip2 zlib1g-dev ca-certificates curl git build-essential \
      libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /usr/python/
RUN wget -O /usr/python/python.tgz "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz" \
    && tar -xf /usr/python/python.tgz -C /usr/python/ \
    && rm /usr/python/python.tgz  \
    && cd /usr/python/Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations --with-ensurepip=install \
    && make altinstall

RUN export PYTHON_MAJOR_VERSION=$(cut -d '.' -f-2 <<< $PYTHON_VERSION) \
    && ln -fs /usr/local/bin/python$PYTHON_MAJOR_VERSION /usr/bin/python \
    && ln -fs /usr/local/bin/pip$PYTHON_MAJOR_VERSION /usr/bin/pip


FROM base_system

ENV PYTHONPATH /usr/src/app

WORKDIR /usr/src/app/

COPY ./translation-api/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./translation-api ./translation-api

EXPOSE 80

ENTRYPOINT ["/usr/src/app/translation-api/entrypoint.sh"]
