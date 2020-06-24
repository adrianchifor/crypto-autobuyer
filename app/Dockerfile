FROM python:3.7-alpine

WORKDIR /app
COPY *.py /app

RUN apk add --no-cache --virtual ccxt-deps g++ libffi-dev openssl-dev \
  && pip install --no-cache-dir 'Flask' 'gunicorn' 'ccxt==1.27.84' \
  && apk del ccxt-deps

COPY --from=gcr.io/berglas/berglas:0.5.0 /bin/berglas /bin/berglas

CMD exec /bin/berglas exec -- gunicorn --log-level info main:app
