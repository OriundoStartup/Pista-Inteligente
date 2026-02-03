import os
from supabase import create_client
from dotenv import load_dotenv
import datetime

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

data = {
    "hipodromo": "CHS",
    "fecha_evento": datetime.date.today().isoformat(),
    "nro_carrera": 10,
    "tipo_apuesta": "Triple N° 2",
    "monto_estimado": 75000000,
    "mensaje_marketing": "¡Pozo Garantizado de Prueba con IA!",
    "created_at": datetime.datetime.now().isoformat(),
    "ticket_sugerido": {
        "titulo": "Sugerencia IA para Triple N° 2",
        "detalle": [
            {"carrera": 10, "caballos": ["#5 El Veloz", "#2 Relámpago"]},
            {"carrera": 11, "caballos": ["#1 Campeón", "#8 Favorito"]},
            {"carrera": 12, "caballos": ["#4 Sorpresa"]}
        ],
        "combinaciones": 4,
        "costo_estimado": 2000
    }
}

try:
    response = supabase.table("pozos_alertas").insert(data).execute()
    print("✅ Inserted test record successfully.")
except Exception as e:
    print(f"❌ Error inserting test record: {e}")
