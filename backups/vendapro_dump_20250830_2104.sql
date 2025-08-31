PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
    );
INSERT INTO usuario VALUES(1,'Henry','9088');
CREATE TABLE cliente (
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
    );
CREATE TABLE funcionario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        data_nascimento TEXT,
        cargo TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    );
CREATE TABLE fornecedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        contato TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    );
CREATE TABLE produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        marca TEXT,
        codigo_barras TEXT,
        preco REAL,
        quantidade INTEGER DEFAULT 0,
        data_fabricacao TEXT,
        data_vencimento TEXT,
        fornecedor_id INTEGER,
        status TEXT DEFAULT 'ATIVO', -- produto ativo ou inativo
        observacao TEXT, -- para registrar se o produto está parado, pouco buscado etc
        FOREIGN KEY(user_id) REFERENCES usuario(id),
        FOREIGN KEY(fornecedor_id) REFERENCES fornecedor(id)
    );
CREATE TABLE estoque_movimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL, -- ENTRADA ou SAÍDA
        quantidade INTEGER NOT NULL,
        data_movimento TEXT NOT NULL,
        observacao TEXT,
        FOREIGN KEY(produto_id) REFERENCES produto(id)
    );
CREATE TABLE vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        cliente_id INTEGER,
        data TEXT,
        total REAL,
        FOREIGN KEY(user_id) REFERENCES usuario(id),
        FOREIGN KEY(cliente_id) REFERENCES cliente(id)
    );
CREATE TABLE delivery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        venda_id INTEGER,
        status TEXT DEFAULT 'pendente',
        data_entrega TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id),
        FOREIGN KEY(venda_id) REFERENCES vendas(id)
    );
CREATE TABLE caixa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        data TEXT,
        entrada REAL DEFAULT 0,
        saida REAL DEFAULT 0,
        saldo REAL,
        observacao TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    );
CREATE TABLE arquivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        caminho TEXT,
        tipo TEXT,
        FOREIGN KEY(user_id) REFERENCES usuario(id)
    );
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('usuario',1);
COMMIT;
