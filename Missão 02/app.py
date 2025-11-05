from flask import Flask, request, jsonify
from flask_cors import CORS
from etl.etl import process_hemogram_file
from alerts_engine.alerts_engine import AlertEngine, MetricsCalculator
from sqlalchemy import create_engine
import logging

# Configuração
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/hemodb"
engine = create_engine(DATABASE_URL)

app = Flask(__name__)
CORS(app)

# Inicialização
alert_engine = AlertEngine(engine)
metrics_calculator = MetricsCalculator(engine)

@app.route('/')
def index():
    return """
    <h1>🏥 Sistema de Monitoramento de Hemogramas</h1>
    <p>API REST para análise de exames hematológicos</p>
    
    <h3>Endpoints disponíveis:</h3>
    <ul>
        <li><b>POST /upload</b> - Upload de arquivos CSV</li>
        <li><b>GET /metrics</b> - Métricas do sistema</li>
        <li><b>GET /alerts</b> - Lista de alertas</li>
        <li><b>GET /heatmap</b> - Dados para heatmap municipal</li>
    </ul>
    
    <p>📊 <a href="/dashboard">Acessar Dashboard</a></p>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <h1>📊 Dashboard - Sistema de Hemogramas</h1>
    <p>Dashboard em desenvolvimento</p>
    <p><a href="/">Voltar para API</a></p>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint para upload de arquivos de hemograma"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Apenas arquivos CSV são suportados'}), 400
        
        # Salvar arquivo
        file_path = f"uploads/{file.filename}"
        file.save(file_path)
        
        # Processar ETL
        success = process_hemogram_file(file_path)
        
        if success:
            # Processar alertas após upload
            alerts_generated = alert_engine.process_alerts(days_back=1)
            
            return jsonify({
                'message': 'Arquivo processado com sucesso',
                'alerts_generated': alerts_generated,
                'file': file.filename
            }), 200
        else:
            return jsonify({'error': 'Erro no processamento do arquivo'}), 500
            
    except Exception as e:
        logging.error(f"Erro no upload: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/metrics')
def get_metrics():
    """Endpoint para métricas com filtros"""
    try:
        # Parâmetros de filtro
        age_min = request.args.get('age_min', type=int)
        age_max = request.args.get('age_max', type=int)
        municipality_code = request.args.get('municipality_code')
        days_back = request.args.get('days_back', 30, type=int)
        
        age_range = None
        if age_min is not None and age_max is not None:
            age_range = (age_min, age_max)
        
        metrics = metrics_calculator.get_basic_metrics(
            age_range=age_range,
            municipality_code=municipality_code,
            days_back=days_back
        )
        
        return jsonify(metrics)
        
    except Exception as e:
        logging.error(f"Erro buscando métricas: {e}")
        return jsonify({'error': 'Erro ao calcular métricas'}), 500

@app.route('/alerts')
def get_alerts():
    """Endpoint para listar alertas"""
    try:
        severity = request.args.get('severity', type=int)
        days_back = request.args.get('days_back', 7, type=int)
        
        # Simulação de alertas
        alerts = [
            {
                'id': 1,
                'condition': 'hb_lt_8',
                'severity': 3,
                'sample_id': 'AMOSTRA001',
                'municipality_code': '5200050',
                'message': 'Hemoglobina baixa (< 8 g/dL) - anemia moderada',
                'hemoglobin': 7.2,
                'patient_age': 42
            },
            {
                'id': 2,
                'condition': 'platelets_lt_50k',
                'severity': 3,
                'sample_id': 'AMOSTRA002',
                'municipality_code': '5200100',
                'message': 'Plaquetas baixas (< 50.000) - risco hemorrágico',
                'platelets': 45000,
                'patient_age': 35
            }
        ]
        
        # Aplicar filtro de severidade
        if severity:
            alerts = [alert for alert in alerts if alert['severity'] == severity]
        
        return jsonify({
            'alerts': alerts,
            'total_count': len(alerts),
            'filters': {
                'severity': severity,
                'days_back': days_back
            }
        })
            
    except Exception as e:
        logging.error(f"Erro buscando alertas: {e}")
        return jsonify({'error': 'Erro ao buscar alertas'}), 500

@app.route('/heatmap')
def get_heatmap():
    """Endpoint para dados do heatmap municipal"""
    try:
        days_back = request.args.get('days_back', 30, type=int)
        
        heatmap_data = metrics_calculator.get_municipality_heatmap(days_back=days_back)
        
        return jsonify({
            'heatmap_data': heatmap_data,
            'generated_at': '2024-01-01T00:00:00Z',  # Simulado
            'total_municipalities': len(heatmap_data)
        })
        
    except Exception as e:
        logging.error(f"Erro gerando heatmap: {e}")
        return jsonify({'error': 'Erro ao gerar heatmap'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
