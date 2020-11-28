FROM ubuntu
WORKDIR /app

RUN apt update
RUN apt install python3 python3-pip -y
RUN pip3 install poetry
# Copy in the config files:
COPY pyproject.toml poetry.lock ./
# Install only dependencies:
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-dev


COPY ./ca-helper /app

ENV FLASK_APP=ca_helper

COPY entrypoint.sh ./entrypoint.sh
CMD ["./entrypoint.sh"]