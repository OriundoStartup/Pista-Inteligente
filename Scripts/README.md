# Scripts Directory

Esta carpeta contiene scripts de utilidad organizados por categoría.

## 📁 Estructura

### `verification/`
Scripts para verificar el estado del sistema:
- `verify_system_v4.py` - Verificación completa del sistema v4.0
- `verify_models.py` - Validación de modelos ML
- `verify_features.py` - Verificación de feature engineering
- `verify_predictions.py` - Validación de predicciones generadas
- `verify_etl.py` - Verificación del pipeline ETL
- `verify_stats.py` - Validación de estadísticas

### `analysis/`
Scripts para análisis y reportes:
- `analizar_predicciones.py` - Análisis detallado de predicciones
- `analizar_debutantes.py` - Análisis de caballos debutantes
- `audit_system.py` - Auditoría completa del sistema

### `maintenance/`
Scripts de mantenimiento:
- `cleanup_firestore.py` - Limpieza de datos obsoletos en Firestore

## 🚀 Uso

### Verificar sistema antes de deploy
```bash
python scripts/verification/verify_system_v4.py
```

### Analizar predicciones de la última jornada
```bash
python scripts/analysis/analizar_predicciones.py
```

### Limpiar datos antiguos en Firestore
```bash
python scripts/maintenance/cleanup_firestore.py
```

## 📝 Notas

- Todos los scripts deben ejecutarse desde la raíz del proyecto
- Los scripts de verificación son seguros y no modifican datos
- Los scripts de maintenance pueden modificar la base de datos (usar con precaución)
