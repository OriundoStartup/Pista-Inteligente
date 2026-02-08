"""
Script para analizar y corregir duplicados de jinetes y caballos
"""
import sqlite3
import re
from collections import defaultdict

def normalize_name(name):
    """Normaliza nombre removiendo puntos, espacios extra y convirtiendo a mayúsculas"""
    if not name:
        return ""
    # Remover caracteres especiales excepto letras y espacios
    name = re.sub(r'[^\w\s]', '', name)
    # Convertir a mayúsculas
    name = name.upper()
    # Remover espacios extras
    name = ' '.join(name.split())
    return name

def find_jinete_duplicates():
    conn = sqlite3.connect('data/db/hipica_data.db')
    c = conn.cursor()
    
    # Obtener todos los jinetes
    c.execute('SELECT id, nombre FROM jinetes')
    jinetes = c.fetchall()
    
    print(f"Total jinetes en BD: {len(jinetes)}")
    
    # Agrupar por nombre normalizado
    groups = defaultdict(list)
    for jid, name in jinetes:
        norm = normalize_name(name)
        groups[norm].append((jid, name))
    
    # Encontrar duplicados
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    
    print(f"\nGrupos con duplicados: {len(duplicates)}")
    print("\nEjemplos de duplicados:")
    
    count = 0
    for norm_name, entries in sorted(duplicates.items(), key=lambda x: -len(x[1])):
        if count >= 20:
            break
        print(f"\n  '{norm_name}':")
        for jid, original in entries:
            # Contar participaciones de este jinete
            c.execute('SELECT COUNT(*) FROM participaciones WHERE jinete_id = ?', (jid,))
            parts = c.fetchone()[0]
            print(f"    ID {jid:4d}: '{original}' ({parts} participaciones)")
        count += 1
    
    # Buscar entradas "basura" (números, muy cortas, etc.)
    print("\n\nEntradas sospechosas (basura):")
    garbage = [j for j in jinetes if len(j[1]) <= 3 or j[1].isdigit()]
    for jid, name in garbage[:20]:
        c.execute('SELECT COUNT(*) FROM participaciones WHERE jinete_id = ?', (jid,))
        parts = c.fetchone()[0]
        print(f"  ID {jid}: '{name}' ({parts} participaciones)")
    
    conn.close()
    return duplicates

def find_caballo_duplicates():
    conn = sqlite3.connect('data/db/hipica_data.db')
    c = conn.cursor()
    
    c.execute('SELECT id, nombre FROM caballos')
    caballos = c.fetchall()
    
    print(f"\n\n{'='*60}")
    print(f"Total caballos en BD: {len(caballos)}")
    
    groups = defaultdict(list)
    for cid, name in caballos:
        norm = normalize_name(name)
        groups[norm].append((cid, name))
    
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    
    print(f"Grupos con duplicados: {len(duplicates)}")
    print("\nEjemplos de duplicados:")
    
    count = 0
    for norm_name, entries in sorted(duplicates.items(), key=lambda x: -len(x[1])):
        if count >= 15:
            break
        print(f"\n  '{norm_name}':")
        for cid, original in entries:
            c.execute('SELECT COUNT(*) FROM participaciones WHERE caballo_id = ?', (cid,))
            parts = c.fetchone()[0]
            print(f"    ID {cid:4d}: '{original}' ({parts} participaciones)")
        count += 1
    
    conn.close()
    return duplicates

if __name__ == "__main__":
    print("ANÁLISIS DE DUPLICADOS EN BASE DE DATOS")
    print("="*60)
    
    jdup = find_jinete_duplicates()
    cdup = find_caballo_duplicates()
    
    print("\n\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Jinetes con duplicados: {len(jdup)} grupos")
    print(f"Caballos con duplicados: {len(cdup)} grupos")
