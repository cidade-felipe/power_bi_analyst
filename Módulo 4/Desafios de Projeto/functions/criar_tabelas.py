def nomes_tabelas(file_path): 
   import re
   try:
      with open(file_path, "r", encoding="utf-8") as f:
         sql = f.read()

      pattern = re.compile(
         r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+("?[\w]+"?)',
         re.IGNORECASE
      )
      tables = pattern.findall(sql)
      tables = [t.replace('"', '') for t in tables]
      return tables
   except Exception as e:
      print(f"Erro ao ler o arquivo SQL: {e}")
      return None

def criar_tabelas(conn_info, sql_file, schema):
   import psycopg as psy
   try:
      with psy.connect(conn_info) as conn:
         with conn.cursor() as cur:
               with open(sql_file, "r", encoding="utf-8") as f:
                  cur.execute(f.read().replace('SCHEMA_NAME', schema))
               
               # Tabelas existentes antes
               cur.execute("""
                  SELECT tablename
                  FROM pg_tables
                  WHERE schemaname = '{}';
               """.format(schema))
               created_tables = {row[0] for row in cur.fetchall()}

               return list(created_tables)

   except (Exception, Exception) as e:
      print(f"Error: {e}")
      import traceback
      traceback.print_exc()

if __name__ == "__main__":
   import re
   from conectar_banco import conectar_db
   file = r'Módulo 4\Desafios de Projeto\sql\tabelas.sql'
   conn_info = conectar_db()
   tabelas_criadas = criar_tabelas(conn_info, file,'public')
   for tabela in tabelas_criadas:
      print(f'Criando tabela: {tabela}')
   
