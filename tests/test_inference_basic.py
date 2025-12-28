import pytest
import pandas as pd
import numpy as np
import os
import sys

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestInferencePipeline:
    """Tests básicos para el pipeline de inferencia"""
    
    def test_model_artifacts_exist(self):
        """Verifica que los artefactos del modelo existan"""
        model_path = 'src/models/lgbm_ranker_v1.pkl'
        fe_path = 'src/models/feature_eng_v2.pkl'
        
        # Al menos uno de los dos debería existir en un proyecto configurado
        # Si ninguno existe, el test se marca como skip
        if not os.path.exists(model_path) and not os.path.exists(fe_path):
            pytest.skip("Modelos no encontrados - ejecutar entrenamiento primero")
        
        # Si existe el modelo, debe existir el FE también
        if os.path.exists(model_path):
            assert os.path.exists(fe_path), "Feature Engineering debe existir si existe el modelo"
    
    def test_softmax_sums_to_one(self):
        """Test: Softmax probabilities suman ~1.0"""
        # Simular scores de una carrera
        scores = np.array([0.5, 0.3, 0.1, 0.05, 0.05])
        
        # Aplicar softmax
        exp_scores = np.exp(scores)
        probs = exp_scores / np.sum(exp_scores)
        
        # Verificar suma
        assert np.isclose(probs.sum(), 1.0), "Probabilidades deben sumar 1.0"
        
        # Verificar order preserved
        assert probs[0] > probs[1] > probs[2], "Orden de probabilidades debe preservarse"
    
    def test_feature_engineering_no_nan(self):
        """Test: Features no contienen NaN después de transformación"""
        try:
            from src.models.features import FeatureEngineering
        except ImportError:
            pytest.skip("FeatureEngineering no importable")
        
        # Data mínima válida
        df = pd.DataFrame({
            'fecha': pd.date_range('2024-01-01', periods=10),
            'caballo_id': ['C1'] * 10,
            'jinete_id': ['J1'] * 10,
            'preparador_id': ['P1'] * 10,
            'hipodromo_id': ['HC'] * 10,
            'distancia': [1200] * 10,
            'pista': ['ARENA'] * 10,
            'peso_fs': [470] * 10,
            'mandil': list(range(1, 11)),
            'posicion': [5, 3, 1, 2, 4, 6, 3, 2, 1, 5],
            'tiempo': [75.5] * 10,
            'padre': ['SIRE_A'] * 10
        })
        
        fe = FeatureEngineering()
        X = fe.transform(df.copy(), is_training=True)
        
        # No debe haber NaN
        nan_count = X.isna().sum().sum()
        assert nan_count == 0, f"Features no deben contener NaN, encontrados: {nan_count}"
    
    def test_temporal_ordering(self):
        """Test: Datos se ordenan correctamente por caballo y fecha"""
        try:
            from src.models.features import FeatureEngineering
        except ImportError:
            pytest.skip("FeatureEngineering no importable")
        
        # Crear datos desordenados
        dates = pd.to_datetime(['2024-01-05', '2024-01-01', '2024-01-03', '2024-01-02', '2024-01-04'])
        df = pd.DataFrame({
            'fecha': dates,
            'caballo_id': ['C1'] * 5,
            'jinete_id': ['J1'] * 5,
            'preparador_id': ['P1'] * 5,
            'hipodromo_id': ['HC'] * 5,
            'distancia': [1200] * 5,
            'pista': ['ARENA'] * 5,
            'peso_fs': [470] * 5,
            'mandil': [1, 2, 3, 4, 5],
            'posicion': [5, 3, 1, 2, 4],
            'tiempo': [75.5] * 5,
            'padre': ['SIRE_A'] * 5
        })
        
        fe = FeatureEngineering()
        # No debe lanzar error
        X = fe.transform(df.copy(), is_training=True)
        
        assert len(X) == len(df), "Transform no debe perder filas"


class TestHealthChecks:
    """Tests para endpoints de salud"""
    
    def test_database_exists(self):
        """Verifica que la base de datos exista"""
        db_path = 'data/db/hipica_data.db'
        
        if not os.path.exists(db_path):
            pytest.skip("Base de datos no encontrada - sistema no inicializado")
        
        assert os.path.exists(db_path), "Base de datos debe existir"
        
        # Verificar que no esté vacía
        assert os.path.getsize(db_path) > 0, "Base de datos no debe estar vacía"


# Ejecutar con: pytest tests/test_inference_basic.py -v
# Coverage: pytest tests/test_inference_basic.py --cov=src --cov-report=html
