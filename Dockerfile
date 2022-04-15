FROM alpine:3.15

ENV PYTHONUNBUFFERED 1

#Install dependencies
COPY ./requirements.txt /requirements.txt
COPY ./setup.cfg /setup.cfg

# --no-cache reduces the size of the docker size
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev libpq-dev python3-dev

RUN apk add --update py3-pip
RUN pip install -r /requirements.txt

# Remove temp requirements
RUN apk del .tmp-build-deps

#Creates the app directory and copies it to the Dockerfile
RUN mkdir /app
WORKDIR /app
COPY ./app /app

#Create user -D creates user for running apps only
RUN adduser -D user
USER user

