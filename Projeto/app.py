import os  # type: ignore
import streamlit as st  # type: ignore
from Utils.descompactador import extrair_arquivos  # type: ignore
from Interface.tela_apresentacao import tela_apresentacao
from Interface.pagina_inicial import pagina_inicial

# ✅ Deve ser o primeiro comando st.*
st.set_page_config(
    page_title="Análise de Acidentes de Trânsito",
    page_icon="🚗",
    layout="wide"
)

# Pasta onde estão os dados
PASTA_DESTINO = os.path.join("dados", "acidentes")

# Inicializa a variável de controle da página
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "apresentacao"

# Verifica se já descompactou os arquivos
CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_RAIZ = os.path.dirname(CAMINHO_ATUAL)

ARQUIVO_ZIP = os.path.join(
    PASTA_RAIZ, 'Arquivos de Pesquisas', 'planilhas_acidentes.zip')
PASTA_DESTINO = os.path.join(CAMINHO_ATUAL, 'Data')

if 'arquivos_extraidos' not in st.session_state:
    print('[LOG] ->', extrair_arquivos(ARQUIVO_ZIP, PASTA_DESTINO))
    st.session_state.arquivos_extraidos = True

# ✅ Controla qual tela exibir
if st.session_state["pagina"] == "apresentacao":
    tela_apresentacao()
elif st.session_state["pagina"] == "analise":
    pagina_inicial(PASTA_DESTINO)
