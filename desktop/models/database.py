import sqlite3
from pathlib import Path

# Caminho do banco
DB_PATH = Path(__file__).parent / "vendapro.db"

def get_connection():
    """Retorna conexão com row_factory para acessar colunas por nome."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria todas as tabelas do sistema se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    # Usuários do sistema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
    )
    """)

    # Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        cpf TEXT,
        endereco TEXT,
        data_nascimento TEXT,
        data_prospeccao TEXT,
        status TEXT DEFAULT 'ATIVO',
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    )
    """)

    # Funcionários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        data_nascimento TEXT,
        cargo TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    )
    """)

    # Fornecedores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fornecedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        contato TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    )
    """)

    # Produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        marca TEXT,
        codigo_barras TEXT,
        preco REAL,
        data_fabricacao TEXT,
        data_vencimento TEXT,
        fornecedor_id INTEGER,
        status TEXT DEFAULT 'ATIVO', -- produto ativo ou inativo
        observacao TEXT, -- para registrar se o produto está parado, pouco buscado etc
        FOREIGN KEY(user_id) REFERENCES usuario(id),
        FOREIGN KEY(fornecedor_id) REFERENCES fornecedor(id)
    )
    """)

    # Estoque
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_movimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL, -- ENTRADA ou SAÍDA
        quantidade INTEGER NOT NULL,
        data_movimento TEXT NOT NULL,
        observacao TEXT,
        FOREIGN KEY(produto_id) REFERENCES produto(id)
    )
    """)

    # Vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        cliente_id INTEGER,
        data TEXT,
        total REAL,
        FOREIGN KEY(user_id) REFERENCES usuario(id),
        FOREIGN KEY(cliente_id) REFERENCES cliente(id)
    )
    """)

    # Delivery
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS delivery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        venda_id INTEGER,
        status TEXT DEFAULT 'pendente',
        data_entrega TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id),
        FOREIGN KEY(venda_id) REFERENCES vendas(id)
    )
    """)

    # Caixa (controle financeiro)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS caixa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        data TEXT,
        entrada REAL DEFAULT 0,
        saida REAL DEFAULT 0,
        saldo REAL,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    )
    """)

    # Arquivos/Pastas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS arquivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        caminho TEXT,
        tipo TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_db()
