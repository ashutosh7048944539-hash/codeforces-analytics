from sqlalchemy.orm import Session

from app.models import AnalyticsEvent


def record_event(
    db: Session,
    event_type: str,
    handle: str | None = None,
    source: str | None = None,
) -> None:
    print(
        "RECORDING ANALYTICS EVENT:",
        event_type,
        handle,
        source,
    )

    event = AnalyticsEvent(
        event_type=event_type,
        handle=handle,
        source=source,
    )

    db.add(event)
    db.commit()

    print("ANALYTICS EVENT COMMITTED")