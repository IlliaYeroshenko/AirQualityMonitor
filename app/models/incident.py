
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, DateTime, ForeignKey,
    Numeric, String, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PollutionIncident(Base):
    __tablename__ = "pollution_incidents"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )

    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("monitoring_stations.id"),
        nullable=False
    )

    pollutant: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    measured_value: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False
    )

    threshold_value: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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
