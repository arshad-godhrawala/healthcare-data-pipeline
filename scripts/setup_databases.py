import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database.postgres_operations import create_postgres_connection
from src.database.models import Base

def create_tables():
    engine, _ = create_postgres_connection()
    Base.metadata.create_all(engine)
    print("Tables created successfully")

if __name__ == "__main__":
    create_tables()

