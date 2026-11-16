
from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime,
    ForeignKey, UniqueConstraint,
    func, true
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserStationSubscription(Base):
    __tablename__ = "user_station_subscriptions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "station_id",
            name="uq_user_station_subscription"
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    station_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("monitoring_stations.id"),
        nullable=False
    )

    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=true(),
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
