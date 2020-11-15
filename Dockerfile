FROM ubuntu
WORKDIR /code

RUN apt update
RUN apt install python3 python3-pip -y
RUN pip3 install poetry


COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

RUN install bin/cfssl /usr/bin/cfssl
RUN install bin/cfssljson /usr/bin/cfssljson

ENV PATH /code:$PATH

CMD ["entrypoint.sh"]