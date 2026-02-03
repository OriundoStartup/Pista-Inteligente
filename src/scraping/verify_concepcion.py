import os
import datetime
import json
from supabase import create_client
from dotenv import load_dotenv
from monitor_pozos import generar_ticket_ia

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def test_chc():
    today = datetime.date.today().isoformat()
    # today = "2026-02-03" # Uncomment if needed
    
    print(f"Generating Real AI Ticket for CHC on {today}...")
    
    # Try generic race 1, Triple (Multi-race)
    # Using 'Triple' to trigger multi-race logic
    ticket = generar_ticket_ia("CHC", today, 1, "Triple")
    
    if ticket:
        print("✅ SUCCESS! Real predictions found.")
        print(json.dumps(ticket, indent=2, ensure_ascii=False))
        
        # Insert this as a "Live Test"
        data = {
            "hipodromo": "CHC",
            "fecha_evento": today,
            "nro_carrera": 1,
            "tipo_apuesta": "Triple Inicial (IA)",
            "monto_estimado": 12500000, # A realistic amount
            "mensaje_marketing": "¡Pozo Estimado con Jugada Inteligente!",
            "ticket_sugerido": ticket
        }
        supabase.table("pozos_alertas").insert(data).execute()
        print("🚀 Inserted 'Real-Data' alert to Supabase.")
    else:
        print("❌ No predictions found for CHC today (or logic failed).")

if __name__ == "__main__":
    # resp = supabase.table("predicciones").select("*").limit(1).execute()
    # print("Predicciones Sample Row:", json.dumps(resp.data, indent=2))
    test_chc()
