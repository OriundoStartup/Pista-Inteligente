import sqlite3

def run():
    try:
        conn = sqlite3.connect('hipica_data.db')
        c = conn.cursor()
        print("Borrando registros del 2025-12-07...")
        c.execute("DELETE FROM programa_carreras WHERE fecha='2025-12-07'")
        print(f"Filas afectadas: {c.rowcount}")
        conn.commit()
        conn.close()
        print("Listo.")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    run()
