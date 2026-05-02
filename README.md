# Sistema de Pedidos — API REST

API REST para gerenciamento de pedidos, produtos e usuários. O sistema simula o fluxo de um restaurante: usuários criam pedidos, adicionam produtos a eles e administradores gerenciam o status dos pedidos.

## Tecnologias

- **Python 3.12**
- **Flask 2.3** — framework web
- **Flask-SQLAlchemy 3.1** — ORM para comunicação com o banco de dados
- **Flask-Login 0.6** — gerenciamento de sessão e autenticação
- **bcrypt 5.0** — criptografia de senhas
- **MySQL** — banco de dados principal (via `pymysql`)
- **Docker** — container do banco de dados MySQL

## Estrutura do projeto

```
.
├── app.py                  # Rotas e configuração da aplicação
├── database.py             # Instância do SQLAlchemy
├── OrderStatus.py          # Enum com os status de pedido
├── models/
│   └── Tables.py           # Modelos das tabelas (User, Product, Order, OrderItem)
├── utils/
│   └── ApiUtils.py         # Utilitário para padronização das respostas
├── docker-compose.yaml     # Configuração do container MySQL
├── .env.template           # Modelo de variáveis de ambiente
└── requirements.txt        # Dependências do projeto
```

## Configuração

### Variáveis de ambiente

O projeto usa um arquivo `.env` para configurar credenciais e conexões. Copie o template e preencha os valores:

```bash
cp .env.template .env
```

O arquivo `.env` **não é versionado** (está no `.gitignore`). Nunca o commite.

#### Variáveis do Docker

| Variável             | Descrição                                                         |
|----------------------|-------------------------------------------------------------------|
| `MYSQL_USER`         | Nome do usuário MySQL que a aplicação vai usar                    |
| `MYSQL_PASSWORD`     | Senha desse usuário                                               |
| `MYSQL_DATABASE`     | Nome do banco de dados a ser criado                               |
| `MYSQL_ROOT_PASSWORD`| Senha do usuário root do MySQL                                    |
| `VOLUME_PATH`        | Caminho absoluto local onde os dados do MySQL serão persistidos   |

#### Variáveis da aplicação

| Variável           | Descrição                                                                          |
|--------------------|------------------------------------------------------------------------------------|
| `SECRET_KEY`       | Chave secreta usada pelo Flask para assinar as sessões. Use um valor longo e aleatório em produção |
| `DATABASE_URL`     | URL de conexão com o banco principal. Formato: `mysql+pymysql://user:senha@host:porta/database` |
| `TEST_DATABASE_URL`| (Opcional) URL de conexão com um banco de testes. Exemplo: `sqlite:///database.db` |

**Exemplo de `.env` preenchido:**
```dotenv
# ======= CONFIGURAÇÕES DO DOCKER =======
MYSQL_USER=admin
MYSQL_PASSWORD=admin123
MYSQL_DATABASE=system-db
MYSQL_ROOT_PASSWORD=admin123
VOLUME_PATH=/caminho/local/para/persistir/dados

# ======= CONFIGURAÇÕES DA APP =======
SECRET_KEY=uma-chave-secreta-longa-e-aleatoria
DATABASE_URL=mysql+pymysql://admin:admin123@127.0.0.1:3306/system-db
TEST_DATABASE_URL=sqlite:///database.db
```
> Se você não quiser usar o banco de testes, basta não preencher a URL de conexão e mantê-lo comentado no arquivo `app.py`

## Como rodar

### 1. Suba o banco de dados com Docker

```bash
docker compose up -d
```

Isso inicia um container MySQL na porta `3306` com as credenciais definidas no `.env`.

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Crie as tabelas no banco

Digite `flask shell` no terminal e insira os comandos abaixo:

```python
db.create_all()
db.session.commit()
exit()
```

### 5. Inicie a aplicação

```bash
python3 app.py
```

A API estará disponível em `http://localhost:5000`.

> **Dica:** para testes locais sem Docker, defina `TEST_DATABASE_URL=sqlite:///database.db` no `.env` e descomente a linha correspondente em `app.py`:
> ```python
> app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URL")  # BANCO DE TESTES
> ```

## Autenticação

A API usa autenticação baseada em sessão via Flask-Login. É necessário fazer login antes de acessar as rotas protegidas.

Existem dois cargos:

| Cargo   | Permissões |
|---------|------------|
| `user`  | Gerencia apenas seus próprios dados e pedidos |
| `admin` | Acesso total ao sistema |

## Rotas

Todas as respostas seguem o padrão:

```json
{ "status": "OK" | "ERROR", "message": "..." }
```

### Autenticação

