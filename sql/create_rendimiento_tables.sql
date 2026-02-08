-- Create rendimiento_stats table for performance metrics
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS rendimiento_stats (
    id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rendimiento_historico table for detailed race history
CREATE TABLE IF NOT EXISTS rendimiento_historico (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hipodromo TEXT NOT NULL,
    nro_carrera INTEGER NOT NULL,
    acierto_ganador BOOLEAN,
    acierto_quiniela BOOLEAN,
    acierto_trifecta BOOLEAN,
    acierto_superfecta BOOLEAN,
    prediccion_top4 JSONB,
    resultado_top4 JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(fecha, hipodromo, nro_carrera)
);

-- Enable RLS (Row Level Security) - allow public read
ALTER TABLE rendimiento_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE rendimiento_historico ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read on rendimiento_stats" 
    ON rendimiento_stats FOR SELECT 
    USING (true);

CREATE POLICY "Allow public read on rendimiento_historico" 
    ON rendimiento_historico FOR SELECT 
    USING (true);

-- Allow service role to insert/update
CREATE POLICY "Allow service role insert on rendimiento_stats" 
    ON rendimiento_stats FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow service role update on rendimiento_stats" 
    ON rendimiento_stats FOR UPDATE 
    USING (true);

CREATE POLICY "Allow service role insert on rendimiento_historico" 
    ON rendimiento_historico FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow service role update on rendimiento_historico" 
    ON rendimiento_historico FOR UPDATE 
    USING (true);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_rendimiento_fecha ON rendimiento_historico(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_rendimiento_hipodromo ON rendimiento_historico(hipodromo);
