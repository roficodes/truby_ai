import os
from dotenv import load_dotenv

load_dotenv()

STORAGE_DIR = os.getenv("STORAGE_DIR")
SQL_DB_PATH = os.getenv("SQL_DB_PATH")
