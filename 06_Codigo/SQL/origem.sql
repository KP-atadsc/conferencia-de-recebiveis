PRAGMA foreign_keys = ON;
CREATE TABLE pedidos (
    pedido_id TEXT PRIMARY KEY NOT NULL,
    estado TEXT NOT NULL,
    compra TEXT NOT NULL
);
CREATE TABLE itens (
    pedido_id TEXT NOT NULL REFERENCES pedidos,
    sequencia INTEGER NOT NULL,
    preco INTEGER NOT NULL CHECK (preco >= 0),
    frete INTEGER NOT NULL CHECK (frete >= 0),
    PRIMARY KEY (pedido_id, sequencia)
);
CREATE TABLE pagamentos (
    pedido_id TEXT NOT NULL REFERENCES pedidos,
    sequencia INTEGER NOT NULL,
    forma TEXT NOT NULL,
    parcelas INTEGER NOT NULL,
    valor INTEGER NOT NULL CHECK (valor >= 0),
    PRIMARY KEY (pedido_id, sequencia)
);
