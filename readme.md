# intro
the idea is to build a simple docker container that can be used as a ca

simple root ca

every csr that is getting uploaded will be signed

user's can create their own user/server cert do download

no public/private keys will be saved

no revoke functionality

# run
```
docker run -p 5000:5000 asauerwein/ca-helper
```

