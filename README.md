# Discount

**Discount** is a Python microservice for generating discount codes.
It can generate multiple codes for a given brand (up to 128,000 at once) and
assign an unused code to a user.
It exposes a REST API using FastAPI and uses MySQL for storage.


## Running

You can run the whole application along with the DB using Docker Compose:

```
docker-compose up
```

It will become available at http://127.0.0.1:8000/.
Interactive API docs are at http://127.0.0.1:8000/docs.

## Using the service

To generate 10 discount codes for a brand named "ibm":

```
$ curl -X POST http://127.0.0.1:8000/generate/ibm
{"result":["AAHLKDABAA","AEHLKDABAA","AIHLKDABAA","AMHLKDABAA","AQHLKDABAA","AUHLKDABAA","AYHLKDABAA","A4HLKDABAA","BAHLKDABAA","BEHLKDABAA"]}
```

To fetch a single code and mark it as used:

```
$ curl -X POST http://127.0.0.1:8000/fetch/IBM
{"result":"B275CDABAA"}
```

## Running tests

```
docker-compose run web pytest
```
