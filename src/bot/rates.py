import os
import json

from redis import StrictRedis
from redis_dec import Cache
from requests import exceptions, Session

from .exceptions import APIError


CONNECTION_ERROR = 'No exchange rate data is available. Please, try again later.'


REDIS_BACKEND = os.environ.get('REDIS_BACKEND')
REDIS_CACHE_TTL = os.environ.get('REDIS_CACHE_TTL')

redis = StrictRedis.from_url(REDIS_BACKEND, decode_responses=True)
cache = Cache(redis)


class ExchangeRatesClient:
    def __init__(self):
        self._base_url = "https://api.exchangeratesapi.io"
        self._session = Session()

    def request(self, method, path, params=None):
        try:
            method = method.lower()
            verb = getattr(self._session, method)
            response = verb(f"{self._base_url}{path}", params=params)
            json_data = json.loads(response.text)

            if 'error' in json_data:
                raise APIError(json_data['error'])

            return json_data

        except exceptions.RequestException:
            raise APIError(CONNECTION_ERROR)

    @cache.dict(ttl=REDIS_CACHE_TTL)
    def latest(self, base):
        """
        Requests exchange rates

        Args:
            base(str): base currency, ex.: "USD"
        """
        params = dict(base=base)
        return self.request("GET", "/latest", params=params)

    @cache.dict(ttl=REDIS_CACHE_TTL)
    def history(self, base, symbols, start_at, end_at):
        """
        Requests exchange rates history

        Args;
            base(str): base currency, ex.: "USD"
            symbols(str): comma-separated against currency, ex.: "CAD,RUB"
            start_at(datetime.datetime): date start
            end_at(datetime.datetime): date_end
        """
        params = dict(base=base, symbols=symbols)

        if start_at:
            params['start_at'] = start_at.strftime('%Y-%m-%d')
        if end_at:
            params['end_at'] = end_at.strftime('%Y-%m-%d')

        return self.request("GET", "/history", params=params)


api = ExchangeRatesClient()
