import pandas as pd

# Nome do arquivo Excel
arquivo = "desafio.xlsx"

# Nome da aba que contém os dados
aba = "Dados - Questão 1"


# Função para converter moeda para o formato brasileiro
def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Função para converter porcentagem para o formato brasileiro
def percentual_br(valor):
    return f"{valor:.2f}".replace(".", ",") + "%"


# Lê a tabela principal (colunas A até G)
df = pd.read_excel(
    arquivo,
    sheet_name=aba,
    usecols="A:G"
)

# Lê a tabela auxiliar que contém o código e o nome dos vendedores
vendedores = pd.read_excel(
    arquivo,
    sheet_name=aba,
    usecols="I:J"
)

# Cria a coluna faturamento
# Valor unitário × quantidade vendida
df["Faturamento"] = df["Valor unitário"] * df["Qtd"]

# Junta a tabela principal com a tabela de vendedores
# Agora cada venda terá o nome do vendedor correspondente
df = df.merge(
    vendedores,
    left_on="Cod Vendedor",
    right_on="Cod Vendedores",
    how="left"
)

# =====================================================
# QUESTÃO 1
# =====================================================

# Soma o faturamento de todas as vendas
faturamento_total = df["Faturamento"].sum()

# Define a alíquota conforme o faturamento da empresa
if faturamento_total <= 2100000:
    aliquota = 0.05

elif faturamento_total <= 2400000:
    aliquota = 0.12

else:
    aliquota = 0.17

# Calcula o imposto total da empresa
imposto_total = faturamento_total * aliquota

print("\nQUESTÃO 1")

print(f"Imposto total: {moeda_br(imposto_total)}")
print(f"Alíquota aplicada: {aliquota:.0%}")

# Agrupa o faturamento por unidade
faturamento_unidade = (
    df.groupby("Unidade")["Faturamento"]
    .sum()
)

# Calcula o imposto de cada unidade
imposto_unidade = faturamento_unidade * aliquota

# Percorre cada unidade e mostra o imposto correspondente
for unidade, imposto in imposto_unidade.items():

    print(
        f"Imposto por unidade - "
        f"{unidade}: "
        f"{moeda_br(imposto)}"
    )

# =====================================================
# QUESTÃO 2
# =====================================================

print("\nQUESTÃO 2")

# Soma a quantidade vendida de cada produto
produto_qtd = (
    df.groupby("Produto")["Qtd"]
    .sum()
)

# Quantidade total vendida de todos os produtos
total_qtd = df["Qtd"].sum()

# Produto mais vendido
mais_produto = produto_qtd.idxmax()

# Quantidade vendida do produto mais vendido
qtd_mais = produto_qtd.max()

# Produto menos vendido
menos_produto = produto_qtd.idxmin()

# Quantidade vendida do produto menos vendido
qtd_menos = produto_qtd.min()

print(
    f"Produto mais vendido: "
    f"{mais_produto} "
    f"({qtd_mais} unidades)"
)

print(
    f"Representa "
    f"{percentual_br(qtd_mais / total_qtd * 100)} "
    f"das vendas"
)

print(
    f"Produto menos vendido: "
    f"{menos_produto} "
    f"({qtd_menos} unidades)"
)

print(
    f"Representa "
    f"{percentual_br(qtd_menos / total_qtd * 100)} "
    f"das vendas"
)

# =====================================================
# QUESTÃO 3
# =====================================================

print("\nQUESTÃO 3")

# Soma o faturamento por vendedor
vendedor_perf = (
    df.groupby("Vendedor")["Faturamento"]
    .sum()
)

# Nome do vendedor que mais faturou
melhor_vendedor = vendedor_perf.idxmax()

# Valor faturado por esse vendedor
fat_melhor_vendedor = vendedor_perf.max()

print(f"Melhor vendedor: {melhor_vendedor}")
print(
    f"Faturamento: "
    f"{moeda_br(fat_melhor_vendedor)}"
)

# =====================================================
# QUESTÃO 4
# =====================================================

print("\nQUESTÃO 4")

# Lucro = faturamento - imposto
lucro_unidade = (
    faturamento_unidade -
    imposto_unidade
)

# Loja com maior lucro
melhor_loja = lucro_unidade.idxmax()

# Valor do maior lucro
maior_lucro = lucro_unidade.max()

print(
    f"Loja com maior lucro: "
    f"{melhor_loja}"
)

print(
    f"Lucro: "
    f"{moeda_br(maior_lucro)}"
)

# =====================================================
# QUESTÃO 5
# =====================================================

print("\nQUESTÃO 5")

# Cria uma coluna contendo apenas Ano-Mês
df["Mês"] = (
    df["Data Compra"]
    .dt.to_period("M")
)

# --------------------------
# Melhor período por loja
# --------------------------

# Agrupa por loja e mês
vendas_mes_unidade = (
    df.groupby(
        ["Unidade", "Mês"]
    )["Faturamento"]
    .sum()
    .reset_index()
)

# Descobre qual mês teve o maior faturamento
# para cada loja
melhor_mes_loja = vendas_mes_unidade.loc[
    vendas_mes_unidade
    .groupby("Unidade")["Faturamento"]
    .idxmax()
]

print("\nMelhor período por loja:")
print(melhor_mes_loja)

# --------------------------
# Melhor período por vendedor
# --------------------------

# Agrupa por vendedor e mês
vendas_mes_vendedor = (
    df.groupby(
        ["Vendedor", "Mês"]
    )["Faturamento"]
    .sum()
    .reset_index()
)

# Descobre qual mês teve o maior faturamento
# para cada vendedor
melhor_mes_vendedor = vendas_mes_vendedor.loc[
    vendas_mes_vendedor
    .groupby("Vendedor")["Faturamento"]
    .idxmax()
]

print("\nMelhor período por vendedor:")
print(melhor_mes_vendedor)

df["Imposto"] = df["Faturamento"] * aliquota
df["Lucro"] = df["Faturamento"] - df["Imposto"]
df["Mês"] = df["Data Compra"].dt.to_period("M").astype(str)

df.to_excel("base_power_bi.xlsx", index=False)