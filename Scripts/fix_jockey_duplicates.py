
import sqlite3
import os
import sys

# Path to DB
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'hipica_data.db')

# Alias Mapping (Must match ETL)
JOCKEY_ALIASES = {
    'J. HERRERA': 'JOAQUIN HERRERA',
    'G. ULLOA': 'GONZALO ULLOA',
    'J. MEDINA': 'JAIME MEDINA',
    'B. SANCHO': 'BENJAMIN SANCHO',
    'N. MOLINA': 'NICOLAS MOLINA',
    'F. HENRIQUEZ': 'FELIPE HENRIQUEZ',
    'J. I. GUAJARDO': 'JAVIER I. GUAJARDO',
    'J. I. GUARJARDO': 'JAVIER I. GUAJARDO',
    'K. ESPINA': 'KEVIN ESPINA',
    'W. QUINTEROS': 'WLADIMIR QUINTEROS',
    'R. CISTERNAS': 'RAFAEL CISTERNAS'
}

def fix_duplicates():
    print(f"Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates_count = 0
    deletes_count = 0
    
    try:
        # 1. Ensure target (canonical) names exist
        for alias, canonical in JOCKEY_ALIASES.items():
            print(f"\nProcessing: {alias} -> {canonical}")
            
            # Find IDs
            cursor.execute("SELECT id FROM jinetes WHERE nombre = ?", (alias,))
            alias_row = cursor.fetchone()
            
            cursor.execute("SELECT id FROM jinetes WHERE nombre = ?", (canonical,))
            canonical_row = cursor.fetchone()
            
            if not alias_row:
                print(f"   - Alias '{alias}' not found. Skipping.")
                continue
                
            alias_id = alias_row[0]
            
            if not canonical_row:
                print(f"   - Canonical '{canonical}' not found. Renaming alias directly.")
                cursor.execute("UPDATE jinetes SET nombre = ? WHERE id = ?", (canonical, alias_id))
                updates_count += 1
                continue
                
            canonical_id = canonical_row[0]
            print(f"   - Merging ID {alias_id} ({alias}) into ID {canonical_id} ({canonical})")
            
            # Update Participaciones
            cursor.execute("UPDATE participaciones SET jinete_id = ? WHERE jinete_id = ?", (canonical_id, alias_id))
            processed = cursor.rowcount
            print(f"     -> Updated {processed} participation records.")
            
            # Update Programa
            cursor.execute("UPDATE programa_carreras SET jinete_id = ? WHERE jinete_id = ?", (canonical_id, alias_id))
            processed_prog = cursor.rowcount
            print(f"     -> Updated {processed_prog} program records.")

             # Update Predicciones
            cursor.execute("UPDATE predicciones SET jinete_id = ? WHERE jinete_id = ?", (canonical_id, alias_id))
            processed_pred = cursor.rowcount
            print(f"     -> Updated {processed_pred} prediction records.")
            
            # Delete Alias
            cursor.execute("DELETE FROM jinetes WHERE id = ?", (alias_id,))
            deletes_count += 1
            print("     -> Deleted alias record.")
            
        conn.commit()
        print("\n" + "="*50)
        print(f"DONE. Updated jockeys: {updates_count}, Merged/Deleted: {deletes_count}")
        print("="*50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_duplicates()
