FROM python:3.8-slim-buster
RUN apt-get update -y && apt-get install -y libpq-dev build-essential 
ENV PORT=5000
ARG FLASK_ENV_ARG
ENV FLASK_ENV=${FLASK_ENV_ARG}

COPY requirements.txt requirements_ts.txt /
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -r requirements_ts.txt

COPY . /
WORKDIR /

RUN useradd runner
USER runner
CMD gunicorn -b 0.0.0.0:$PORT wsgi:app