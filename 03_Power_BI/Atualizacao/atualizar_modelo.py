"""Atualiza as linhas incorporadas nas tabelas Mensal e Fila do projeto Power BI."""
import argparse
import csv
import json
import os
from collections import Counter
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile


ACEITOS = {"Exato", "Até R$ 0,01"}
CAMPOS_MENSAIS = [("Mês", "text"), ("Resultado", "text"), ("Quantidade", "Int64.Type")]
CAMPOS_FILA = [
    ("Ordem", "Int64.Type"), ("Pedido", "text"), ("Mês", "text"), ("Resultado", "text"),
    ("Itens", "Int64.Type"), ("Registros", "Int64.Type"), ("Esperado (R$)", "Currency.Type"),
    ("Registrado (R$)", "Currency.Type"), ("Diferença (R$)", "Currency.Type"),
    ("Módulo (R$)", "Currency.Type"), ("Ação", "text"),
]
VALORES = ("esperado_centavos", "registrado_centavos", "delta_centavos", "abs_delta_centavos")
COLUNAS_CSV = {"pedido_id", "mes", "resultado", "itens", "registros_pagamento", "acao", *VALORES}


def m_value(value):
    if value is None:
        return "null"
    if isinstance(value, str):
        texto = value.replace("#(", "#(#)(").replace('"', '""')
        texto = texto.replace("\r", "#(cr)").replace("\n", "#(lf)").replace("\t", "#(tab)")
        return '"' + texto + '"'
    return str(value)


def ler_pedidos(source):
    mensal, excecoes, ids = Counter(), [], set()
    with source.open(encoding="utf-8-sig", newline="") as handle:
        leitor = csv.DictReader(handle)
        faltantes = COLUNAS_CSV.difference(leitor.fieldnames or ())
        if faltantes:
            raise ValueError("Colunas ausentes no CSV: " + ", ".join(sorted(faltantes)))
        for row in leitor:
            pedido = (row["pedido_id"] or "").strip()
            if not pedido:
                raise ValueError(f"Linha {leitor.line_num}: pedido_id vazio.")
            if pedido in ids:
                raise ValueError(f"Linha {leitor.line_num}: pedido_id duplicado ({pedido}).")
            ids.add(pedido)
            row["pedido_id"] = pedido
            mensal[row["mes"], row["resultado"]] += 1
            if row["resultado"] not in ACEITOS:
                excecoes.append(row)
    excecoes.sort(key=lambda r: (r["abs_delta_centavos"] != "", -int(r["abs_delta_centavos"] or 0), r["pedido_id"]))
    resumo = [(mes, resultado, n) for (mes, resultado), n in sorted(mensal.items())]
    fila = [
        (ordem, r["pedido_id"], r["mes"], r["resultado"], int(r["itens"]), int(r["registros_pagamento"]),
         *[Decimal(int(r[c])) / 100 if r[c] != "" else None for c in VALORES], r["acao"])
        for ordem, r in enumerate(excecoes, 1)
    ]
    return len(ids), resumo, fila


def atualizar_linhas(modelo, nome, campos, dados):
    tabelas = modelo["model"]["tables"]
    tabela = next((t for t in tabelas if t["name"] == nome), None)
    particoes = tabela.get("partitions", []) if tabela else []
    particao = next((p for p in particoes if p["name"] == nome), {})
    fonte = particao.get("source", {})
    expressao = fonte.get("expression", [])
    linhas = expressao.splitlines() if isinstance(expressao, str) else list(expressao)
    tipos = ", ".join(f'#"{col}" = {tipo}' for col, tipo in campos)
    cabecalho = "Dados = #table(type table [" + tipos + "], {"
    inicio = next((i for i, linha in enumerate(linhas) if linha.strip() == cabecalho), None)
    if fonte.get("type") != "m" or inicio is None:
        raise ValueError(f"A tabela {nome} não contém a fonte incorporada esperada. Verifique o modelo.")
    fim = next((i for i in range(inicio + 1, len(linhas)) if linhas[i].strip() in {"})", "}),"}), None)
    if fim is None:
        raise ValueError(f"Bloco de dados incompleto na tabela {nome}.")
    linhas[inicio + 1:fim] = [
        "        {" + ", ".join(map(m_value, row)) + ("}," if i < len(dados) - 1 else "}")
        for i, row in enumerate(dados)
    ]
    fonte["expression"] = "\n".join(linhas) if isinstance(expressao, str) else linhas


def write_model(dest, source):
    total, resumo, fila = ler_pedidos(source)
    caminho = dest / "Conferencia.SemanticModel/model.bim"
    modelo = json.loads(caminho.read_text(encoding="utf-8-sig"))
    atualizar_linhas(modelo, "Mensal", CAMPOS_MENSAIS, resumo)
    atualizar_linhas(modelo, "Fila", CAMPOS_FILA, fila)

    # Só substitui o modelo depois de validar as duas partições e fechar o arquivo.
    with NamedTemporaryFile(dir=caminho.parent, delete=False) as arquivo:
        temporario = Path(arquivo.name)
    try:
        with temporario.open("w", encoding="utf-8", newline="\n") as arquivo:
            json.dump(modelo, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        os.replace(temporario, caminho)
    finally:
        temporario.unlink(missing_ok=True)
    return total, len(fila)


if __name__ == "__main__":
    painel = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=painel.parent / "02_Dados/Pedidos/pedidos.csv")
    parser.add_argument("--projeto", type=Path, default=painel / "Projeto_editavel")
    args = parser.parse_args()
    if not (args.projeto / "Conferencia.pbip").is_file():
        parser.error("A pasta do projeto deve conter Conferencia.pbip.")
    try:
        total, fila = write_model(args.projeto, args.csv)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Não foi possível atualizar o modelo: {erro}\n")
    print(f"Base incorporada atualizada. Pedidos: {total}. Na fila: {fila}.")
