
"""Partition air quality records by month.

Revision ID: d9474e9ffe00
Revises: e9f61a177730
"""

from alembic import op


revision = "d9474e9ffe00"
down_revision = "e9f61a177730"
branch_labels = None
depends_on = None


def upgrade():

    # 1. Create a new partitioned table
    op.execute("""
        CREATE TABLE air_quality_records_new (
            id BIGSERIAL NOT NULL,
            station_id BIGINT NOT NULL,
            recorded_at TIMESTAMPTZ NOT NULL,
            pm2_5 NUMERIC(6, 2),
            pm10 NUMERIC(6, 2),
            no2 NUMERIC(6, 2),
            o3 NUMERIC(6, 2),
            co NUMERIC(6, 2),
            aqi SMALLINT,
            created_at TIMESTAMPTZ
                NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ
                NOT NULL DEFAULT NOW(),

            CONSTRAINT air_quality_records_new_pkey
                PRIMARY KEY (id, recorded_at),

            CONSTRAINT uq_air_quality_station_time_new
                UNIQUE (station_id, recorded_at),

            CONSTRAINT air_quality_records_new_station_id_fkey
                FOREIGN KEY (station_id)
                REFERENCES monitoring_stations(id)
                ON DELETE RESTRICT,

            CONSTRAINT ck_air_quality_aqi_nonnegative_new
                CHECK (aqi IS NULL OR aqi >= 0)

        ) PARTITION BY RANGE (recorded_at)
    """)

    # 2. Create indexes
    op.execute("""
        CREATE INDEX ix_air_quality_station_aqi_new
        ON air_quality_records_new (station_id, aqi)
    """)

    op.execute("""
        CREATE INDEX ix_air_quality_recorded_at_new
        ON air_quality_records_new (recorded_at)
    """)

    # 3. Create monthly partitions for 2026-2028
    for year in range(2026, 2029):
        for month in range(1, 13):

            if month == 12:
                next_year = year + 1
                next_month = 1
            else:
                next_year = year
                next_month = month + 1

            start = (
                f"{year}-{month:02d}-01 "
                f"00:00:00+00"
            )

            end = (
                f"{next_year}-{next_month:02d}-01 "
                f"00:00:00+00"
            )

            partition_name = (
                f"air_quality_records_{year}_{month:02d}"
            )

            op.execute(f"""
                CREATE TABLE {partition_name}
                PARTITION OF air_quality_records_new
                FOR VALUES FROM ('{start}')
                TO ('{end}')
            """)

    # 4. Create a default partition
    op.execute("""
        CREATE TABLE air_quality_records_default
        PARTITION OF air_quality_records_new
        DEFAULT
    """)

    # 5. Copy existing measurements
    op.execute("""
        INSERT INTO air_quality_records_new (
            id, station_id, recorded_at,
            pm2_5, pm10, no2, o3, co, aqi,
            created_at, updated_at
        )
        SELECT
            id, station_id, recorded_at,
            pm2_5, pm10, no2, o3, co, aqi,
            created_at, updated_at
        FROM air_quality_records
    """)

    # 6. Update the ID sequence
    op.execute("""
        SELECT setval(
            pg_get_serial_sequence(
                'air_quality_records_new', 'id'
            ),
            GREATEST(
                (SELECT COALESCE(MAX(id), 0)
                 FROM air_quality_records_new),
                1
            ),
            EXISTS(
                SELECT 1 FROM air_quality_records_new
            )
        )
    """)

    # 7. Verify copied records
    op.execute("""
        DO $$
        BEGIN
            IF (SELECT COUNT(*) FROM air_quality_records)
                <> (SELECT COUNT(*) FROM air_quality_records_new)
            THEN
                RAISE EXCEPTION 'Record count mismatch';
            END IF;
        END $$;
    """)

    # 8. Rename the original table
    op.execute("""
        ALTER TABLE air_quality_records
        RENAME TO air_quality_records_legacy
    """)

    # 9. Activate the new partitioned table
    op.execute("""
        ALTER TABLE air_quality_records_new
        RENAME TO air_quality_records
    """)

    # 10. Remove the original table
    op.execute("""
        DROP TABLE air_quality_records_legacy
    """)

    # 11. Restore constraint names
    op.execute("""
        ALTER TABLE air_quality_records
        RENAME CONSTRAINT air_quality_records_new_pkey
        TO air_quality_records_pkey
    """)

    op.execute("""
        ALTER TABLE air_quality_records
        RENAME CONSTRAINT uq_air_quality_station_time_new
        TO uq_air_quality_station_time
    """)

    op.execute("""
        ALTER TABLE air_quality_records
        RENAME CONSTRAINT air_quality_records_new_station_id_fkey
        TO air_quality_records_station_id_fkey
    """)

    op.execute("""
        ALTER TABLE air_quality_records
        RENAME CONSTRAINT ck_air_quality_aqi_nonnegative_new
        TO ck_air_quality_aqi_nonnegative
    """)

    # 12. Restore index names
    op.execute("""
        ALTER INDEX ix_air_quality_station_aqi_new
        RENAME TO ix_air_quality_station_aqi
    """)

    op.execute("""
        ALTER INDEX ix_air_quality_recorded_at_new
        RENAME TO ix_air_quality_recorded_at
    """)

    # 13. Restore the ID sequence name
    op.execute("""
        ALTER SEQUENCE air_quality_records_new_id_seq
        RENAME TO air_quality_records_id_seq
    """)


def downgrade():
    raise RuntimeError(
        "Automatic rollback is disabled. "
        "Restore the validated database backup "
        "if necessary."
    )
