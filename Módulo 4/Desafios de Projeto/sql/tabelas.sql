CREATE TABLE IF NOT EXISTS dim_professor (
   id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   pnome    VARCHAR(50) NOT NULL,
   mnome    VARCHAR(50),
   unome    VARCHAR(50) NOT NULL,
   idade   INTEGER NOT NULL,
   titulacao VARCHAR(20) CHECK (titulacao IN ('Doutorado', 'Mestrado', 'Bacharelado','Licenciatura')),
   sexo    VARCHAR(1) CHECK (sexo IN ('M', 'F')),
   cidade  VARCHAR(255),
   estado  VARCHAR(50),
   pais    VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_departamento (
   id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_curso (
   id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome            VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_disciplina (
   id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   nome             VARCHAR(50) NOT NULL,
   id_pre_requisito INTEGER,
   FOREIGN KEY (id_pre_requisito) REFERENCES dim_disciplina(id)
);

CREATE TABLE IF NOT EXISTS dim_tempo (
   id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   data      DATE NOT NULL,
   ano       INTEGER,
   semestre  INTEGER,
   mes       INTEGER,
   dia       INTEGER
);

CREATE TABLE IF NOT EXISTS dim_aluno (
   id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   Pnome   VARCHAR(50) NOT NULL,
   Mnome   VARCHAR(50),
   Unome VARCHAR(50) NOT NULL,
   idade   INTEGER NOT NULL,
   sexo    VARCHAR(1) CHECK (sexo IN ('M', 'F')),
   cidade  VARCHAR(255),
   estado  VARCHAR(50),
   pais    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS fato_professor (
   id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
   id_professor    INTEGER NOT NULL,
   id_departamento INTEGER NOT NULL,
   id_curso        INTEGER NOT NULL,
   id_disciplina   INTEGER NOT NULL,
   id_tempo        INTEGER NOT NULL,
   id_aluno        INTEGER NOT NULL,
   qtd_turmas      INTEGER,
   qtd_alunos      INTEGER,
   carga_horaria   INTEGER,
   nota_media      NUMERIC(5,2),
   UNIQUE (id_professor, id_departamento, id_curso, id_disciplina, id_tempo),
   FOREIGN KEY (id_professor)  REFERENCES dim_professor(id),
   FOREIGN KEY (id_departamento) REFERENCES dim_departamento(id),
   FOREIGN KEY (id_curso)      REFERENCES dim_curso(id),
   FOREIGN KEY (id_disciplina) REFERENCES dim_disciplina(id),
   FOREIGN KEY (id_tempo)      REFERENCES dim_tempo(id),
   FOREIGN KEY (id_aluno)      REFERENCES dim_aluno(id)
);