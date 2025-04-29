import os # type: ignore
import streamlit as st # type: ignore
from Utils.descompactador import extrair_arquivos # type: ignore
from Interface.pagina_inicial import pagina_inicial


CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_RAIZ = os.path.dirname(CAMINHO_ATUAL)

ARQUIVO_ZIP = os.path.join(PASTA_RAIZ, 'Arquivos de Pesquisas', 'planilhas_acidentes.zip')
PASTA_DESTINO = os.path.join(CAMINHO_ATUAL, 'Data')

# Fazer a verificação dos arquivos descompactados apenas uma vez
if 'arquivos_extraidos' not in st.session_state:
    print('[LOG] ->', extrair_arquivos(ARQUIVO_ZIP, PASTA_DESTINO))
    st.session_state.arquivos_extraidos = True    

pagina_inicial(PASTA_DESTINO)
