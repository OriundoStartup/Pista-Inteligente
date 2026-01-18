import pandas as pd
import os
import re

# Define the files and their mapping to tracks
FILES = [
    {"path": "exports/RESULTADOS_CHC_2026-01-02.csv", "track": "Club Hípico de Santiago", "date": "2026-01-02"},
    {"path": "exports/RESULTADOS_CHC_2026-01-09.csv", "track": "Club Hípico de Santiago", "date": "2026-01-09"},
    {"path": "exports/RESULTADOS_HC_2026-01-03.csv", "track": "Hipódromo Chile", "date": "2026-01-03"},
    {"path": "exports/RESULTADOS_HC_2026-01-10.csv", "track": "Hipódromo Chile", "date": "2026-01-10"},
    {"path": "exports/RESULTADOS_HC_2026-01.15.csv", "track": "Hipódromo Chile", "date": "2026-01-15"},
    {"path": "exports/RESULTADOS_VAL_2026-01-04.csv", "track": "Valparaíso Sporting", "date": "2026-01-04"},
    {"path": "exports/RESULTADO_VAL2026-01-11..csv", "track": "Valparaíso Sporting", "date": "2026-01-11"},
    {"path": "exports/RESULTADOS_VAL_2026-01-14.csv", "track": "Valparaíso Sporting", "date": "2026-01-14"},
]

BASE_DIR = r"c:\espacioDeTrabajo\HipicaAntigracity"

