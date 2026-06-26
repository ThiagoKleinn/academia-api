# Academia API

REST API para gerenciamento de academia, construída com FastAPI e PostgreSQL.

## Tecnologias

- Python 3.9+
- FastAPI
- PostgreSQL
- psycopg2 / SQLAlchemy
- python-jose (JWT)
- passlib + bcrypt (hash de senha)
- Uvicorn
- Pytest

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

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=academia
    DB_USER=postgres
    DB_PASSWORD=sua_senha

    SECRET_KEY=uma_chave_secreta_bem_aleatoria
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=uma_senha_forte

### 5. Crie o usuário admin no banco

A API autentica usuários a partir da tabela `usuarios` no banco de dados.
Para criar (ou atualizar) o usuário admin com a senha definida no `.env`, rode:

    python seed.py

Esse script gera o hash bcrypt da senha automaticamente — não é necessário
inserir hashes manualmente.

### 6. Execute o servidor

    uvicorn app.main:app --reload

Acesse a documentação em: http://127.0.0.1:8000/docs

---

## Autenticação

Todos os endpoints (exceto `/` e `/auth/login`) exigem autenticação via JWT.

### Obter token

    POST /auth/login
    Content-Type: application/x-www-form-urlencoded

    username=admin&password=sua_senha

Resposta:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### Usar o token

Inclua o token no header `Authorization` das requisições:

    Authorization: Bearer eyJhbGciOi...

O token expira em 60 minutos. Usuários marcados como inativos (`ativo = false`
na tabela `usuarios`) não conseguem autenticar, mesmo com um token ainda válido.

---

## Endpoints

### Autenticação

| Método | Rota         | Descrição                  |
|--------|--------------|-----------------------------|
| POST   | /auth/login  | Autentica e retorna um token JWT |

### Alunos

| Método | Rota         | Descrição             |
|--------|--------------|------------------------|
| GET    | /alunos/     | Lista todos os alunos |
| GET    | /alunos/{id} | Busca um aluno por ID |
| POST   | /alunos/     | Cadastra novo aluno   |
| PUT    | /alunos/{id} | Atualiza um aluno     |
| DELETE | /alunos/{id} | Remove um aluno       |

### Planos

| Método | Rota     | Descrição             |
|--------|----------|------------------------|
| GET    | /planos/ | Lista todos os planos |

### Matrículas

| Método | Rota             | Descrição                  |
|--------|------------------|------------------------------|
| GET    | /matriculas/     | Lista todas as matrículas  |
| GET    | /matriculas/{id} | Busca uma matrícula por ID |
| POST   | /matriculas/     | Cria nova matrícula        |
| DELETE | /matriculas/{id} | Remove uma matrícula       |

### Pagamentos

| Método | Rota              | Descrição                 |
|--------|-------------------|-----------------------------|
| GET    | /pagamentos/      | Lista todos os pagamentos |
| GET    | /pagamentos/{id}  | Busca um pagamento por ID  |
| POST   | /pagamentos/      | Registra novo pagamento   |

### Relatórios

| Método | Rota                              | Descrição                                  |
|--------|------------------------------------|----------------------------------------------|
| GET    | /relatorios/faturamento           | Receita total por mês                       |
| GET    | /relatorios/inadimplentes         | Alunos com matrícula vencida sem pagamento  |
| GET    | /relatorios/planos/popularidade   | Ranking de planos por número de matrículas  |

> Todas as rotas acima (exceto `/auth/login`) exigem o header `Authorization: Bearer <token>`.

---

## Testes

O projeto possui testes automatizados com Pytest cobrindo alunos, matrículas,
pagamentos, relatórios e controle de acesso.

    pytest tests/ -v

> Os testes usam o usuário admin definido no `.env`. Rode `python seed.py`
> antes de testar pela primeira vez, ou sempre que o banco for recriado.

---

## Estrutura do projeto

    academia-api/
    ├── app/
    │   ├── main.py
    │   ├── database.py
    │   ├── auth.py
    │   └── routers/
    │       ├── auth.py
    │       ├── alunos.py
    │       ├── planos.py
    │       ├── matriculas.py
    │       ├── pagamentos.py
    │       └── relatorios.py
    ├── tests/
    │   ├── test_alunos.py
    │   ├── test_matriculas.py
    │   ├── test_pagamentos.py
    │   └── test_relatorios.py
    ├── seed.py
    ├── test_main.http
    ├── .env
    ├── .gitignore
    ├── requirements.txt
    └── README.md

---

## Banco de dados

Este projeto utiliza o banco de dados do repositório [Academia](https://github.com/ThiagoKleinn/Academia),
que contém o schema, seeds e dashboard Power BI.

> A tabela `usuarios` (usada para autenticação) deve ser criada com as colunas
> `username`, `password` (hash bcrypt) e `ativo` (boolean). A senha do usuário
> admin deve ser definida via `python seed.py`, e não inserida manualmente
> no schema SQL.