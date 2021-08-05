FROM greenbirdit/locust

RUN apk add build-base

COPY ./translation-api-perf/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

ADD ./translation-api-perf/test.py /usr/src/app/test.py

ENV LOCUSTFILE_PATH=/usr/src/app/test.py
