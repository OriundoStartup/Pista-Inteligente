"""
Script para verificar y limpiar datos duplicados de jornadas/carreras,
y luego disparar redeploy en Vercel.
"""
import sys
import os
import requests
sys.path.append('.')

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
c = db.get_client()

print("=" * 60)
print("VERIFICANDO DATOS EN SUPABASE")
print("=" * 60)

# 1. Hipódromos
h = c.table('hipodromos').select('id, nombre').execute()
hip_map = {x['id']: x['nombre'] for x in h.data}
print("\nHIPODROMOS:")
for row in h.data:
    print(f"  {row['id']}: {row['nombre']}")

# 2. Jornadas
j = c.table('jornadas').select('id, fecha, hipodromo_id').order('fecha').execute()
print("\nJORNADAS:")
for row in j.data:
    hip_name = hip_map.get(row['hipodromo_id'], 'DESCONOCIDO')
    print(f"  Jornada #{row['id']}: {row['fecha']} -> {hip_name} (id: {row['hipodromo_id']})")

# 3. Contar carreras por jornada
car = c.table('carreras').select('id, numero, jornada_id').execute()
jornada_counts = {}
for carro in car.data:
    jid = carro['jornada_id']
    jornada_counts[jid] = jornada_counts.get(jid, 0) + 1

print("\nCARRERAS POR JORNADA:")
for jid, cnt in jornada_counts.items():
    j_info = [x for x in j.data if x['id'] == jid]
    if j_info:
        fecha = j_info[0]['fecha']
        hip_id = j_info[0]['hipodromo_id']
        hip_name = hip_map.get(hip_id, 'DESCONOCIDO')
        print(f"  Jornada #{jid} ({fecha}, {hip_name}): {cnt} carreras")

# 4. Verificar si hay jornadas del 14 con hipódromo incorrecto
valp_id = 89  # Valparaíso Sporting
print("\n" + "=" * 60)
print("VERIFICANDO JORNADAS DEL 2026-01-14")
print("=" * 60)

jornadas_14 = [x for x in j.data if x['fecha'] == '2026-01-14']
for jorn in jornadas_14:
    hip_name = hip_map.get(jorn['hipodromo_id'], 'DESCONOCIDO')
    status = "✅ CORRECTO" if jorn['hipodromo_id'] == valp_id else "❌ INCORRECTO - debería ser Valparaíso"
    print(f"  Jornada #{jorn['id']}: hipodromo_id={jorn['hipodromo_id']} ({hip_name}) {status}")

# 5. Corregir si es necesario
for jorn in jornadas_14:
    if jorn['hipodromo_id'] != valp_id:
        print(f"\n  Corrigiendo jornada #{jorn['id']} a Valparaíso Sporting...")
        c.table('jornadas').update({'hipodromo_id': valp_id}).eq('id', jorn['id']).execute()
        print(f"  ✅ Corregido!")

# 6. Disparar redeploy de Vercel
print("\n" + "=" * 60)
print("DISPARANDO REDEPLOY EN VERCEL")
print("=" * 60)

deploy_hook = os.getenv('VERCEL_DEPLOY_HOOK')
if deploy_hook:
    try:
        r = requests.post(deploy_hook, timeout=30)
        if r.status_code in [200, 201]:
            print("✅ Redeploy disparado exitosamente!")
        else:
            print(f"⚠️ Respuesta de Vercel: {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️ VERCEL_DEPLOY_HOOK no está configurado")
    print("   Necesitas hacer redeploy manual desde el dashboard de Vercel")
    print("   O configurar el hook en tu .env")

print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
