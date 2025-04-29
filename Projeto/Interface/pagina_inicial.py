# Importação de bibliotecas
import pandas as pd  # type: ignore
import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import locale  # type: ignore
import os # type: ignore


def pagina_inicial(pasta_destino_dados):
    # Configurações da página
    st.set_page_config(
        page_title="Acidentes de Trânsito no Brasil",
        page_icon="🚗",
        layout="wide"
    )

    # Título principal
    st.title("Painel de Acidentes de Trânsito no Brasil (2021-2025)")

    # Carregar dados
    df = carregar_dados(pasta_destino_dados)

    # Barra lateral - Filtros
    st.sidebar.header("Filtros")

    ufs = st.sidebar.multiselect(
        "UF (Estado)",
        options=sorted(df['uf'].unique()),
        default=sorted(df['uf'].unique())
    )

    anos = st.sidebar.multiselect(
        "Ano",
        options=sorted(df['data_inversa'].dt.year.unique()),
        default=[2021, 2022, 2023, 2024, 2025]
    )

    tipos = st.sidebar.multiselect(
        "Tipo de Acidente",
        options=sorted(df['tipo_acidente'].dropna().unique()),
        default=sorted(df['tipo_acidente'].dropna().unique())
    )

    # Filtro de Sexo (sem "Ignorado")
    sexos = st.sidebar.multiselect(
        "Sexo",
        options=sorted(df[df['sexo'] != 'Ignorado']
                    ['sexo'].dropna().unique()),  # Excluindo "Ignorado"
        default=sorted(df[df['sexo'] != 'Ignorado']
                    ['sexo'].dropna().unique())  # Excluindo "Ignorado"
    )

    # Aplicar filtros
    df_filtrado = df[
        (df['uf'].isin(ufs)) &
        (df['data_inversa'].dt.year.isin(anos)) &
        (df['tipo_acidente'].isin(tipos)) &
        (df['sexo'].isin(sexos))
    ].copy()

    # Indicadores principais
    st.subheader("📊 Indicadores Gerais")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Acidentes", len(df_filtrado))
    col2.metric("Total de Estados (UFs)", len(df_filtrado['uf'].unique()))
    col3.metric("Tipos de Acidente", len(df_filtrado['tipo_acidente'].unique()))

    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')

    # Gráfico 1 - Acidentes por Mês
    st.subheader("📅 Acidentes por Mês")
    df_mes = df_filtrado.groupby(df_filtrado['data_inversa'].dt.to_period(
        'M')).size().reset_index(name='Quantidade')
    df_mes['data'] = df_mes['data_inversa'].dt.to_timestamp(
    ).dt.strftime('%B/%Y').str.capitalize()

    fig1 = px.line(df_mes, x='data', y='Quantidade', markers=True,
                title="Evolução Mensal dos Acidentes")
    fig1.update_layout(xaxis_title="Mês/Ano")

    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2 - Tipos de Acidente
    st.subheader("🚗 Tipos de Acidentes")
    df_tipos = df_filtrado['tipo_acidente'].value_counts().reset_index()
    df_tipos.columns = ['tipo_acidente', 'count']
    fig2 = px.bar(df_tipos, x='tipo_acidente', y='count',
                labels={'tipo_acidente': 'Tipo de Acidente',
                        'count': 'Quantidade'},
                title="Distribuição dos Tipos de Acidente")
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3 - Top 10 Municípios com Mais Acidentes
    st.subheader("🏙️ Top 10 Municípios com Mais Acidentes")

    # Filtragem conforme os critérios aplicados (ano, uf, tipo de acidente)
    df_filtrado = df[(df['uf'].isin(ufs)) & (
        df['data_inversa'].dt.year.isin(anos)) & (df['tipo_acidente'].isin(tipos))].copy()

    # Contagem de acidentes por município e ordenação
    df_municipios = df_filtrado['municipio'].value_counts().reset_index()
    df_municipios.columns = ['municipio', 'quantidade']

    # Selecionando os top 10 municípios
    df_top10_municipios = df_municipios.head(10)

    # Gráfico de barras para os 10 municípios
    fig3 = px.bar(df_top10_municipios, x='municipio', y='quantidade',
                labels={'municipio': 'Município',
                        'quantidade': 'Número de Acidentes'},
                title="Top 10 Municípios Brasileiros com Mais Acidentes")
    st.plotly_chart(fig3, use_container_width=True)

    # Gráfico 4 - Sexo com Mais Acidentes por Ano
    st.subheader("♀♂ Sexo com Mais Acidentes por Ano")

    # Garantir que a coluna 'data_inversa' esteja em formato datetime
    df_filtrado['data_inversa'] = pd.to_datetime(
        df_filtrado['data_inversa'], errors='coerce')

    # Remover o valor "Ignorado" da coluna sexo
    df_sexo_ano = df_filtrado[df_filtrado['sexo'].str.strip().isin(
        ['Masculino', 'Feminino', 'Não Informado'])]

    # Contagem de acidentes por sexo e ano
    df_sexo_ano = df_sexo_ano.groupby([df_sexo_ano['data_inversa'].dt.year, 'sexo']).size(
    ).reset_index(name='Quantidade de Acidentes')


    # Gráfico de barras agrupadas - Acidentes por Sexo ao longo dos anos
    fig_sexo_ano = px.bar(df_sexo_ano, x='data_inversa', y='Quantidade de Acidentes', color='sexo',
                        title="Evolução de Acidentes por Sexo ao Longo dos Anos",
                        labels={
                            'data_inversa': 'Ano', 'Quantidade de Acidentes': 'Número de Acidentes', 'sexo': 'Sexo'},
                        barmode='group',  # Usando o barmode para agrupar as barras
                        color_discrete_map={'F': 'pink', 'M': 'green', 'Não Informado': 'gray'})

    # Exibir o gráfico
    st.plotly_chart(fig_sexo_ano, use_container_width=True)

    # Gráfico 5 - Lesões por Sexo
    st.subheader("🚑 Lesões por Sexo")

    # Exemplo de estrutura para agregação (substitua pelo seu df_filtrado real)
    df_filtrado['ano'] = df_filtrado['data_inversa'].dt.year

    # Agrupamento por ano e sexo, somando as variáveis de interesse
    df_grouped = df_filtrado.groupby(['ano', 'sexo'])[
        ['mortos', 'feridos_graves', 'feridos_leves', 'ilesos']
    ].sum().reset_index()

    # Criar figura com múltiplos eixos y
    fig = go.Figure()

    # Lista de consequências
    consequencias = ['mortos', 'feridos_graves', 'feridos_leves', 'ilesos']
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

    st.plotly_chart(fig, use_container_width=True)

    # Gráfico 1 e 2 - Sunburst para 'tipo_veiculo' e 'condicao_metereologica' em colunas
    col1, col2 = st.columns(2)

    # Gráfico 1 - Sunburst para 'tipo_veiculo'
    with col1:
        st.subheader("🚗 Tipos de Veículo")

        # Garantir que a coluna 'tipo_veiculo' seja do tipo string
        df_filtrado['tipo_veiculo'] = df_filtrado['tipo_veiculo'].astype(str)

        # Criar o gráfico Sunburst para tipo_veiculo
        fig_tipo_veiculo = px.sunburst(df_filtrado, path=['tipo_veiculo'],
                                    title="Distribuição dos Tipos de Veículo")
        st.plotly_chart(fig_tipo_veiculo, use_container_width=True)

    # Gráfico 2 - Sunburst para 'condicao_metereologica'
    with col2:
        st.subheader("🌦️ Condição Meteorológica")

        # Garantir que a coluna 'condicao_metereologica' seja do tipo string
        df_filtrado['condicao_metereologica'] = df_filtrado['condicao_metereologica'].astype(str)

        # Criar o gráfico Sunburst para condicao_metereologica
        fig_condicao_metereologica = px.sunburst(df_filtrado, path=['condicao_metereologica'],
                                                title="Distribuição das Condições Meteorológicas")
        st.plotly_chart(fig_condicao_metereologica, use_container_width=True)


    # Rodapé
    st.markdown("---")
    st.caption(
        "Fonte: Polícia Rodoviária Federal (PRF) • Projeto Integrador III - Ciência de Dados")


