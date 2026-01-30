import os
import psycopg2
import urllib.parse

urllib.parse.uses_netloc.append("postgres")

db_url = os.environ.get("DATABASE_URL")

db_params = psycopg2.extensions.parse_dsn(db_url)
