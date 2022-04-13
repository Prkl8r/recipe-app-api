FROM alpine:3.15

ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /requirements.txt
RUN apk add --update py3-pip
RUN pip install -r /requirements.txt

#Creates the app directory and copies it to the Dockerfile
RUN mkdir /app
WORKDIR /app
COPY ./app /app

#Create user -D creates user for running apps only
RUN adduser -D user
USER user

