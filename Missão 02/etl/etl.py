import hashlib
import json
import logging
import pandas as pd
from datetime import datetime, date
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hemogram_etl')

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/hemodb"
engine = create_engine(DATABASE_URL)

class HemogramValidator:
    """Validação de dados de hemograma"""
    
    @staticmethod
    def validate_age(age):
        return isinstance(age, (int, float)) and 0 <= age <= 120
    
    @staticmethod
    def validate_hemoglobin(hb):
        return hb is None or (isinstance(hb, (int, float)) and 0 < hb < 30)
    
    @staticmethod
    def validate_platelets(plt):
        return plt is None or (isinstance(plt, (int, float)) and 0 < plt < 2000000)
    
    @staticmethod
    def validate_leukocytes(wbc):
        return wbc is None or (isinstance(wbc, (int, float)) and 0 < wbc < 1000)
    
    @staticmethod
    def validate_municipality_code(code):
        if not code or pd.isna(code):
            return False
        return bool(re.match(r'^\d{7}$', str(code)))
    
    @staticmethod
    def validate_sample_id(sample_id):
        return sample_id and not pd.isna(sample_id) and len(str(sample_id)) >= 5

class DataProcessor:
    """Processamento e transformação de dados"""
    
    def __init__(self):
        self.validator = HemogramValidator()
        self.stats = {
            'processed': 0,
            'valid': 0,
            'invalid': 0,
            'errors': 0
        }
    
    def calculate_age(self, birth_date):
        """Calcula idade a partir da data de nascimento"""
        if not birth_date or pd.isna(birth_date):
            return None
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        except Exception as e:
            logger.warning(f"Erro ao calcular idade: {e}")
            return None
    
    def create_patient_hash(self, birth_date, municipality_code, sex):
        """Cria hash único para paciente mantendo privacidade"""
        if not all([birth_date, municipality_code, sex]):
            return None
        try:
            base_string = f"{birth_date}_{municipality_code}_{sex}"
            return hashlib.sha256(base_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Erro ao criar patient_hash: {e}")
            return None
    
    def validate_row(self, row):
        """Valida uma linha completa de dados"""
        errors = []
        
        if not self.validator.validate_sample_id(row.get('sample_id')):
            errors.append("sample_id inválido")
        
        if not self.validator.validate_municipality_code(row.get('municipality_code')):
            errors.append("municipality_code inválido")
        
        if not self.validator.validate_hemoglobin(row.get('hemoglobin')):
            errors.append("hemoglobina fora da faixa aceitável")
        
        if not self.validator.validate_platelets(row.get('platelets')):
            errors.append("plaquetas fora da faixa aceitável")
        
        if not self.validator.validate_leukocytes(row.get('leukocytes')):
            errors.append("leucócitos fora da faixa aceitável")
        
        return len(errors) == 0, errors
    
    def process_dataframe(self, df):
        """Processa um DataFrame completo"""
        processed_rows = []
        
        for idx, row in df.iterrows():
            try:
                self.stats['processed'] += 1
                
                # Validação
                is_valid, errors = self.validate_row(row)
                
                if not is_valid:
                    self.stats['invalid'] += 1
                    logger.warning(f"Linha {idx} inválida: {errors}")
                    continue
                
                # Processamento
                processed_row = {
                    'sample_id': str(row['sample_id']),
                    'municipality_code': str(row['municipality_code']),
                    'hemoglobin': float(row['hemoglobin']) if pd.notna(row.get('hemoglobin')) else None,
                    'platelets': int(row['platelets']) if pd.notna(row.get('platelets')) else None,
                    'leukocytes': float(row['leukocytes']) if pd.notna(row.get('leukocytes')) else None,
                    'lymphocytes': float(row['lymphocytes']) if pd.notna(row.get('lymphocytes')) else None,
                    'neutrophils': float(row['neutrophils']) if pd.notna(row.get('neutrophils')) else None,
                    'exam_date': row.get('exam_date'),
                    'patient_age': row.get('patient_age'),
                    'sex': row.get('sex'),
                    'birth_date': row.get('birth_date'),
                    'lab_id': row.get('lab_id'),
                    'is_valid': True,
                    'validation_notes': None
                }
                
                # Calcular patient_hash se tiver dados suficientes
                if all([processed_row['birth_date'], processed_row['municipality_code'], processed_row['sex']]):
                    processed_row['patient_hash'] = self.create_patient_hash(
                        processed_row['birth_date'],
                        processed_row['municipality_code'],
                        processed_row['sex']
                    )
                
                processed_rows.append(processed_row)
                self.stats['valid'] += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Erro processando linha {idx}: {e}")
        
        logger.info(f"Processamento concluído: {self.stats}")
        return pd.DataFrame(processed_rows)

def process_hemogram_file(file_path):
    """Função principal do ETL"""
    try:
        logger.info(f"Iniciando processamento do arquivo: {file_path}")
        
        # Extração
        df = pd.read_csv(file_path)
        logger.info(f"Arquivo lido: {len(df)} registros")
        
        # Transformação
        processor = DataProcessor()
        processed_df = processor.process_dataframe(df)
        
        logger.info(f"ETL concluído: {processor.stats}")
        return True
        
    except Exception as e:
        logger.error(f"Erro no processamento do arquivo: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_hemogram_file(sys.argv[1])
    else:
        print("Uso: python etl.py <arquivo_csv>")
