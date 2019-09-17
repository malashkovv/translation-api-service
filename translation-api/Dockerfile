FROM python:3.7

ENV PYTHONPATH /usr/src/app

WORKDIR /usr/src/app/

RUN pip install py-translate aiohttp requests

COPY ./translation-api ./translation-api

EXPOSE 8080

CMD python -m aiohttp.web -H 0.0.0.0 -P 8080 translation-api.app:init_func