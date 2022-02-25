FROM python:3.9-slim as prod

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl

RUN curl -sSL https://install.python-poetry.org -o poetry_installer.sh
RUN python poetry_installer.sh
RUN rm poetry_installer.sh
ENV PATH="/root/.local/bin:$PATH"

COPY poetry.lock pyproject.toml ./
COPY tasks.py ./
COPY beeapi ./beeapi
COPY spec ./spec
RUN poetry install --no-dev
RUN poetry run inv run-indexing
ENTRYPOINT bash


FROM prod as dev
WORKDIR /app
RUN poetry install # install dev requirements
ENTRYPOINT bash
