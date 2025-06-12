import plotly.express as px  # type: ignore
import streamlit as st  # type: ignore
import pandas as pd    # type: ignore


def acidente_mes(df):
    df_mes = df.groupby(df['mes']).size().reset_index(name='Quantidade')
    df_mes['data'] = df_mes['mes'].dt.to_timestamp(
    ).dt.strftime('%B/%Y').str.capitalize()

    fig = px.line(df_mes, x='data', y='Quantidade', markers=True,)
    fig.update_layout(xaxis_title="Mês/Ano")

    return fig


def tipos_acidente(df):
    df_tipos = df['tipo_acidente'].value_counts().reset_index()
    df_tipos.columns = ['tipo_acidente', 'count']

    fig = px.bar(df_tipos, x='tipo_acidente', y='count',
                 labels={'tipo_acidente': 'Tipo de Acidente',
                         'count': 'Quantidade'},)

    return fig


def top10_municipios(df):
    df_municipios = df['municipio'].value_counts().reset_index()
    df_municipios.columns = ['municipio', 'quantidade']
    df_top10_municipios = df_municipios.head(10)
    fig = px.bar(df_top10_municipios, x='municipio', y='quantidade',
                 labels={'municipio': 'Município',
                         'quantidade': 'Número de Acidentes'},
                 )

    return fig


def sexo_acidentes(df):
    df_sexo_ano = df[df['sexo'].str.strip().isin(
        ['Masculino', 'Feminino', 'Não Informado'])]
    df_sexo_ano = df_sexo_ano.groupby([df['ano'], 'sexo']).size(
    ).reset_index(name='Quantidade de Acidentes')
    fig = px.bar(df_sexo_ano, x='ano', y='Quantidade de Acidentes', color='sexo',
                 labels={
                     'ano': 'Ano', 'Quantidade de Acidentes': 'Número de Acidentes', 'sexo': 'Sexo'},
                 barmode='group',  # Usando o barmode para agrupar as barras
                 color_discrete_map={'F': 'pink', 'M': 'green', 'Não Informado': 'gray'})

    return fig


def lesoes_sexo(df):
    import plotly.graph_objects as go  # type: ignore

    colunas = ['mortos', 'feridos_graves', 'feridos_leves', 'ilesos']
    df[colunas] = df[colunas].astype('Int16')
    df_grouped = df.groupby(['ano', 'sexo'])[colunas].sum().reset_index()
    fig = go.Figure()
    consequencias = colunas
    cores = ['red', 'orange', 'blue', 'green']
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


def horarios_acidentes(df):
    df_horario = df['horario'].value_counts().sort_index().reset_index()
    df_horario.columns = ['horario', 'quantidade']

    fig = px.bar(df_horario, x='horario', y='quantidade',
                 labels={'horario': 'Horário',
                         'quantidade': 'Número de Acidentes'},
                 title="Número de Acidentes por Horário do Dia")

    return fig


def tipo_veiculo(df, top_num):
    df_tipo_veiculo = df['tipo_veiculo'].value_counts().reset_index()
    df_tipo_veiculo.rename(
        columns={'tipo_veiculo': 'Tipo de Veículo', 'count': 'Quantidade'}, inplace=True)
    top = df_tipo_veiculo.head(top_num)
    fig = px.pie(top, values=top['Quantidade'], names=top['Tipo de Veículo'],)

    return fig, df_tipo_veiculo


def condicao_metereologica(df, top_num=10):
    df_condicao_metereologica = df['condicao_metereologica'].value_counts(
    ).reset_index()
    df_condicao_metereologica.rename(columns={
                                     'condicao_metereologica': 'Condição Meteorológica', 'count': 'Quantidade'}, inplace=True)
    top = df_condicao_metereologica.head(top_num)
    fig = px.pie(top, values=top['Quantidade'], names=top['Condição Meteorológica'],
                 title=f"Distribuição das Condições Meteorológicas (TOP {top_num})")

    return fig, df_condicao_metereologica


def morte_dia(df):
    dias = ['domingo', 'segunda-feira', 'terça-feira',
            'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado']
    soma_morte = df.groupby('dia_semana')['mortos'].sum().reindex(
        dias).fillna(0).reset_index()
    soma_morte.columns = ['dia_semana', 'total_mortes']

    fig_mortes_dia = px.bar(soma_morte, x='dia_semana', y='total_mortes',
                            labels={'dia_semana': 'Dia da Semana',
                                    'total_mortes': 'Total de Mortes'},
                            )

    return fig_mortes_dia


