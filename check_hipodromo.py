import sqlite3

def run():
    try:
        conn = sqlite3.connect('hipica_data.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT hipodromo FROM programa_carreras WHERE fecha='2025-12-07'")
        res = c.fetchall()
        print(f"Hipodromo para 2025-12-07: {res}")
        conn.close()
    except Exception as e:
        print(e)
if __name__ == "__main__":
    run()
