
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Numeric,
    String,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ThresholdStandard(Base):
    __tablename__ = "threshold_standards"

    __table_args__ = (
        UniqueConstraint(
            "pollutant",
            name="uq_threshold_pollutant",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    pollutant: Mapped[str] = mapped_column(
        Enum(
            "pm2_5",
            "pm10",
            "no2",
            "o3",
            name="pollutant_type",
        ),
        nullable=False,
    )

    warning_threshold: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    critical_threshold: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
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
