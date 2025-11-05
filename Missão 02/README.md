# Missão 02 - Sistema de Monitoramento de Hemogramas

Sistema completo para análise de exames hematológicos.

## Estrutura:
- sql/hemograma.sql - Schema do banco
- etl/etl.py - Processamento de dados
- alerts_engine/ - Motor de alertas
- app.py - API Flask

## Como usar:
```bash
pip install -r requirements.txt
python app.py

### 3.6 Dashboard HTML Básico

```bash
# Criar dashboard simples
cat > templates/dashboard.html << 'ENDFILE'
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Hemogramas</title>
</head>
<body>
    <h1>Dashboard - Sistema de Hemogramas</h1>
    <p>Sistema em desenvolvimento</p>
</body>
</html>
