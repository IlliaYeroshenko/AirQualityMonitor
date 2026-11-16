
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.air_quality import AirQualityRecord


def save_records(records: list[dict]) -> int:
    if not records:
        return 0

    # Remove duplicate station/time pairs
    unique_records = {}

    for record in records:
        key = (
            record["station_id"],
            record["recorded_at"],
        )
        unique_records[key] = record

    rows = list(unique_records.values())

    # Prepare PostgreSQL INSERT
    statement = insert(AirQualityRecord).values(rows)

    # Fields updated when a record already exists
    update_fields = {
        "pm2_5": statement.excluded.pm2_5,
        "pm10": statement.excluded.pm10,
        "no2": statement.excluded.no2,
        "o3": statement.excluded.o3,
        "co": statement.excluded.co,
        "aqi": statement.excluded.aqi,
        "updated_at": func.now(),
    }

    # INSERT or UPDATE
    upsert_statement = statement.on_conflict_do_update(
        index_elements=["station_id", "recorded_at"],
        set_=update_fields,
    )

    with SessionLocal() as session:
        session.execute(upsert_statement)
        session.commit()

    return len(rows)
