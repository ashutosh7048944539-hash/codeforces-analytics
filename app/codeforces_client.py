import time

import httpx


class CodeforcesClient:
    BASE_URL = "https://codeforces.com/api"
    REQUEST_DELAY = 2.0

    def __init__(self):
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=10.0,
        )

        self.last_request_time: float | None = None

    def close(self):
        self.client.close()

    def _wait_for_rate_limit(self):
        if self.last_request_time is None:
            return

        elapsed = time.monotonic() - self.last_request_time

        if elapsed < self.REQUEST_DELAY:
            time.sleep(
                self.REQUEST_DELAY - elapsed,
            )

    def _get_result(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict | list:
        self._wait_for_rate_limit()

        self.last_request_time = time.monotonic()

        response = self.client.get(
            endpoint,
            params=params,
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] != "OK":
            raise ValueError(
                data.get(
                    "comment",
                    "Codeforces API error",
                )
            )

        return data["result"]

    def get_user_info(
        self,
        handle: str,
    ) -> dict:
        result = self._get_result(
            "/user.info",
            params={"handles": handle},
        )

        return result[0]

    def get_user_rating(
        self,
        handle: str,
    ) -> list[dict]:
        return self._get_result(
            "/user.rating",
            params={"handle": handle},
        )

    def get_user_submissions(
        self,
        handle: str,
    ) -> list[dict]:
        return self._get_result(
            "/user.status",
            params={"handle": handle},
        )

    def get_problemset(self) -> dict:
        return self._get_result(
            "/problemset.problems",
        )