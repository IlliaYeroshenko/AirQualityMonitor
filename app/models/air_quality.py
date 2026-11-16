
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    SmallInteger,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AirQualityRecord(Base):
    __tablename__ = "air_quality_records"

    __table_args__ = (
        UniqueConstraint(
            "station_id",
            "recorded_at",
            name="uq_air_quality_station_time",
        ),
        Index(
            "ix_air_quality_station_aqi",
            "station_id",
            "aqi",
        ),
        Index(
            "ix_air_quality_recorded_at",
            "recorded_at",
        ),
        CheckConstraint(
            "aqi IS NULL OR aqi >= 0",
            name="ck_air_quality_aqi_nonnegative",
        ),
        {
            "postgresql_partition_by": "RANGE (recorded_at)"
        },
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "monitoring_stations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        nullable=False,
    )

    pm2_5: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    pm10: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    no2: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    o3: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    co: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    aqi: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
