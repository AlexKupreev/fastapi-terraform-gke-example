FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y curl supervisor vim && mkdir -p /var/supervisor

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

ENV PYTHONPATH=/app

# setting up supervisord service for pubsub
COPY docker/config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080

COPY ./ .

ENTRYPOINT ["/usr/bin/supervisord"]
