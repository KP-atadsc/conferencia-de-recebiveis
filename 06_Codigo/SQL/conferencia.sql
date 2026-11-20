-- Cada CTE devolve uma linha por pedido antes do cruzamento.
CREATE TABLE conferencia AS
WITH por_item AS (
    SELECT pedido_id, COUNT(*) AS itens, SUM(preco) AS itens_centavos,
           SUM(frete) AS frete_centavos, SUM(preco + frete) AS esperado_centavos
    FROM itens GROUP BY pedido_id
), por_pagamento AS (
    SELECT pedido_id, COUNT(*) AS registros_pagamento, SUM(valor) AS registrado_centavos
    FROM pagamentos GROUP BY pedido_id
), formas_distintas AS (
    SELECT DISTINCT pedido_id, forma FROM pagamentos ORDER BY pedido_id, forma
), meios AS (
    SELECT pedido_id, GROUP_CONCAT(forma, ' + ') AS formas
    FROM formas_distintas GROUP BY pedido_id
), valores AS (
    SELECT p.pedido_id, SUBSTR(p.compra, 1, 7) AS mes, p.estado,
           COALESCE(i.itens, 0) AS itens, COALESCE(g.registros_pagamento, 0) AS registros_pagamento,
           m.formas, i.itens_centavos, i.frete_centavos, i.esperado_centavos,
           g.registrado_centavos, g.registrado_centavos - i.esperado_centavos AS delta_centavos
    FROM pedidos AS p
    LEFT JOIN por_item AS i USING (pedido_id)
    LEFT JOIN por_pagamento AS g USING (pedido_id)
    LEFT JOIN meios AS m USING (pedido_id)
    WHERE p.estado = 'delivered'
), classificados AS (
    SELECT *, ABS(delta_centavos) AS abs_delta_centavos,
           CASE WHEN itens = 0 AND registros_pagamento = 0 THEN 'Sem ambos'
                WHEN itens = 0 THEN 'Sem itens'
                WHEN registros_pagamento = 0 THEN 'Sem pagamento'
                WHEN delta_centavos = 0 THEN 'Exato'
                WHEN ABS(delta_centavos) = 1 THEN 'Até R$ 0,01'
                ELSE 'Revisar valor' END AS resultado
    FROM valores
)
SELECT *, CASE resultado
            WHEN 'Sem pagamento' THEN 'Verificar se a extração de pagamentos está completa'
            WHEN 'Sem itens' THEN 'Verificar se a extração de itens está completa'
            WHEN 'Sem ambos' THEN 'Conferir a presença do pedido nas duas origens'
            WHEN 'Revisar valor' THEN 'Conferir composição dos itens, frete e pagamentos'
            WHEN 'Até R$ 0,01' THEN 'Monitorar efeito acumulado da tolerância'
            ELSE 'Manter em amostragem de controle' END AS acao
FROM classificados;
CREATE UNIQUE INDEX conferencia_por_pedido ON conferencia (pedido_id);

-- Lacunas de evidência vêm primeiro. Para elas, diferença monetária é desconhecida.
CREATE VIEW fila AS
SELECT * FROM conferencia
WHERE resultado NOT IN ('Exato', 'Até R$ 0,01')
ORDER BY (delta_centavos IS NOT NULL), abs_delta_centavos DESC, pedido_id;
