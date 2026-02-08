"""
Script para fusionar entidades duplicadas (jinetes)
Consolida participaciones bajo un único ID canónico.
"""
import sqlite3
import re
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_name(name):
    """Normaliza nombre para comparación"""
    if not name:
        return ""
    # Remover puntos y caracteres especiales
    name = re.sub(r'[^\w\s]', '', name)
    name = name.upper().strip()
    name = ' '.join(name.split())
    return name

def merge_jinetes():
    """Fusiona jinetes duplicados consolidando participaciones"""
    conn = sqlite3.connect('data/db/hipica_data.db')
    c = conn.cursor()
    
    logger.info("="*60)
    logger.info("FUSIÓN DE JINETES DUPLICADOS")
    logger.info("="*60)
    
    # Obtener todos los jinetes
    c.execute('SELECT id, nombre FROM jinetes')
    jinetes = c.fetchall()
    
    logger.info(f"Total jinetes antes: {len(jinetes)}")
    
    # Agrupar por nombre normalizado
    groups = defaultdict(list)
    for jid, name in jinetes:
        norm = normalize_name(name)
        if norm and len(norm) > 3:  # Ignorar entradas basura
            groups[norm].append((jid, name))
    
    # Procesar duplicados
    merged_count = 0
    participations_moved = 0
    ids_to_delete = []
    
    for norm_name, entries in groups.items():
        if len(entries) <= 1:
            continue
        
        # Elegir el ID canónico (el que tiene más participaciones)
        entries_with_count = []
        for jid, name in entries:
            c.execute('SELECT COUNT(*) FROM participaciones WHERE jinete_id = ?', (jid,))
            count = c.fetchone()[0]
            entries_with_count.append((jid, name, count))
        
        # Ordenar por participaciones (desc), tomar el primero como canónico
        entries_with_count.sort(key=lambda x: -x[2])
        canonical_id, canonical_name, canonical_count = entries_with_count[0]
        
        # Fusionar los demás hacia el canónico
        for jid, name, count in entries_with_count[1:]:
            if count > 0:
                logger.info(f"  Fusionando '{name}' (ID:{jid}, {count} parts) → '{canonical_name}' (ID:{canonical_id})")
                
                # Actualizar participaciones
                c.execute('UPDATE participaciones SET jinete_id = ? WHERE jinete_id = ?', 
                         (canonical_id, jid))
                participations_moved += count
            
            ids_to_delete.append(jid)
            merged_count += 1
    
    # Eliminar jinetes duplicados
    if ids_to_delete:
        placeholders = ','.join('?' * len(ids_to_delete))
        c.execute(f'DELETE FROM jinetes WHERE id IN ({placeholders})', ids_to_delete)
        logger.info(f"\nEliminados {len(ids_to_delete)} registros de jinetes duplicados")
    
    # Eliminar entradas basura (números, muy cortas)
    c.execute("DELETE FROM jinetes WHERE LENGTH(nombre) <= 3 OR nombre GLOB '[0-9]*'")
    garbage_deleted = c.rowcount
    logger.info(f"Eliminadas {garbage_deleted} entradas basura")
    
    conn.commit()
    
    # Verificar resultado
    c.execute('SELECT COUNT(*) FROM jinetes')
    final_count = c.fetchone()[0]
    
    logger.info("\n" + "="*60)
    logger.info("RESUMEN")
    logger.info("="*60)
    logger.info(f"Jinetes fusionados: {merged_count}")
    logger.info(f"Participaciones reasignadas: {participations_moved}")
    logger.info(f"Total jinetes después: {final_count}")
    
    conn.close()
    return merged_count, participations_moved

def update_programa_carreras():
    """Actualiza referencias en programa_carreras"""
    conn = sqlite3.connect('data/db/hipica_data.db')
    c = conn.cursor()
    
    logger.info("\nActualizando referencias en programa_carreras...")
    
    # Obtener mapeo de jinetes
    c.execute('SELECT id, nombre FROM jinetes')
    jinete_map = {normalize_name(r[1]): r[0] for r in c.fetchall()}
    
    # Obtener programa sin jinete_id válido
    c.execute('SELECT id, jinete_id FROM programa_carreras WHERE jinete_id IS NULL OR jinete_id = 0')
    to_update = c.fetchall()
    
    logger.info(f"  Encontradas {len(to_update)} entradas sin jinete_id válido")
    
    conn.close()

if __name__ == "__main__":
    try:
        merged, moved = merge_jinetes()
        print(f"\n✅ Fusión completada: {merged} jinetes fusionados, {moved} participaciones reasignadas")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
