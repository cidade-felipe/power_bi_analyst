import random
import re
from datetime import date, timedelta
from collections import defaultdict

import psycopg as psy
from psycopg import sql

from conectar_banco import conectar_db

BASE_DEPARTAMENTOS = [
   "Computacao",
   "Matematica",
   "Fisica",
   "Quimica",
   "Letras",
   "Administracao",
   "Engenharia",
   "Biologia",
   "Historia",
   "Geografia",
]

COURSES_BY_DEPT = {
   "Computacao": [
      "Sistemas de Informacao",
      "Engenharia de Software",
      "Ciencia da Computacao",
   ],
   "Matematica": ["Matematica", "Estatistica"],
   "Fisica": ["Fisica", "Astronomia"],
   "Quimica": ["Quimica", "Engenharia Quimica"],
   "Letras": ["Letras", "Linguistica"],
   "Administracao": ["Administracao", "Contabilidade", "Economia"],
   "Engenharia": [
      "Engenharia Civil",
      "Engenharia Eletrica",
      "Engenharia Mecanica",
      "Engenharia de Producao",
   ],
   "Biologia": ["Biologia", "Ciencias Biologicas"],
   "Historia": ["Historia"],
   "Geografia": ["Geografia"],
}

DISC_TEMPLATES = [
   "Introducao a {curso}",
   "{curso} I",
   "{curso} II",
   "Projeto Integrador de {curso}",
   "Metodos de Pesquisa em {curso}",
   "Laboratorio de {curso}",
]

FIRST_NAMES_BY_SEX = [
   ("Ana","F"),
   ("Bruno","M"),
   ("Carla","F"),
   ("Daniel","M"),
   ("Eduarda","F"),
   ("Felipe","M"),
   ("Gabriela","F"),
   ("Hugo","M"),   
   ("Isabella","F"),
   ("Joaquim","M"),
   ("Larissa","F"),
   ("Marcos","M"),
   ("Natália","F"),
   ("Otávio","M"),
   ("Paula","F"),
   ("Rafael","M"),
   ("Sandra","F"),
   ("Thiago","M"),
   ("Vanessa","F"),
   ("Wagner","M"),   
   ("Yasmin","F"),
]

MIDLE_NAMES = [
   "Silva",
   "Souza",
   "Oliveira",
   "Santos",
   "Lima",
   "Pereira",
   "Costa",
   "Rodrigues",
   "Almeida",
   "Nascimento",
   "Gomes",
   "Barbosa",
]


LAST_NAMES = [
   "Silva",
   "Souza",
   "Oliveira",
   "Santos",
   "Lima",
   "Pereira",
   "Costa",
   "Rodrigues",
   "Almeida",
   "Nascimento",
   "Gomes",
   "Barbosa",
]

CIDADES = [
   ("Sao Paulo", "São Paulo"),
   ("Rio de Janeiro", "Rio de Janeiro"),
   ("Belo Horizonte", "Minas Gerais"),
   ("Curitiba", "Paraná"),
   ("Porto Alegre", "Rio Grande do Sul"),
   ("Salvador", "Bahia"),
   ("Recife", "Pernambuco"),
   ("Fortaleza", "Ceará"),
   ("Manaus", "Amazonas"),
   ("Goiania", "Goiás"),
   ("Florianopolis", "Santa Catarina"),
   ("Brasilia", "Distrito Federal"),
   ("Natal", "Rio Grande do Norte"),
]

TITULACOES = ["Doutorado", "Mestrado", "Bacharelado", "Licenciatura"]

ROMAN_PREV = {"II": "I", "III": "II", "IV": "III"}
ROMAN_RE = re.compile(r"^(.*)\s+(I|II|III|IV)$")

DEFAULTS = {
   "departamentos": 7,
   "cursos": 12,
   "disciplinas": 30,
   "professores": 25,
   "dias": 365,
   "fatos": 800,
}

def _build_departamentos(qtd):
   names = list(BASE_DEPARTAMENTOS)
   while len(names) < qtd:
      names.append(f"Departamento {len(names) + 1}")
   return names[:qtd]


def _build_cursos(qtd, departamentos):
   cursos = []
   for dept in departamentos:
      cursos.extend((curso, dept) for curso in COURSES_BY_DEPT.get(dept, []))
   if len(cursos) < qtd:
      i = len(cursos) + 1
      while len(cursos) < qtd:
         dept = random.choice(departamentos)
         cursos.append((f"Curso {i}", dept))
         i += 1
   if len(cursos) > qtd:
      random.shuffle(cursos)
      cursos = cursos[:qtd]
   return cursos


