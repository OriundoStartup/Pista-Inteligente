"""
Script to verify top jockeys in 2026 from Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)

print("🔍 Verificando jinetes con más victorias en 2026...\n")

# Query participaciones con joins
response = supabase.from_('participaciones').select(
    '''
    posicion,
    jinetes (nombre),
    carreras!inner (
        jornadas!inner (
            fecha
        )
    )
    '''
).gte('carreras.jornadas.fecha', '2026-01-01').execute()

print(f"📊 Total participaciones desde 2026-01-01: {len(response.data)}")

# Aggregate stats
stats = {}
for row in response.data:
    jinete_name = row.get('jinetes', {}).get('nombre', 'Desconocido') if row.get('jinetes') else 'Desconocido'
    nombre = jinete_name.strip()
    
    if nombre not in stats:
        stats[nombre] = {'ganadas': 0, 'montes': 0}
    
    stats[nombre]['montes'] += 1
    
    if row.get('posicion') == 1 or row.get('posicion') == '1':
        stats[nombre]['ganadas'] += 1

# Sort by wins
sorted_jinetes = sorted(
    [
        {
            'jinete': nombre, 
            'ganadas': stat['ganadas'], 
            'montes': stat['montes'],
            'eficiencia': (stat['ganadas'] / stat['montes'] * 100) if stat['montes'] > 0 else 0
        }
        for nombre, stat in stats.items()
    ],
    key=lambda x: x['ganadas'],
    reverse=True
)

output_lines = []
output_lines.append(f"\n🏆 Top 10 Jinetes 2026:\n")
output_lines.append(f"{'#':<4} {'Jinete':<30} {'Ganadas':<10} {'Montes':<10} {'Eficiencia':<12}")
output_lines.append("="*70)

for idx, jinete in enumerate(sorted_jinetes[:10], 1):
    line = f"{idx:<4} {jinete['jinete']:<30} {jinete['ganadas']:<10} {jinete['montes']:<10} {jinete['eficiencia']:<12.1f}%"
    output_lines.append(line)
    print(line)

output_lines.append(f"\n✅ Consulta completada")

# Save to file
with open('jinetes_2026_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\n✅ Resultados guardados en jinetes_2026_results.txt")
