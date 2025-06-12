# Importação de bibliotecas
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import streamlit as st  # type: ignore
import plotly.express as px  # type: ignore
import locale  # type: ignore
import os  # type: ignore
import time  # type: ignore
import io  # type: ignore
from Graficos import graficos  # type: ignore
from Graficos.graficos import veiculos_por_horario


def gerar_csv(df):
    df_exportar = df.copy()
    for col in df_exportar.select_dtypes(include='object'):
        df_exportar[col] = df_exportar[col].fillna('').astype(str).str.strip()

    return df_exportar.to_csv(index=False, sep=';', encoding='utf-8-sig')


def pagina_inicial(pasta_destino_dados):
    print('-=' * 30)
    print('[LOG] -> Recarregando página inicial')
    print('-=' * 30)
    tempo_inicial = time.time()

    # Título e descrição da página
    st.title("Painel de Acidentes de Trânsito no Brasil (2021-2025)")

    # Carregar dados (cache para evitar recarregamento)
    if 'df' not in st.session_state:
        with st.spinner("Carregando dados de Acidentes (2021-2025)..."):
            st.session_state.df = carregar_dados(pasta_destino_dados)

    df = st.session_state.df

    # Filtros na barra lateral
    st.sidebar.header("Filtros")

    opcoes_ufs = sorted(df['uf'].dropna().unique())
    ufs_selecionados = st.sidebar.multiselect(
        "UF (Estado)", ["Todos"] + opcoes_ufs, default=["Todos"])
    ufs_filtrados = opcoes_ufs if "Todos" in ufs_selecionados else ufs_selecionados

    opcoes_anos = sorted(df['ano'].dropna().unique())
    anos_selecionados = st.sidebar.multiselect(
        "Ano", ["Todos"] + opcoes_anos, default=["Todos"])
    anos_filtrados = opcoes_anos if "Todos" in anos_selecionados else anos_selecionados

    opcoes_tipos = sorted(df['tipo_acidente'].dropna().unique())
    tipos_selecionados = st.sidebar.multiselect(
        "Tipo de Acidente", ["Todos"] + opcoes_tipos, default=["Todos"])
    tipos_filtrados = opcoes_tipos if "Todos" in tipos_selecionados else tipos_selecionados

    opcoes_sexos = sorted(
        df.loc[df['sexo'] != 'Ignorado', 'sexo'].dropna().unique())
    sexos_selecionados = st.sidebar.multiselect(
        "Sexo", ["Todos"] + opcoes_sexos, default=["Todos"])
    sexos_filtrados = opcoes_sexos if "Todos" in sexos_selecionados else sexos_selecionados

    intervalos = carrega_intervalos_horarios(df['horario'])
    opcoes_horarios = intervalos.unique().tolist()
    horarios_selecionados = st.sidebar.multiselect(
        "Horário", ["Todos"] + opcoes_horarios, default=["Todos"])
    horarios_filtrados = opcoes_horarios if "Todos" in horarios_selecionados else horarios_selecionados

    # Aplicando filtros
    df_filtrado = df[
        (df['uf'].isin(ufs_filtrados)) &
        (df['data_inversa'].dt.year.isin(anos_filtrados)) &
        (df['tipo_acidente'].isin(tipos_filtrados)) &
        (df['sexo'].isin(sexos_filtrados)) &
        (intervalos.isin(horarios_filtrados))
    ].copy()

    locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')

    # Indicadores gerais
    st.subheader("📊 Indicadores Gerais")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Acidentes", len(df_filtrado))
    col2.metric("Total de Estados (UFs)", len(df_filtrado['uf'].unique()))
    col3.metric("Tipos de Acidente", len(
        df_filtrado['tipo_acidente'].unique()))

    st.markdown("---")

    # Botão para baixar os dados filtrados em CSV
    csv_bytes = gerar_csv(df_filtrado)
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=csv_bytes,
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )

    # Abas para gráficos
    abas = st.tabs([
        "📅 Acidentes",
        "🏙️ Top 10",
        "♀♂ Sexo",
        "⏰ Horários Criticos",
        "🌦️ Condições Meteorológicas",
        "☠️ Mortes"
    ])

    with abas[0]:
        st.subheader("📅 Evolução de Acidentes por Mês")
        fig = graficos.acidente_mes(df_filtrado)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🚗 Tipos de Acidente")
        fig2 = graficos.tipos_acidente(df_filtrado)
        st.plotly_chart(fig2, use_container_width=True)

    with abas[1]:
        st.subheader("🏙️ Top 10 Municípios com Mais Acidentes")
        st.plotly_chart(graficos.top10_municipios(
            df_filtrado), use_container_width=True)

        st.subheader("🏙️ Top 10 Municípios com Mais Mortes")
        st.plotly_chart(graficos.top10_municipios_mortes(
            df_filtrado), use_container_width=True)

        st.subheader("🛣️ Top 10 BRs com Mais Acidentes")
        st.plotly_chart(graficos.top10_brs(df_filtrado),
                        use_container_width=True)

        st.subheader("🚗 Top 10 Tipos de Veículo")
        grafico07, dados07 = graficos.tipo_veiculo(df_filtrado, 10)
        st.plotly_chart(grafico07, use_container_width=True)
        st.dataframe(dados07, hide_index=True)

    with abas[2]:
        st.subheader("♀♂ Sexo com Mais Acidentes por Ano")
        st.plotly_chart(graficos.sexo_acidentes(
            df_filtrado), use_container_width=True)

        st.subheader("🚑 Lesões por Sexo")
        st.plotly_chart(graficos.lesoes_sexo(
            df_filtrado), use_container_width=True)

    with abas[3]:
        st.subheader("⏰ Distribuição de Acidentes por Horário")
        st.plotly_chart(graficos.horarios_acidentes(
            df_filtrado), use_container_width=True)

        st.subheader("🚗 Tipos de Veículos em Acidentes por Horário")
        fig = veiculos_por_horario(df_filtrado)
        st.plotly_chart(fig, use_container_width=True)

    with abas[4]:
        st.subheader("🌦️ Condição Meteorológica")
        grafico08, dados08 = graficos.condicao_metereologica(df_filtrado, 7)
        st.plotly_chart(grafico08, use_container_width=True)
        st.dataframe(dados08, hide_index=True)

    with abas[5]:
        st.subheader("☠️ Total de Mortes por Dia da Semana")
        st.plotly_chart(graficos.morte_dia(df_filtrado),
                        use_container_width=True)

        st.subheader("☠️ Total de Mortes por Tipo de Acidente")
        graficos.mortes_por_tipo_acidente(df_filtrado)

        st.subheader("☠️ Total de Mortes por Faixa Etária e Sexo")
        graficos.mortes_por_faixa_etaria_e_sexo(df_filtrado)

    st.markdown("---")
    st.caption(
        "Fonte: Polícia Rodoviária Federal (PRF) • Projeto Integrador III - Ciência de Dados")

    print(
        f"Tempo de carregamento da Página: {time.time() - tempo_inicial:.2f}")