def mortes_por_tipo_acidente(df):
    mortes_tipo = df.groupby('tipo_acidente')['mortos'].sum().reset_index()
    mortes_tipo = mortes_tipo.sort_values(by='mortos', ascending=False)

    fig = px.bar(
        mortes_tipo,
        x='tipo_acidente',
        y='mortos',
        labels={'tipo_acidente': 'Tipo de Acidente',
                'mortos': 'Número de Mortes'},
        text='mortos',
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def mortes_por_faixa_etaria_e_sexo(df):
    df['idade'] = pd.to_numeric(df['idade'], errors='coerce')
    df = df.dropna(subset=['idade'])
    df['faixa_etaria'] = pd.cut(
        df['idade'],
        bins=[0, 12, 18, 30, 45, 60, 75, 100],
        labels=['0-12', '13-18', '19-30', '31-45', '46-60', '61-75', '76+'],
        right=False
    )

    bins = list(range(0, 101, 10))
    labels = [f"{i}-{i+9}" for i in bins[:-1]]
    df['faixa_etaria'] = pd.cut(
        df['idade'], bins=bins, labels=labels, right=False)

    mortes_faixa_sexo = df.groupby(['faixa_etaria', 'sexo'])[
        'mortos'].sum().reset_index()

    fig = px.bar(
        mortes_faixa_sexo,
        x='faixa_etaria',
        y='mortos',
        color='sexo',
        barmode='group',
        labels={'faixa_etaria': 'Faixa Etária',
                'mortos': 'Número de Mortes', 'sexo': 'Sexo'},
        text='mortos',
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)


def top10_municipios_mortes(df):
    df['mortos'] = pd.to_numeric(df['mortos'], errors='coerce')
    mortes_por_municipio = df.groupby('municipio')['mortos'].sum(
    ).sort_values(ascending=False).head(10).reset_index()

    fig = px.bar(
        mortes_por_municipio,
        x='municipio',
        y='mortos',
        labels={'municipio': 'Município', 'mortos': 'Número de Mortes'},
        color='mortos',
        color_continuous_scale='Reds'
    )

    return fig


def top10_brs(df):
    if 'br' not in df.columns:
        return px.bar(title="Coluna 'br' não encontrada.")
    df_brs = df['br'].dropna().astype(str)
    df_brs = "BR-" + df_brs
    top_brs = df_brs.value_counts().nlargest(10).reset_index()
    top_brs.columns = ['BR', 'Quantidade de Acidentes']
    fig = px.bar(
        top_brs,
        x='Quantidade de Acidentes',
        y='BR',
        orientation='h',
        color='Quantidade de Acidentes',
        color_continuous_scale='bluered'
    )
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    return fig


def veiculos_por_horario(df, inter_minutos=60):
    horarios = pd.to_datetime(df['horario'], errors='coerce')
    minutos = horarios.dt.hour * 60 + horarios.dt.minute
    bins = list(range(0, 24*60 + inter_minutos, inter_minutos))
    labels = [
        f"{h:02d}:{m:02d} - {h2:02d}:{m2:02d}"
        for h, m, h2, m2 in [
            (divmod(b, 60)[0], divmod(b, 60)[1],
             divmod(b + inter_minutos, 60)[0] % 24, divmod(b + inter_minutos, 60)[1])
            for b in bins[:-1]
        ]
    ]
    intervalo_horario = pd.cut(
        minutos, bins=bins, labels=labels, right=False, include_lowest=True)

    df['intervalo_horario'] = intervalo_horario

    df_grouped = df.groupby(
        ['intervalo_horario', 'tipo_veiculo']).size().reset_index(name='count')

    tabela_pivot = df_grouped.pivot(
        index='intervalo_horario', columns='tipo_veiculo', values='count').fillna(0)

    fig = px.imshow(
        tabela_pivot.T,  # transpondo para tipo_veiculo nas linhas
        labels=dict(x='Faixa Horária', y='Tipo de Veículo',
                    color='Número de Acidentes'),
        x=tabela_pivot.index,
        y=tabela_pivot.columns,
        aspect='auto',
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        title='Tipos de Veículos Envolvidos em Acidentes por Horário')

    return fig
