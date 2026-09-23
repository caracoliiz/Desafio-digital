import pandas as pd

arquivo = "desafio.xlsx"
aba = "Dados - Questão 1"

##cria data frame e seleciona as colunas de A à G
df = pd.read_excel(arquivo, sheet_name=aba, usecols="A:G")

##cria nova coluna chamada faturamento , *obs: faturamento de cada linha
df["Faturamento"] = df["Valor unitário"] * df["Qtd"]


##print(df.info()) = RG da tabela ##“Que tipo de dados eu tenho?”
##print(df.isnull().sum()) ##“Quantos valores vazios existem em cada coluna?”
##print(df.duplicated().sum()) ##"Tenho linhas duplicadas?” valor !* linha duplicada

faturamento_total = df["Faturamento"].sum()

#print(f"Faturamento total: R$ {faturamento_total:,.2f}")

##calculo imposto
if faturamento_total <= 2100000:
    aliquota = 0.05

elif faturamento_total <= 2400000:
    aliquota = 0.12

else:
    aliquota = 0.17

imposto = faturamento_total * aliquota

## questão 1

print(f"Imposto a ser pago pela empresa: R$ {imposto:,.2f}")
print(f"Alíquota aplicada: {aliquota:.0%}")

faturamento_por_und = df.groupby("Unidade")["Faturamento"].sum()
#for unidade, valor in faturamento_por_und.items():
    #print(f"Faturamento por unidade: {unidade}: R$ {valor:,.2f}")

imposto_por_und = faturamento_por_und * aliquota
for unidade, valor in imposto_por_und.items():
    print(f"Imposto por unidade: {unidade}: R$ {valor:,.2f}")

## questão 4
lucro_por_und = faturamento_por_und - imposto_por_und

valor_maior_lucro = lucro_por_und.max()
und_maior_lucro = lucro_por_und.idxmax()

print(f"A loja com maior lucro: {und_maior_lucro}")
print(f"E o valor foi de: R$ {valor_maior_lucro:,.2f} ")

####questao 2
produto_qtd = df.groupby("Produto")["Qtd"].sum()
#print(produto_qtd)
produto_mais_vend = produto_qtd.idxmax()
qtd_prod_mais = produto_qtd.max()
produto_menos_vend = produto_qtd.idxmin()
qtd_prod_menos = produto_qtd.min()

print(f"O produto mais vendido da empresa é: {produto_mais_vend}")
print(f"E a quantidade vendida foi de: {qtd_prod_mais}")
print(f"O produto menos vendido da empresa é: {produto_menos_vend}")
print(f"E a quantidade foi: {qtd_prod_menos}")

total_prod_vend = df["Qtd"].sum()
represent_maior = qtd_prod_mais / total_prod_vend * 100
represent_menor = qtd_prod_menos / total_prod_vend * 100

print(f"O produto mais vendido representa {represent_maior:.2f}% da venda total")
print(f"O produto menos vendido representa {represent_menor:.2f}% da venda total")

##questão 3
##tabela auxiliar de vendedores + tabela principal
vendedores = pd.read_excel(arquivo, sheet_name=aba, usecols="I:J")

df = df.merge(
    vendedores,
    left_on="Cod Vendedor",
    right_on="Cod Vendedores",
    how="left"
)

vendedor_perf = df.groupby("Vendedor")["Faturamento"].sum()

melhor_vend = vendedor_perf.idxmax()
melhor_fat_vend = vendedor_perf.max()

print(f"O melhor vendedor da empresa foi: {melhor_vend}")
print(f"E obteve o faturamento de: R$ {melhor_fat_vend:,.2f}")

##questão 5 
# converter para Ano-Mês

df["Mês"] = df["Data Compra"].dt.to_period("M")

#separa por unidade e por mês
vendas_mes_unidade = df.groupby(["Unidade", "Mês"])["Faturamento"].sum()

#transforma em tabela
vendas_mes_unidade = (
    df.groupby(["Unidade", "Mês"])["Faturamento"]
    .sum()
    .reset_index()
)

#melhor periodo de vendas por unidade
idx = vendas_mes_unidade.groupby("Unidade")["Faturamento"].idxmax()

melhor_mes_loja = vendas_mes_unidade.loc[idx]

print(melhor_mes_loja)

## melhor periodo de vendas por vendedor
vendas_mes_vendedor = (
    df.groupby(["Vendedor", "Mês"])["Faturamento"]
    .sum()
    .reset_index()
)

idx_vendedor = vendas_mes_vendedor.groupby("Vendedor")["Faturamento"].idxmax()

melhor_mes_vendedor = vendas_mes_vendedor.loc[idx_vendedor]

print(melhor_mes_vendedor)