# Conferência de recebíveis

Um pedido tem dois itens de R$ 72,07 com frete. O cliente usou R$ 124,14 no cartão e R$ 20,00 em vale. A conta fecha em **R$ 144,14**. Um cruzamento entre as linhas de itens e pagamentos pode dobrar os dois lados para R$ 288,28 e ainda indicar que está tudo certo.

Esse pedido existe na base pública da Olist. Ele explica uma escolha deste projeto de portfólio: somar itens e pagamentos separadamente e só depois comparar os totais por pedido. A aplicação é uma pergunta de supervisão em contas a receber: **com tempo limitado, quais registros vale abrir primeiro?** Uma descrição de trabalho da Ambev em Jaguariúna cita a conciliação para baixa de notas. Todos os números desta demonstração vêm da Olist. [Atividade descrita pela Ambev](https://ambev.gupy.io/jobs/12773411) · [Base original da Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

### Abra um pedido

Baixe o [relatório pronto para Power BI Desktop](03_Power_BI/Relatorio/Conferencia_de_recebiveis.pbix). A aba **Visão do supervisor** resume os pedidos entregues e os motivos de revisão. A lista de pedidos, valores e ações fica na aba **Fila de revisão**. Com os filtros limpos e na ordem inicial, a primeira linha mostra um pedido sem registro de pagamento. A segunda traz a maior diferença comparável, R$ 182,81. Cada aba tem seu próprio filtro de mês. Para investigar o mesmo período nas duas, selecione o mês em ambas.

Para ver as linhas de itens e pagamentos, baixe e abra o [visualizador offline de pedidos](03_Power_BI/Auditoria_offline/Abrir_auditoria.html) no navegador. A busca cobre os 300 pedidos da fila e um pedido de controle. O atalho de dois itens e dois pagamentos abre esse controle de R$ 144,14. Para consultar outro pedido da fonte, use o comando com `--pedido` abaixo e substitua o ID. Os [seis slides em PDF](04_Apresentacao/PDF/Conferencia_de_recebiveis.pdf) resumem os resultados para o time.

### Por que são 300 pedidos?

Dos 99.441 pedidos da fonte, 96.478 estavam entregues. A regra aceita uma diferença de até um centavo por pedido com dados dos dois lados. Restam **299 pedidos com diferença mensurável e um sem registro de pagamento**. O total absoluto dos 299 é R$ 3.230,30. Para saber a causa ou confirmar liquidação, seria preciso verificar documentos da venda e do recebimento. [Contas e exemplos](01_Projeto/Leitura_dos_resultados.md) · [Fila em CSV](02_Dados/Fila/fila.csv)

Para experimentar, rode este comando na pasta do projeto com Python 3.10 ou posterior. Ele usa o CSV incluído e funciona sem internet. Troque o último número por `0` e veja por que outros 270 pedidos entram na fila.

```shell
python 06_Codigo/testar_tolerancia.py 1
```

### Da origem ao relatório

O primeiro comando abaixo baixa a versão 2 da Olist, recria os CSVs e totais de controle e exibe os registros do pedido indicado. O segundo executa os testes da conferência, da exportação e da atualização do modelo do Power BI. Ambos usam a biblioteca padrão do Python. Para trabalhar com um download já feito, acrescente `--zip caminho/olist.zip` ao primeiro comando.

```shell
python 06_Codigo/executar.py --pedido 32e4fa9bb468884309b58b9348de70c3
python -m unittest discover -s 06_Codigo/Testes -v
```

A [consulta SQL](06_Codigo/SQL/conferencia.sql) concentra a regra. O [dicionário](02_Dados/Dicionario.md) explica as colunas monetárias em centavos. O gráfico mensal usa o mês de compra dos pedidos entregues. Há 23 meses com pedidos entre setembro de 2016 e agosto de 2018. Novembro de 2016 não tem pedidos entregues no recorte e por isso fica fora do eixo. A [proposta de piloto](01_Projeto/Proposta.md) especifica o que precisaria mudar para testar uma carteira com títulos, parcelas, liquidações e estornos.

### Atualizar os materiais após recriar os dados

1. Baixe o repositório completo em **Code → Download ZIP** e extraia a pasta, ou faça um clone com Git. O [projeto editável do Power BI](03_Power_BI/Projeto_editavel/Conferencia.pbip) usa as pastas irmãs `Conferencia.Report` e `Conferencia.SemanticModel`.
2. Com o Power BI Desktop fechado, execute `python 03_Power_BI/Atualizacao/atualizar_modelo.py` a partir da raiz do repositório. Esse comando atualiza os dados das tabelas Mensal e Fila no projeto editável.
3. Abra `Conferencia.pbip` no Power BI Desktop e clique em **Atualizar**. Para distribuir o relatório atualizado como arquivo único, use **Arquivo → Salvar como** e escolha o formato **.pbix**. O PBIX distribuído é uma cópia separada do projeto editável.
4. Para recriar o visualizador de pedidos, execute `python 06_Codigo/gerar_auditoria.py`. O parâmetro `--zip caminho/olist.zip` também permite usar a base já baixada.

O projeto foi preparado com apoio de IA na pesquisa, na implementação e nos materiais de apresentação. A fonte, as transformações e as contas por pedido estão abertas à inspeção. [Créditos e licença dos dados derivados](01_Projeto/Fontes_e_licenca.md)
