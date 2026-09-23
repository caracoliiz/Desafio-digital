import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Vendas Bemol",
    layout="wide"
)

# =========================
# ESTILO VISUAL
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
    font-size: 62px !important;
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

/* Corrige o texto selecionado nos filtros */
[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #0A1F44 !important;
}

/* Cor do campo fechado do selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
}

/* Cor das opções quando abre o dropdown */
[data-baseweb="popover"] div {
    color: #0A1F44 !important;
    background-color: #FFFFFF !important;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(0, 153, 216, 0.20);
    padding: 24px;
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
    font-size: 34px;
}

.stPlotlyChart {
    background: rgba(255, 255, 255, 0.72);
    border-radius: 24px;
    padding: 18px;
    box-shadow: 0 8px 28px rgba(0, 109, 182, 0.12);
}

.card-title {
    font-family: 'Coda', sans-serif;
    color: #0B4DA2;
    font-size: 16px;
    font-weight: 800;
}

.material-symbols-rounded {
    font-family: 'Material Symbols Rounded';
    font-weight: normal;
    font-style: normal;
    font-size: 28px;
    vertical-align: middle;
    margin-right: 8px;
}

hr {
    border-color: rgba(0, 109, 182, 0.18);
}
</style>
""", unsafe_allow_html=True)

# =========================
# DADOS
# =========================
arquivo = "desafio.xlsx"
aba = "Dados - Questão 1"

def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def moeda_resumida(valor):
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} Mi".replace(".", ",")
    if valor >= 1_000:
        return f"R$ {valor / 1_000:.2f} Mil".replace(".", ",")
    return moeda_br(valor)

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

# =========================
# SIDEBAR / FILTROS
# =========================
st.sidebar.image("logo_bemol.png", use_container_width=True)

st.sidebar.markdown("## Filtros")

unidades = ["Todas"] + sorted(df["Unidade"].unique())
produtos = ["Todos"] + sorted(df["Produto"].unique())
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
# KPIs
# =========================
faturamento_total = df_filtrado["Faturamento"].sum()
qtd_vendas = len(df_filtrado)
qtd_produtos = df_filtrado["Qtd"].sum()
ticket_medio = faturamento_total / qtd_vendas if qtd_vendas > 0 else 0

vendedor_perf = df_filtrado.groupby("Vendedor")["Faturamento"].sum()
melhor_vendedor = vendedor_perf.idxmax() if not vendedor_perf.empty else "-"

faturamento_unidade = df_filtrado.groupby("Unidade")["Faturamento"].sum()
loja_mais_faturou = faturamento_unidade.idxmax() if not faturamento_unidade.empty else "-"

produto_qtd = df_filtrado.groupby("Produto")["Qtd"].sum()
produto_mais_vendido = produto_qtd.idxmax() if not produto_qtd.empty else "-"

# =========================
# DASHBOARD
# =========================
st.markdown("<h1>Dashboard de Vendas</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#0B4DA2; font-family:Coda; margin-top:-18px;'>Visão geral de performance comercial</p>",
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Faturamento Total", moeda_resumida(faturamento_total))
col2.metric("Quantidade de Vendas", qtd_vendas)
col3.metric("Produtos Vendidos", int(qtd_produtos))
col4.metric("Ticket Médio", moeda_br(ticket_medio))

col5, col6, col7 = st.columns(3)

col5.metric("Melhor Vendedor", melhor_vendedor)
col6.metric("Melhor Loja", loja_mais_faturou)
col7.metric("Produto Destaque", produto_mais_vendido)

st.divider()

# =========================
# CORES DOS GRÁFICOS
# =========================
cor_bom = "#00B050"
cor_medio = "#0099D8"
cor_ruim = "#E63946"

layout_base = dict(
    template="plotly_white",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",

    font=dict(
        color="#0A1F44",
        family="Coda"
    ),

    title_font=dict(
        family="Coda",
        color="#0A1F44",
        size=16
    ),

    margin=dict(
        l=20,
        r=20,
        t=50,
        b=30
    ),

    # Hover maior e mais legível
    hoverlabel=dict(
        bgcolor="#0099D8",
        font_color="white",
        font_size=18,
        font_family="Coda",
        bordercolor="white"
    ),

    # Animação suave
    transition_duration=800
)

# =========================
# GRÁFICOS
# =========================
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Faturamento por Unidade")

    fat_unid_df = (
        df_filtrado.groupby("Unidade")["Faturamento"]
        .sum()
        .reset_index()
        .sort_values("Faturamento", ascending=False)
    )

    fig_unidade = px.bar(
        fat_unid_df,
        x="Unidade",
        y="Faturamento",
        color="Faturamento",
        color_continuous_scale=[cor_ruim, cor_medio, cor_bom],
        title="Faturamento por Unidade"
    )

    fig_unidade.update_layout(
        **layout_base,
        xaxis_title="Unidade",
        yaxis_title="Faturamento"
    )
    fig_unidade.update_traces(
    hovertemplate=
    "<b> %{x}</b><br><br>"
    "Faturamento:<br>"
    "R$ %{y:,.2f}"
    "<extra></extra>"
)
    st.plotly_chart(fig_unidade, use_container_width=True)

with col_graf2:
    st.subheader("Quantidade Vendida por Produto")

    prod_qtd_df = (
        df_filtrado.groupby("Produto")["Qtd"]
        .sum()
        .reset_index()
        .sort_values("Qtd", ascending=False)
        .head(10)
    )

    fig_produto = px.bar(
        prod_qtd_df,
        x="Qtd",
        y="Produto",
        orientation="h",
        color="Qtd",
        color_continuous_scale=[cor_ruim, cor_medio, cor_bom],
        title="Top Produtos por Quantidade"
    )

    fig_produto.update_layout(
        **layout_base,
        xaxis_title="Quantidade",
        yaxis_title="Produto"
    )
    fig_produto.update_traces(
    hovertemplate=
    "<b> %{y}</b><br><br>"
    "Quantidade:<br>"
    "%{x}"
    "<extra></extra>"
)

    st.plotly_chart(fig_produto, use_container_width=True)

st.subheader("Evolução do Faturamento Mensal")

vendas_mes = (
    df_filtrado.groupby("Mês")["Faturamento"]
    .sum()
    .reset_index()
    .sort_values("Mês")
)

fig_mes = px.line(
    vendas_mes,
    x="Mês",
    y="Faturamento",
    markers=True,
    title="Faturamento por Mês"
)

fig_mes.update_traces(
    line=dict(color=cor_medio, width=4),
    marker=dict(size=9, color=cor_bom)
)

fig_mes.update_layout(
    **layout_base,
    xaxis_title="Mês",
    yaxis_title="Faturamento"
)
fig_mes.update_traces(
    hovertemplate=
    "<b> %{x}</b><br><br>"
    "Faturamento:<br>"
    "R$ %{y:,.2f}"
    "<extra></extra>"
)

st.plotly_chart(fig_mes, use_container_width=True)

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("Faturamento por Vendedor")

    vend_df = (
        df_filtrado.groupby("Vendedor")["Faturamento"]
        .sum()
        .reset_index()
        .sort_values("Faturamento", ascending=False)
        .head(10)
    )

    fig_vendedor = px.bar(
        vend_df,
        x="Vendedor",
        y="Faturamento",
        color="Faturamento",
        color_continuous_scale=[cor_ruim, cor_medio, cor_bom],
        title="Ranking de Vendedores"
    )

    fig_vendedor.update_layout(
        **layout_base,
        xaxis_title="Vendedor",
        yaxis_title="Faturamento"
    )
    fig_vendedor.update_traces(
    hovertemplate=
    "<b> %{x}</b><br><br>"
    "Faturamento:<br>"
    "R$ %{y:,.2f}"
    "<extra></extra>"
)
    st.plotly_chart(fig_vendedor, use_container_width=True)

with col_graf4:
    st.subheader("Distribuição por Unidade")

    dist_unidade = (
        df_filtrado.groupby("Unidade")["Faturamento"]
        .sum()
        .reset_index()
    )

    fig_pizza = px.pie(
        dist_unidade,
        names="Unidade",
        values="Faturamento",
        title="Participação no Faturamento",
        color_discrete_sequence=[
            cor_bom,
            cor_medio,
            "#7B61FF",
            "#FF9F1C",
            cor_ruim,
            "#2EC4B6"
        ]
    )

    fig_pizza.update_layout(**layout_base)

    st.plotly_chart(fig_pizza, use_container_width=True)

st.subheader("Dados Detalhados")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)