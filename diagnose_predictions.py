import sqlite3
import os
import datetime

DB_PATH = 'data/db/hipica_data.db'
FECHA_HOY = '2026-01-04'

def check():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check archivos_procesados
    try:
        cursor.execute("SELECT * FROM archivos_procesados WHERE nombre_archivo LIKE ?", (f'%{FECHA_HOY}%',))
        archivos = cursor.fetchall()
        print(f"📂 Archivos procesados para {FECHA_HOY}:")
        for a in archivos:
            print(f"   - {a}")
    except Exception as e:
        print(f"⚠️ Error checking archivos_procesados: {e}")

    # Check programa_carreras
    try:
        cursor.execute("SELECT count(*), hipodromo FROM programa_carreras WHERE fecha = ? GROUP BY hipodromo", (FECHA_HOY,))
        rows = cursor.fetchall()
        print(f"\n📊 Carreras en DB para {FECHA_HOY}:")
        if not rows:
            print("   (Ninguna carrera encontrada)")
        else:
            for count, hip in rows:
                print(f"   - {hip}: {count} caballos/inscripciones")
    except Exception as e:
        print(f"⚠️ Error checking programa_carreras: {e}")

    # Check predicciones
    try:
        cursor.execute("SELECT count(*) FROM predicciones WHERE fecha_carrera = ?", (FECHA_HOY,))
        preds = cursor.fetchone()[0]
        print(f"\n🔮 Predicciones para {FECHA_HOY}: {preds}")
    except Exception as e:
        print(f"⚠️ Error checking predicciones: {e}")

    conn.close()

if __name__ == "__main__":
    check()
