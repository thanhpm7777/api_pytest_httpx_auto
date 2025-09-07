import os
import pytest
from dotenv import load_dotenv
from tests.utils.auth import login_and_get_token
from tests.utils.http_client import client
from tests.utils.config import SETTINGS


load_dotenv()


@pytest.fixture(scope="session")
def base_url():
    return SETTINGS.base_url


@pytest.fixture(scope="session")
def auth_token():
    return login_and_get_token()


@pytest.fixture()
def http(auth_token):
    with client(token=auth_token) as c:
        yield c


@pytest.fixture()
def http_public():
    with client() as c:
        yield c