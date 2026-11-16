
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models.station import MonitoringStation


STATIONS = [
    ("Kyiv", "50.45010", "30.52340"),
    ("Kharkiv", "49.99350", "36.23040"),
    ("Lviv", "49.83970", "24.02970"),
    ("Odesa", "46.48250", "30.72330"),
    ("Dnipro", "48.46470", "35.04620"),
]


def seed_stations():
    added = 0

    with SessionLocal() as session:
        for name, latitude, longitude in STATIONS:

            existing = session.scalar(
                select(MonitoringStation.id).where(
                    MonitoringStation.name == name
                )
            )

            if existing is not None:
                print(f"Already exists: {name}")
                continue

            station = MonitoringStation(
                name=name,
                latitude=Decimal(latitude),
                longitude=Decimal(longitude),
                is_active=True
            )

            session.add(station)
            added += 1

        session.commit()

    print(f"Successfully added {added} stations!")


if __name__ == "__main__":
    seed_stations()
