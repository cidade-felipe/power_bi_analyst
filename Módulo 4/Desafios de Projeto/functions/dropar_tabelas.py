def dropar_tabelas(conn_info, schema):
   import psycopg
   from psycopg import sql

   try:
      with psycopg.connect(conn_info) as conn:
         with conn.cursor() as cur:
               cur.execute(
                  """
                  SELECT tablename
                  FROM pg_tables
                  WHERE schemaname = %s;
                  """,
                  (schema,)
               )

               droped_tables ={row[0] for row in cur.fetchall()}

               for table_name in droped_tables:
                  query = sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE;").format(
                     sql.Identifier(schema),
                     sql.Identifier(table_name)
                  )
                  cur.execute(query)
               return list(droped_tables)

   except (Exception, Exception) as e:
      print(f"Error: {e}")
      import traceback
      traceback.print_exc()


if __name__ == "__main__":
   
   from conectar_banco import conectar_db

   conn_info = conectar_db()
   tabelas_dropadas = dropar_tabelas(conn_info,'public')
   for tabela in tabelas_dropadas:
      print(f"Dropando tabela: {tabela}")
