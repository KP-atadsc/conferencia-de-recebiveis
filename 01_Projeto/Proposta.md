# Conferência de recebíveis

**Pergunta do supervisor** — Com uma manhã disponível para conferir registros, quais pedidos merecem a primeira investigação e que evidência justifica a escolha?

A Ambev descreve na área de Order to Cash do CSC de Jaguariúna a conciliação de pagamentos dos clientes para a baixa de notas e o apoio ao fechamento. Este portfólio usa essa responsabilidade como ponto de partida. A base é o comércio eletrônico da Olist. O vínculo entre seus itens e pagamentos permite ensaiar o controle anterior à decisão de baixa. A ocorrência e a dimensão de qualquer problema no CSC precisariam de diagnóstico com a equipe. [Descrição da posição na Ambev](https://ambev.gupy.io/jobs/12773411)

## A decisão do dia

O analista confere, por pedido entregue, se a soma dos preços e fretes coincide com o valor dos pagamentos registrados. O supervisor separa a falta de evidência das diferenças mensuráveis. O primeiro grupo segue para checagem de completude da extração. No segundo, o analista começa pelas maiores diferenças absolutas, revisa a composição dos dois lados e documenta a origem. A regra gera uma fila de investigação. Uma baixa em produção exigiria confirmação de liquidação, vínculo com o título e aprovação do responsável.

## Escopo e escolhas

- Unidade de análise: um pedido. Uma compra pode reunir vários itens e várias formas de pagamento.
- População: pedidos com estado final `delivered` na versão 2 da base. O corte reduz situações de cancelamento ou indisponibilidade que têm regras próprias. A competência exibida corresponde ao mês de compra.
- Esperado: soma de preço e frete de cada linha. Registrado: soma dos valores de pagamento, inclusive vouchers. Parcelas descrevem a condição de pagamento.
- Diferença: registrado menos esperado, em centavos inteiros. A ausência de um lado deixa a diferença em branco.
- Tolerância demonstrativa: um centavo por pedido com os dois lados presentes. O painel preserva os casos de um centavo como grupo separado. O gestor de processo precisaria aprovar a regra e avaliar o acúmulo por cliente ou título antes de um piloto.
- Evidência: valor registrado no conjunto da Olist. A investigação de uma diferença pode exigir extrato, tarifas, descontos, estornos e contratos, dados ausentes neste recorte.

## Como testar no CSC

Proposta de piloto de duas semanas, em modo de leitura, com uma carteira escolhida pelo supervisor. Na primeira semana, alinhar grão (empresa, cliente, título, parcela e recebimento), data de corte, tolerância e regras de alocação. Extrair uma amostra histórica autorizada, incluir estornos e pagamentos parciais, fechar totais contra os controles de origem e medir o tempo de revisão atual.

Na segunda semana, analista e responsável pelo processo revisam a fila e uma amostra aleatória dos casos que passaram na regra. Registrar causa confirmada, tempo por caso, falsos alertas e diferenças que a regra deixou passar. Comparar tempo por 100 títulos em grupos de complexidade semelhante. Avaliar a qualidade por amostragem antes de definir uma meta com o time. Qualquer baixa continua no fluxo aprovado da empresa.

O entregável do piloto é a decisão documentada de manter, recalibrar ou encerrar a regra. Um caso relevante classificado como conferido exige investigar a falha, corrigir a regra e repetir a validação. A demonstração pública não estima economia, prazo de fechamento ou taxa de erro da Ambev.
