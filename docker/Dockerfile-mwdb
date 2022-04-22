FROM python:3.8

RUN apt update && apt install -y build-essential libffi-dev libfuzzy-dev postgresql-client libmagic1

RUN pip install mwdb-core==2.7.0 karton-core==4.3.0

COPY docker/uwsgi.ini docker/start.sh /app/

WORKDIR /app

CMD ["/app/start.sh"]
