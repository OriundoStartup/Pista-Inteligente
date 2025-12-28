import sqlite3
from datetime import datetime

print("🔍 Analizando caballos nuevos (debutantes) en Carrera 9 - Hoy\n")
print("=" * 70)

# Fecha de hoy
hoy = datetime.now().strftime('%Y-%m-%d')
print(f"📅 Fecha: {hoy}\n")

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

# Obtener caballos de la carrera 9 de hoy
cursor.execute("""
    SELECT pc.numero, c.nombre as caballo, c.id as caballo_id, j.nombre as jinete
    FROM programa_carreras pc
    LEFT JOIN caballos c ON pc.caballo_id = c.id
    LEFT JOIN jinetes j ON pc.jinete_id = j.id
    WHERE pc.fecha = ? AND pc.nro_carrera = 9
    ORDER BY pc.numero
""", (hoy,))

caballos_carrera = cursor.fetchall()

if not caballos_carrera:
    print(f"⚠️ No se encontró programa para hoy ({hoy}) o no hay carrera 1")
    conn.close()
    exit()

print(f"🏇 CARRERA 9 - {hoy}")
print(f"Total de caballos en la carrera: {len(caballos_carrera)}\n")
print("-" * 70)

debutantes = []
con_historial = []

for numero, caballo, caballo_id, jinete in caballos_carrera:
    # Verificar si el caballo tiene historial
    cursor.execute("""
        SELECT COUNT(*) FROM participaciones 
        WHERE caballo_id = ?
    """, (caballo_id,))
    
    carreras_previas = cursor.fetchone()[0]
    
    status = "🆕 DEBUTANTE" if carreras_previas == 0 else f"📊 {carreras_previas} carreras"
    
    print(f"#{numero:2d} - {caballo:30s} ({jinete:25s}) - {status}")
    
    if carreras_previas == 0:
        debutantes.append({
            'numero': numero,
            'caballo': caballo,
            'jinete': jinete
        })
    else:
        con_historial.append({
            'numero': numero,
            'caballo': caballo,
            'jinete': jinete,
            'carreras': carreras_previas
        })

# Resumen
print("\n" + "=" * 70)
print("📊 RESUMEN")
print("=" * 70)
print(f"🆕 Caballos DEBUTANTES (sin historial): {len(debutantes)}")
print(f"📊 Caballos con HISTORIAL: {len(con_historial)}")
print(f"📈 Porcentaje de debutantes: {(len(debutantes)/len(caballos_carrera)*100):.1f}%")

if debutantes:
    print(f"\n🆕 Lista de DEBUTANTES:")
    for d in debutantes:
        print(f"   #{d['numero']} - {d['caballo']} ({d['jinete']})")

# Estadística adicional
if con_historial:
    promedio_carreras = sum(h['carreras'] for h in con_historial) / len(con_historial)
    max_carreras = max(h['carreras'] for h in con_historial)
    caballo_mas_exp = [h for h in con_historial if h['carreras'] == max_carreras][0]
    
    print(f"\n📊 Estadísticas de caballos con historial:")
    print(f"   • Promedio de carreras: {promedio_carreras:.1f}")
    print(f"   • Más experimentado: {caballo_mas_exp['caballo']} con {max_carreras} carreras")

conn.close()
