import streamlit as st# type: ignore
import pandas as pd# type: ignore
import plotly.express as px# type: ignore


# Gráfico 01
def acidente_mes(df):
    df_mes = df.groupby(df['mes']).size().reset_index(name='Quantidade')
    df_mes['data'] = df_mes['mes'].dt.to_timestamp(
    ).dt.strftime('%B/%Y').str.capitalize()

    fig = px.line(df_mes, x='data', y='Quantidade', markers=True,
                title="Evolução Mensal dos Acidentes")
    fig.update_layout(xaxis_title="Mês/Ano")

    return fig


# Gráfico 02
def tipos_acidente(df):
    df_tipos = df['tipo_acidente'].value_counts().reset_index()
    df_tipos.columns = ['tipo_acidente', 'count']
    
    fig = px.bar(df_tipos, x='tipo_acidente', y='count',
                labels={'tipo_acidente': 'Tipo de Acidente',
                        'count': 'Quantidade'},
                title="Distribuição dos Tipos de Acidente")

    return fig


# Gráfico 03
def top10_municipios(df):
    # Contagem de acidentes por município e ordenação
    df_municipios = df['municipio'].value_counts().reset_index()
    df_municipios.columns = ['municipio', 'quantidade']

    # Selecionando os top 10 municípios
    df_top10_municipios = df_municipios.head(10)

    # Gráfico de barras para os 10 municípios
    fig = px.bar(df_top10_municipios, x='municipio', y='quantidade',
                labels={'municipio': 'Município',
                        'quantidade': 'Número de Acidentes'},
                title="Top 10 Municípios Brasileiros com Mais Acidentes")

    return fig


# Gráfico 04
def sexo_acidentes(df):
    # Remover o valor "Ignorado" da coluna sexo
    df_sexo_ano = df[df['sexo'].str.strip().isin(
        ['Masculino', 'Feminino', 'Não Informado'])]

    # Contagem de acidentes por sexo e ano
    df_sexo_ano = df_sexo_ano.groupby([df['ano'], 'sexo']).size(
    ).reset_index(name='Quantidade de Acidentes')


    # Gráfico de barras agrupadas - Acidentes por Sexo ao longo dos anos
    fig = px.bar(df_sexo_ano, x='ano', y='Quantidade de Acidentes', color='sexo',
                        title="Evolução de Acidentes por Sexo ao Longo dos Anos",
                        labels={
                            'ano': 'Ano', 'Quantidade de Acidentes': 'Número de Acidentes', 'sexo': 'Sexo'},
                        barmode='group',  # Usando o barmode para agrupar as barras
                        color_discrete_map={'F': 'pink', 'M': 'green', 'Não Informado': 'gray'})

    return fig


# Gráfico 05
def lesoes_sexo(df):
    import plotly.graph_objects as go  # type: ignore

    colunas = ['mortos', 'feridos_graves', 'feridos_leves', 'ilesos']

    # Agrupamento por ano e sexo, somando as variáveis de interesse
    df[colunas] = df[colunas].astype('Int16')
    df_grouped = df.groupby(['ano', 'sexo'])[colunas].sum().reset_index()

    # Criar figura com múltiplos eixos y
    fig = go.Figure()

    # Lista de consequências
    consequencias = colunas
    cores = ['red', 'orange', 'blue', 'green']

    # Adicionar linhas para cada variável, separadas por sexo
    for i, var in enumerate(consequencias):
        fig.add_trace(go.Scatter(
            x=df_grouped[df_grouped['sexo'] == 'Feminino']['ano'],
            y=df_grouped[df_grouped['sexo'] == 'Feminino'][var],
            mode='lines+markers',
            name=f'{var.capitalize()} (F)',
            line=dict(color=cores[i], dash='solid')
        ))
        fig.add_trace(go.Scatter(
            x=df_grouped[df_grouped['sexo'] == 'Masculino']['ano'],
            y=df_grouped[df_grouped['sexo'] == 'Masculino'][var],
            mode='lines+markers',
            name=f'{var.capitalize()} (M)',
            line=dict(color=cores[i], dash='dash')
        ))

    fig.update_layout(
        title="Consequências dos Acidentes por Sexo e Ano",
        xaxis_title="Ano",
        yaxis_title="Quantidade",
        legend_title="Variáveis por Sexo",
        template="plotly_white"
    )

    return fig


# Gráfico 06
def horarios_acidentes(df):
    df_horario = df['horario'].value_counts().sort_index().reset_index()
    df_horario.columns = ['horario', 'quantidade']

    fig = px.bar(df_horario, x='horario', y='quantidade',
                        labels={'horario': 'Horário', 'quantidade': 'Número de Acidentes'},
                        title="Número de Acidentes por Horário do Dia")

    return fig


# Gráfico 07
def tipo_veiculo(df, top_num):
    # Conta as ocorrências
    df_tipo_veiculo = df['tipo_veiculo'].value_counts().reset_index()

    df_tipo_veiculo.rename(columns={'tipo_veiculo': 'Tipo de Veículo', 'count': 'Quantidade'}, inplace=True)
    
    top = df_tipo_veiculo.head(top_num)

    # Criar o gráfico Sunburst para tipo_veiculo
    fig = px.pie(top, values=top['Quantidade'], names=top['Tipo de Veículo'],
                                title=f"Distribuição dos Tipos de Veículo (TOP {top_num})", hole=0.5)

    return  fig, df_tipo_veiculo


# Gráfico 08
def condicao_metereologica(df, top_num=10):
     # Garantir que a coluna 'condicao_metereologica' seja do tipo string
    df_condicao_metereologica = df['condicao_metereologica'].value_counts().reset_index()

    df_condicao_metereologica.rename(columns={'condicao_metereologica': 'Condição Meteorológica', 'count': 'Quantidade'}, inplace=True)

    top = df_condicao_metereologica.head(top_num)

    # Criar o gráfico Sunburst para condicao_metereologica
    fig = px.pie(top, values=top['Quantidade'], names=top['Condição Meteorológica'],
                                            title=f"Distribuição das Condições Meteorológicas (TOP {top_num})")
    
    return fig, df_condicao_metereologica


# Gráfico 09
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
