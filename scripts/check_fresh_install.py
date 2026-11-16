
import os
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from alembic import command
from alembic.config import Config


# Project directory
ROOT = Path(__file__).resolve().parent.parent

# Read the original database configuration
env = dotenv_values(ROOT / ".env")

original_url = env.get("DATABASE_URL")

if not original_url:
    raise RuntimeError("DATABASE_URL not found")


# Use a separate test database
test_url = make_url(original_url).set(
    database="air_monitor_fresh_test"
)

os.environ["DATABASE_URL"] = (
    test_url.render_as_string(hide_password=False)
)


def check_fresh_install():

    print("Starting fresh database test...")

    # Run all migrations
    config = Config(str(ROOT / "alembic.ini"))

    config.set_main_option(
        "script_location",
        str(ROOT / "alembic")
    )

    command.upgrade(config, "head")

    print("Migrations completed.")

    engine = create_engine(test_url)

    try:
        with engine.connect() as connection:

            # Count main tables
            tables = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name IN (
                          'users',
                          'monitoring_stations',
                          'air_quality_records',
                          'daily_pollution_summaries',
                          'threshold_standards',
                          'pollution_incidents',
                          'user_station_subscriptions'
                      )
                """)
            ).scalar_one()

            # Count partitions
            partitions = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM pg_inherits
                    WHERE inhparent =
                        'public.air_quality_records'::regclass
                """)
            ).scalar_one()

            # Count only parent-level foreign keys
            foreign_keys = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM pg_constraint
                    WHERE contype = 'f'
                      AND connamespace =
                          'public'::regnamespace
                      AND conparentid = 0
                """)
            ).scalar_one()

        print(f"Main tables: {tables}")
        print(f"Partitions: {partitions}")
        print(f"Foreign keys: {foreign_keys}")

        # Verify database structure
        assert tables == 7, (
            f"Expected 7 tables, found {tables}"
        )

        assert partitions == 37, (
            f"Expected 37 partitions, found {partitions}"
        )

        assert foreign_keys == 5, (
            f"Expected 5 foreign keys, found {foreign_keys}"
        )

        print("Fresh installation test PASSED!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    check_fresh_install()
