import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sqlalchemy import create_engine
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Criminalidade no Brasil", layout="wide")



# Obter o diretório onde app.py está localizado
BASE_DIR = Path(__file__).parent

# Construir o caminho completo do arquivo de dados
csv_path = BASE_DIR / 'dados' / 'simulacao_criminalidade_brasil.csv'

df = pd.read_csv(csv_path)

df = carregar_dados()

# ---------- Título e Descrição ----------
st.title("📊 Criminalidade em Grandes Cidades Brasileiras")
st.markdown("""
Este dashboard apresenta uma análise exploratória dos dados simulados de criminalidade
em grandes cidades brasileiras. O objetivo é identificar padrões, KPIs e tendências
para apoiar a tomada de decisão em segurança pública.
""")

# ---------- Filtros Interativos (Funcionalidade Intermediária) ----------
st.sidebar.header("🔍 Filtros")

regioes = st.sidebar.multiselect("Região", sorted(df['regiao'].unique()),
                                 default=sorted(df['regiao'].unique()))
cidades = st.sidebar.multiselect("Cidade", sorted(df['cidade'].unique()),
                                 default=sorted(df['cidade'].unique()))
tipos = st.sidebar.multiselect("Tipo de Crime", sorted(df['tipo_crime'].unique()),
                               default=sorted(df['tipo_crime'].unique()))
periodos = st.sidebar.multiselect("Período do Dia", sorted(df['periodo_dia'].unique()),
                                  default=sorted(df['periodo_dia'].unique()))
anos = st.sidebar.slider("Ano", int(df['ano'].min()), int(df['ano'].max()),
                         (int(df['ano'].min()), int(df['ano'].max())))

df_f = df[
    (df['regiao'].isin(regioes)) &
    (df['cidade'].isin(cidades)) &
    (df['tipo_crime'].isin(tipos)) &
    (df['periodo_dia'].isin(periodos)) &
    (df['ano'].between(anos[0], anos[1]))
]

# ---------- KPIs Dinâmicos (Funcionalidade Intermediária) ----------
st.subheader("📈 KPIs Principais")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Ocorrências", f"{df_f['ocorrencias'].sum():,}")
col2.metric("Vítimas", f"{df_f['vitimas'].sum():,}")
col3.metric("Prisões", f"{df_f['prisoes'].sum():,}")
taxa = df_f['prisoes'].sum() / df_f['ocorrencias'].sum() if df_f['ocorrencias'].sum() > 0 else 0
col4.metric("Taxa de Prisão", f"{taxa:.1%}")
col5.metric("Índice Médio Violência", f"{df_f['indice_violencia'].mean():.2f}")

# ---------- Seções do Dashboard ----------
st.markdown("---")

# Seção 1: Análise por Região
st.subheader("🌎 Ocorrências por Região")
fig1, ax1 = plt.subplots(figsize=(10, 4))
df_f.groupby('regiao')['ocorrencias'].sum().sort_values().plot(kind='barh', ax=ax1, color='#c0392b')
ax1.set_xlabel("Ocorrências")
st.pyplot(fig1)

# Seção 2: Top 10 Cidades
st.subheader("🏙️ Top 10 Cidades com Mais Ocorrências")
top10 = df_f.groupby('cidade')['ocorrencias'].sum().nlargest(10).reset_index()
fig2 = px.bar(top10, x='ocorrencias', y='cidade', orientation='h',
              color='ocorrencias', color_continuous_scale='Reds')
st.plotly_chart(fig2, use_container_width=True)

# Seção 3: Tipo de Crime
st.subheader("🔫 Distribuição por Tipo de Crime")
fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.countplot(data=df_f, y='tipo_crime',
              order=df_f['tipo_crime'].value_counts().index,
              palette='Reds_r', ax=ax3)
st.pyplot(fig3)

# Seção 4: Análise Temporal (Funcionalidade Intermediária)
st.subheader("📅 Evolução Temporal das Ocorrências")
serie = df_f.groupby('ano_mes')['ocorrencias'].sum().reset_index()
fig4 = px.line(serie, x='ano_mes', y='ocorrencias', markers=True,
               title="Ocorrências por Mês")
st.plotly_chart(fig4, use_container_width=True)

# Seção 5: Heatmap Período x Crime
st.subheader("🔥 Heatmap: Período do Dia x Tipo de Crime")
pivot = df_f.pivot_table(values='ocorrencias', index='periodo_dia',
                         columns='tipo_crime', aggfunc='sum').fillna(0)
fig5, ax5 = plt.subplots(figsize=(10, 4))
sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Reds', ax=ax5)
st.pyplot(fig5)

# Seção 6: Nível de Risco
st.subheader("⚠️ Distribuição por Nível de Risco")
fig6 = px.pie(df_f, names='nivel_risco', values='ocorrencias',
              color='nivel_risco',
              color_discrete_map={'Baixo':'#2ecc71','Médio':'#f1c40f',
                                  'Alto':'#e67e22','Crítico':'#c0392b'})
st.plotly_chart(fig6, use_container_width=True)

# ---------- Tabela ----------
st.subheader("📋 Dados Filtrados")
st.dataframe(df_f.head(100))

# ---------- Interpretação Textual ----------
st.markdown("---")
st.subheader("🧠 Interpretação dos Resultados")
st.markdown(f"""
- Foram analisadas **{df_f['ocorrencias'].sum():,} ocorrências** no período selecionado.
- A região com mais ocorrências é **{df_f.groupby('regiao')['ocorrencias'].sum().idxmax()}**.
- A cidade mais crítica é **{df_f.groupby('cidade')['ocorrencias'].sum().idxmax()}**.
- O crime mais frequente é **{df_f.groupby('tipo_crime')['ocorrencias'].sum().idxmax()}**.
- O período do dia com mais ocorrências é **{df_f.groupby('periodo_dia')['ocorrencias'].sum().idxmax()}**.
- A taxa de prisão no período é de **{taxa:.1%}**, indicando a eficácia das ações policiais.
""")

# ---------- Conclusão Executiva ----------
st.subheader("✅ Conclusão Executiva")
st.success("""
A análise revela que a criminalidade se concentra em determinadas regiões e horários,
com destaque para crimes patrimoniais (Furto e Roubo). A taxa de prisão varia
significativamente, sugerindo oportunidades de melhoria na alocação de recursos.
Recomenda-se priorizar ações em cidades de nível de risco Crítico e nos períodos
Noturno e Madrugada.
""")
