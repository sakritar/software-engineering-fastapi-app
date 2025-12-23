FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

RUN apk update

ADD pyproject.toml /app

RUN pip install --upgrade pip
RUN pip install poetry
#RUN pip install --no-cache-dir "psycopg[binary,pool]"

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

COPY . /app/

RUN chmod +x entrypoint.sh
