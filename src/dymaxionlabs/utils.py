import http
import json
import os
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 30  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


# Set debug level
#http.client.HTTPConnection.debuglevel = 1

# Setup a Retry strategy, with exponential backoff
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[413, 429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)
session = requests.Session()

session.mount("https://", adapter)
session.mount("http://", adapter)


class BadRequestError(Exception):
    pass


class InternalServerError(Exception):
    pass


class NotFoundError(Exception):
    pass


def get_api_url():
    """Get current API URL from environment"""
    return os.getenv("DYM_API_URL", "https://api.dymaxionlabs.com")


def get_api_key():
    """Get current API Key from environment"""
    return os.environ.get("DYM_API_KEY")


def request(method,
            path,
            body=None,
            files=None,
            params={},
            headers={},
            binary=False,
            parse_response=True):
    """Makes an HTTP request to the API"""
    headers = {'Authorization': 'Api-Key {}'.format(get_api_key()), **headers}
    request_method = getattr(session, method)
    url = urljoin(get_api_url(), path)
    if files:
        response = request_method(url,
                                  files=files,
                                  data=body,
                                  params=params,
                                  headers=headers)
    else:
        if binary:
            response = request_method(url,
                                      data=body,
                                      params=params,
                                      headers=headers)
        else:
            response = request_method(url,
                                      json=body,
                                      params=params,
                                      headers=headers)
    code = response.status_code

    # Error handling
    if code == 404:
        raise NotFoundError(response.text)
    elif code in range(400, 500):
        raise BadRequestError(response.text)
    elif code in range(500, 600):
        raise InternalServerError(response.text)

    # If code is 204, return nothing
    if code == 204:
        return

    # Otherwise, parse json response and return
    if parse_response:
        return json.loads(response.text)
    else:
        return response.content


def fetch_from_list_request(path, params={}):
    """Fetches all entities from a paginated result"""
    res = []
    response = request('get', path, params=params)
    res.extend(response['results'])
    if response['next']:
        p = urlparse(response['next'])
        new_path = '{}?{}#{}'.format(p.path, p.query, p.fragment)
        next_items = fetch_from_list_request(path=new_path, params=params)
        res.extend(next_items)
    return res
