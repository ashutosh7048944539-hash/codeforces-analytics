from app.database import SessionLocal
from app.models import AnalyticsEvent
from app.services.analytics_event_service import record_event


def test_record_event_postgres():
    db = SessionLocal()

    try:
        record_event(
            db,
            event_type="analysis_started",
            handle="analytics_test_user",
            source="whatsapp",
        )

        event = (
            db.query(AnalyticsEvent)
            .filter(
                AnalyticsEvent.event_type == "analysis_started",
                AnalyticsEvent.handle == "analytics_test_user",
            )
            .first()
        )

        assert event is not None
        assert event.handle == "analytics_test_user"
        assert event.source == "whatsapp"

    finally:
        db.query(AnalyticsEvent).filter(
            AnalyticsEvent.handle == "analytics_test_user"
        ).delete()

        db.commit()
        db.close()