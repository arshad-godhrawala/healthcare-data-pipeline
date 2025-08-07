from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
print("Loading .env from:", env_path)
load_dotenv(env_path)



def create_postgres_connection():
    """Create a connection to the PostgreSQL database"""

    DB_USER=os.getenv('POSTGRES_USER')
    DB_PASSWORD=os.getenv('POSTGRES_PASSWORD')
    DB_NAME=os.getenv('POSTGRES_DB')
    DB_HOST=os.getenv('POSTGRES_HOST', 'localhost')
    DB_PORT=os.getenv('POSTGRES_PORT', '5432')

    DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(DATABASE_URL)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session

def connect(engine):
    try:
        conn = engine.connect()
        print("PostgreSQL connected")
        return conn
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return None


