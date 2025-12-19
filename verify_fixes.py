
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, timezone

def check_dates_updated():
    db_path = 'data/db/hipica_data.db'
    conn = sqlite3.connect(db_path)
    
    print("--- Updated Logic Verification ---")
    
    # Emulate the new logic
    chile_time = datetime.now(timezone.utc) - timedelta(hours=3)
    today_str = chile_time.strftime('%Y-%m-%d')
    print(f"Python Calculated Today (Chile): {today_str}")
    
    query = f"SELECT fecha, nro_carrera FROM programa_carreras WHERE fecha >= '{today_str}' ORDER BY fecha ASC"
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No races found.")
    else:
        print(f"Found {len(df)} races starting from {today_str}.")
        dates = df['fecha'].unique()
        print(f"Dates returned: {dates}")
        
        if min(dates) < today_str:
            print("FAIL: Returned dates older than today!")
        else:
            print("PASS: All dates are valid.")
            
    conn.close()

if __name__ == "__main__":
    check_dates_updated()
