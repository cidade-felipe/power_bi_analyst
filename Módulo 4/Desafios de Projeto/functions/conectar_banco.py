import os
from dotenv import load_dotenv
import psycopg as psy

def conectar_db():
   load_dotenv()
   host = os.getenv("HOST")
   db_name = os.getenv("DB_NAME")
   user = os.getenv("USER")
   password = os.getenv("PASSWORD")
   porta = os.getenv("PORTA")
   
   conn_info = f'dbname={db_name} user={user} password={password} host={host} port={porta}'
   try:
      with psy.connect(conn_info) as conn:
         with conn.cursor() as cur:
            cur = conn.cursor()
            cur.execute("SELECT version();")
            record = cur.fetchone()
            print("You are connected to - ", record)

   except psy.Error as e:
      print("Error: Could not make connection to the Postgres database")
      print(e)
   except Exception as e:
      print(f'Error: {e}')
      import traceback
      traceback.print_exc()
      conn.rollback()
      
   return conn_info

def connection_string():
   load_dotenv()
   return os.getenv('DB_POOL_URL')

if __name__ == '__main__':
   conectar_db()
   print(connection_string())