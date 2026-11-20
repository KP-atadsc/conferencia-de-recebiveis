"""Carrega três tabelas da versão pública da Olist. Requer apenas Python 3.10+."""

import csv
import hashlib
import io
import sqlite3
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
from zipfile import ZipFile


SQL = Path(__file__).resolve().parent / "SQL"
URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce?datasetVersionNumber=2"
HASHES = {
    "olist_orders_dataset.csv": "8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf",
    "olist_order_items_dataset.csv": "0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279",
    "olist_order_payments_dataset.csv": "4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0",
}


def centavos(texto):
    valor = Decimal(texto) * 100
    if not valor.is_finite() or valor != valor.to_integral_value():
        raise ValueError(f"Valor monetário inválido: {texto!r}")
    return int(valor)


@contextmanager
def arquivo_fonte(local=None):
    if local:
        with ZipFile(local) as arquivo:
            yield arquivo
        return
    with TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "olist-v2.zip"
        requisicao = Request(URL, headers={"User-Agent": "conferencia-recebiveis/1.0"})
        with urlopen(requisicao, timeout=120) as resposta, caminho.open("wb") as saida:
            while bloco := resposta.read(1024 * 1024):
                saida.write(bloco)
        with ZipFile(caminho) as arquivo:
            yield arquivo


def linhas(arquivo, nome):
    conteudo = arquivo.read(nome)
    if hashlib.sha256(conteudo).hexdigest() != HASHES[nome]:
        raise ValueError(f"O conteúdo de {nome} diverge da versão 2 conferida.")
    with io.TextIOWrapper(io.BytesIO(conteudo), encoding="utf-8-sig", newline="") as texto:
        yield from csv.DictReader(texto)


def carregar(db: sqlite3.Connection, arquivo: ZipFile):
    db.executescript((SQL / "origem.sql").read_text(encoding="utf-8"))
    with db:
        db.executemany("INSERT INTO pedidos VALUES (?, ?, ?)", (
            (r["order_id"], r["order_status"], r["order_purchase_timestamp"])
            for r in linhas(arquivo, "olist_orders_dataset.csv")
        ))
        db.executemany("INSERT INTO itens VALUES (?, ?, ?, ?)", (
            (r["order_id"], int(r["order_item_id"]), centavos(r["price"]), centavos(r["freight_value"]))
            for r in linhas(arquivo, "olist_order_items_dataset.csv")
        ))
        db.executemany("INSERT INTO pagamentos VALUES (?, ?, ?, ?, ?)", (
            (r["order_id"], int(r["payment_sequential"]), r["payment_type"],
             int(r["payment_installments"]), centavos(r["payment_value"]))
            for r in linhas(arquivo, "olist_order_payments_dataset.csv")
        ))
