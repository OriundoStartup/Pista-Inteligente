import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os

# Ensure we can find the serviceAccountKey.json
def init_firebase():
    """Inicializa Firebase Admin SDK."""
    cred_path = 'serviceAccountKey.json'
    # Check root or current dir
    if not os.path.exists(cred_path) and os.path.exists(f'../../{cred_path}'):
        cred_path = f'../../{cred_path}'
        
    try:
        if not firebase_admin._apps:
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {'projectId': 'pista-inteligente'})
        return firestore.client()
    except Exception as e:
        print(f"❌ Error Init Firebase: {e}")
        sys.exit(1)

def delete_collection(db, coll_ref, batch_size=400):
    """Ref: https://firebase.google.com/docs/firestore/manage-data/delete-data#collections"""
    docs = list(coll_ref.limit(batch_size).stream())
    deleted_total = 0

    while docs:
        print(f"   Deleting batch of {len(docs)} documents...")
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        
        batch.commit()
        deleted_total += len(docs)
        
        # Fetch next batch
        docs = list(coll_ref.limit(batch_size).stream())

    return deleted_total

def clean_all():
    print("🧹 Iniciando limpieza de Firestore...")
    db = init_firebase()
    
    # Collections to clean
    collections = ['predicciones']
    
    for coll_name in collections:
        print(f"🔍 Limpiando colección: {coll_name}")
        coll_ref = db.collection(coll_name)
        count = delete_collection(db, coll_ref)
        print(f"✅ Eliminados {count} documentos de '{coll_name}'.")

    print("🎉 Limpieza completada.")

if __name__ == "__main__":
    clean_all()