@st.cache_data
def carregar_dados(pasta_destino_dados):
    nome_arquivos = ['acidentes2021.csv', 'acidentes2022.csv',
                     'acidentes2023.csv', 'acidentes2024.csv', 'acidentes2025.csv']
    lista_df = []

    for arq in nome_arquivos:
        df = pd.read_csv(os.path.join(pasta_destino_dados, arq),
                         sep=";", encoding="utf-8", low_memory=False, dtype=str)
        df.columns = df.columns.str.strip().str.replace('ï»¿', '')
        lista_df.append(df)

    df = pd.concat(lista_df, ignore_index=True)
    df['data_inversa'] = pd.to_datetime(
        df['data_inversa'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['data_inversa'])

    df['ano'] = df['data_inversa'].dt.year
    df['mes'] = df['data_inversa'].dt.to_period('M')

    ufs_validas = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                   'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                   'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    df = df[df['uf'].isin(ufs_validas)].dropna()

    return df


def carrega_intervalos_horarios(serie, inter_minutos=60):
    INTERVALOS_EM_MINUTOS = pd.to_datetime(
        serie, errors='coerce').dt.hour * 60 + pd.to_datetime(serie, errors='coerce').dt.minute
    bins = list(range(0, 24*60 + inter_minutos, inter_minutos))

    labels = [
        f"{h:02d}:{m:02d} - {h2:02d}:{m2:02d}"
        for h, m, h2, m2 in [
            (divmod(b, 60)[0], divmod(b, 60)[1],
             divmod(b + inter_minutos, 60)[0] % 24, divmod(b + inter_minutos, 60)[1])
            for b in bins[:-1]
        ]
    ]

    intervalos = pd.cut(
        INTERVALOS_EM_MINUTOS,
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    return intervalos
