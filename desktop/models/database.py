import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vendapro.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cliente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        data_nascimento TEXT
    )
    """)

    # Funcionários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        data_nascimento TEXT,
        cargo TEXT
    )
    """)

    # Fornecedores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fornecedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        contato TEXT
    )
    """)

    # Produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL,
        fornecedor_id INTEGER,
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedor(id)
    )
    """)

    # Estoque
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        FOREIGN KEY (produto_id) REFERENCES produto(id)
    )
    """)

    # Vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        data TEXT,
        total REAL,
        FOREIGN KEY (cliente_id) REFERENCES cliente(id)
    )
    """)

    # Delivery
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS delivery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER,
        status TEXT DEFAULT 'pendente',
        data_entrega TEXT,
        FOREIGN KEY (venda_id) REFERENCES vendas(id)
    )
    """)

    # Caixa (controle financeiro)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS caixa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        entrada REAL DEFAULT 0,
        saida REAL DEFAULT 0,
        saldo REAL
    )
    """)

    # Arquivos/Pastas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS arquivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        caminho TEXT,
        tipo TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados criado com sucesso!")
