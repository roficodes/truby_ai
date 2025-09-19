import os
from dotenv import load_dotenv

load_dotenv()

STORAGE_DIR = os.getenv("STORAGE_DIR")
SQL_DB_PATH = os.getenv("SQL_DB_PATH")
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
# MONGODB_CONNECTION = os.getenv("MONGODB_CONNECTION")
# MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# USE FOR LOCAL
# Use for LOCAL
MONGODB_CONNECTION = "mongodb://localhost:27017/"
MONGODB_DATABASE = "trubyai_local"
