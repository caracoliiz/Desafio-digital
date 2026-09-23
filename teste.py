import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard de Vendas Bemol",
    layout="wide"
)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Changa+One&family=Coda:wght@400;800&family=Tilt+Neon&family=Material+Symbols+Rounded');

.stApp {
    background: linear-gradient(135deg, #EAF6FF, #F7FBFF, #EDF4FF);
    color: #0A1F44;
    font-family: 'Tilt Neon', sans-serif;
}

h1 {
    font-family: 'Changa One', cursive;
    color: #0A1F44;
    font-size: 58px !important;
}

h2, h3 {
    font-family: 'Coda', sans-serif;
    color: #0B4DA2;
}

p, span, label, div {
    font-family: 'Tilt Neon', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0099D8, #006DB6);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #0A1F44 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
}

[data-baseweb="popover"] div {
    color: #0A1F44 !important;
    background-color: #FFFFFF !important;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(0, 153, 216, 0.20);
    padding: 22px;
    border-radius: 22px;
    box-shadow: 0 8px 28px rgba(0, 109, 182, 0.15);
}

[data-testid="stMetricLabel"] {
    color: #0B4DA2 !important;
    font-family: 'Coda', sans-serif;
}

[data-testid="stMetricValue"] {
    color: #0A1F44 !important;
    font-family: 'Changa One', cursive;
    font-size: 32px;
}

.stPlotlyChart {
    background: rgba(255, 255, 255, 0.75);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 8px 28px rgba(0, 109, 182, 0.12);
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def moeda_resumida(valor):
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} Mi".replace(".", ",")
    if valor >= 1_000:
        return f"R$ {valor / 1_000:.2f} Mil".replace(".", ",")
    return moeda_br(valor)

def calcular_aliquota(faturamento):
    if faturamento <= 2_100_000:
        return 0.05
    elif faturamento <= 2_400_000:
        return 0.12
    else:
        return 0.17

def grafico_empilhado_com_total(df_base, eixo_x, categoria, valor, titulo, eixo_y):
    tabela = (
        df_base
        .groupby([eixo_x, categoria])[valor]
        .sum()
        .reset_index()
    )

    pivot = tabela.pivot(
        index=eixo_x,
        columns=categoria,
        values=valor
    ).fillna(0)

    pivot = pivot.sort_index()

    fig = go.Figure()

    for coluna in pivot.columns:
        fig.add_trace(
            go.Bar(
                x=pivot.index,
                y=pivot[coluna],
                name=str(coluna),
                text=pivot[coluna],
                texttemplate="%{text:,.0f}",
                textposition="inside",
                hovertemplate=f"<b>{categoria}: {coluna}</b><br>{eixo_x}: %{{x}}<br>Valor: R$ %{{y:,.2f}}<extra></extra>"
            )
        )

    total = pivot.sum(axis=1)

    fig.add_trace(
        go.Scatter(
            x=pivot.index,
            y=total,
            mode="lines+markers+text",
            name="Total",
            text=[moeda_resumida(v) for v in total],
            textposition="top center",
            line=dict(color="black", width=4),
            marker=dict(size=8, color="black"),
            hovertemplate="<b>Total</b><br>%{x}<br>R$ %{y:,.2f}<extra></extra>"
        )
    )

    fig.update_layout(
        barmode="stack",
        title=titulo,
        xaxis_title=eixo_x,
        yaxis_title=eixo_y,
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#0A1F44", family="Coda"),
        title_font=dict(color="#0A1F44", family="Coda", size=17),
        hoverlabel=dict(
            bgcolor="#0099D8",
            font_color="white",
            font_size=16,
            font_family="Coda"
        ),
        legend_title_text=categoria,
        margin=dict(l=20, r=20, t=55, b=35),
        transition_duration=800
    )

    return fig

# =========================
# DADOS
# =========================
arquivo = "desafio.xlsx"
aba = "Dados - Questão 1"

df = pd.read_excel(arquivo, sheet_name=aba, usecols="A:G")
vendedores = pd.read_excel(arquivo, sheet_name=aba, usecols="I:J")

df["Faturamento"] = df["Valor unitário"] * df["Qtd"]

df = df.merge(
    vendedores,
    left_on="Cod Vendedor",
    right_on="Cod Vendedores",
    how="left"
)

df["Mês"] = df["Data Compra"].dt.to_period("M").astype(str)

# Imposto por venda baseado no faturamento total da empresa
faturamento_empresa = df["Faturamento"].sum()
aliquota_empresa = calcular_aliquota(faturamento_empresa)
df["Imposto"] = df["Faturamento"] * aliquota_empresa
df["Lucro Líquido"] = df["Faturamento"] - df["Imposto"]

# =========================
# FILTROS
# =========================
try:
    st.sidebar.image("logo_bemol.png", use_container_width=True)
except:
    st.sidebar.title("Bemol")

st.sidebar.markdown("## Filtros")

unidades = ["Todas"] + sorted(df["Unidade"].dropna().unique())
produtos = ["Todos"] + sorted(df["Produto"].dropna().unique())
vendedores_lista = ["Todos"] + sorted(df["Vendedor"].dropna().unique())

unidade = st.sidebar.selectbox("Unidade", unidades)
produto = st.sidebar.selectbox("Produto", produtos)
vendedor = st.sidebar.selectbox("Vendedor", vendedores_lista)

df_filtrado = df.copy()

if unidade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Unidade"] == unidade]

if produto != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Produto"] == produto]

if vendedor != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Vendedor"] == vendedor]

# =========================
# INDICADORES
# =========================
faturamento_total = df_filtrado["Faturamento"].sum()
imposto_total = df_filtrado["Imposto"].sum()
lucro_liquido_total = df_filtrado["Lucro Líquido"].sum()
qtd_vendas = len(df_filtrado)
qtd_produtos = df_filtrado["Qtd"].sum()
ticket_medio = faturamento_total / qtd_vendas if qtd_vendas > 0 else 0

produto_qtd = df_filtrado.groupby("Produto")["Qtd"].sum()
produto_mais_vendido = produto_qtd.idxmax() if not produto_qtd.empty else "-"
produto_menos_vendido = produto_qtd.idxmin() if not produto_qtd.empty else "-"

vendedor_perf = df_filtrado.groupby("Vendedor")["Faturamento"].sum()
melhor_vendedor = vendedor_perf.idxmax() if not vendedor_perf.empty else "-"

lucro_unidade = df_filtrado.groupby("Unidade")["Lucro Líquido"].sum()
melhor_loja_lucro = lucro_unidade.idxmax() if not lucro_unidade.empty else "-"

mes_loja = df_filtrado.groupby(["Unidade", "Mês"])["Faturamento"].sum().reset_index()
periodo_loja = mes_loja.loc[mes_loja["Faturamento"].idxmax()] if not mes_loja.empty else None

mes_vendedor = df_filtrado.groupby(["Vendedor", "Mês"])["Faturamento"].sum().reset_index()
periodo_vendedor = mes_vendedor.loc[mes_vendedor["Faturamento"].idxmax()] if not mes_vendedor.empty else None

# =========================
# DASHBOARD
# =========================
st.markdown("<h1>Dashboard de Vendas</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#0B4DA2; font-family:Coda; margin-top:-18px;'>Respostas das 5 questões principais da atividade</p>",
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento Total", moeda_resumida(faturamento_total))
col2.metric("Imposto Total", moeda_resumida(imposto_total))
col3.metric("Lucro Líquido", moeda_resumida(lucro_liquido_total))
col4.metric("Ticket Médio", moeda_br(ticket_medio))

col5, col6, col7, col8 = st.columns(4)
col5.metric("Produto Mais Vendido", produto_mais_vendido)
col6.metric("Produto Menos Vendido", produto_menos_vendido)
col7.metric("Melhor Vendedor", melhor_vendedor)
col8.metric("Melhor Loja", melhor_loja_lucro)

st.divider()

# =========================
# 1ª QUESTÃO
# =========================
st.header("1ª - Imposto total e imposto por unidade")

imposto_unidade = (
    df_filtrado
    .groupby("Unidade")
    .agg(
        Faturamento=("Faturamento", "sum"),
        Imposto=("Imposto", "sum"),
        Lucro_Liquido=("Lucro Líquido", "sum")
    )
    .reset_index()
    .sort_values("Imposto", ascending=False)
)

col_a, col_b = st.columns(2)

with col_a:
    fig_imposto = px.bar(
        imposto_unidade,
        x="Unidade",
        y="Imposto",
        color="Imposto",
        color_continuous_scale=["#E63946", "#0099D8", "#00B050"],
        text="Imposto",
        title="Imposto por Unidade"
    )

    fig_imposto.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Imposto: R$ %{y:,.2f}<extra></extra>"
    )

    fig_imposto.update_layout(
        template="plotly_white",
        xaxis_title="Unidade",
        yaxis_title="Imposto",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)"
    )

    st.plotly_chart(fig_imposto, use_container_width=True)

