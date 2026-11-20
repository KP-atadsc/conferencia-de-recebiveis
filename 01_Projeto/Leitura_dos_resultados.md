# O que entra na fila de revisão

**No histórico da Olist, 300 de 96.478 pedidos entregues exigem uma segunda conferência sob a regra de um centavo (0,31%).** A primeira providência depende do motivo. Um pedido exige checar a completude dos pagamentos. Em 299 pedidos com registros dos dois lados, é possível ordenar o trabalho pelo tamanho da diferença.

| Resultado | Pedidos | Decisão sugerida |
|---|---:|---|
| Valores idênticos | 95.908 | Manter amostragem de controle. |
| Diferença de um centavo | 270 | Monitorar separadamente e validar a tolerância com o dono do processo. |
| Diferença acima de um centavo | 299 | Investigar composição e regras comerciais, por ordem de valor absoluto. |
| Registro de pagamento ausente | 1 | Conferir extração e referência do pedido. O valor esperado é R$ 143,46. |

**De onde vêm os 96.478?** A extração leu 99.441 pedidos, 112.650 linhas de itens e 103.886 registros de pagamento. Dos pedidos, 2.963 estavam em outros estados. Entre os entregues, o programa preservou as 110.197 linhas de itens e os 100.756 registros de pagamento na agregação. [Controle de cobertura](../02_Dados/Controle/cobertura.csv) · [Conferência com a origem](../02_Dados/Controle/validacao.json)

## Quanto muda quando a regra muda?

| Tolerância inclusiva por pedido | Casos na fila | Interpretação |
|---|---:|---|
| R$ 0,00 | 570 | Inclui os 270 casos com diferença de um centavo. |
| R$ 0,01 | 300 | Critério escolhido para a demonstração. |
| R$ 0,05 | 257 | Outros 43 casos sairiam da revisão individual. |

A lacuna de pagamento permanece nos três cenários. A diferença absoluta de um centavo nos 270 pedidos soma R$ 2,70. Uma tolerância aceita requer decisão do responsável, registro da regra aplicada e monitoramento de acúmulos.

## Qual caso abrir primeiro?

Para o analista de dados, o caso sem registro de pagamento tem prioridade de integridade. Para o analista financeiro que investiga diferenças comparáveis, a maior está no pedido **ce6d150fb29ada17d2082f4847107665**. Um item de R$ 1.299,00 tem frete de R$ 104,66. O esperado é R$ 1.403,66. O cartão registra R$ 1.586,47 em dez parcelas. A diferença é **+R$ 182,81**. Para descobrir a causa, seria preciso consultar os termos da venda e a discriminação do recebimento.

Nos 299 casos, 260 têm diferença positiva e 39 têm diferença negativa. Os módulos somam R$ 3.230,30. Os dez maiores explicam R$ 803,23 desse montante (24,9%). Esse é um critério de ordem para conferência. A falta de extrato impede estimar perda e recuperação de caixa. [Fila por prioridade](../02_Dados/Fila/fila.csv)

## A armadilha do cruzamento

No pedido **32e4fa9bb468884309b58b9348de70c3** há dois itens. Cada um custa R$ 59,00 e tem frete de R$ 13,07. O pagamento combina cartão de R$ 124,14 e voucher de R$ 20,00. Cada lado soma **R$ 144,14**.

Unir os dois itens aos dois pagamentos diretamente gera quatro combinações. As duas somas apareceriam como R$ 288,28 e a diferença continuaria zero. Por isso a consulta agrupa cada origem por pedido antes do cruzamento e valida os totais monetários de cada lado separadamente. [SQL da conferência](../06_Codigo/SQL/conferencia.sql)
