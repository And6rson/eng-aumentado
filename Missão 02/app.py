from flask import Flask, jsonify, request
from etl.etl import process_hemogram_file
from alerts_engine.alerts_engine import AlertEngine, MetricsCalculator

app = Flask(__name__)

alert_engine = AlertEngine()
metrics_calc = MetricsCalculator()

@app.route('/')
def home():
    return "Sistema de Hemogramas - Missão 02"

@app.route('/upload', methods=['POST'])
def upload():
    return jsonify({"message": "Endpoint upload funcionando"})

@app.route('/metrics')
def metrics():
    return jsonify(metrics_calc.get_basic_metrics())

@app.route('/alerts')
def alerts():
    return jsonify({"alerts": []})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
