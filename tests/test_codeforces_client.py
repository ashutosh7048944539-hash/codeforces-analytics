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