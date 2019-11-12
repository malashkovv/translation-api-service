FROM locustio/locust

ADD ./translation-api-perf/test.py /usr/src/app/test.py

ENV LOCUSTFILE_PATH=/usr/src/app/test.py
ARG TARGET_URL=https://abc.com