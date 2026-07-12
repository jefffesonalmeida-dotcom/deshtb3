import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Configurações de Layout da Página (Modo Amplo e Fundo Escuro Mantido)
st.set_page_config(layout="wide", page_title="Cockpit Operacional Descomplica", page_icon="📈")

# Estilização CSS (Black Premium e Cores de Destaque da Referência)
st.markdown("""
    <style>
    .main { background-color: #0B0E14; }
    div[data-testid="stMetricValue"] { font-size: 26px; font-weight: bold; color: #FFFFFF; }
    div[data-testid="stMetricDelta"] { font-size: 14px; }
    h1, h2, h3, h4 { color: #E0E6ED; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stTabs [data-baseweb="tab"] { color: #8E9AA6; font-size: 16px; font-weight: 600; }
    .stTabs [data-baseweb="tab"]:hover { color: #00F2FE; }
    .stTabs [aria-selected="true"] { color: #00F2FE; border-bottom-color: #00F2FE; }
    .reportview-container .main .block-container{ padding-top: 1rem; }
    div.stSelectbox > div > div > div { color: #0B0E14; background-color: #FFFFFF; }
    div[data-testid="stMetric"] { border-radius: 8px; border: 1px solid #1E293B; background-color: #111827; padding: 10px; }
    .stDataFrame > div > div { border: 1px solid #1E293B; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNÇÕES E SIMULAÇÕES PARA REPLICAR A ESTRUTURA OPERACIONAL
# -----------------------------------------------------------------------------
@st.cache_data(ttl=120)
def obter_dados(ticker, janela_tempo):
    dias = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "YTD": 365}[janela_tempo]
    data_de_inicio = datetime.now() - timedelta(days=dias)
    if janela_tempo == "YTD":
        data_de_inicio = datetime(datetime.now().year, 1, 1)
        
    df = yf.download(ticker, start=data_de_inicio, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df

# Simulação fidedigna da estrutura operacional
def simular_operacoes():
    return pd.DataFrame({
        'Nome da Operação': ['Implementação do Cockpit B3', 'Setup de Alertas de Curva de DI', 'Análise de Matriz Setorial', 'Setup de Fluxo Operacional'],
        'Setor': ['Mercado', 'Risco Fiscal', 'Macro', 'Operacional'],
        'Responsável': ['João G.', 'Maria S.', 'Pedro L.', 'Ana P.'],
        'Progresso (%)': [100, 85, 95, 100],
        'Data Início': [datetime(2023, 10, 1), datetime(2023, 10, 5), datetime(2023, 10, 10), datetime(2023, 10, 15)],
        'Data Fim (Est.)': [datetime(2023, 11, 1), datetime(2023, 11, 15), datetime(2023, 11, 20), datetime(2023, 11, 25)]
    })

def simular_atividades_recentes():
    return [
        {"texto": "João G. concluiu o commit 'Ajuste final do layout Black'.", "timestamp": "há 2 min"},
        {"texto": "Maria S. iniciou a análise da curva DI longa (2031).", "timestamp": "há 15 min"},
        {"texto": "Pedro L. reportou desvio na correlação WTI vs Vale.", "timestamp": "há 45 min"},
        {"texto": "Ana P. concluiu a análise do fluxo de capital gringo.", "timestamp": "há 1h"}
    ]

# -----------------------------------------------------------------------------
# CABEÇALHO OPERACIONAL
# -----------------------------------------------------------------------------
st.title("🦅 Cockpit Operacional Descomplica — Painel Integrado B3")
col_info, col_status = st.columns([4, 1])
with col_info:
    st.caption(f"Operação Completa: Mercado, Risco e Desempenho Operacional • Atualizado em tempo real")
with col_status:
    st.success("🟢 SISTEMA OPERACIONAL")

st.markdown("---")

# =============================================================================
# SEÇÃO 1: VISÃO DE MERCADO E CONTEXTO OPERACIONAL (Cotações no Topo)
# =============================================================================
st.subheader("📊 Visão de Mercado e Contexto Operacional")
st.markdown("---")
ativos_macro = {
    "Ibovespa": "^BVSP",
    "Fluxo Gringo (EWZ)": "EWZ",
    "Petróleo (WTI)": "CL=F",
    "Minério (Vale)": "VALE3.SA",
    "Par Latino (EWW)": "EWW",
    "Dólar Futuro": "BRL=X"
}

# 1.1 Cartões de Cotação - Replicando o conceito operacional
col1, col2, col3, col4, col5, col6 = st.columns(6)
for idx, (nome, ticker) in enumerate(ativos_macro.items()):
    with [col1, col2, col3, col4, col5, col6][idx]:
        try:
            df_kpi = obter_dados(ticker, "1M")
            if not df_kpi.empty:
                f_atual = float(df_kpi['Close'].iloc[-1])
                f_anterior = float(df_kpi['Close'].iloc[-2])
                v_diaria = ((f_atual - f_anterior) / f_anterior) * 100
                st.metric(label=nome, value=f"{f_atual:,.2f}", delta=f"{v_diaria:+.2f}%")
        except:
            st.metric(label=nome, value="N/A", delta="0.00%")

st.markdown("---")

# =============================================================================
# SEÇÃO 2: GRÁFICO E ANÁLISE DE MERCADO (Gráfico no Meio)
# =============================================================================
# 2.1 Controles Laterais
st.sidebar.markdown("# 🕹️ Painel de Controle")
ativo_selecionado = st.sidebar.selectbox("Escolha o Ativo Principal:", list(ativos_macro.keys()), index=0)
periodo_grafico = st.sidebar.selectbox("Período Histórico:", ["1M", "3M", "6M", "1Y", "YTD"], index=1)
curva_di = st.sidebar.selectbox("Vencimento DI (Juros):", ["DI1F25", "DI1F27", "DI1F29"], index=1)

# 2.2 Gráfico de Mercado
st.subheader(f"📈 Gráfico Interativo de Mercado — {ativo_selecionado}")
st.markdown("---")
col_grafico, col_extra = st.columns([4, 1])

with col_grafico:
    df_dados = obter_dados(ativos_macro[ativo_selecionado], periodo_grafico)
    if not df_dados.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8])
        fig.add_trace(go.Candlestick(x=df_dados.index, open=df_dados['Open'], high=df_dados['High'], low=df_dados['Low'], close=df_dados['Close'], name="Preço"), row=1, col=1)
        fig.add_trace(go.Bar(x=df_dados.index, y=df_dados['Volume'], name="Volume", marker_color='#3A4D62'), row=2, col=1)
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with col_extra:
    st.info("""
    **Dica Operacional:**
    No site Descomplica, eles usam esta seção para análise de desempenho. Aqui nós usamos para análise de mercado, que é o motor da nossa operação. Use a Matriz de Correlação para refinar a análise.
    """)

st.markdown("---")

# =============================================================================
# SEÇÃO 3: REPLICANDO A ESTRUTURA OPERACIONAL COMPLETA (ROLANDO PARA BAIXO)
# =============================================================================
st.subheader("🔄 Estrutura Operacional Completa — Foco e Desempenho")
st.markdown("---")

col_left, col_right = st.columns([1, 1])

# 3.1 Seção Esquerda: Operações e Status
with col_left:
    st.markdown("#### 🔄 Operações em Andamento e Status do Cronograma")
    df_ops = simular_operacoes()
    
    # Gráfico de Progresso das Operações
    fig_prog = px.bar(df_ops, x='Progresso (%)', y='Nome da Operação', orientation='h', color='Progresso (%)', color_continuous_scale='RdBu_r', text_auto=True)
    fig_prog.update_layout(template="plotly_dark", xaxis_range=[0, 100], yaxis_tickangle=0, margin=dict(l=0, r=10, t=20, b=0), height=250, xaxis_title='Progresso (%)', yaxis_title='', showlegend=False)
    st.plotly_chart(fig_prog, use_container_width=True)
    
    st.markdown("#### 📋 Detalhe das Operações e Status")
    # Formatação condicional simples simulada na exibição da tabela
    st.dataframe(df_ops.style.format({'Data Início': '{:%Y-%m-%d}', 'Data Fim (Est.)': '{:%Y-%m-%d}'}), use_container_width=True)

# 3.2 Seção Direita: Risco e Atividades
with col_right:
    st.markdown("#### 🎯 Análise de Risco Operacional e Atividades")
    
    # Simulação de Matriz de Risco Setorial (Baseado no fluxo operacional)
    df_risco = pd.DataFrame({
        'Setor': ['Petróleo', 'Mineração', 'Bancos', 'Varejo', 'Tecnologia'],
        'Risco': [random.uniform(1, 10) for _ in range(5)],
        'Impacto': ['Médio', 'Baixo', 'Baixo', 'Alto', 'Médio']
    }).sort_values(by='Risco', ascending=False)
    
    fig_bar_risco = px.bar(df_risco, x='Setor', y='Risco', color='Impacto', color_discrete_map={'Alto': '#ef4444', 'Médio': '#f97316', 'Baixo': '#eab308'})
    fig_bar_risco.update_layout(template="plotly_dark", showlegend=True, height=250, margin=dict(l=0, r=0, t=20, b=0), xaxis_title='', yaxis_title='')
    st.plotly_chart(fig_bar_risco, use_container_width=True)
    
    # Atividades Recentes
    st.markdown("#### 📋 Feed de Atividades Recentes")
    st.markdown("---")
    for atividade in simular_atividades_recentes():
        st.markdown(f"> **{atividade['timestamp']}** | {atividade['texto']}")
        st.markdown("---")

st.markdown("---")

# =============================================================================
# SEÇÃO 4: ABAS DE INTELIGÊNCIA MACRO (MATRIZ NO FINAL)
# =============================================================================
st.subheader("🌐 Inteligência Macro e Dinâmica de Risco (Aba de Ferramentas)")
st.markdown("---")
tab_correl, tab_analise = st.tabs(["🧮 Matriz de Correlação Operacional", "🌍 Inteligência Intermercados e Juros"])

with tab_correl:
    st.subheader("Matriz de Correlação Operacional (Retornos Percentuais)")
    # Mantivemos a matriz que já tínhamos, que é essencial
    lista_retornos = []
    for nome, ticker in ativos_macro.items():
        df_c = obter_dados(ticker, periodo_grafico)
        if not df_c.empty:
            retornos_diarios = df_c['Close'].pct_change().dropna()
            retornos_diarios.name = nome.split(" (")[0]
            lista_retornos.append(retornos_diarios)
    if lista_retornos:
        df_final_corr = pd.concat(lista_retornos, axis=1).dropna()
        matriz = df_final_corr.corr()
        fig_hm = px.imshow(matriz, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, template="plotly_dark")
        fig_hm.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=450)
        st.plotly_chart(fig_hm, use_container_width=True)

with tab_analise:
    c_i_e, c_i_d = st.columns(2)
    with c_i_e:
        st.info("""
        **📌 A Lógica do Juro Futuro (DI) na B3:**
        O comportamento do DI é um dos principais termômetros de risco do mercado nacional.
        * **DI em Alta (Curva Estressada):** Sinaliza aposta em inflação maior ou risco fiscal. Isso retira capital da Bolsa e joga para a Renda Fixa.
        * **DI em Baixa (Curva Fechando):** Abre espaço para a valorização de ativos de crescimento na B3 (Varejo, Construção Civil e Tecnologia).
        """)
    with c_i_d:
        st.success("""
        **🌍 Correlação México x Brasil (EWW vs EWZ):**
        O Índice do México (EWW) serve como um excelente par de comparação para o Ibovespa dolarizado (EWZ). Como ambos são os maiores mercados emergentes da América Latina, grandes gestores globais costumam fazer arbitragem ou rotação de capital entre os dois países.
        Fique atento quando um mercado descolar drasticamente do outro!
        """)
