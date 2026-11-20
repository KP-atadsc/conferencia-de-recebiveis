# Conferência de recebíveis

Um pedido tem dois itens de R$ 72,07 com frete. O cliente usou R$ 124,14 no cartão e R$ 20,00 em vale. A conta fecha em **R$ 144,14**. Um cruzamento entre as linhas de itens e pagamentos pode dobrar os dois lados para R$ 288,28 e ainda indicar que está tudo certo.

Esse pedido existe na base pública da Olist. Ele explica uma escolha deste projeto de portfólio: somar itens e pagamentos separadamente e só depois comparar os totais por pedido. A aplicação é uma pergunta de supervisão em contas a receber: **com tempo limitado, quais registros vale abrir primeiro?** Uma descrição de trabalho da Ambev em Jaguariúna cita a conciliação para baixa de notas. Todos os números desta demonstração vêm da Olist. [Atividade descrita pela Ambev](https://ambev.gupy.io/jobs/12773411) · [Base original da Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

### Abra um pedido

Baixe o [relatório pronto para Power BI Desktop](03_Power_BI/Relatorio/Conferencia_de_recebiveis.pbix). Em **Visão do supervisor**, veja a fila completa. Em **Fila de revisão**, a primeira linha mostra um pedido sem registro de pagamento. A segunda traz a maior diferença comparável, R$ 182,81.

Para ver as linhas originais, baixe e abra o [visualizador offline de pedidos](03_Power_BI/Auditoria_offline/Abrir_auditoria.html) no navegador. O atalho do pedido com dois itens e dois pagamentos mostra o exemplo de R$ 144,14. Os [seis slides em PDF](04_Apresentacao/PDF/Conferencia_de_recebiveis.pdf) contam a história para o time.

### Por que são 300 pedidos?

Dos 99.441 pedidos da fonte, 96.478 estavam entregues. A regra aceita uma diferença de até um centavo por pedido com dados dos dois lados. Restam **299 pedidos com diferença mensurável e um sem registro de pagamento**. O total absoluto dos 299 é R$ 3.230,30. Para saber a causa ou confirmar liquidação, seria preciso verificar documentos da venda e do recebimento. [Contas e exemplos](01_Projeto/Leitura_dos_resultados.md) · [Fila em CSV](02_Dados/Fila/fila.csv)

Para experimentar, rode este comando na pasta do projeto com Python 3.10 ou posterior. Ele usa o CSV incluído e funciona sem internet. Troque o último número por `0` e veja por que outros 270 pedidos entram na fila.

```shell
python 06_Codigo/testar_tolerancia.py 1
```

### Da origem ao relatório

O primeiro comando abaixo baixa a versão 2 da Olist e recria os CSVs e totais de controle. O segundo executa os quatro testes da lógica de conferência. Ambos usam a biblioteca padrão do Python. Para trabalhar com um download já feito, acrescente `--zip caminho/olist.zip` ao primeiro comando.

```shell
python 06_Codigo/executar.py --pedido 32e4fa9bb468884309b58b9348de70c3
python -m unittest discover -s 06_Codigo/Testes -v
```

A [consulta SQL](06_Codigo/SQL/conferencia.sql) concentra a regra. O [dicionário](02_Dados/Dicionario.md) explica as colunas monetárias em centavos. A [proposta de piloto](01_Projeto/Proposta.md) especifica o que precisaria mudar para testar uma carteira com títulos, parcelas, liquidações e estornos. Para atualizar o projeto editável do Power BI com uma nova execução dos CSVs, feche o Desktop, rode `python 03_Power_BI/Atualizacao/atualizar_modelo.py`, abra o [arquivo PBIP](03_Power_BI/Projeto_editavel/Conferencia.pbip) com as pastas irmãs e clique em **Atualizar**. Para recriar a consulta offline de itens e pagamentos, execute `python 06_Codigo/gerar_auditoria.py`.

O projeto foi preparado com apoio de IA na pesquisa, na implementação e nos materiais de apresentação. A fonte, as transformações e as contas por pedido estão abertas à inspeção. [Créditos e licença dos dados derivados](01_Projeto/Fontes_e_licenca.md)
