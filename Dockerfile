FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev


RUN pip install --upgrade pip \
    pip install -r ./requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /recipe_app
WORKDIR /recipe_app
COPY ./recipe_app /recipe_app

# Create a user that'll be used only to run apps (-D)
RUN adduser -D app_user
# Use said user
USER app_user