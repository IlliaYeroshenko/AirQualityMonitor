
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.threshold import ThresholdStandard


# Demonstration thresholds (not official standards)
THRESHOLDS = [
    {
        "pollutant": "pm2_5",
        "warning_threshold": Decimal("25.00"),
        "critical_threshold": Decimal("50.00"),
        "description": "DEMO: Fine particles PM2.5",
    },
    {
        "pollutant": "pm10",
        "warning_threshold": Decimal("50.00"),
        "critical_threshold": Decimal("100.00"),
        "description": "DEMO: Particles PM10",
    },
    {
        "pollutant": "no2",
        "warning_threshold": Decimal("100.00"),
        "critical_threshold": Decimal("200.00"),
        "description": "DEMO: Nitrogen dioxide",
    },
    {
        "pollutant": "o3",
        "warning_threshold": Decimal("100.00"),
        "critical_threshold": Decimal("180.00"),
        "description": "DEMO: Ozone",
    },
]


def seed_thresholds():
    statement = insert(ThresholdStandard).values(
        THRESHOLDS
    )

    statement = statement.on_conflict_do_update(
        index_elements=["pollutant"],
        set_={
            "warning_threshold":
                statement.excluded.warning_threshold,
            "critical_threshold":
                statement.excluded.critical_threshold,
            "description":
                statement.excluded.description,
            "updated_at": func.now(),
        },
    )

    with SessionLocal() as session:
        session.execute(statement)
        session.commit()

    print("Successfully synchronized 4 thresholds!")


if __name__ == "__main__":
    seed_thresholds()
