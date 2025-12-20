import sqlite3

def cleanup():
    db_path = 'data/db/hipica_data.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("🧹 Iniciando Limpieza de Duplicados (VAL vs Valparaíso Sporting)...")

    # 1. Identify IDs
    # We want to keep 'Valparaíso Sporting' and delete 'VAL'
    target_name = 'VAL'
    keep_name = 'Valparaíso Sporting'
    
    c.execute("SELECT id FROM hipodromos WHERE nombre = ?", (target_name,))
    res_val = c.fetchone()
    
    c.execute("SELECT id FROM hipodromos WHERE nombre = ?", (keep_name,))
    res_vsc = c.fetchone()
    
    if not res_val:
        print("✅ No se encontró hipódromo 'VAL'. Nada que limpiar.")
        return

    val_id = res_val[0]
    print(f"   • Encontrado '{target_name}' con ID: {val_id}")

    # 2. Get Jornadas to delete
    c.execute("SELECT id, fecha FROM jornadas WHERE hipodromo_id = ?", (val_id,))
    jornadas_to_delete = c.fetchall()
    
    if not jornadas_to_delete:
         print("   • Sin jornadas asociadas a VAL.")
    else:
         ids_jornadas = [str(j[0]) for j in jornadas_to_delete]
         print(f"   • Eliminando {len(ids_jornadas)} jornadas de VAL...")
         
         # 3. Cascading Deletes
         # Participaciones
         c.execute(f"""
             DELETE FROM participaciones 
             WHERE carrera_id IN (
                 SELECT id FROM carreras WHERE jornada_id IN ({','.join(ids_jornadas)})
             )
         """)
         print(f"     - Participaciones eliminadas: {c.rowcount}")
         
         # Carreras
         c.execute(f"DELETE FROM carreras WHERE jornada_id IN ({','.join(ids_jornadas)})")
         print(f"     - Carreras eliminadas: {c.rowcount}")

         # Jornadas
         c.execute(f"DELETE FROM jornadas WHERE id IN ({','.join(ids_jornadas)})")
         print(f"     - Jornadas eliminadas: {c.rowcount}")

    # 4. Delete Hipodromo entry
    c.execute("DELETE FROM hipodromos WHERE id = ?", (val_id,))
    print(f"   • Hipódromo 'VAL' eliminado: {c.rowcount}")

    conn.commit()
    conn.close()
    print("✨ Limpieza completada.")

if __name__ == "__main__":
    cleanup()
