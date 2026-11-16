
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, func, select, text

from app.database import SessionLocal
from app.models.air_quality import AirQualityRecord
from app.models.station import MonitoringStation
from app.services.record_writer import save_records


# Two different months
date1 = datetime(2027, 1, 15, 10, 0, tzinfo=timezone.utc)
date2 = datetime(2027, 2, 15, 10, 0, tzinfo=timezone.utc)


def test_partitioning():

    with SessionLocal() as session:
        station_id = session.scalar(
            select(MonitoringStation.id).where(
                MonitoringStation.name == "Kyiv"
            )
        )

        if station_id is None:
            raise RuntimeError("Kyiv station not found")

        existing = session.scalar(
            select(func.count())
            .select_from(AirQualityRecord)
            .where(
                AirQualityRecord.station_id == station_id,
                AirQualityRecord.recorded_at.in_(
                    [date1, date2]
                )
            )
        )

    if existing:
        raise RuntimeError(
            "Test dates already contain measurements"
        )

    try:
        # January measurement
        record1 = {
            "station_id": station_id,
            "recorded_at": date1,
            "pm2_5": Decimal("15.50"),
            "pm10": Decimal("25.00"),
            "no2": Decimal("12.00"),
            "o3": Decimal("30.00"),
            "co": Decimal("150.00"),
            "aqi": 45,
        }

        # February measurement
        record2 = {
            **record1,
            "recorded_at": date2,
            "pm2_5": Decimal("22.80"),
            "aqi": 65,
        }

        print("Saving January and February...")
        save_records([record1, record2])

        # Repeat January with updated values
        updated_record = {
            **record1,
            "pm2_5": Decimal("18.90"),
            "aqi": 55,
        }

        save_records([updated_record])

        with SessionLocal() as session:
            results = session.execute(
                text("""
                    SELECT
                        recorded_at,
                        pm2_5,
                        aqi,
                        tableoid::regclass::text
                            AS partition_name
                    FROM air_quality_records
                    WHERE station_id = :station_id
                    AND recorded_at IN (:date1, :date2)
                    ORDER BY recorded_at
                """),
                {
                    "station_id": station_id,
                    "date1": date1,
                    "date2": date2,
                }
            ).mappings().all()

            assert len(results) == 2
            assert results[0]["partition_name"] == (
                "air_quality_records_2027_01"
            )
            assert results[1]["partition_name"] == (
                "air_quality_records_2027_02"
            )
            assert results[0]["pm2_5"] == Decimal("18.90")
            assert results[0]["aqi"] == 55

            print(f"Total records: {len(results)}")

            for row in results:
                print(
                    f"{row['recorded_at']} -> "
                    f"{row['partition_name']}"
                )

        print("Partitioning test PASSED!")

    finally:
        # Remove only the two test measurements
        with SessionLocal() as session:
            session.execute(
                delete(AirQualityRecord).where(
                    AirQualityRecord.station_id == station_id,
                    AirQualityRecord.recorded_at.in_(
                        [date1, date2]
                    )
                )
            )
            session.commit()

        print("Test measurements cleaned up.")


if __name__ == "__main__":
    test_partitioning()

