from datetime import datetime, timedelta, timezone

from app.models import User
from app.services.user_service import is_user_cache_fresh


def test_cache_is_stale_without_timestamp():
    user = User(
        handle="test_user",
        last_synced_at=None,
    )

    assert is_user_cache_fresh(user) is False


def test_cache_is_fresh():
    user = User(
        handle="test_user",
        last_synced_at=datetime.now(timezone.utc),
    )

    assert is_user_cache_fresh(user) is True


def test_cache_is_stale_after_30_minutes():
    user = User(
        handle="test_user",
        last_synced_at=datetime.now(timezone.utc)
        - timedelta(minutes=31),
    )

    assert is_user_cache_fresh(user) is False