# Crypto Autobuyer

[![Docker](https://github.com/adrianchifor/crypto-autobuyer/workflows/Publish%20Docker/badge.svg)](https://github.com/adrianchifor/crypto-autobuyer/actions?query=workflow%3A%22Publish+Docker%22)

Easily and quickly automate recurring cryptocurrency purchases and take profits. Supports 122 exchanges and thousands of markets/pairs. Main usecases are to average-in on downtrends and periodically cash out on uptrends, as the majority of passive investors are highly unlikely to catch exact market tops and bottoms.

Designed to run on Google [Cloud Run](https://cloud.google.com/run/) + [Cloud Scheduler](https://cloud.google.com/scheduler/) and managed using [run-marathon](https://github.com/adrianchifor/run-marathon), but can be deployed in any environment that supports Python3.

## Setup

 1. Install [run-marathon](https://github.com/adrianchifor/run-marathon#quickstart) (python 3.6+)
```
pip3 install --user run-marathon
```

2. Create a trade-only API key on your favourite exchange

3. Save your API secret and password (if applicable) to GCP Secret Manager. These will be automatically decrypted and loaded on container startup using [Berglas](https://github.com/GoogleCloudPlatform/berglas)
```
echo -n 'your-api-secret' | \
  gcloud secrets create api-secret \
    --replication-policy="automatic" \
    --data-file=- \
    --project your-project

echo -n 'your-api-password' | \
  gcloud secrets create api-password \
    --replication-policy="automatic" \
    --data-file=- \
    --project your-project
```

4. Modify the example [run.yaml](./run.yaml) to fit your needs and then build + deploy

Note: If you want to use a pre-built Docker image, you can `echo "FROM adrianchifor/crypto-autobuyer:latest" > Dockerfile` and change `dir` to the location of the Dockerfile.
```
$ run check
Cloud Run, Build, Container Registry, PubSub and Scheduler APIs are enabled. All good!

$ run build
Build logs: https://console.cloud.google.com/cloud-build/builds?project=your-project
Building crypto-autobuyer-cbpro ...
Waiting for builds to finish ...

Builds finished

$ run deploy
Deployment status: https://console.cloud.google.com/run?project=your-project
Deploying crypto-autobuyer-cbpro ...
Waiting for deployments to finish ...
Created service account [crypto-autobuyer-cbpro-sa].
Creating Cloud Scheduler job for crypto-autobuyer-cbpro ...
[crypto-autobuyer-cbpro]: https://your-app-url.a.run.app

Deployments finished

$ run ls
   SERVICE                 REGION        URL                             LAST DEPLOYED BY      LAST DEPLOYED AT
✔  crypto-autobuyer-cbpro  europe-west1  https://your-app-url.a.run.app  your-user@domain.com  2020-01-08T01:14:44.496Z

# Wait for Cloud Scheduler job to run or invoke manually
$ run invoke crypto-autobuyer-cbpro -X POST
Bought 0.156231 BTC (1000 GBP)
```

## Configuration

The app takes the following environment variables:

* **EXCHANGE** (required): The `id` of any of the [exchanges that ccxt supports](https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets) (122)

* **API_KEY** (required)

* **API_SECRET** (required, store in GCP Secret Manager)

* **PASSWORD** (required by some exchanges, like coinbasepro; store in GCP Secret Manager)

* **PAIR** (required): The exchange ticker pair to use, e.g. BTC/GBP

* **AMOUNT** (required): For the BTC/GBP pair it's the GBP amount, e.g. "1000" would buy £1000 worth of BTC

* **TAKE_PROFIT** (optional): The percentage gain for taking profits on purchases, e.g. "30" would place a limit sell 30% above the buy price for the same amount
