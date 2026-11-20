"""Gera a consulta offline dos pedidos em revisão e de um pedido de controle."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from extrair import SQL, arquivo_fonte, carregar


PASTA = Path(__file__).resolve().parent
DESTINO = PASTA.parent / "03_Power_BI" / "Auditoria_offline" / "Abrir_auditoria.html"
CONTROLE = "32e4fa9bb468884309b58b9348de70c3"


def selecionar(db):
    db.row_factory = sqlite3.Row
    pedidos = db.execute("""
        SELECT pedido_id, mes, resultado, esperado_centavos, registrado_centavos,
               delta_centavos, acao
        FROM conferencia
        WHERE pedido_id IN (SELECT pedido_id FROM fila) OR pedido_id = ?
        ORDER BY resultado = 'Exato', delta_centavos IS NOT NULL, abs_delta_centavos DESC, pedido_id
    """, (CONTROLE,))
    casos = []
    for pedido in pedidos:
        caso = dict(pedido)
        chave = (caso["pedido_id"],)
        caso["itens"] = [dict(r) for r in db.execute("""
            SELECT sequencia, preco, frete FROM itens WHERE pedido_id=? ORDER BY sequencia
        """, chave)]
        caso["pagamentos"] = [dict(r) for r in db.execute("""
            SELECT sequencia, forma, parcelas, valor FROM pagamentos
            WHERE pedido_id=? ORDER BY sequencia
        """, chave)]
        casos.append(caso)
    return casos


def main():
    comando = argparse.ArgumentParser(description=__doc__)
    comando.add_argument("--zip", type=Path, help="Cópia local do ZIP da Olist v2")
    comando.add_argument("--saida", type=Path, default=DESTINO, help="Caminho de saída do HTML")
    args = comando.parse_args()
    with closing(sqlite3.connect(":memory:")) as db:
        with arquivo_fonte(args.zip) as arquivo:
            carregar(db, arquivo)
        db.executescript((SQL / "conferencia.sql").read_text(encoding="utf-8"))
        casos = selecionar(db)
    dados = json.dumps(casos, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    modelo = (PASTA / "Modelos" / "auditoria.html").read_text(encoding="utf-8")
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(modelo.replace("{{DADOS}}", dados), encoding="utf-8")
    print(f"{len(casos)} pedidos com suas linhas de origem em {args.saida}")


if __name__ == "__main__":
    main()
