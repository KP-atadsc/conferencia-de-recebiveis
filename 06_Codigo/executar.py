"""Reproduz a conferência, gera os CSVs e verifica cada lado contra a origem."""

import argparse
import csv
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from extrair import HASHES, SQL, URL, arquivo_fonte, carregar


PASTA_DADOS = Path(__file__).resolve().parents[1] / "02_Dados"
CONSULTAS = {
    "Pedidos/pedidos.csv": "SELECT * FROM conferencia ORDER BY pedido_id",
    "Fila/fila.csv": "SELECT * FROM fila",
    "Controle/mensal.csv": """
        SELECT mes, resultado, COUNT(*) AS pedidos,
               SUM(abs_delta_centavos) AS soma_diferencas_absolutas_centavos
        FROM conferencia GROUP BY mes, resultado ORDER BY mes, resultado
    """,
    "Controle/cobertura.csv": """
        SELECT estado, COUNT(*) AS pedidos,
               CASE WHEN estado = 'delivered' THEN 'Incluído' ELSE 'Fora do recorte' END AS escopo
        FROM pedidos GROUP BY estado ORDER BY pedidos DESC, estado
    """,
}
ARQUIVOS = (*CONSULTAS, "Controle/validacao.json")


def verificar(db):
    # Consultas independentes sobre cada fonte, sem usar as CTEs da conferência.
    esperado = db.execute("""
        SELECT COUNT(*), SUM(i.preco), SUM(i.frete)
        FROM itens i JOIN pedidos p USING (pedido_id) WHERE p.estado = 'delivered'
    """).fetchone()
    registrado = db.execute("""
        SELECT COUNT(*), SUM(g.valor)
        FROM pagamentos g JOIN pedidos p USING (pedido_id) WHERE p.estado = 'delivered'
    """).fetchone()
    controle = db.execute("""
        SELECT COALESCE(SUM(itens), 0), SUM(itens_centavos), SUM(frete_centavos),
               COALESCE(SUM(registros_pagamento), 0), SUM(registrado_centavos)
        FROM conferencia
    """).fetchone()
    if controle != esperado + registrado:
        raise ValueError("Total ou quantidade de linhas diverge da origem.")
    entregues = db.execute("SELECT COUNT(*) FROM pedidos WHERE estado='delivered'").fetchone()[0]
    if db.execute("SELECT COUNT(*) FROM conferencia").fetchone()[0] != entregues:
        raise ValueError("População de entregues incompleta.")
    return {
        "fonte": URL, "sha256_arquivos_origem": HASHES,
        "linhas_origem": {nome: db.execute(f"SELECT COUNT(*) FROM {nome}").fetchone()[0]
                         for nome in ("pedidos", "itens", "pagamentos")},
        "pedidos_entregues": entregues,
        "linhas_itens_entregues": esperado[0], "preco_centavos_entregues": esperado[1],
        "frete_centavos_entregues": esperado[2], "linhas_pagamentos_entregues": registrado[0],
        "valor_registrado_centavos_entregues": registrado[1],
        "resultados": dict(db.execute("SELECT resultado, COUNT(*) FROM conferencia GROUP BY resultado")),
        "pedidos_na_fila": db.execute("SELECT COUNT(*) FROM fila").fetchone()[0],
        "fila_diferenca_absoluta_centavos": db.execute("SELECT SUM(abs_delta_centavos) FROM fila").fetchone()[0],
    }


def restaurar(pasta, base, diario):
    for nome in ARQUIVOS:
        anterior = diario.execute("SELECT dados FROM anteriores WHERE nome = ?", (nome,)).fetchone()
        if anterior is None:
            continue
        destino = pasta / nome
        dados = anterior[0]
        if dados is None:
            destino.unlink(missing_ok=True)
        elif not destino.exists() or destino.read_bytes() != dados:
            copia = base / "restauracao.tmp"
            copia.write_bytes(dados)
            os.replace(copia, destino)
    with diario:
        diario.execute("DELETE FROM anteriores")


def publicar(pasta, base):
    # Um único publicador por pasta. O diário sobrevive a interrupções do processo.
    with closing(sqlite3.connect(pasta / ".publicacao.sqlite3", timeout=30)) as diario:
        diario.execute("PRAGMA locking_mode = EXCLUSIVE")
        diario.execute("PRAGMA auto_vacuum = FULL")
        diario.execute("BEGIN EXCLUSIVE")
        diario.execute("CREATE TABLE IF NOT EXISTS anteriores (nome TEXT PRIMARY KEY, dados BLOB)")
        diario.commit()
        restaurar(pasta, base, diario)
        alterados = []
        with diario:
            for nome in ARQUIVOS:
                destino = pasta / nome
                destino.parent.mkdir(parents=True, exist_ok=True)
                anterior = destino.read_bytes() if destino.exists() else None
                if anterior != (base / nome).read_bytes():
                    diario.execute("INSERT INTO anteriores VALUES (?, ?)", (nome, anterior))
                    alterados.append(nome)
        try:
            for nome in alterados:
                os.replace(base / nome, pasta / nome)
            with diario:
                diario.execute("DELETE FROM anteriores")
        except BaseException:
            restaurar(pasta, base, diario)
            raise


def exportar(db, pasta, controle):
    pasta.mkdir(parents=True, exist_ok=True)
    # Só publica os arquivos depois de terminar e conferir a extração.
    with TemporaryDirectory(dir=pasta) as temporaria:
        base = Path(temporaria)
        for nome, consulta in CONSULTAS.items():
            destino = base / nome
            destino.parent.mkdir(parents=True, exist_ok=True)
            cursor = db.execute(consulta)
            with destino.open("w", encoding="utf-8", newline="") as arq:
                escritor = csv.writer(arq, lineterminator="\n")
                escritor.writerow([coluna[0] for coluna in cursor.description])
                escritor.writerows(cursor)
        (base / "Controle/validacao.json").write_text(
            json.dumps(controle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        publicar(pasta, base)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, help="Usa cópia local do ZIP da Olist v2")
    parser.add_argument("--saida", type=Path, default=PASTA_DADOS, help="Pasta dos CSVs e do controle")
    parser.add_argument("--pedido", help="Mostra as linhas de origem de um pedido após a execução")
    args = parser.parse_args()
    with closing(sqlite3.connect(":memory:")) as db:
        with arquivo_fonte(args.zip) as arquivo:
            carregar(db, arquivo)
        db.executescript((SQL / "conferencia.sql").read_text(encoding="utf-8"))
        controle = verificar(db)
        exportar(db, args.saida, controle)
        print(f"{controle['pedidos_entregues']} entregues; {controle['pedidos_na_fila']} pedidos na fila.")
        if args.pedido:
            for tabela in ("pedidos", "itens", "pagamentos", "conferencia"):
                consulta = db.execute(f"SELECT * FROM {tabela} WHERE pedido_id = ?", (args.pedido,))
                print(tabela, [col[0] for col in consulta.description], *consulta.fetchall(), sep="\n")


if __name__ == "__main__":
    main()