with col_b:
    tabela_imposto = imposto_unidade.copy()
    tabela_imposto["Faturamento"] = tabela_imposto["Faturamento"].apply(moeda_br)
    tabela_imposto["Imposto"] = tabela_imposto["Imposto"].apply(moeda_br)
    tabela_imposto["Lucro_Liquido"] = tabela_imposto["Lucro_Liquido"].apply(moeda_br)

    st.dataframe(tabela_imposto, use_container_width=True, hide_index=True)

# =========================
# 2ª QUESTÃO
# =========================
st.header("2ª - Produto mais e menos vendido e percentual sobre o total")

produtos_df = (
    df_filtrado
    .groupby("Produto")
    .agg(
        Quantidade=("Qtd", "sum"),
        Faturamento=("Faturamento", "sum")
    )
    .reset_index()
)

total_qtd = produtos_df["Quantidade"].sum()
produtos_df["Percentual"] = produtos_df["Quantidade"] / total_qtd * 100 if total_qtd > 0 else 0
produtos_df = produtos_df.sort_values("Quantidade", ascending=True)

fig_produtos = px.bar(
    produtos_df,
    x="Quantidade",
    y="Produto",
    orientation="h",
    color="Quantidade",
    color_continuous_scale=["#E63946", "#0099D8", "#00B050"],
    text="Percentual",
    title="Produtos mais e menos vendidos"
)

