FROM python:3.7

ENV PYTHONPATH /usr/src/app

WORKDIR /usr/src/app/

COPY ./translation-api/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./translation-api ./translation-api

EXPOSE 80

CMD ["uvicorn", "translation-api.app:app", "--host", "0.0.0.0", "--port", "80"]
#uvicorn translation-api.app:app --host 0.0.0.0 --port 80