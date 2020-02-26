# Telegram exchange bot

## Quickstart

### Install Docker

https://docs.docker.com/compose/install/

### Authorize bot

https://core.telegram.org/bots/api#authorizing-your-bot


### Env-file explain

Environment variables should be set in `.env` file:

    # You should provide bot api token
    API_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
    
    # You can use proxy for request
    PROXY_BACKEND=http://<some.proxy>:<port>

    # You can set custom Redis as database
    REDIS_BACKEND=redis://<some.redis>:<port>/<db>
    
    # TTL for Redis-cache
    REDIS_CACHE_TTL=600

    
### Run

    docker-compose build
    docker-compose up bot
   


## Commands:

If `base` parameter is not set in command it would be `USD` by default.


### __/list {base}__

returns list of all available rates for `base`

    /list USD
    >>>    
    CAD 1.32
    HKD 7.79
    ISK 128.76
    ...

### __/exchange {amount} {base} to {currency}__ 

converts `amount` of `base` to `currency`

    /exchange 10 USD to CAD
    >>>
    13.28

### __/history {base} {currency} for {N} days__

return an image graph chart with the exchange rate of the selected `base`/`currency` for the last `N` days

    /history USD CAD for 7 days
    >>>
    <image.png>
