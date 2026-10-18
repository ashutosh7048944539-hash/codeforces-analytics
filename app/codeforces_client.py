import httpx


class CodeforcesClient:
    BASE_URL = "https://codeforces.com/api"

    def __init__(self):
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=10.0,
        )

    def close(self):
        self.client.close()

    def get_user_info(self, handle: str) -> dict:
        response = self.client.get(
            "/user.info",
            params={"handles": handle},
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(data.get("comment", "Codeforces API error"))

        return data["result"][0]

    def get_user_rating(self, handle: str) -> list[dict]:
        response = self.client.get(
            "/user.rating",
            params={"handle": handle},
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(data.get("comment", "Codeforces API error"))

        return data["result"]

    def get_user_submissions(self, handle: str) -> list[dict]:
        response = self.client.get(
            "/user.status",
            params={"handle": handle},
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(data.get("comment", "Codeforces API error"))

        return data["result"]

    def get_problemset(self) -> dict:
        response = self.client.get(
            "/problemset.problems",
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(data.get("comment", "Codeforces API error"))

        return data["result"]