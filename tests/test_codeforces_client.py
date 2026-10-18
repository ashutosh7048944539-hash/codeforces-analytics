from unittest.mock import Mock

import pytest

from app.codeforces_client import CodeforcesClient


def test_codeforces_client_base_url():
    client = CodeforcesClient()

    assert client.BASE_URL == "https://codeforces.com/api"

    client.close()


def test_codeforces_client_methods():
    client = CodeforcesClient()

    assert callable(client.get_user_info)
    assert callable(client.get_user_rating)
    assert callable(client.get_user_submissions)
    assert callable(client.get_problemset)

    client.close()


def test_get_result_success():
    client = CodeforcesClient()

    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "OK",
        "result": {"handle": "test_user"},
    }

    client.client.get = Mock(return_value=mock_response)

    result = client._get_result("/test")

    assert result == {"handle": "test_user"}

    client.close()


def test_get_result_failure():
    client = CodeforcesClient()

    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "FAILED",
        "comment": "Handle not found",
    }

    client.client.get = Mock(return_value=mock_response)

    with pytest.raises(ValueError, match="Handle not found"):
        client._get_result("/test")

    client.close()

def test_get_result_http_error():
    client = CodeforcesClient()

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("HTTP error")

    client.client.get = Mock(return_value=mock_response)

    with pytest.raises(Exception, match="HTTP error"):
        client._get_result("/test")

    client.close()