-- hemograma.sql
CREATE TABLE IF NOT EXISTS patient (
    patient_hash VARCHAR(64) PRIMARY KEY,
    birth_date DATE,
    sex VARCHAR(1),
    municipality_code VARCHAR(7),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS hemogram (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(100) UNIQUE NOT NULL,
    patient_hash VARCHAR(64) REFERENCES patient(patient_hash),
    municipality_code VARCHAR(7),
    
    -- Valores principais
    hemoglobin DECIMAL(5,2),
    platelets INTEGER,
    leukocytes DECIMAL(6,2),
    lymphocytes DECIMAL(6,2),
    neutrophils DECIMAL(6,2),
    
    -- Metadados
    exam_date DATE,
    patient_age INTEGER,
    lab_id VARCHAR(50),
    
    -- Controle de qualidade
    is_valid BOOLEAN DEFAULT true,
    validation_notes TEXT,
    
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alert (
    id SERIAL PRIMARY KEY,
    alert_key VARCHAR(100) UNIQUE,
    alert_at TIMESTAMP DEFAULT now(),
    condition VARCHAR(50) NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    sample_id VARCHAR(100) NOT NULL,
    patient_hash VARCHAR(64) REFERENCES patient(patient_hash),
    municipality_code VARCHAR(7),
    is_active BOOLEAN DEFAULT true,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    
    payload JSONB,
    
    created_at TIMESTAMP DEFAULT now()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_hemogram_patient_hash ON hemogram(patient_hash);
CREATE INDEX IF NOT EXISTS idx_hemogram_municipality_code ON hemogram(municipality_code);
CREATE INDEX IF NOT EXISTS idx_hemogram_exam_date ON hemogram(exam_date);
CREATE INDEX IF NOT EXISTS idx_hemogram_created_at ON hemogram(created_at);
CREATE INDEX IF NOT EXISTS idx_alert_condition ON alert(condition);
CREATE INDEX IF NOT EXISTS idx_alert_severity ON alert(severity);
CREATE INDEX IF NOT EXISTS idx_alert_municipality_code ON alert(municipality_code);
CREATE INDEX IF NOT EXISTS idx_alert_is_active ON alert(is_active);
CREATE INDEX IF NOT EXISTS idx_alert_created_at ON alert(created_at);

-- Índice GIN para busca em JSON
CREATE INDEX IF NOT EXISTS idx_alert_payload ON alert USING GIN (payload);
