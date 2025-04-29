import zipfile
import os


def extrair_arquivos(arquivo_zip, pasta_destino):
    # Cria a pasta de destino, caso ela não exista previamente
    os.makedirs(pasta_destino, exist_ok=True)

    # Abre o arquivo ZIP
    with zipfile.ZipFile(arquivo_zip, 'r') as arq_zip:
        # Lista todos os arquivos dentro do arquivo zip
        lista_arquivos_zip = arq_zip.namelist()

        if not lista_arquivos_zip:
            return 'O arquivo ZIP está vazio!'
        
        todos_existem = all(
            os.path.exists(os.path.join(pasta_destino, nome_arquivo)) for nome_arquivo in lista_arquivos_zip
        )

        if todos_existem:
            return 'Todos os arquivos já foram exportados anteriormente.'

        arq_zip.extractall(pasta_destino)

    arq_zip.close()

    return 'Arquivos Extraidos na pasta: { ' + os.path.relpath(pasta_destino) + ' }'