# Função para carregar dados
@st.cache_data
def carregar_dados(pasta_destino_dados):
    # Carregar dados com tratamento para BOM (Byte Order Mark)

    nome_arquivos = [
        'acidentes2021.csv',
        'acidentes2022.csv',
        'acidentes2023.csv',
        'acidentes2024.csv',
        'acidentes2025.csv',
    ]

    """
    # Detalhes dos dados presentes na lista: lista_df[]
    lista_df[0] = df_2021
    lista_df[1] = df_2022
    lista_df[2] = df_2023
    lista_df[3] = df_2024
    lista_df[4] = df_2025
    """
    lista_df = []

    for arq in nome_arquivos:
        lista_df.append(pd.read_csv(f"{pasta_destino_dados + os.sep + arq}", sep=";",
                        encoding="utf-8", low_memory=False))

    # Remover qualquer coluna com nomes estranhos
    lista_df[2].columns = lista_df[2].columns.str.strip().str.replace('ï»¿', '')
    lista_df[3].columns = lista_df[3].columns.str.strip().str.replace('ï»¿', '')

    # Renomear as colunas para corrigir quaisquer problemas de codificação
    lista_df[2].columns = lista_df[2].columns.str.strip()
    lista_df[3].columns = lista_df[3].columns.str.strip()

    # Concatenar os DataFrames
    df = pd.concat([lista_df[0], lista_df[1], lista_df[2], lista_df[3],
                lista_df[4]], ignore_index=True)

    # Converter datas e limpar
    df['data_inversa'] = pd.to_datetime(
        df['data_inversa'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['data_inversa'])

    # Lista de UFs válidas
    ufs_validas = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]

    # Filtrar apenas UFs válidas
    df = df[df['uf'].isin(ufs_validas)]

    return df