FROM python:3.7-alpine

RUN mkdir /app
COPY *.py /app

RUN apk add --no-cache --virtual ccxt-deps g++ libffi-dev openssl-dev \
  && pip install --no-cache-dir 'Flask' 'gunicorn' 'ccxt==1.27.84' \
  && apk del ccxt-deps \
  && rm -r /root/.cache

WORKDIR /app

CMD ["gunicorn", "-w", "3", "main:app"]
