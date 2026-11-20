"""Conta quantos pedidos seriam revisados com a tolerância escolhida."""

import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("centavos", type=int, help="Maior diferença aceita, em centavos")
args = parser.parse_args()
if args.centavos < 0:
    parser.error("A tolerância deve ser zero ou positiva.")

pedidos = Path(__file__).resolve().parents[1] / "02_Dados/Pedidos/pedidos.csv"
sem_base = 0
acima = 0
with pedidos.open(encoding="utf-8", newline="") as arquivo:
    for pedido in csv.DictReader(arquivo):
        diferenca = pedido["delta_centavos"]
        if diferenca == "":
            sem_base += 1
        elif abs(int(diferenca)) > args.centavos:
            acima += 1

print(f"{acima + sem_base} pedidos na fila: {acima} acima do limite e {sem_base} sem base para comparar.")
