FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client \
    # Pillow requirements
    jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    # Pillow requirements
    musl-dev zlib zlib-dev


RUN pip install --upgrade pip \
    pip install -r ./requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /recipe_app
WORKDIR /recipe_app
COPY ./recipe_app /recipe_app

# Pillow media folder (-p: recursive creation)
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Create a user that'll be used only to run apps (-D)
RUN adduser -D app_user

# Give ownership and permissions to our user on both folders
RUN chown -R app_user:app_user /vol/
RUN chmod -R 755 /vol/web

# Use said user
USER app_user