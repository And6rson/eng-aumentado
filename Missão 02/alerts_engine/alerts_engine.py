import hashlib
import json
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger('alerts_engine')

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/hemodb"
engine = create_engine(DATABASE_URL)

class AlertEngine:
    """Motor de geração de alertas médicos"""
    
    def __init__(self, db_engine):
        self.engine = db_engine
        self.alert_rules = self._load_alert_rules()
    
    def _load_alert_rules(self):
        """Define as regras de alerta baseadas em critérios médicos"""
        return [
            {
                'condition': 'platelets_lt_50k',
                'severity': 3,
                'rule': lambda r: r.platelets and r.platelets < 50000,
                'message': 'Plaquetas baixas (< 50.000) - risco hemorrágico'
            },
            {
                'condition': 'platelets_lt_100k',
                'severity': 2,
                'rule': lambda r: r.platelets and 50000 <= r.platelets < 100000,
                'message': 'Plaquetas moderadamente baixas (< 100.000)'
            },
            {
                'condition': 'hb_lt_8',
                'severity': 3,
                'rule': lambda r: r.hemoglobin and r.hemoglobin < 8,
                'message': 'Hemoglobina baixa (< 8 g/dL) - anemia moderada'
            },
            {
                'condition': 'hb_lt_10',
                'severity': 2,
                'rule': lambda r: r.hemoglobin and 8 <= r.hemoglobin < 10,
                'message': 'Hemoglobina moderadamente baixa (< 10 g/dL)'
            },
            {
                'condition': 'wbc_lt_2',
                'severity': 3,
                'rule': lambda r: r.leukocytes and r.leukocytes < 2.0,
                'message': 'Leucócitos baixos (< 2.000) - risco infeccioso'
            }
        ]
    
    def make_alert_key(self, condition, sample_id):
        """Cria chave única para evitar alertas duplicados"""
        return hashlib.sha1(f"{condition}|{sample_id}".encode()).hexdigest()
    
    def process_alerts(self, days_back=1):
        """Processa alertas para os últimos N dias"""
        try:
            with self.engine.begin() as conn:
                # Busca hemogramas recentes
                query = text("""
                    SELECT * FROM hemogram 
                    WHERE created_at >= now() - interval ':days days'
                    AND is_valid = true
                """)
                
                rows = conn.execute(query, {'days': days_back}).fetchall()
                alerts_generated = 0
                
                for r in rows:
                    for rule in self.alert_rules:
                        if rule['rule'](r):
                            payload = {
                                'hemoglobin': r.hemoglobin,
                                'platelets': r.platelets,
                                'leukocytes': r.leukocytes,
                                'message': rule['message'],
                                'exam_date': r.exam_date.isoformat() if r.exam_date else None
                            }
                            
                            # Inserir alerta (implementação simplificada)
                            logger.info(f"Alerta gerado: {rule['condition']} para {r.sample_id}")
                            alerts_generated += 1
                
                logger.info(f"Processados {len(rows)} hemogramas, gerados {alerts_generated} alertas")
                return alerts_generated
                
        except Exception as e:
            logger.error(f"Erro no processamento de alertas: {e}")
            return 0

class MetricsCalculator:
    """Calculadora de métricas epidemiológicas"""
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def get_basic_metrics(self, age_range=None, municipality_code=None, days_back=30):
        """Calcula métricas básicas com filtros"""
        try:
            # Simulação - em produção, isso consultaria o banco
            metrics = {
                'total_exams': 150,
                'avg_hemoglobin': 12.8,
                'avg_platelets': 245000,
                'avg_leukocytes': 6.2,
                'anemia_severe_percent': 2.5,
                'anemia_moderate_percent': 8.7,
                'thrombocytopenia_severe_percent': 1.2,
                'thrombocytopenia_moderate_percent': 4.3,
                'leukopenia_percent': 3.1
            }
            
            # Aplicar filtros simulados
            if municipality_code:
                metrics['municipality_filter'] = municipality_code
            if age_range:
                metrics['age_filter'] = f"{age_range[0]}-{age_range[1]}"
            
            metrics['days_back'] = days_back
            return metrics
                
        except Exception as e:
            logger.error(f"Erro calculando métricas: {e}")
            return {}
    
    def get_municipality_heatmap(self, days_back=30):
        """Dados simulados para heatmap municipal"""
        return [
            {
                'municipality_code': '5200050',
                'exam_count': 45,
                'anemia_rate': 5.2,
                'thrombocytopenia_rate': 3.1
            },
            {
                'municipality_code': '5200100', 
                'exam_count': 67,
                'anemia_rate': 8.7,
                'thrombocytopenia_rate': 2.4
            },
            {
                'municipality_code': '5200159',
                'exam_count': 23,
                'anemia_rate': 12.3,
                'thrombocytopenia_rate': 5.8
            }
        ]

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    alert_engine = AlertEngine(engine)
    alerts_count = alert_engine.process_alerts()
    print(f"Alertas gerados: {alerts_count}")
