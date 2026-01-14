import sys
import os
sys.path.append(os.getcwd())
from src.etl.etl_pipeline import HipicaETL

def debug():
    etl = HipicaETL()
    file_path = 'exports/PROGRAMA_VAL_2026-01-04.csv'
    
    print(f"Debug processing {file_path}")
    
    # Call process_csv directly
    # process_csv prints to stdout
    num = etl.process_csv(file_path)
    print(f"Resulting num_registros: {num}")

if __name__ == "__main__":
    debug()
