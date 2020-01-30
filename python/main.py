import psycopg2

from .config import *
# creating database connection
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
