# Base de Datos del Sistema 🗄️

## Ubicación Correcta

La base de datos **DEBE** estar ubicada en:

```
data/db/hipica_data.db
```

## ⚠️ Problema Común: Database Duplicada en Raíz

### Síntoma
Se crea un archivo `hipica_data.db` vacío en la raíz del proyecto.

### Causa
Scripts temporales o de debugging que usan la ruta incorrecta:
```python
# ❌ INCORRECTO - crea BD en raíz
sqlite3.connect('hipica_data.db')

# ✅ CORRECTO
sqlite3.connect('data/db/hipica_data.db')
```

### Solución
1. **Eliminar el archivo duplicado**:
   ```bash
   rm hipica_data.db  # (en raíz del proyecto)
   ```

2. **Verificar que no se vuelva a crear**:
   - Los scripts de producción (`etl_pipeline.py`, `train_v2.py`, `data_manager.py`) ya usan la ruta correcta.
   - Scripts de debugging en raíz (`debug_*.py`, `check_*.py`) NO deben usarse en producción.
   - El `.gitignore` está configurado para ignorar `*.db` incluyendo el archivo duplicado.

3. **Si persiste el problema**:
   - Buscar en el código: `sqlite3.connect('hipica_data.db')`
   - Cambiar a: `sqlite3.connect('data/db/hipica_data.db')`

## Rutas Correctas en el Código

### ETL Pipeline
```python
# src/etl/etl_pipeline.py línea 24
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                       'data', 'db', 'hipica_data.db')
```

### Train V2
```python
# src/models/train_v2.py línea 12
def __init__(self, db_path='data/db/hipica_data.db'):
```

### Data Manager
```python
# src/models/data_manager.py líneas 14, 32, 89
def cargar_datos(nombre_db='data/db/hipica_data.db'):
def cargar_datos_3nf(nombre_db='data/db/hipica_data.db'):
def cargar_programa(nombre_db='data/db/hipica_data.db'):
```

## Estructura de Directorios

```
HipicaAntigracity/
├── data/
│   ├── db/
│   │   └── hipica_data.db    ✅ UBICACIÓN CORRECTA
│   └── cache_analisis.json
├── exports/                   CSV de entrada
├── src/
│   ├── etl/
│   └── models/
└── hipica_data.db             ❌ NO DEBE EXISTIR
```

## Prevención

El `.gitignore` incluye:
```gitignore
*.db                    # Ignora todos los .db
/hipica_data.db         # Explícitamente ignora BD en raíz
debug_*.py              # Scripts temporales
check_*.py
list_*.py
```

> [!IMPORTANT]
> Si ves `hipica_data.db` en la raíz del proyecto, **elimínalo inmediatamente**. Es una copia vacía creada por error.
