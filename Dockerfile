FROM python:3.10.14-alpine3.20
LABEL maintainer="tiunovmixs@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR /app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/media
RUN mkdir -p /app/data

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /app/media
RUN chown -R my_user /app/data
RUN chmod -R 755 /app/media
RUN chmod -R 755 /app/data

USER my_user
