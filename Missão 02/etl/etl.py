import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('hemogram_etl')

def process_hemogram_file(file_path):
    """Processa arquivo CSV de hemogramas"""
    try:
        logger.info(f"Processando: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Registros: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("ETL carregado")
