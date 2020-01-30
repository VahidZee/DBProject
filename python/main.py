import psycopg2

from config import *

# creating database connection
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
cur = conn.cursor()
cur.execute('SELECT version()')


def db_create_user(phone, fname, lname='null', bio='null', uname='null', ):
    try:
        cur.execute(f"INSERT INTO userperson VALUES(DEFAULT, '{uname}', '{phone}','{fname}', '{lname}','{bio}')")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


db_create_user('902', 'vahid', 'salam', 'shit', 'head', )


def handle_command():
    pass
if __name__ == '__main__':
   pass