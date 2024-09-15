from dotenv import load_dotenv
import pandas as pd
import os
import json
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


# Load environment variables from .env file
load_dotenv()

# Retrieve the DB_CONFIG environment variable
db_config_str = os.getenv("DB_CONFIG")

def create_engine_from_config():
    """Create an SQLAlchemy engine from the DB config."""
    try:
        # Parse the JSON configuration string
        db_config = json.loads(db_config_str)
        
        # Ensure all required keys are present
        required_keys = ['host', 'port', 'user', 'password', 'database']
        for key in required_keys:
            if key not in db_config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Create connection string
        conn_str = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config.get('port', 5432)}/{db_config['database']}"
        
        # Create and return SQLAlchemy engine
        return create_engine(conn_str)
    
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing DB_CONFIG: {e}")
        sys.exit(1)
        
def create_async_engine_from_config():
    """Create an SQLAlchemy async engine from the DB config."""
    try:
        # Parse the JSON configuration string
        db_config = json.loads(db_config_str)
        
        # Ensure all required keys are present
        required_keys = ['host', 'port', 'user', 'password', 'database']
        for key in required_keys:
            if key not in db_config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Create connection string
        conn_str = f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config.get('port', 5432)}/{db_config['database']}"
        
        # Create and return SQLAlchemy async engine
        return create_async_engine(conn_str, echo=True)
    
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing DB_CONFIG: {e}")
        sys.exit(1)

def fetch_data(query, engine):
    """Fetch data from the database using the SQLAlchemy engine."""
    with engine.connect() as conn:
        return pd.read_sql_query(query, conn)
