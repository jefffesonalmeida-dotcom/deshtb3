import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Configurações de Layout da Página (Modo Amplo)
st.set_page_config(layout="wide", page_title="Dashboard B3 - Operação Descomplica", page_icon="📈")

# Estilização CSS para emular o visual Black/Premium de plataformas de trading
st.markdown("""
    <style>
    .main { background-color: #0B0E14; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #FFFFFF; }
    div[data-testid="stMetricDelta"] { font-size: 14px; }
    h1, h2, h3, h4 { color: #E0E6ED; font-family: 'Arial', sans-serif; }
    .stTabs [data-baseweb="tab"] { color: #8E9AA6; font-size: 16px; }
    .stTabs [data-baseweb="tab"]:hover { color: #00F2FE; }
    .stTabs [aria-selected="true"] { color: #00F2FE; border-bottom-color: #00F2FE; }
    </style>
    """, unsafe_allow_html=True)

# Cabeçalho Principal
st.title("🦅 Dashboard B3 — Painel de Análise Macro & Correlações")
st.caption(f"Foco Operacional • Dados extraídos via Yahoo Finance • Atualizado em tempo real")
st.markdown("---")

# -----------------------------------------------------------------------------
# DICIONÁRIO DE ATIVOS
# -----------------------------------------------------------------------------
ativos_macro = {
    "Ibovespa (IBOV)": "^BVSP",
    "EWZ (ETF Brasil em NY)": "EWZ",
    "WTI Crude Oil (Petróleo)": "CL=F",
    "Vale SA (Proxy Minério)": "VALE3.SA",
    "Índice México (EWW)": "EWW",
    "Dólar Futuro (USDBRL)": "BRL=X"
}

# -----------------------------------------------------------------------------
# FUNÇÃO CACHEADA PARA CAPTURA DE DADOS
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)  # Atualiza o painel a cada 5 minutos
def obter_dados(ticker, janela_tempo):
    dias = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "YTD": 365}[janela_tempo]
    data_de_inicio = datetime.now() - timedelta(days=dias)
    if janela_tempo == "YTD":
        data_de_inicio = datetime(datetime.now().year, 1, 1)
        
    df = yf.download(ticker, start=data_de_inicio, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

# -----------------------------------------------------------------------------
# 1. TOP CARDS (Visão Geral das Variações de Mercado)
# -----------------------------------------------------------------------------
cols_cards = st.columns(len(ativos_macro))
for idx, (nome, ticker) in enumerate(ativos_macro.items()):
    try:
        df_kpi = obter_dados(ticker, "1M")
        if not df_kpi.empty:
            fechamento_atual = float(df_kpi['Close'].iloc[-1])
            fechamento_anterior = float(df_kpi['Close'].iloc[-2])
            variacao_diaria = ((fechamento_atual - fechamento_anterior) / fechamento_anterior) * 100
            
            cols_cards[idx].metric(
                label=nome.split(" (")[0],
                value=f"{fechamento_atual:,.2f}",
                delta=f"{variacao_diaria:+.2f}%"
            )
    except:
        cols_cards[idx].metric(label=nome, value="N/A", delta="0.00%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. CONTROLES LATERAIS (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.header("📊 Painel de Controle")
ativo_selecionado = st.sidebar.selectbox("Escolha o Ativo Principal:", list(ativos_macro.keys()))
periodo_grafico = st.sidebar.selectbox("Selecione o Tempo Histórico:", ["1M", "3M", "6M", "1Y", "YTD"], index=1)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Dica Operacional:** Compare o comportamento do EWZ com o Ibovespa em momentos de virada do dólar para identificar fluxo estrangeiro.")

# -----------------------------------------------------------------------------
# 3. CONSTRUÇÃO DO VISUAL PRINCIPAL (TABS)
# -----------------------------------------------------------------------------
tab_grafico, tab_correlacao, tab_analise_di = st.tabs(["📈 Gráfico Avançado (Candle)", "🧮 Matriz de Correlação", "🎯 Dinâmica de Juros (DI)"])

# ABA 1: GRÁFICO DE CANDLE + VOLUME
with tab_grafico:
    st.subheader(f"Análise Gráfica — {ativo_selecionado}")
    df_dados = obter_dados(ativos_macro[ativo_selecionado], periodo_grafico)
    
    if not df_dados.empty:
        fig_principal = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                      vertical_spacing=0.03, row_width=[0.2, 0.8])
        
        fig_principal.add_trace(px.Candlestick(
            x=df_dados.index, open=df_dados['Open'], high=df_dados['High'],
            low=df_dados['Low'], close=df_dados['Close'], name="Preço"
        ).data[0], row=1, col=1)
        
        fig_principal.add_trace(px.bar(
            x=df_dados.index, y=df_dados['Volume'], name="Volume"
        ).data[0], row=2, col=1)
        
        fig_principal.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_principal, use_container_width=True)
    else:
        st.error("Não foi possível renderizar o gráfico para este ativo.")

# ABA 2: MATRIZ DE CORRELAÇÃO MACRO
with tab_correlacao:
    st.subheader("Matriz de Correlação Linear (Retornos Percentuais)")
    
    lista_retornos = []
    for nome, ticker in ativos_macro.items():
        df_corr = obter_dados(ticker, periodo_grafico)
        if not df_corr.empty:
            retornos_diarios = df_corr['Close'].pct_change().dropna()
            retornos_diarios.name = nome.split(" (")[0]
            lista_retornos.append(retornos_diarios)
            
    if lista_retornos:
        df_final_corr = pd.concat(lista_retornos, axis=1).dropna()
        matriz_calculada = df_final_corr.corr()
        
        fig_heatmap = px.imshow(
            matriz_calculada,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            template="plotly_dark"
        )
        fig_heatmap.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=450)
        st.plotly_chart(fig_heatmap, use_container_width=True)

# ABA 3: INTELIGÊNCIA MACRO E DINÂMICA DE JUROS (DI)
with tab_analise_di:
    st.subheader("Análise de Intermercados e Curva Forward")
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.info("""
        **📌 A Lógica do Juro Futuro (DI):**
        O comportamento do DI é um dos principais termômetros de risco do mercado nacional.
        
        * **DI em Alta (Curva Estressada):** Sinaliza aposta em inflação maior ou risco fiscal. Isso retira capital da Bolsa (Renda Variável) e joga para a Renda Fixa.
        * **DI em Baixa (Curva Fechando):** Abre espaço para a valorização de ativos de crescimento na B3 (Varejo, Construção Civil e Tecnologia).
        """)
        
    with col_direita:
        st.success("""
        **🌍 Correlação México x Brasil:**
        O Índice do México (EWW) serve como um excelente par de comparação para o Ibovespa (EWZ). Como ambos são os maiores mercados emergentes da América Latina, grandes gestores globais costumam fazer arbitragem ou rotação de capital entre os dois países.
        """)
