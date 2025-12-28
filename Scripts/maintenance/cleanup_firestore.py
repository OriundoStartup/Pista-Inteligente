import firebase_admin
from firebase_admin import credentials, firestore
import sys

def cleanup_firestore_predictions():
    """Limpia todas las predicciones de Firestore antes de regenerar con mejoras"""
    
    print("🧹 Iniciando limpieza de Firestore...")
    
    # Initialize Firebase
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print(f"❌ Error inicializando Firebase: {e}")
        sys.exit(1)
    
    # Get all prediction documents
    try:
        collection_ref = db.collection('predicciones')
        docs = collection_ref.stream()
        
        # Count first
        doc_list = list(docs)
        total_docs = len(doc_list)
        
        if total_docs == 0:
            print("ℹ️  No hay predicciones para borrar.")
            return
        
        print(f"📊 Encontradas {total_docs} predicciones para borrar...")
        
        # Confirm
        confirm = input(f"\n⚠️  ¿Confirmas borrar {total_docs} documentos? (escribe 'SI' para confirmar): ")
        
        if confirm != 'SI':
            print("❌ Operación cancelada por el usuario.")
            return
        
        # Delete in batches
        batch_size = 500
        deleted = 0
        
        # Re-fetch (iterator was consumed)
        docs = collection_ref.stream()
        batch = db.batch()
        count = 0
        
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            deleted += 1
            
            if count >= batch_size:
                batch.commit()
                print(f"   Borrados {deleted}/{total_docs}...")
                batch = db.batch()
                count = 0
        
        # Commit remaining
        if count > 0:
            batch.commit()
        
        print(f"✅ Se borraron {deleted} predicciones de Firestore exitosamente!")
        print("\n📝 Ahora ejecuta la sincronización forzada:")
        print("   python sync_system.py --force")
        
    except Exception as e:
        print(f"❌ Error borrando predicciones: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    cleanup_firestore_predictions()