fig_produtos.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<br>Percentual: %{text:.2f}%<extra></extra>"
)

fig_produtos.update_layout(
    template="plotly_white",
    xaxis_title="Quantidade Vendida",
    yaxis_title="Produto",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)"
)

st.plotly_chart(fig_produtos, use_container_width=True)

# =========================
# 3ª QUESTÃO
# =========================
st.header("3ª - Vendedor com melhor performance")

vendedor_df = (
    df_filtrado
    .groupby("Vendedor")
    .agg(
        Faturamento=("Faturamento", "sum"),
        Quantidade=("Qtd", "sum")
    )
    .reset_index()
    .sort_values("Faturamento", ascending=False)
)

fig_vendedor = px.bar(
    vendedor_df.head(10),
    x="Vendedor",
    y="Faturamento",
    color="Faturamento",
    color_continuous_scale=["#E63946", "#0099D8", "#00B050"],
    text="Faturamento",
    title="Ranking de Vendedores por Faturamento"
)

fig_vendedor.update_traces(
    texttemplate="R$ %{text:,.0f}",
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>"
)

fig_vendedor.update_layout(
    template="plotly_white",
    xaxis_title="Vendedor",
    yaxis_title="Faturamento",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)"
)

st.plotly_chart(fig_vendedor, use_container_width=True)

# =========================
# 4ª QUESTÃO
# =========================
st.header("4ª - Loja com maior lucro após impostos")

lucro_df = (
    df_filtrado
    .groupby("Unidade")
    .agg(
        Faturamento=("Faturamento", "sum"),
        Imposto=("Imposto", "sum"),
        Lucro_Liquido=("Lucro Líquido", "sum")
    )
    .reset_index()
    .sort_values("Lucro_Liquido", ascending=False)
)

fig_lucro = go.Figure()

fig_lucro.add_trace(go.Bar(
    x=lucro_df["Unidade"],
    y=lucro_df["Faturamento"],
    name="Faturamento Bruto"
))

fig_lucro.add_trace(go.Bar(
    x=lucro_df["Unidade"],
    y=lucro_df["Imposto"],
    name="Imposto"
))

fig_lucro.add_trace(go.Bar(
    x=lucro_df["Unidade"],
    y=lucro_df["Lucro_Liquido"],
    name="Lucro Líquido"
))

fig_lucro.update_layout(
    barmode="group",
    title="Faturamento, Imposto e Lucro Líquido por Unidade",
    xaxis_title="Unidade",
    yaxis_title="Valor",
    template="plotly_white",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)"
)

st.plotly_chart(fig_lucro, use_container_width=True)

# =========================
# 5ª QUESTÃO
# =========================
st.header("5ª - Período em que cada loja e vendedor mais vendeu")

col_c, col_d = st.columns(2)

with col_c:
    if periodo_loja is not None:
        st.metric(
            "Maior venda por loja",
            f"{periodo_loja['Unidade']} - {periodo_loja['Mês']}",
            moeda_resumida(periodo_loja["Faturamento"])
        )

with col_d:
    if periodo_vendedor is not None:
        st.metric(
            "Maior venda por vendedor",
            f"{periodo_vendedor['Vendedor']} - {periodo_vendedor['Mês']}",
            moeda_resumida(periodo_vendedor["Faturamento"])
        )

st.subheader("Evolução mensal por loja")
fig_mes_loja = grafico_empilhado_com_total(
    df_filtrado,
    eixo_x="Mês",
    categoria="Unidade",
    valor="Faturamento",
    titulo="Vendas mensais por loja com linha de total",
    eixo_y="Faturamento"
)
st.plotly_chart(fig_mes_loja, use_container_width=True)

st.subheader("Evolução mensal por vendedor")
fig_mes_vendedor = grafico_empilhado_com_total(
    df_filtrado,
    eixo_x="Mês",
    categoria="Vendedor",
    valor="Faturamento",
    titulo="Vendas mensais por vendedor com linha de total",
    eixo_y="Faturamento"
)
st.plotly_chart(fig_mes_vendedor, use_container_width=True)

# =========================
# DADOS DETALHADOS
# =========================
st.header("Dados detalhados")

df_tabela = df_filtrado.copy()
df_tabela["Faturamento"] = df_tabela["Faturamento"].apply(moeda_br)
df_tabela["Imposto"] = df_tabela["Imposto"].apply(moeda_br)
df_tabela["Lucro Líquido"] = df_tabela["Lucro Líquido"].apply(moeda_br)

st.dataframe(df_tabela, use_container_width=True, hide_index=True)