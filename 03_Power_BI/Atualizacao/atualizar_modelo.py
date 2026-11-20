"""Generate the offline snapshot from the analytical CSV without storing a personal path."""
import csv
import json
from collections import Counter
from pathlib import Path
from decimal import Decimal

def save(path, document, schema):
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_url = "https://developer.microsoft.com/json-schemas/fabric/" + schema + "/schema.json"
    path.write_text(json.dumps({"$schema": schema_url, **document}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



ACEITOS = {"Exato", "Até R$ 0,01"}
BRL = '"R$" #,##0.00;-"R$" #,##0.00;"R$" 0.00'


def m_value(value):
    if value is None:
        return "null"
    if isinstance(value, str):
        return '"' + value.replace('"', '""').replace("\n", "#(lf)") + '"'
    return str(value)


def table(name, fields, data, measures):
    tabular_types = {"text": "string", "Int64.Type": "int64", "Currency.Type": "decimal"}
    columns = []
    for col, dtype in fields:
        spec = {"name": col, "dataType": tabular_types[dtype], "sourceColumn": col, "summarizeBy": "none"}
        if dtype == "Currency.Type":
            spec["formatString"] = BRL
        columns.append(spec)
    row_type = ", ".join('#"' + col + '" = ' + dtype for col, dtype in fields)
    expression = ["let", "    Dados = #table(type table [" + row_type + "], {"]
    # A short, auditable Power Query source. Currency stays in fixed-decimal types.
    for i, row in enumerate(data):
        suffix = "," if i + 1 < len(data) else ""
        expression.append("        {" + ", ".join(map(m_value, row)) + "}" + suffix)
    expression += ["    })", "in", "    Dados"]
    return {"name": name, "columns": columns,
            "partitions": [{"name": name, "mode": "import", "source": {"type": "m", "expression": expression}}],
            "measures": [{"name": label, "expression": dax, "formatString": fmt} for label, dax, fmt in measures]}


def as_brl(cents):
    return Decimal(cents) / 100 if cents != "" else None


def write_model(dest, source):
    monthly, exceptions = Counter(), []
    with source.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            monthly[row["mes"], row["resultado"]] += 1
            if row["resultado"] not in ACEITOS:
                exceptions.append(row)
    exceptions.sort(key=lambda r: (r["abs_delta_centavos"] != "", -int(r["abs_delta_centavos"] or 0), r["pedido_id"]))
    summary = table("Mensal", [("Mês", "text"), ("Resultado", "text"), ("Quantidade", "Int64.Type")],
                    [(month, result, n) for (month, result), n in sorted(monthly.items())],
                    [("Pedidos entregues", "SUM('Mensal'[Quantidade])", "#,##0"),
                     ("Pedidos aceitos", 'CALCULATE([Pedidos entregues], KEEPFILTERS(\'Mensal\'[Resultado] IN {"Exato", "Até R$ 0,01"}))', "#,##0"),
                     ("Dentro da tolerância", "DIVIDE([Pedidos aceitos], [Pedidos entregues])", "0.00%"),
                     ("Casos na fila", 'CALCULATE([Pedidos entregues], KEEPFILTERS(NOT (\'Mensal\'[Resultado] IN {"Exato", "Até R$ 0,01"})))', "#,##0"),
                     ("Pedidos para revisão", "COALESCE([Casos na fila], 0)", "#,##0")])
    cols = [("Ordem", "Int64.Type"), ("Pedido", "text"), ("Mês", "text"), ("Resultado", "text"), ("Itens", "Int64.Type"),
            ("Registros", "Int64.Type"), ("Esperado (R$)", "Currency.Type"), ("Registrado (R$)", "Currency.Type"),
            ("Diferença (R$)", "Currency.Type"), ("Módulo (R$)", "Currency.Type"), ("Ação", "text")]
    data = [(i, r["pedido_id"], r["mes"], r["resultado"], int(r["itens"]), int(r["registros_pagamento"]),
             *[as_brl(r[c]) for c in ["esperado_centavos", "registrado_centavos", "delta_centavos", "abs_delta_centavos"]],
             r["acao"]) for i, r in enumerate(exceptions, 1)]
    detail = table("Fila", cols, data,
                   [("Casos selecionados", "COALESCE(COUNTROWS('Fila'), 0)", "#,##0"),
                    ("Diferença absoluta", "SUM('Fila'[Módulo (R$)])", BRL)])
    folder = dest / "Conferencia.SemanticModel"
    save(folder / "definition.pbism", {"version": "1.0", "settings": {}}, "item/semanticModel/definitionProperties/1.0.0")
    model = {"name": "Conferencia", "compatibilityLevel": 1601, "model": {"culture": "pt-BR", "sourceQueryCulture": "pt-BR",
              "defaultPowerBIDataSourceVersion": "powerBI_V3", "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
              "tables": [summary, detail], "annotations": [{"name": "PBI_QueryOrder", "value": '["Mensal","Fila"]'},
                                                           {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"}]}}
    (folder / "model.bim").write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sum(monthly.values()), len(exceptions)


if __name__ == "__main__":
    import argparse
    painel = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Atualiza a base incorporada ao Power BI com o CSV gerado pelo pipeline.")
    parser.add_argument("--csv", type=Path, default=painel.parent / "02_Dados/Pedidos/pedidos.csv")
    parser.add_argument("--projeto", type=Path, default=painel / "Projeto_editavel")
    args = parser.parse_args()
    if not (args.projeto / "Conferencia.pbip").is_file():
        parser.error("A pasta do projeto deve conter Conferencia.pbip.")
    total, fila = write_model(args.projeto, args.csv)
    print(f"Base incorporada atualizada. Pedidos: {total}. Na fila: {fila}.")
