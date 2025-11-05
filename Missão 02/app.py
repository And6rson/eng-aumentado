from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from etl.etl import process_hemogram_file
from alerts_engine.alerts_engine import AlertEngine, MetricsCalculator
from sqlalchemy import create_engine
import logging

# ... (o resto do seu app.py existente aqui) ...

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
