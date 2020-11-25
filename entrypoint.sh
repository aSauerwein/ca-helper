#!/bin/bash

# create gunicorn public / private key if not exists
if ! test -f "ssl/ca-helper.pem"; then
    cfssl selfsign gunicorn ssl/ca-helper-csr.json | cfssljson -bare ssl/ca-helper
fi

gunicorn --bind 0.0.0.0:5000 ca-helper:app --keyfile ssl/ca-helper-key.pem --certfile ssl/ca-helper.pem