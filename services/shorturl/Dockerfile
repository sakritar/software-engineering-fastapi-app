FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

RUN apk update && apk add --no-cache gcc musl-dev

ADD pyproject.toml /app

RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

COPY services/shorturl /app/

RUN chmod +x ./entrypoint.sh

CMD ["sh", "./entrypoint.sh"]

