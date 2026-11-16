
from alembic import context

from app.database import Base, engine

# Import all database models
from app.models.station import MonitoringStation
from app.models.air_quality import AirQualityRecord
from app.models.threshold import ThresholdStandard
from app.models.daily_summary import DailyPollutionSummary
from app.models.incident import PollutionIncident
from app.models.user import User
from app.models.subscription import UserStationSubscription


# Metadata containing all database tables
target_metadata = Base.metadata


# Exclude partitions and unrelated database tables
# from Alembic autogeneration
def include_name(name, type_, parent_names):
    if type_ == "table":
        return (
            parent_names["schema_qualified_table_name"]
            in target_metadata.tables
        )

    return True


def run_migrations_offline():
    context.configure(
        url=engine.url.render_as_string(
            hide_password=False
        ),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
