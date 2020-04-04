import json
import os

import requests


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


def request(method, path, body=None, params={}, headers={}, binary=False, parse_response=True):
    """Makes an HTTP request to the API"""
    headers = {'Authorization': 'Api-Key {}'.format(get_api_key()), **headers}
    request_method = getattr(requests, method)
    url = '{url}{path}'.format(url=get_api_url(), path=path)
    if binary:
        response = request_method(
            url, data=body, params=params, headers=headers)
    else:
        response = request_method(
            url, json=body, params=params, headers=headers)
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
        next_resp = fetch_from_list_request(
            path=response['next'], params=params)
        res.extend(next_resp['results'])
    return res
