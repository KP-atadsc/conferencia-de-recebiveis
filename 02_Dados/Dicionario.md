# Como ler os dados

O arquivo `Pedidos/pedidos.csv` contém uma linha por pedido entregue. `Fila/fila.csv` preserva as mesmas colunas, apenas para casos que exigem revisão. CSVs em UTF-8, delimitados por vírgulas. O valor 18281 numa coluna monetária significa R$ 182,81. Uma célula monetária vazia indica ausência de evidência para o cálculo.

| Campo | Origem ou significado |
|---|---|
| pedido_id | Identificador anonimizado do pedido, comum às três fontes. |
| mes | Ano e mês de compra, extraídos de order_purchase_timestamp. |
| estado | Estado do pedido. O recorte usa delivered (entregue). |
| itens | Quantidade de linhas de itens. Cada linha tem sequência própria. |
| registros_pagamento | Quantidade de sequências de pagamento associadas ao pedido. |
| formas | Meios de pagamento distintos informados na fonte. credit_card = cartão de crédito, debit_card = débito, boleto = boleto, voucher = vale. |
| itens_centavos | Soma dos preços das linhas de itens. |
| frete_centavos | Soma dos fretes das linhas de itens. |
| esperado_centavos | Soma de itens e frete. Usada como referência comercial do pedido. |
| registrado_centavos | Soma dos valores das sequências de pagamento. Inclui vouchers. |
| delta_centavos | Registrado menos esperado. Valor positivo indica que o registrado excede o esperado. |
| abs_delta_centavos | Módulo da diferença. Permite ordenar a fila sem compensar diferenças positivas com negativas. |
| resultado | Exato, Até R$ 0,01, Revisar valor ou indicação de ausência de registros de origem. |
| acao | Próxima verificação sugerida ao analista. |

No arquivo mensal, soma_diferencas_absolutas_centavos tem o mesmo escopo do resultado da linha. Para reproduzir a diferença absoluta da fila, selecione Revisar valor. No controle de cobertura, estados fora do recorte são preservados para que o denominador possa ser auditado. O JSON de validação registra quantidades e somas conferidas diretamente nas origens.
