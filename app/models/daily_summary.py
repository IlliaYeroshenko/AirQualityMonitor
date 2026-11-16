
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Date, DateTime, Enum,
    ForeignKey, Numeric, SmallInteger,
    UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyPollutionSummary(Base):
    __tablename__ = "daily_pollution_summaries"

    __table_args__ = (
        UniqueConstraint(
            "station_id",
            "summary_date",
            name="uq_daily_station_date"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )

    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("monitoring_stations.id"),
        nullable=False
    )

    summary_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    avg_pm2_5: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2)
    )

    max_pm2_5: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2)
    )

    avg_pm10: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2)
    )

    max_pm10: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2)
    )

    worst_aqi: Mapped[int | None] = mapped_column(
        SmallInteger
    )

    hazard_level: Mapped[str] = mapped_column(
        Enum(
            "good", "moderate",
            "unhealthy", "hazardous",
            name="hazard_level_type"
        ),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
