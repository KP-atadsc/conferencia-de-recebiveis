import csv
import json
import shutil
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

PAINEL = Path(__file__).resolve().parents[2] / "03_Power_BI"
sys.path.insert(0, str(PAINEL / "Atualizacao"))
from atualizar_modelo import write_model


class AtualizacaoModeloTest(unittest.TestCase):
    def setUp(self):
        temporaria = TemporaryDirectory()
        self.addCleanup(temporaria.cleanup)
        self.projeto = Path(temporaria.name)
        relativo = Path("Conferencia.SemanticModel/model.bim")
        self.modelo = self.projeto / relativo
        self.modelo.parent.mkdir()
        shutil.copyfile(PAINEL / "Projeto_editavel" / relativo, self.modelo)
        self.csv = self.projeto / "pedidos.csv"
        origem = PAINEL.parent / "02_Dados/Fila/fila.csv"
        with origem.open(encoding="utf-8", newline="") as arquivo:
            self.pedido = next(csv.DictReader(arquivo))

    def gravar_csv(self, linhas):
        with self.csv.open("w", encoding="utf-8", newline="") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=self.pedido.keys())
            writer.writeheader()
            writer.writerows(linhas)

    def test_duplicado_preserva_modelo_anterior(self):
        self.gravar_csv([self.pedido, self.pedido])
        anterior = self.modelo.read_bytes()
        with self.assertRaisesRegex(ValueError, "duplicado"):
            write_model(self.projeto, self.csv)
        self.assertEqual(self.modelo.read_bytes(), anterior)

    def test_atualizar_linhas_preserva_medida_personalizada(self):
        modelo = json.loads(self.modelo.read_text(encoding="utf-8"))
        mensal = next(t for t in modelo["model"]["tables"] if t["name"] == "Mensal")
        medida = {"name": "Medida personalizada", "expression": "1"}
        mensal["measures"].append(medida)
        self.modelo.write_text(json.dumps(modelo), encoding="utf-8")
        self.gravar_csv([self.pedido])
        self.assertEqual(write_model(self.projeto, self.csv), (1, 1))
        atualizado = json.loads(self.modelo.read_text(encoding="utf-8"))
        tabelas = {t["name"]: t for t in atualizado["model"]["tables"]}
        self.assertIn(medida, tabelas["Mensal"]["measures"])
        linhas = tabelas["Fila"]["partitions"][0]["source"]["expression"]
        self.assertEqual(sum(self.pedido["pedido_id"] in linha for linha in linhas), 1)
        self.assertEqual(sum(linha.lstrip().startswith("{") for linha in linhas), 1)
