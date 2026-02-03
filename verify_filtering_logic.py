
import os
from supabase import create_client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import collections

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def verify_logic():
    print("--- Simulating Backend Filtering Logic ---")
    today_str = datetime.now().strftime('%Y-%m-%d')
    past_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    # 1. Fetch Future Races
    print(f"Fetching future races >= {today_str}...")
    res_future = supabase.table('predicciones').select(
        'carrera_id, numero_caballo, carreras!inner(jornadas!inner(fecha))'
    ).gte('carreras.jornadas.fecha', today_str).execute()
    
    future_races = collections.defaultdict(set)
    for row in res_future.data:
        future_races[row['carrera_id']].add(row['numero_caballo'])
    
    print(f"Found {len(future_races)} future races.")
    
    # 2. Fetch Past Results
    print(f"Fetching past results >= {past_date}...")
    res_past = supabase.table('participaciones').select(
        'carrera_id, posicion, numero_mandil, carreras!inner(jornadas!inner(fecha))'
    ).gte('carreras.jornadas.fecha', past_date).lte('posicion', 4).execute()
    
    races_past = collections.defaultdict(list)
    for row in res_past.data:
        races_past[row['carrera_id']].append(row)
        
    print(f"Found {len(races_past)} past races.")
    
    # 3. Find Patterns
    pattern_counts = collections.defaultdict(lambda: {'numeros': [], 'veces': 0})
    
    for c_id, participants in races_past.items():
        participants.sort(key=lambda x: x['posicion'])
        numeros = [p['numero_mandil'] for p in participants if p['numero_mandil'] is not None]
        
        if len(numeros) < 2: continue
        
        # Quinela
        sig = tuple(sorted(numeros[:2]))
        key = f"Q:{'-'.join(map(str, sig))}"
        pattern_counts[key]['numeros'] = list(sig)
        pattern_counts[key]['veces'] += 1
        
        # Trifecta
        if len(numeros) >= 3:
            sig = tuple(sorted(numeros[:3]))
            key = f"T:{'-'.join(map(str, sig))}"
            pattern_counts[key]['numeros'] = list(sig)
            pattern_counts[key]['veces'] += 1

    # 4. Filter
    print("\n--- Filtering Results ---")
    matched_patterns = []
    
    for key, data in pattern_counts.items():
        # Condition 1: Repeated exactly twice
        if data['veces'] != 2:
            continue
            
        # Condition 2: Present in future
        pset = set(data['numeros'])
        is_possible = False
        for race_horses in future_races.values():
            if pset.issubset(race_horses):
                is_possible = True
                break
        
        if is_possible:
            matched_patterns.append((key, data['veces']))
    
    matched_patterns.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n✅ Logic Verification Complete.")
    print(f"Total Patterns Found (Any count): {len(pattern_counts)}")
    print(f"Patterns passing filter (Count=2 AND In Future): {len(matched_patterns)}")
    
    if matched_patterns:
        print("\nTop Matches:")
        for mp in matched_patterns[:10]:
            print(f"  - {mp[0]} (Veces: {mp[1]})")
    else:
        print("\nNo patterns matched the strict criteria.")

if __name__ == "__main__":
    verify_logic()
