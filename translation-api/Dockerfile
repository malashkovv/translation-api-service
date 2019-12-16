FROM python:3.7

ENV PYTHONPATH /usr/src/app

WORKDIR /usr/src/app/

RUN pip install aiohttp aiohttp-swagger aws-xray-sdk gunicorn uvloop

COPY ./translation-api ./translation-api

EXPOSE 8080

CMD ["gunicorn", "translation-api.app:init_func", "-c", "/usr/src/app/translation-api/gunicorn_conf.py"]