
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

# Init Firebase (Copy-paste logic to be safe)
def init_firebase():
    if firebase_admin._apps:
        return firestore.client()
        
    cred_path = 'serviceAccountKey.json'
    if not os.path.exists(cred_path) and os.path.exists(f'../../{cred_path}'):
        cred_path = f'../../{cred_path}'
    if not os.path.exists(cred_path) and os.path.exists('src/utils/serviceAccountKey.json'):
         cred_path = 'src/utils/serviceAccountKey.json'

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': 'pista-inteligente'})
    return firestore.client()

def delete_club_hipico():
    db = init_firebase()
    print("🔥 Buscando predicciones de 'Club Hípico' para eliminar...")
    
    # Busca 'Club Hípico' y variaciones
    # Nota: Firestore no tiene 'OR', hay que hacer queries separadas o filtrar en cliente
    # Borraremos todo lo futuro para ser limpios
    
    import datetime
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    docs = db.collection('predicciones').where('fecha', '>=', today).stream()
    
    batch = db.batch()
    count = 0
    deleted = 0
    
    for d in docs:
        data = d.to_dict()
        hip = data.get('hipodromo', '').lower()
        if 'club' in hip or 'chile' in hip: # User mentioned "clun hipico", implying Club Hipico. But let's be safe.
            # User specifically said "clun hipico".
            if 'club' in hip:
                print(f" -> Marcando para borrar: {d.id} ({data['hipodromo']})")
                batch.delete(d.reference)
                count += 1
                deleted += 1
        
        if count >= 400:
            batch.commit()
            batch = db.batch()
            count = 0
            
    if count > 0:
        batch.commit()
        
    print(f"✅ Se eliminaron {deleted} documentos de Club Hípico.")

if __name__ == "__main__":
    delete_club_hipico()
