import mysql.connector as mysql
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connect(
   host=os.getenv("HOST"),
   user=os.getenv("USER"),
   password=os.getenv("PASSWORD"),
   database=os.getenv("DATABASE")

)