def _build_disciplinas(qtd, cursos):
   disciplinas = []
   for curso, _dept in cursos:
      templates = list(DISC_TEMPLATES)
      random.shuffle(templates)
      disciplinas.extend(
          (template.format(curso=curso), curso) for template in templates[:3])
   if len(disciplinas) < qtd:
      i = len(disciplinas) + 1
      while len(disciplinas) < qtd:
         curso, _dept = random.choice(cursos)
         disciplinas.append((f"Topicos Especiais {i}", curso))
         i += 1
   if len(disciplinas) > qtd:
      random.shuffle(disciplinas)
      disciplinas = disciplinas[:qtd]
   return disciplinas


def _generate_names_sex(qtd):
   names = []
   for _ in range(qtd):
      name, sex = random.choice(FIRST_NAMES_BY_SEX)
      names.append((name, random.choice(MIDLE_NAMES), random.choice(LAST_NAMES), sex))
   return names

def _insert_rows(cur, schema, table, columns, rows):
   if not rows:
      return []
   query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id;").format(
      sql.Identifier(schema, table),
      sql.SQL(", ").join(sql.Identifier(col) for col in columns),
      sql.SQL(", ").join(sql.Placeholder() for _ in columns),
   )
   ids = []
   for row in rows:
      cur.execute(query, row)
      ids.append(cur.fetchone()[0])
   return ids


