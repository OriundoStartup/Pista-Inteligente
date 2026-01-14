import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env vars
load_dotenv()

class SupabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.init_client()
        return cls._instance
    
    def init_client(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("⚠️ Supabase Credentials missing. Please set SUPABASE_URL and SUPABASE_KEY in .env")
            return
            
        try:
            self.client: Client = create_client(url, key)
            # Test connection basic
            # self.client.table('hipodromos').select("id").limit(1).execute()
        except Exception as e:
            print(f"❌ Error initializing Supabase: {e}")
            self.client = None

    def get_client(self) -> Client:
        if not self.client:
            self.init_client()
        return self.client
    
    def insert(self, table: str, data: dict):
        """Insert a single record"""
        c = self.get_client()
        if not c: return None
        try:
            return c.table(table).insert(data).execute()
        except Exception as e:
            print(f"Error inserting into {table}: {e}")
            return None

    def upsert(self, table: str, data: dict, conflict_columns: list = None):
        """Upsert a record"""
        c = self.get_client()
        if not c: return None
        try:
            query = c.table(table).upsert(data)
            return query.execute()
        except Exception as e:
            print(f"Error upserting into {table}: {e}")
            return None

    def bulk_insert(self, table: str, data_list: list):
        """Bulk insert records"""
        c = self.get_client()
        if not c: return None
        try:
            return c.table(table).insert(data_list).execute()
        except Exception as e:
            print(f"Error bulk inserting into {table}: {e}")
            return None
