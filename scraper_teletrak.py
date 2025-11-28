# scraper_teletrak.py
"""Scraper para Teletrak.cl con fallback a modo sin autenticación.

- Primero intenta iniciar sesión con las credenciales provistas.
- Si el login falla (cuenta no habilitada, credenciales incorrectas, endpoint
  desconocido, etc.) el script continúa **sin token**, usando los mismos
  endpoints públicos.
- Los datos (programa del día y resultados recientes) se aplanan y se guardan
  en la base SQLite `hipica_data.db` en las tablas `programa_carreras` y
  `resultados`.
- Cuando la cuenta sea válida, el mismo script volverá a usar el token y
  obtendrá los datos “gated” automáticamente.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------
USERNAME = "juan campos"
PASSWORD = "Juan2041980"

# Endpoints (según la información proporcionada por el usuario)
LOGIN_URL = "https://www.teletrak.cl/api/v1/auth/login"  # se asume, pero puede fallar
PROGRAM_URL = "https://www.teletrak.cl/api/v1/carreras/programa-del-dia"
RESULT_URL = "https://www.teletrak.cl/api/v1/carreras/resultados-recientes"

DB_PATH = Path("hipica_data.db")

# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------
def aplanar_json(data: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    """Convierte un JSON anidado en un diccionario plano.
    - Las listas se convierten a cadena JSON para no perder información.
    """
    items = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(aplanar_json(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = json.dumps(v, ensure_ascii=False)
        else:
            items[new_key] = v
    return items


def guardar_en_db(df: pd.DataFrame, tabla: str) -> None:
    """Inserta un DataFrame en SQLite (crea tabla si no existe)."""
    if df.empty:
        print(f"[⚠️] DataFrame vacío → no se escribe en la tabla '{tabla}'.")
        return
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(tabla, conn, if_exists="append", index=False)
    conn.close()
    print(f"[✅] {len(df)} filas guardadas en la tabla '{tabla}'.")


def obtener_json(sess: requests.Session, url: str) -> Dict:
    """GET → JSON (maneja errores de red)."""
    try:
        resp = sess.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"[❌] Error al solicitar {url}: {e}")
    return resp.json()


def procesar_lista(json_data: Dict) -> pd.DataFrame:
    """Busca la primera lista dentro del JSON y la convierte en DataFrame aplanado."""
    if isinstance(json_data, list):
        lista = json_data
    else:
        lista = None
        for v in json_data.values():
            if isinstance(v, list):
                lista = v
                break
        if lista is None:
            raise RuntimeError("[❌] No se encontró lista de datos en la respuesta.")
    filas = [aplanar_json(item) for item in lista]
    return pd.DataFrame(filas)

# ---------------------------------------------------------------------------
# AUTENTICACIÓN CON FALLBACK
# ---------------------------------------------------------------------------
def intentar_login() -> str | None:
    """Intenta login y devuelve token Bearer o None si falla."""
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
    }
    try:
        resp = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[⚠️] Login falló (se usará modo sin auth): {e}")
        return None
    data = resp.json()
    token = (
        data.get("access_token")
        or data.get("token")
        or data.get("jwt")
        or data.get("authorization")
    )
    if not token:
        print("[⚠️] Login respondió, pero no se encontró token en la respuesta.")
        return None
    print("[🔐] Login exitoso – token obtenido.")
    return token

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    session = requests.Session()
    token = intentar_login()
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
        modo = "AUTENTICADO"
    else:
        modo = "SIN AUTENTICACIÓN (público)"
    print(f"[🚀] Ejecutando scraper en modo **{modo}**")

    # Programa del día
    print("[⏳] Solicitando programa del día …")
    prog_json = obtener_json(session, PROGRAM_URL)
    df_programa = procesar_lista(prog_json)
    print(f"[📊] Programa: {len(df_programa)} carreras encontradas.")
    guardar_en_db(df_programa, "programa_carreras")

    # Resultados recientes
    print("[⏳] Solicitando resultados recientes …")
    res_json = obtener_json(session, RESULT_URL)
    df_resultados = procesar_lista(res_json)
    print(f"[📊] Resultados: {len(df_resultados)} registros encontrados.")
    guardar_en_db(df_resultados, "resultados")

    # Esquema final
    print("\n=== ESQUEMA FINAL – Programa ===")
    print(df_programa.columns.tolist())
    print("\n=== ESQUEMA FINAL – Resultados ===")
    print(df_resultados.columns.tolist())
    print("\n✅  Scraping completado y datos guardados en 'hipica_data.db'.")

if __name__ == "__main__":
    main()
