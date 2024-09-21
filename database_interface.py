import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables
load_dotenv()

db_config_str = os.getenv("DB_CONFIG")

# Check if JSON parsing works correctly
try:
    db_config = json.loads(db_config_str)
except json.JSONDecodeError as e:
    print(f"Failed to parse DB_CONFIG: {e}")

def create_engine_from_config():
    """Create an SQLAlchemy engine from the DB config."""
    # Load environment variables from .env file
    try:
        # Parse the JSON configuration string
        db_config = json.loads(db_config_str)        
        required_keys = ['host', 'user', 'password', 'database']
        for key in required_keys:
            if key not in db_config:
                raise ValueError(f"Missing required configuration key: {key}")\
            
        conn_str = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config.get('port', 5432)}/{db_config['database']}"
        
        # Create and return SQLAlchemy engine
        return create_engine(conn_str)
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing DB_CONFIG: Invalid JSON format: {e}")
    except ValueError as e:
        raise ValueError(f"Error in DB_CONFIG: {e}")

def create_async_engine_from_config():
    """Create an SQLAlchemy async engine from the DB config."""
    try:
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
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing DB_CONFIG: Invalid JSON format: {e}")
    except ValueError as e:
        raise ValueError(f"Error in DB_CONFIG: {e}")

def fetch_data(query, engine):
    """Fetch data from the database using the SQLAlchemy engine with transaction management."""
    connection = engine.connect()
    transaction = connection.begin() 
    try:
        data = pd.read_sql_query(query, connection)
        transaction.commit()  
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        transaction.rollback()
    finally:
        connection.close()  