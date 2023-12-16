from services.auth import is_admin_user
import pytest
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def admin_api_key() -> str:
    return os.environ["ADMIN_TOKEN"]


@pytest.fixture
def wrong_api_key() -> str:
    return "bullshit"


def test_admin_api_key(admin_api_key):
    assert is_admin_user(admin_api_key)


def test_wrong_api_key(wrong_api_key):
    assert not is_admin_user(wrong_api_key)
