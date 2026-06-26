# Academia API

REST API para gerenciamento de academia, construída com FastAPI e PostgreSQL.

## Tecnologias

- Python 3.9+
- FastAPI
- PostgreSQL
- psycopg2
- Uvicorn

## Como executar

### 1. Clone o repositório

    git clone https://github.com/ThiagoKleinn/academia-api.git
    cd academia-api

### 2. Crie e ative o ambiente virtual

    python -m venv .venv
    source .venv/bin/activate  # Mac/Linux
    .venv\Scripts\activate     # Windows

### 3. Instale as dependências

    pip install -r requirements.txt

### 4. Configure o banco de dados

Crie um arquivo `.env` na raiz do projeto:

    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=academia
    DB_USER=postgres
    DB_PASSWORD=sua_senha

### 5. Execute o servidor

    uvicorn app.main:app --reload

Acesse a documentação em: http://127.0.0.1:8000/docs

---

## Endpoints

### Alunos

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /alunos/ | Lista todos os alunos |
| GET | /alunos/{id} | Busca um aluno por ID |
| POST | /alunos/ | Cadastra novo aluno |
| PUT | /alunos/{id} | Atualiza um aluno |
| DELETE | /alunos/{id} | Remove um aluno |

### Planos

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /planos/ | Lista todos os planos |

### Matrículas

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /matriculas/ | Lista todas as matrículas |
| GET | /matriculas/{id} | Busca uma matrícula por ID |
| POST | /matriculas/ | Cria nova matrícula |
| DELETE | /matriculas/{id} | Remove uma matrícula |

### Pagamentos

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /pagamentos/ | Lista todos os pagamentos |
| GET | /pagamentos/{id} | Busca um pagamento por ID |
| POST | /pagamentos/ | Registra novo pagamento |

### Relatórios

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /relatorios/faturamento | Receita total por mês |
| GET | /relatorios/inadimplentes | Alunos com matrícula vencida sem pagamento |
| GET | /relatorios/planos/popularidade | Ranking de planos por número de matrículas |

---

## Estrutura do projeto

    academia-api/
    ├── app/
    │   ├── main.py
    │   ├── database.py
    │   └── routers/
    │       ├── alunos.py
    │       ├── planos.py
    │       ├── matriculas.py
    │       ├── pagamentos.py
    │       └── relatorios.py
    ├── .env
    ├── .gitignore
    ├── requirements.txt
    └── README.md

---

## Banco de dados

Este projeto utiliza o banco de dados do repositório [Academia](https://github.com/ThiagoKleinn/Academia),
que contém o schema, seeds e dashboard Power BI.