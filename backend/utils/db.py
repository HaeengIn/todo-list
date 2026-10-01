# Import required modules
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load env keys from .env
load_dotenv()

# Define URL of database
DB_URL = os.environ["DB_URL"]


# Connect database
def ConnectDB():
    return psycopg.connect(
        DB_URL,
        row_factory=dict_row,  # type: ignore
    )
