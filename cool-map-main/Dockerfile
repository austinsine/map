FROM python:3.10-slim

ENV APP_HOME /cool-map-main
WORKDIR $APP_HOME
COPY ./cool-map-main ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