| Método | Rota      | Descrição                    | Auth |
|--------|-----------|------------------------------|------|
| POST   | /login    | Autentica o usuário          | Não  |
| GET    | /logout   | Encerra a sessão do usuário  | Não  |

**Exemplo — login:**
```json
POST /login
{
  "username": "clara",
  "password": "senha123"
}
```

---

### Usuários

| Método | Rota           | Descrição                                         | Auth  |
|--------|----------------|---------------------------------------------------|-------|
| POST   | /users         | Cria um novo usuário (cargo padrão: `user`)       | Não   |
| GET    | /users         | Lista usuários (`admin`: todos / `user`: próprio) | Sim   |
| GET    | /users/\<id\>  | Retorna um usuário pelo ID                        | Sim   |
| PATCH  | /users/\<id\>  | Atualiza dados do usuário                         | Sim   |
| DELETE | /users/\<id\>  | Remove o usuário                                  | Sim   |

**Exemplo — criar usuário:**
```json
POST /users
{
  "username": "clara",
  "password": "senha123"
}
```

---

### Produtos

| Método | Rota              | Descrição                        | Auth        |
|--------|-------------------|----------------------------------|-------------|
| POST   | /products         | Cadastra um novo produto         | Sim         |
| GET    | /products         | Lista todos os produtos          | Sim         |
| GET    | /products/\<id\>  | Retorna um produto pelo ID       | Sim         |
| PATCH  | /products/\<id\>  | Atualiza dados do produto        | Sim (admin) |
| DELETE | /products/\<id\>  | Remove o produto                 | Sim (admin) |

**Exemplo — cadastrar produto:**
```json
POST /products
{
  "name": "Hamburguer",
  "price": 29.90
}
```

---

### Pedidos

| Método | Rota                          | Descrição                                        | Auth        |
|--------|-------------------------------|--------------------------------------------------|-------------|
| POST   | /order                        | Cria um novo pedido (status inicial: `PENDENTE`) | Sim         |
| GET    | /order                        | Lista todos os pedidos                           | Sim (admin) |
| GET    | /order/\<id\>                 | Retorna um pedido pelo ID                        | Sim         |
| GET    | /order/user                   | Lista os pedidos do usuário autenticado          | Sim         |
| GET    | /order/\<id\>/order-items     | Lista os itens de um pedido específico           | Sim         |
| PATCH  | /order/\<action\>/\<id\>      | Atualiza o status do pedido (`pay` ou `cancel`)  | Sim (admin) |
| DELETE | /order/\<id\>                 | Remove o pedido                                  | Sim (admin) |

- **POST /order** — não requer body. O pedido é criado automaticamente vinculado ao usuário autenticado.
- **GET /order** — exclusivo para `admin`. Retorna todos os pedidos do sistema.
- **GET /order/\<id\>** — `admin` pode consultar qualquer pedido; `user` só pode consultar os seus.
- **GET /order/user** — atalho para listar apenas os pedidos do usuário autenticado.
- **GET /order/\<id\>/order-items** — retorna os itens de um pedido específico. `user` só pode consultar itens dos seus próprios pedidos.
- **PATCH /order/\<action\>/\<id\>** — altera o status do pedido. Só funciona em pedidos com status `PENDENTE`.
- **DELETE /order/\<id\>** — remove permanentemente o pedido e todos os seus itens (cascade).

**Exemplo — resposta de um pedido:**
```json
{
  "status": "OK",
  "message": "Pedido obtido com sucesso.",
  "order": {
    "id": 1,
    "status": "PENDENTE",
    "user_id": 2,
    "customer_name": "clara",
    "items": [
      {
        "id": 1,
        "quantity": 2,
        "order_id": 1,
        "product_id": 3,
        "product_name": "Hamburguer",
        "product_price": 29.90,
        "subtotal": 59.80
      }
    ],
    "total": 59.80
  }
}
```

**Exemplo — atualizar status:**
```
PATCH /order/pay/1    → marca o pedido 1 como PAGO
PATCH /order/cancel/1 → cancela o pedido 1
```

Status possíveis: `PENDENTE`, `PAGO`, `CANCELADO`.

---

### Itens do pedido

| Método | Rota                  | Descrição                              | Auth |
|--------|-----------------------|----------------------------------------|------|
| POST   | /order-item           | Adiciona um produto ao pedido em aberto | Sim  |
| PATCH  | /order-item/\<id\>    | Atualiza a quantidade de um item       | Sim  |
| DELETE | /order-item/\<id\>    | Remove um item do pedido               | Sim  |

**Exemplo — adicionar item:**
```json
POST /order-item
{
  "product_name": "Hamburguer",
  "quantity": 2
}
```

> O item é adicionado ao pedido com status `PENDENTE` do usuário autenticado.
