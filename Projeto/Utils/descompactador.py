import zipfile
import os


def extrair_arquivos(arquivo_zip, pasta_destino):
    os.makedirs(pasta_destino, exist_ok=True)

    with zipfile.ZipFile(arquivo_zip, 'r') as arq_zip:
        arq_zip.extractall(pasta_destino)

    return 'Arquivos Extraidos na pasta: { ' + os.path.relpath(pasta_destino) + ' }'