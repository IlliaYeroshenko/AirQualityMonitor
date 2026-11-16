
from sqlalchemy import text
from app.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )

        database, user = result.one()

        print("Connection successful!")
        print(f"Database: {database}")
        print(f"User: {user}")

except Exception as error:
    print("Connection failed!")
    print(error)
