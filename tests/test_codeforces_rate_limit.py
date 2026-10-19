from unittest.mock import Mock, patch

from app.codeforces_client import CodeforcesClient


def test_rate_limit_waits_before_second_request():
    client = CodeforcesClient()

    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "OK",
        "result": [],
    }

    with patch.object(
        client.client,
        "get",
        return_value=mock_response,
    ), patch(
        "app.codeforces_client.time.monotonic",
        side_effect=[100.0, 100.5, 100.5],
    ), patch(
        "app.codeforces_client.time.sleep"
    ) as mock_sleep:

        client._get_result("/test")

        client._get_result("/test")

    mock_sleep.assert_called_once_with(1.5)

    client.close()