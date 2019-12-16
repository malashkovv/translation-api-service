FROM greenbirdit/locust

RUN apk add build-base

RUN pip install geventhttpclient locustio==0.12.1

ADD ./translation-api-perf/test.py /usr/src/app/test.py

ENV LOCUSTFILE_PATH=/usr/src/app/test.py