def popular_banco(
   schema="public",
   departamentos=DEFAULTS["departamentos"],
   cursos=DEFAULTS["cursos"],
   disciplinas=DEFAULTS["disciplinas"],
   professores=DEFAULTS["professores"],
   dias=DEFAULTS["dias"],
   fatos=DEFAULTS["fatos"],
   seed=None,
):
   if seed is not None:
      random.seed(seed)

   conn_info = conectar_db()
   departamentos_nomes = _build_departamentos(departamentos)
   cursos_defs = _build_cursos(cursos, departamentos_nomes)
   disciplinas_defs = _build_disciplinas(disciplinas, cursos_defs)

   with psy.connect(conn_info) as conn:
      with conn.cursor() as cur:
         dept_ids = _insert_rows(
            cur,
            schema,
            "dim_departamento",
            ["nome"],
            [(nome,) for nome in departamentos_nomes],
         )
         dept_by_name = dict(zip(departamentos_nomes, dept_ids))

         curso_rows = [(nome,) for nome, _dept in cursos_defs]
         curso_ids = _insert_rows(
            cur,
            schema,
            "dim_curso",
            ["nome"],
            curso_rows,
         )
         curso_by_name = {nome: curso_id for (nome, _), curso_id in zip(cursos_defs, curso_ids)}
         dept_by_curso = {
            curso_by_name[nome]: dept_by_name[dept]
            for nome, dept in cursos_defs
         }
         dept_to_cursos = defaultdict(list)
         for curso_id, dept_id in dept_by_curso.items():
            dept_to_cursos[dept_id].append(curso_id)

         curso_to_disciplinas = defaultdict(list)
         for curso_nome, _dept in cursos_defs:
            curso_to_disciplinas[curso_by_name[curso_nome]] = []

         disciplina_ids = []
         for curso_nome, _dept in cursos_defs:
            curso_id = curso_by_name[curso_nome]
            disc_do_curso = [d for d, c in disciplinas_defs if c == curso_nome]
            random.shuffle(disc_do_curso)
            name_to_id = {}

            def insert_disciplina(nome, prereq_id):
               new_ids = _insert_rows(
                  cur,
                  schema,
                  "dim_disciplina",
                  ["nome", "id_pre_requisito"],
                  [(nome, prereq_id)],
               )
               disc_id = new_ids[0]
               disciplina_ids.append(disc_id)
               curso_to_disciplinas[curso_id].append(disc_id)
               name_to_id[nome] = disc_id
               return disc_id

            def ensure_roman_chain(base, numeral):
               nome = f"{base} {numeral}"
               if nome in name_to_id:
                  return name_to_id[nome]
               if numeral == "I":
                  return insert_disciplina(nome, None)
               prev = ROMAN_PREV.get(numeral)
               if not prev:
                  return insert_disciplina(nome, None)
               prev_id = ensure_roman_chain(base, prev)
               return insert_disciplina(nome, prev_id)

            last_disc_id = None
            for disc_nome in disc_do_curso:
               if disc_nome in name_to_id:
                  continue

               if disc_nome.startswith("Introducao a "):
                  last_disc_id = insert_disciplina(disc_nome, None)
                  continue

               match = ROMAN_RE.match(disc_nome)
               if match:
                  base = match.group(1).strip()
                  numeral = match.group(2)
                  last_disc_id = ensure_roman_chain(base, numeral)
                  continue

               prereq_id = None
               if last_disc_id and random.random() < 0.35:
                  prereq_id = last_disc_id
               last_disc_id = insert_disciplina(disc_nome, prereq_id)

         nomes_generos_professores = _generate_names_sex(professores)
         prof_rows = []
         prof_to_dept = {}
         for fname, mname, lname, gender in nomes_generos_professores:
            cidade, estado = random.choice(CIDADES)
            prof_rows.append(
               (
                  fname,
                  mname,
                  lname,
                  random.randint(25,70),
                  random.choice(TITULACOES),
                  gender,
                  cidade,
                  estado,
                  "Brasil",
               )
            )
         prof_ids = _insert_rows(
            cur,
            schema,
            "dim_professor",
            ["pnome", "mnome", "unome", "idade", "titulacao", "sexo", "cidade", "estado", "pais"],
            prof_rows,
         )
         for prof_id in prof_ids:
            prof_to_dept[prof_id] = random.choice(dept_ids)

         start_date = date.today().replace(month=1, day=1)
         tempo_rows = []
         for i in range(dias):
            d = start_date + timedelta(days=i)
            semestre = 1 if d.month <= 6 else 2
            tempo_rows.append((d, d.year, semestre, d.month, d.day))
         tempo_ids = _insert_rows(
            cur,
            schema,
            "dim_tempo",
            ["data", "ano", "semestre", "mes", "dia"],
            tempo_rows,
         )

         fact_rows = []
         used = set()
         attempts = 0
         max_attempts = fatos * 10
         while len(fact_rows) < fatos and attempts < max_attempts:
            attempts += 1
            prof_id = random.choice(prof_ids)
            dept_id = prof_to_dept[prof_id]
            cursos_do_dept = dept_to_cursos.get(dept_id) or list(curso_by_name.values())
            curso_id = random.choice(cursos_do_dept)
            disciplinas_do_curso = curso_to_disciplinas.get(curso_id) or disciplina_ids
            disc_id = random.choice(disciplinas_do_curso)
            tempo_id = random.choice(tempo_ids)

            key = (prof_id, dept_id, curso_id, disc_id, tempo_id)
            if key in used:
               continue
            used.add(key)

            fact_rows.append(
               (
                  prof_id,
                  dept_id,
                  curso_id,
                  disc_id,
                  tempo_id,
                  random.randint(1, 4),
                  random.randint(10, 60),
                  random.randint(30, 120),
                  round(random.uniform(5.0, 10.0), 2),
               )
            )

         fact_query = sql.SQL(
            """
            INSERT INTO {} (
               id_professor,
               id_departamento,
               id_curso,
               id_disciplina,
               id_tempo,
               qtd_turmas,
               qtd_alunos,
               carga_horaria,
               nota_media
            ) VALUES ({})
            ON CONFLICT (id_professor, id_departamento, id_curso, id_disciplina, id_tempo)
            DO NOTHING;
            """
         ).format(
            sql.Identifier(schema, "fato_professor"),
            sql.SQL(", ").join(sql.Placeholder() for _ in range(9)),
         )
         for row in fact_rows:
            cur.execute(fact_query, row)

   return {
      "departamentos": len(dept_ids),
      "cursos": len(curso_ids),
      "disciplinas": len(disciplina_ids),
      "professores": len(prof_ids),
      "tempo": len(tempo_ids),
      "fatos": len(fact_rows),
   }


if __name__ == "__main__":
   import argparse

   parser = argparse.ArgumentParser(description="Popula o banco com dados aleatorios coerentes.")
   parser.add_argument("--schema", default="public")
   parser.add_argument("--departamentos", type=int, default=DEFAULTS["departamentos"])
   parser.add_argument("--cursos", type=int, default=DEFAULTS["cursos"])
   parser.add_argument("--disciplinas", type=int, default=DEFAULTS["disciplinas"])
   parser.add_argument("--professores", type=int, default=DEFAULTS["professores"])
   parser.add_argument("--dias", type=int, default=DEFAULTS["dias"])
   parser.add_argument("--fatos", type=int, default=DEFAULTS["fatos"])
   parser.add_argument("--seed", type=int)
   args = parser.parse_args()

   resumo = popular_banco(
      schema=args.schema,
      departamentos=args.departamentos,
      cursos=args.cursos,
      disciplinas=args.disciplinas,
      professores=args.professores,
      dias=args.dias,
      fatos=args.fatos,
      seed=args.seed,
   )

   print("Populacao concluida:")
   for chave, valor in resumo.items():
      print(f"- {chave}: {valor}")
