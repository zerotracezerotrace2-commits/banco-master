import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DB = "banco.db"

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()

# =========================
# TABELAS
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    agency TEXT NOT NULL,
    account_number TEXT UNIQUE NOT NULL,
    balance_cents INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(client_id) REFERENCES clients(id)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    account_id INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES accounts(id)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS pix_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE NOT NULL,
    sender_account_id INTEGER NOT NULL,
    receiver_account_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(sender_account_id) REFERENCES accounts(id),
    FOREIGN KEY(receiver_account_id) REFERENCES accounts(id)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# =========================
# CLIENTES E CONTAS
# =========================

nomes = ['João da Silva', 'Maria Oliveira', 'Carlos Santos', 'Ana Souza', 'Lucas Pereira', 'Juliana Costa', 'Rafael Almeida', 'Camila Rodrigues', 'Gabriel Ferreira', 'Larissa Martins', 'Bruno Gomes', 'Mariana Barbosa', 'Felipe Ribeiro', 'Beatriz Carvalho', 'Diego Lima', 'Fernanda Alves', 'Mateus Rocha', 'Patrícia Mendes', 'Gustavo Nunes', 'Isabela Castro', 'Eduardo Moreira', 'Carolina Dias', 'Thiago Teixeira', 'Renata Correia', 'Leonardo Cardoso', 'Bianca Araújo', 'Rodrigo Freitas', 'Vanessa Monteiro', 'Daniel Vieira', 'Letícia Ramos', 'André Moura', 'Priscila Campos', 'Marcelo Batista', 'Natália Pinto', 'Vinícius Farias', 'Débora Cunha', 'Henrique Duarte', 'Gabriela Moraes', 'Felipe Tavares', 'Manuela Reis', 'Alexandre Neves', 'Luana Borges', 'Ricardo Mendes', 'Jéssica Andrade', 'Pedro Henrique', 'Amanda Fernandes', 'Samuel Martins', 'Cláudia Lopes', 'Caio Barbosa', 'Elaine Teixeira']

for i in range(1, 51):

    name = nomes[i - 1]
    cpf = f"000000000{i:02d}"
    email = f"cliente{i:02d}@bancomaster.local"
    phone = f"2199999{i:04d}"
    account_number = f"{100000 + i}"
    balance = 200000

    c.execute(
        """
        INSERT INTO clients
        (id, name, cpf, email, phone)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            cpf = excluded.cpf,
            email = excluded.email,
            phone = excluded.phone
        """,
        (i, name, cpf, email, phone)
    )

    c.execute(
        """
        INSERT OR IGNORE INTO accounts
        (id, client_id, agency, account_number, balance_cents)
        VALUES (?, ?, ?, ?, ?)
        """,
        (i, i, "0001", account_number, balance)
    )

# =========================
# CONTA ADMIN
# =========================

c.execute(
    """
    INSERT OR IGNORE INTO accounts
    (id, client_id, agency, account_number, balance_cents)
    VALUES (?, NULL, ?, ?, ?)
    """,
    (51, "0001", "000001", 0)
)

# =========================
# USUÁRIOS
# =========================

for i in range(1, 51):

    username = f"cliente{i:02d}"
    senha = f"Master@{i:02d}"

    c.execute(
        """
        INSERT OR IGNORE INTO users
        (username, password_hash, account_id)
        VALUES (?, ?, ?)
        """,
        (
            username,
            generate_password_hash(senha),
            i
        )
    )

# ADMIN
c.execute(
    """
    INSERT OR IGNORE INTO users
    (username, password_hash, account_id)
    VALUES (?, ?, ?)
    """,
    (
        "admin",
        generate_password_hash("Master@2026"),
        51
    )
)

conn.commit()

# =========================
# VERIFICAÇÃO
# =========================

clientes = c.execute(
    "SELECT COUNT(*) FROM clients"
).fetchone()[0]

contas = c.execute(
    "SELECT COUNT(*) FROM accounts"
).fetchone()[0]

usuarios = c.execute(
    "SELECT COUNT(*) FROM users"
).fetchone()[0]

conn.close()

print("================================")
print(" BANCO MASTER INICIALIZADO")
print("================================")
print(f"Clientes : {clientes}")
print(f"Contas   : {contas}")
print(f"Usuários : {usuarios}")
print("================================")
