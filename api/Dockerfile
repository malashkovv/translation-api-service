FROM python:3.7.11

ENV PYTHONPATH /usr/src/app

WORKDIR /usr/src/app/

COPY ./api/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./api ./api

EXPOSE 80

ENTRYPOINT ["/usr/src/app/api/entrypoint.sh"]
