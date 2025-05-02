# Importação de bibliotecas
import pandas as pd  # type: ignore
import numpy as np # type: ignore
import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import locale  # type: ignore
import os # type: ignore
import time # type: ignore
from Graficos import graficos # type: ignore


def pagina_inicial(pasta_destino_dados):
    print('-=' * 30)
    print('[LOG] -> Recarregando página inicial')
    print('-=' * 30)
    tempo_inicial = time.time()

    # Configurações da página
    st.set_page_config(
        page_title="Acidentes de Trânsito no Brasil",
        page_icon="🚗",
        layout="wide"
    )

    # Título principal
    st.title("Painel de Acidentes de Trânsito no Brasil (2021-2025)")

    # Carregar dados
    if 'df' not in st.session_state:
        with st.spinner("Carregando dados de Acidentes (2021-2025)..."):
            st.session_state.df = carregar_dados(pasta_destino_dados)
        st.success("Dados Carregados com sucesso!")

    df = st.session_state.df

    # Barra lateral - Filtros
    st.sidebar.header("Filtros")

    # Filtro UF (Estado)
    opcoes_ufs = sorted(df['uf'].dropna().unique())
    opcoes_ufs_com_todos = ["Todos"] + opcoes_ufs
    ufs_selecionados = st.sidebar.multiselect(
        "UF (Estado)",
        options=opcoes_ufs_com_todos,
        default=["Todos"]
    )
    ufs_filtrados = opcoes_ufs if "Todos" in ufs_selecionados else ufs_selecionados

    # Filtro Ano
    opcoes_anos = sorted(df['ano'].dropna().unique())
    opcoes_anos_com_todos = ["Todos"] + opcoes_anos
    anos_selecionados = st.sidebar.multiselect(
        "Ano",
        options=opcoes_anos_com_todos,
        default=["Todos"]
    )
    anos_filtrados = opcoes_anos if "Todos" in anos_selecionados else anos_selecionados

    # Filtro Tipo de Acidente
    opcoes_tipos = sorted(df['tipo_acidente'].dropna().unique())
    opcoes_tipos_com_todos = ["Todos"] + opcoes_tipos
    tipos_selecionados = st.sidebar.multiselect(
        "Tipo de Acidente",
        options=opcoes_tipos_com_todos,
        default=["Todos"]
    )
    tipos_filtrados = opcoes_tipos if "Todos" in tipos_selecionados else tipos_selecionados

    # Filtro Sexo (sem "Ignorado")
    opcoes_sexos = sorted(df.loc[df['sexo'] != 'Ignorado', 'sexo'].dropna().unique())
    opcoes_sexos_com_todos = ["Todos"] + opcoes_sexos
    sexos_selecionados = st.sidebar.multiselect(
        "Sexo",
        options=opcoes_sexos_com_todos,
        default=["Todos"]
    )
    sexos_filtrados = opcoes_sexos if "Todos" in sexos_selecionados else sexos_selecionados

    # Novo filtro para Horário
    intervalo_de_minutos = 60 # Intervalo de minutos utiulizado pela função para criar os filtros.
    intervalos = carrega_intervalos_horarios(df['horario'], intervalo_de_minutos)

    # Obter todas as opções de intervalos únicas
    opcoes_horarios = intervalos.unique().tolist()

    # Adiciona a opção "Todos" no topo da lista
    opcoes_horarios_com_todos = ["Todos"] + opcoes_horarios

    # Componente multiselect com "Todos"
    horarios_selecionados = st.sidebar.multiselect(
        "Horário",
        options=opcoes_horarios_com_todos,
        default=["Todos"]
    )

    # Se "Todos" estiver selecionado, considerar todas as opções (exceto o próprio "Todos")
    if "Todos" in horarios_selecionados:
        horarios_filtrados = opcoes_horarios  # Todas as opções reais
    else:
        horarios_filtrados = horarios_selecionados

    # Aplicar os filtros
    df_filtrado = df[
        (df['uf'].isin(ufs_filtrados)) &
        (df['data_inversa'].dt.year.isin(anos_filtrados)) &
        (df['tipo_acidente'].isin(tipos_filtrados)) &
        (df['sexo'].isin(sexos_filtrados)) &
        (intervalos.isin(horarios_filtrados))
    ].copy()


    # Indicadores principais
    st.subheader("📊 Indicadores Gerais")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Acidentes", len(df_filtrado))
    col2.metric("Total de Estados (UFs)", len(df_filtrado['uf'].unique()))
    col3.metric("Tipos de Acidente", len(df_filtrado['tipo_acidente'].unique()))

    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')

    st.html('<hr>')
    
    # Gráfico 1 - Acidentes por Mês
    with st.spinner('Carregando Gráfico 01...'):
        st.subheader("📅 Acidentes por Mês")
        grafico01 = graficos.acidente_mes(df_filtrado)
        st.plotly_chart(grafico01, use_container_width=True)

    st.html('<hr>')

    # Gráfico 2 - Tipos de Acidente
    with st.spinner('Carregando Gráfico 02...'):
        st.subheader("🚗 Tipos de Acidentes")
        grafico02 = graficos.tipos_acidente(df_filtrado)
        st.plotly_chart(grafico02, use_container_width=True)

    st.html('<hr>')

    # Gráfico 3 - Top 10 Municípios com Mais Acidentes
    with st.spinner('Carregando Gráfico 03...'):
        st.subheader("🏙️ Top 10 Municípios com Mais Acidentes")
        grafico03 = graficos.top10_municipios(df_filtrado)
        st.plotly_chart(grafico03, use_container_width=True)

    st.html('<hr>')

    # Gráfico 4 - Sexo com Mais Acidentes por Ano
    with st.spinner('Carregando Gráfico 04...'):
        st.subheader("♀♂ Sexo com Mais Acidentes por Ano")
        grafico04 = graficos.sexo_acidentes(df_filtrado)
        st.plotly_chart(grafico04, use_container_width=True)

    st.html('<hr>')

    # Gráfico 05 - Lesões por Sexo
    with st.spinner('Carregando o Gráfico 05...'):
        st.subheader("🚑 Lesões por Sexo")
        grafico05 = graficos.lesoes_sexo(df_filtrado)
        st.plotly_chart(grafico05, use_container_width=True)
    
    st.html('<hr>')

    # Gráfico 06 - Distribuição de Acidentes por Horário
    with st.spinner('Carregando o Gráfico 06....'):
        st.subheader("⏰ Distribuição de Acidentes por Horário")
        grafico06 = graficos.horarios_acidentes(df_filtrado)
        st.plotly_chart(grafico06, use_container_width=True)

    st.html('<hr>')

    # Gráfico 07 e 08 - Sunburst para 'tipo_veiculo' e 'condicao_metereologica' em colunas
    with st.spinner('Carregando Gráficos 07 e 08...'):
        col1, col2 = st.columns(2)

        # Gráfico 07 - Sunburst para 'tipo_veiculo'
        with col1:
            st.subheader("🚗 Tipos de Veículo")
            grafico07, dados_grafico07 = graficos.tipo_veiculo(df_filtrado, 10)
            st.plotly_chart(grafico07, use_container_width=True)

            st.dataframe(dados_grafico07, hide_index=True)


        # Gráfico 8 - Sunburst para 'condicao_metereologica'
        with col2:
            st.subheader("🌦️ Condição Meteorológica")
            grafico08, dados_grafico08 = graficos.condicao_metereologica(df_filtrado, 7)           
            st.plotly_chart(grafico08, use_container_width=True)

            st.dataframe(dados_grafico08, hide_index=True, )
    
    st.html('<hr>')

    grafico09 = graficos.morte_dia(df_filtrado)
    st.plotly_chart(grafico09, use_container_width=True)
    

    # Rodapé
    st.markdown("---")
    st.caption(
        "Fonte: Polícia Rodoviária Federal (PRF) • Projeto Integrador III - Ciência de Dados")


    print(f"Tempo de carregamento da Página: {time.time() - tempo_inicial:.2f}")


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
        lista_df.append(pd.read_csv(os.path.join(pasta_destino_dados, arq), sep=";",
                        encoding="utf-8", low_memory=False, dtype=str))

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

    df['ano'] = df['data_inversa'].dt.year
    df['mes'] = df['data_inversa'].dt.to_period('M')

    # Lista de UFs válidas
    ufs_validas = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]

    # Filtrar apenas UFs válidas
    df = df[df['uf'].isin(ufs_validas)]
    
    # Exclui os valores  nulos do DF
    df = df.dropna()

    df = pd.DataFrame(df)

    return df


def carrega_intervalos_horarios(serie, inter_minutos=60):
    # Converter horário para minutos totais
    serie = pd.to_datetime(serie, errors='coerce', format='%d/%m/%Y')
    INTERVALOS_EM_MINUTOS = serie.dt.hour * 60 + serie.dt.minute

    bins = list(range(0, 24*60 + inter_minutos, inter_minutos))  # [0, 30, 60, ..., 1440]

    # Criar os labels para cada intervalo
    labels = [
        f"{h:02d}:{m:02d} - {h2:02d}:{m2:02d}"
        for h, m, h2, m2 in [
            (divmod(b, 60)[0], divmod(b, 60)[1],
             divmod(b + inter_minutos, 60)[0] % 24, divmod(b + inter_minutos, 60)[1])
            for b in bins[:-1]
        ]
    ]

    # Mapear cada valor da série para o intervalo correspondente
    intervalos = pd.cut(
        INTERVALOS_EM_MINUTOS,
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    return intervalos