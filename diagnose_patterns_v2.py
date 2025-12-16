
from src.models.data_manager import cargar_datos_3nf, calcular_todos_patrones
import pandas as pd

def diagnose():
    print("Loading data...")
    df = cargar_datos_3nf()
    print(f"Total rows: {len(df)}")
    
    if df.empty:
        print("Dataframe is empty.")
        return

    valid_pos = df['posicion'].notna().sum()
    print(f"Rows with valid 'posicion': {valid_pos}")
    
    if valid_pos > 0:
        # Create a duplicated race to test logic
        valid_races = df[df['posicion'].notna()].groupby(['hipodromo', 'fecha', 'nro_carrera'])
        if len(valid_races) > 0:
            name, group = next(iter(valid_races))
            print(f"Duplicating race: {name}")
            
            # Create a duplicate with different date/race number
            dup_group = group.copy()
            dup_group['fecha'] = '2099-01-01'
            dup_group['nro_carrera'] = 99
            
            df_test = pd.concat([df, dup_group], ignore_index=True)
            print("Running pattern check on data WITH duplicate...")
            patterns_test = calcular_todos_patrones(df_test)
            print(f"Found {len(patterns_test)} patterns in TEST data.")
            if patterns_test:
                print("Test Pattern 1:", patterns_test[0])
        else:
            print("No valid races to duplicate.")

        print("\nPosition distribution:")

        print(df['posicion'].value_counts().head())

    print("\nCalculating patterns...")
    patterns = calcular_todos_patrones(df)
    print(f"Found {len(patterns)} patterns")
    
    if patterns:
        print("Top 3 patterns:")
        for p in patterns[:3]:
            print(p)
    else:
        print("No patterns found. Debugging `calcular_todos_patrones` logic:")
        # Manual check
        # Group by race
        try:
             carreras_groups = df.groupby(['hipodromo', 'fecha', 'nro_carrera'])
             print(f"Total races found: {len(carreras_groups)}")
             
             count_potential = 0
             for name, group in carreras_groups:
                 llegada = group.sort_values('posicion')
                 top4 = llegada.head(4)
                 # Check if top4 has valid positions
                 if top4['posicion'].notna().all() and len(top4) >= 2:
                     count_potential += 1
                     if count_potential <= 3:
                         print(f"Potential valid race: {name}")
                         print(top4[['posicion', 'caballo']])
             
             print(f"Races with at least 2 valid positions: {count_potential}")
             
        except Exception as e:
            print(f"Error grouping: {e}")

if __name__ == "__main__":
    diagnose()
