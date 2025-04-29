import streamlit as st# type: ignore
import pandas as pd# type: ignore
import plotly.express as px# type: ignore

# Supondo que 'df' já esteja carregado e 'dia_semana' e 'mortos' sejam colunas existentes
def morte_dia(df):
    dias = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado']
    soma_morte = df.groupby('dia_semana')['mortos'].sum().reindex(dias).fillna(0).reset_index()
    soma_morte.columns = ['dia_semana', 'total_mortes']

    # Gráfico do Total de Mortes por Dia da Semana
    st.subheader("💀 Total de Mortes por Dia da Semana")

    fig_mortes_dia = px.bar(soma_morte, x='dia_semana', y='total_mortes',
                        labels={'dia_semana': 'Dia da Semana', 'total_mortes': 'Total de Mortes'},
                        title="Total de Mortes em Acidentes por Dia da Semana")
    
    return fig_mortes_dia


