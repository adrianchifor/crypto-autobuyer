FROM python:3.7-alpine

RUN apk add --no-cache --virtual ccxt-deps g++ libffi-dev openssl-dev \
  && pip install --no-cache-dir 'Flask' 'gunicorn' 'ccxt==1.32.39' \
  && apk del ccxt-deps

WORKDIR /app
COPY *.py /app

COPY --from=gcr.io/berglas/berglas:0.5.0 /bin/berglas /bin/berglas

CMD exec /bin/berglas exec -- gunicorn --log-level info main:app
