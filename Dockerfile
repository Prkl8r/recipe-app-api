FROM alpine:3.15

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

#Install dependencies
COPY ./requirements.txt /requirements.txt
COPY ./.flake8 /.flake8

# --no-cache reduces the size of the docker size
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev libpq-dev python3-dev

RUN apk add --update py3-pip
RUN pip install -r /requirements.txt

# Remove temp requirements
RUN apk del .tmp-build-deps

#Creates the app directory and copies it to the Dockerfile
#RUN mkdir /app
WORKDIR /app
COPY ./app/ /app


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

RUN adduser -D user
USER user

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# File wsgi.py was not found in subfolder: 'vscode-django-docker'. Please enter the Python path to wsgi file.
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]