def load_data():
    all_data = []
    
    for entry in FILES:
        full_path = os.path.join(BASE_DIR, entry["path"])
        if not os.path.exists(full_path):
            print(f"Warning: File not found: {full_path}")
            continue
            
        try:
            # Detect delimiter (comma or semicolon)
            with open(full_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if ';' in first_line:
                    sep = ';'
                else:
                    sep = ','
            
            df = pd.read_csv(full_path, sep=sep)
            
            # Normalize columns
            cols = [c.lower().strip() for c in df.columns]
            df.columns = cols
            
            # Identify columns
            # HC: lugar, jinete
            # VAL/CHC: posicion/lugar, jinete
            # VAL 2026-01-11: lº
            
            if 'posicion' in df.columns:
                df['posicion_norm'] = df['posicion']
            elif 'lugar' in df.columns:
                df['posicion_norm'] = df['lugar']
            elif 'lº' in df.columns:
                df['posicion_norm'] = df['lº']
            else:
                # Try to find a column starting with 'l' and short
                found = False
                for c in df.columns:
                    if c.startswith('l') and len(c) <= 3:
                        df['posicion_norm'] = df[c]
                        found = True
                        break
                if not found:
                    print(f"Warning: No position column in {entry['path']}. Columns: {df.columns.tolist()}")
                    continue
                
            if 'jinete' not in df.columns:
                 print(f"Warning: No jinete column in {entry['path']}")
                 continue

            # Add metadata
            df['track'] = entry['track']
            df['date'] = entry['date']
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error reading {full_path}: {e}")
            
    if not all_data:
        return pd.DataFrame()
        
    return pd.concat(all_data, ignore_index=True)

def clean_position(pos):
    pos = str(pos).strip().lower()
    if pos in ['1', 'ganador']:
        return 1
    if pos == '2':
        return 2
    if pos == '3':
        return 3
    return 0 # Other

def calculate_stats(df):
    stats = []
    
    # Clean position
    df['pos_clean'] = df['posicion_norm'].apply(clean_position)
    
    # Group by Jinete
    grouped = df.groupby('jinete')
    
    for jinete, group in grouped:
        total_rides = len(group)
        wins = len(group[group['pos_clean'] == 1])
        seconds = len(group[group['pos_clean'] == 2])
        thirds = len(group[group['pos_clean'] == 3])
        efficiency = (wins / total_rides * 100) if total_rides > 0 else 0
        
        stats.append({
            'Jinete': jinete,
            'Carreras Ganadas': wins,
            'Segundos': seconds,
            'Terceros': thirds,
            'Total Montas': total_rides,
            'Eficiencia (%)': round(efficiency, 2)
        })
        
    stats_df = pd.DataFrame(stats)
    if not stats_df.empty:
        stats_df = stats_df.sort_values(by=['Carreras Ganadas', 'Segundos', 'Terceros'], ascending=False)
        # Add Rank
        stats_df.reset_index(drop=True, inplace=True)
        stats_df.index += 1
        stats_df.index.name = 'Lugar'
        stats_df = stats_df.reset_index()
        
    return stats_df

def main():
    df = load_data()
    if df.empty:
        print("No data loaded.")
        return

    tracks = df['track'].unique()
    
    file_map = {
        "Club Hípico de Santiago": "stats_chc.txt",
        "Hipódromo Chile": "stats_hc.txt",
        "Valparaíso Sporting": "stats_val.txt"
    }

    for track in tracks:
        print(f"\nProcessing {track}...")
        track_df = df[df['track'] == track]
        stats = calculate_stats(track_df)
        
        # Select columns for display
        display_cols = ['Lugar', 'Jinete', 'Carreras Ganadas', 'Segundos', 'Terceros', 'Eficiencia (%)']
        
        # Write to file
        fname = file_map.get(track, "stats_other.txt")
        with open(os.path.join(BASE_DIR, fname), 'w', encoding='utf-8') as f:
            f.write(f"Estadísticas: {track}\n")
            f.write(stats[display_cols].to_markdown(index=False, tablefmt="grid"))
        print(f"Written to {fname}")

    # Progression Analysis
    print("\nCalculating Progression...")
    df['date_dt'] = pd.to_datetime(df['date'])
    week1 = df[(df['date_dt'] >= '2026-01-01') & (df['date_dt'] <= '2026-01-08')]
    week2 = df[(df['date_dt'] >= '2026-01-09') & (df['date_dt'] <= '2026-01-16')]
    
    jockeys = df['jinete'].unique()
    progression = []
    
    for jockey in jockeys:
        # Calculate wins in week 1
        w1_rides = week1[week1['jinete'] == jockey]
        if not w1_rides.empty:
            w1_rides['pos_clean'] = w1_rides['posicion_norm'].apply(clean_position)
            w1_wins = len(w1_rides[w1_rides['pos_clean'] == 1])
            w1_eff = (w1_wins / len(w1_rides)) * 100
        else:
            w1_wins = 0
            w1_eff = 0
            
        # Calculate wins in week 2
        w2_rides = week2[week2['jinete'] == jockey]
        if not w2_rides.empty:
            w2_rides['pos_clean'] = w2_rides['posicion_norm'].apply(clean_position)
            w2_wins = len(w2_rides[w2_rides['pos_clean'] == 1])
            w2_eff = (w2_wins / len(w2_rides)) * 100
        else:
            w2_wins = 0
            w2_eff = 0
            
        if not w1_rides.empty or not w2_rides.empty:
            progression.append({
                'Jinete': jockey,
                'Week1 Wins': w1_wins,
                'Week2 Wins': w2_wins,
                'Win Delta': w2_wins - w1_wins,
                'Week1 Eff': w1_eff,
                'Week2 Eff': w2_eff,
                'Eff Delta': w2_eff - w1_eff,
                'Total Runs': len(w1_rides) + len(w2_rides)
            })
            
    prog_df = pd.DataFrame(progression)
    prog_df = prog_df.sort_values(by=['Win Delta', 'Eff Delta'], ascending=False)
    
    with open(os.path.join(BASE_DIR, "progression.txt"), 'w', encoding='utf-8') as f:
        f.write("Top 5 Jinetes con Mayor Progresión (Semana 1 vs Semana 2):\n")
        f.write(prog_df[['Jinete', 'Week1 Wins', 'Week2 Wins', 'Win Delta', 'Week1 Eff', 'Week2 Eff', 'Eff Delta']].head(5).to_markdown(index=False, tablefmt="grid"))
        
        best_prog = prog_df.iloc[0]
        f.write(f"\n\nJinete destacado con mayor progresión: {best_prog['Jinete']} (Aumento en victorias: {best_prog['Win Delta']}, Mejora eficiencia: {best_prog['Eff Delta']:.2f}%)")
    
    print("Written to progression.txt")


if __name__ == "__main__":
    main()
