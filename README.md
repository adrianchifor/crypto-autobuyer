# Crypto Autobuyer

Easily and quickly automate recurring cryptocurrency purchases. Supports 122 exchanges and thousands of markets/pairs. Main usecases are to average-in on downtrends and periodically cash out on uptrends, as the majority of passive investors are highly unlikely to catch exact market tops and bottoms.

Designed to run on Google [Cloud Run](https://cloud.google.com/run/) + [Cloud Scheduler](https://cloud.google.com/scheduler/) and managed using [run-marathon](https://github.com/adrianchifor/run-marathon), but can be deployed in any environment that supports Python3.

## Setup

 Install [run-marathon](https://github.com/adrianchifor/run-marathon#quickstart) (python 3.6+)
```
pip3 install --user run-marathon
```

Create trade-only API keys on your favourite exchanges and modify the example [run.yaml](https://github.com/adrianchifor/crypto-autobuyer/blob/master/run.yaml) to fit your needs. The pair/exchange combinations + order chains (using multiple services) are limitless.
```
$ cat run.yaml
project: your-project
region: europe-west1

allow-invoke:
  - user:your-user@domain.com

crypto-autobuyer-cbpro:
  dir: app
  image: gcr.io/${project}/crypto-autobuyer:latest
  env:
    EXCHANGE: coinbasepro
    API_KEY: your-api-key
    API_SECRET: *****
    PASSWORD: *****
    PAIR: BTC/GBP
    AMOUNT: "1000"
  cron:
    schedule: 0 9 * * 6  # Every Saturday 9am

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

**Security note:** It's highly recommended that you encrypt your `API_SECRET` and `PASSWORD` (if applicable) env vars and decrypt them at container startup. I recommend using [Berglas](https://github.com/GoogleCloudPlatform/berglas); here's [a relevant example](https://github.com/GoogleCloudPlatform/berglas/tree/master/examples/cloudrun/python).

The app takes the following environment variables:

* **EXCHANGE** (required): The `id` of any of the [exchanges that ccxt supports](https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets) (122)

* **API_KEY** (required)

* **API_SECRET** (required, see security note above)

* **PASSWORD** (required by some exchanges, like coinbasepro; see security note above)

* **PAIR** (required): The exchange ticker pair to use, e.g. BTC/GBP

* **AMOUNT** (required): For the BTC/GBP pair it's the GBP amount, e.g. "1000" would buy £1000 worth of BTC

* **TYPE** (optional, default "BUY"): The type of market order. The main usecase for the app is to automate periodic buys but you can also sell by setting TYPE to "SELL"
