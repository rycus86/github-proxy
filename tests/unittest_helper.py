import os
from api import ApiClient


def get_api_client():
    return ApiClient(token=os.environ.get('GITHUB_TOKEN', _get_cached_token()))


def _get_cached_token():
    directory = os.path.dirname(__file__) or '.'
    path = os.path.join(os.path.abspath(directory), '../../github_token.txt')

    if os.path.exists(path):
        with open(path) as token_file:
            return token_file.read()
