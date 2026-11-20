import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from executar import verificar
from extrair import SQL, centavos


class ConferenciaTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript((SQL / "origem.sql").read_text(encoding="utf-8"))

    def pedido(self, chave, itens, pagamentos, estado="delivered"):
        self.db.execute("INSERT INTO pedidos VALUES (?, ?, ?)", (chave, estado, "2018-01-10"))
        self.db.executemany("INSERT INTO itens VALUES (?, ?, ?, ?)", [
            (chave, pos, preco, frete) for pos, (preco, frete) in enumerate(itens, 1)
        ])
        self.db.executemany("INSERT INTO pagamentos VALUES (?, ?, ?, ?, ?)", [
            (chave, pos, forma, parcelas, valor)
            for pos, (forma, parcelas, valor) in enumerate(pagamentos, 1)
        ])

    def calcular(self):
        self.db.executescript((SQL / "conferencia.sql").read_text(encoding="utf-8"))
        return verificar(self.db)

    def test_dois_itens_duas_formas_e_parcelamento(self):
        self.pedido("dois", [(5900, 1307)] * 2, [("cartao", 4, 12414), ("voucher", 1, 2000)])
        self.calcular()
        self.assertEqual(self.db.execute("""
            SELECT itens, registros_pagamento, esperado_centavos, registrado_centavos, resultado
            FROM conferencia
        """).fetchone(), (2, 2, 14414, 14414, "Exato"))

    def test_ausencia_tolerancia_sinal_e_recorte(self):
        for chave, delta in (("mais_um", 1), ("menos_um", -1), ("mais_dois", 2), ("menos_tres", -3)):
            self.pedido(chave, [(100, 0)], [("a", 1, 100 + delta)])
        self.pedido("sem_itens", [], [("a", 1, 100)])
        self.pedido("sem_pagamento", [(100, 0)], [])
        self.pedido("sem_ambos", [], [])
        self.pedido("cancelado", [], [], "canceled")
        resumo = self.calcular()
        self.assertEqual(resumo["pedidos_entregues"], 7)
        self.assertEqual(resumo["pedidos_na_fila"], 5)
        self.assertEqual(resumo["fila_diferenca_absoluta_centavos"], 5)
        fila = self.db.execute("SELECT pedido_id, delta_centavos FROM fila").fetchall()
        self.assertEqual(fila, [("sem_ambos", None), ("sem_itens", None), ("sem_pagamento", None),
                               ("menos_tres", -3), ("mais_dois", 2)])
        self.assertEqual(resumo["resultados"]["Até R$ 0,01"], 2)

    def test_chave_duplicada_ou_orfa(self):
        self.pedido("duplicado", [(100, 0)], [])
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO itens VALUES ('duplicado', 1, 100, 0)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO pagamentos VALUES ('ausente', 1, 'a', 1, 100)")

    def test_conversao_monetaria(self):
        self.assertEqual(centavos("59.90"), 5990)
        with self.assertRaises(ValueError):
            centavos("0.001")


if __name__ == "__main__":
    unittest.main()
