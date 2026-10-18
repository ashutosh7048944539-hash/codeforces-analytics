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

    def _get_result(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict | list:    
        response = self.client.get(
            endpoint,
            params=params,
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(
                data.get("comment", "Codeforces API error")
            )

        return data["result"]

    def get_user_info(self, handle: str) -> dict:
        result = self._get_result(
            "/user.info",
            params={"handles": handle},
        )

        return result[0]

    def get_user_rating(self, handle: str) -> list[dict]:
        return self._get_result(
            "/user.rating",
            params={"handle": handle},
        )

    def get_user_submissions(self, handle: str) -> list[dict]:
        return self._get_result(
            "/user.status",
            params={"handle": handle},
        )

    def get_problemset(self) -> dict:
        return self._get_result(
            "/problemset.problems",
        )