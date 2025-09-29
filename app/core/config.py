"""Configuration constants for the application.

This module loads environment variables and exposes configuration
values used across the application such as database paths, LLM and
embedding models, and MongoDB connection settings. Values are simple
module-level constants intended to be imported where needed.

Constants:
	SQL_DB_PATH (str): Path to the SQLite database file (from env).
	LLM_MODEL (str): Default language model identifier.
	EMBEDDING_MODEL (str): Default embedding model identifier.
	MONGODB_CONNECTION (str): MongoDB connection URI.
	MONGODB_DATABASE (str): MongoDB database name.
"""

import os
from dotenv import load_dotenv

load_dotenv()

SQL_DB_PATH = os.getenv("SQL_DB_PATH")
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Local MongoDB defaults; override with environment variables in production
MONGODB_CONNECTION = "mongodb://localhost:27017/"
MONGODB_DATABASE = "trubyai_local"
TOP_K_CONTEXTS = 5
