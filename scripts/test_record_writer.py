
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models.air_quality import AirQualityRecord
from app.services.record_writer import save_records


# Example measurement time (UTC)
record_time = datetime(
    2026, 11, 12, 10, 0,
    tzinfo=timezone.utc
)

# First measurement
record = {
    "station_id": 1,
    "recorded_at": record_time,
    "pm2_5": Decimal("15.40"),
    "pm10": Decimal("22.10"),
    "no2": Decimal("12.50"),
    "o3": Decimal("30.00"),
    "co": Decimal("150.00"),
    "aqi": 45,
}

print("First save:")
save_records([record])

# Update the same measurement
record["pm2_5"] = Decimal("18.70")
record["aqi"] = 60

print("Second save:")
save_records([record])

# Check database
with SessionLocal() as session:
    results = session.scalars(
        select(AirQualityRecord).where(
            AirQualityRecord.station_id == 1,
            AirQualityRecord.recorded_at == record_time,
        )
    ).all()

    print(f"Total records: {len(results)}")

    if results:
        print(f"PM2.5: {results[0].pm2_5}")
        print(f"AQI: {results[0].aqi}")
