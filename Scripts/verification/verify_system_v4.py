"""
Script de Verificación del Sistema Optimizado v4.0
Verifica que todos los componentes estén correctamente integrados

Author: ML Engineering Team
Date: 2025-12-28
"""

import os
import sys
import json

def check_file_exists(path, description):
    """Verifica que un archivo existe"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_module_imports(module_name):
    """Verifica que un módulo se puede importar"""
    try:
        __import__(module_name)
        print(f"✅ Módulo importable: {module_name}")
        return True
    except Exception as e:
        print(f"❌ Error importando {module_name}: {e}")
        return False

def main():
    print("="*70)
    print("VERIFICACIÓN DEL SISTEMA V4.0")
    print("="*70)
    
    all_ok = True
    
    # 1. Verificar archivos críticos
    print("\n[1/4] Verificando archivos críticos...")
    files_to_check = [
        ("src/models/inference_ensemble.py", "Pipeline de inferencia ensemble"),
        ("src/models/train_v4_ensemble.py", "Script de entrenamiento ensemble"),
        ("src/models/ensemble_ranker.py", "Clase EnsembleRanker"),
        ("src/models/features.py", "Feature Engineering"),
        ("sync_system.py", "Sistema de sincronización"),
        ("src/utils/migrate_to_firebase.py", "Migración a Firebase"),
    ]
    
    for path, desc in files_to_check:
        if not check_file_exists(path, desc):
            all_ok = False
    
    # 2. Verificar que los módulos se pueden importar
    print("\n[2/4] Verificando importaciones...")
    modules_to_check = [
        "src.models.ensemble_ranker",
        "src.models.features",
        "src.models.inference_ensemble",
    ]
    
    for module in modules_to_check:
        if not check_module_imports(module):
            all_ok = False
    
    # 3. Verificar estructura de directorios
    print("\n[3/4] Verificando estructura de directorios...")
    dirs_to_check = [
        "src/models",
        "src/utils",
        "src/etl",
        "data",
        "data/db",
    ]
    
    for dir_path in dirs_to_check:
        if not check_file_exists(dir_path, f"Directorio {dir_path}"):
            all_ok = False
    
    # 4. Verificar configuración de sync_system
    print("\n[4/4] Verificando integración de sync_system...")
    
    with open('sync_system.py', 'r', encoding='utf-8') as f:
        sync_content = f.read()
        
    checks = [
        ("inference_ensemble" in sync_content, "Referencia a inference_ensemble"),
        ("use_ensemble" in sync_content, "Parámetro use_ensemble"),
        ("gc.collect()" in sync_content, "Gestión de memoria"),
        ("--baseline" in sync_content, "Argumento --baseline"),
        ("V4.0" in sync_content, "Versión 4.0"),
    ]
    
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"{status} {description}")
        if not check:
            all_ok = False
    
    # Resumen
    print("\n" + "="*70)
    if all_ok:
        print("✅ VERIFICACIÓN EXITOSA")
        print("="*70)
        print("\n🎯 Próximos pasos:")
        print("   1. Entrenar ensemble: python -m src.models.train_v4_ensemble")
        print("   2. Ejecutar sync: python sync_system.py")
        print("   3. Verificar en Firestore: python src/utils/verify_full_cloud.py")
    else:
        print("❌ VERIFICACIÓN FALLÓ")
        print("="*70)
        print("\nRevisa los errores arriba y corrige los problemas.")
        sys.exit(1)

if __name__ == "__main__":
    main()
