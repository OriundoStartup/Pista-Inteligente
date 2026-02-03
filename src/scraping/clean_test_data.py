import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

try:
    # Delete records with the test message
    response = supabase.table("pozos_alertas").delete().like("mensaje_marketing", "%Prueba%").execute()
    print("✅ Test data deleted successfully.")
except Exception as e:
    print(f"❌ Error deleting test data: {e}")
