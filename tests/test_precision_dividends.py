import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add src to path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # HipicaAntigracity
sys.path.append(parent_dir)

from src.models.data_manager import calcular_precision_modelo

class TestPrecisionDividends(unittest.TestCase):
    
    @patch('src.models.data_manager.sqlite3.connect')
    @patch('src.models.data_manager.pd.read_sql_query')
    def test_calcular_precision_dividends(self, mock_read_sql, mock_connect):
        # Mock DB connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # Mock DataFrame return
        # Scenario: 
        # Race 1: Pred Rank 1, Result 1 (Win), Div 2.5
        # Race 2: Pred Rank 1, Result 2 (Loss), Div 3.0 (Should not be summed)
        # Race 3: Pred Rank 1, Result 1 (Win), Div "4,5" (String with comma, should be converted and summed)
        
        data = {
            'fecha_carrera': ['2023-01-01', '2023-01-01', '2023-01-02'],
            'hipodromo': ['HIPO', 'HIPO', 'CLUB'],
            'nro_carrera': [1, 2, 1],
            'numero_caballo': [1, 2, 3],
            'caballo_id': [101, 102, 103],
            'ranking_prediccion': [1, 1, 1], 
            'posicion_real': [1, 2, 1],      
            'dividendo': [2.5, 3.0, '4,5']   
        }
        df_mock = pd.DataFrame(data)
        mock_read_sql.return_value = df_mock
        
        # Call function
        print("\n--- Testing calcular_precision_modelo with Mock Data ---")
        result = calcular_precision_modelo(fecha_inicio='2023-01-01', fecha_fin='2023-01-02')
        
        # Calculations:
        # Match 1: 2.5
        # Match 2: Loss (ignored)
        # Match 3: 4.5 (converted from "4,5")
        # Total Dividends = 2.5 + 4.5 = 7.0
        
        print("Result:", result)
        
        self.assertEqual(result['top1_correct'], 2)
        self.assertEqual(result['top1_total'], 3)
        self.assertAlmostEqual(result['total_dividendos'], 7.0)
        self.assertTrue('total_dividendos' in result)
        print("--- Test Passed ---")

if __name__ == '__main__':
    unittest.main()
