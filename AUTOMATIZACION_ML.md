# Automatización y Predicciones con Machine Learning

## 🎯 Descripción

Este sistema automatiza el scraping de datos y genera predicciones de llegadas ganadoras usando Machine Learning (Random Forest).

## 📋 Componentes

### 1. `predictor_ml.py`
- **Función**: Entrena modelos de ML y genera predicciones
- **Tecnología**: Random Forest Classifier (sklearn)
- **Salida**: Predicciones guardadas en tabla `predicciones` de la BD

### 2. `automatizacion.py`
- **Función**: Ejecuta scraping y predicciones automáticamente
- **Uso**: Ejecutar antes de cada jornada de carreras

### 3. `scraper.py`
- **Función**: Obtiene datos de Club Hípico e Hipódromo Chile
- **Datos**: Resultados históricos y programa de próximas carreras

## 🚀 Uso

### Ejecución Manual (Antes de cada jornada)

```bash
# Activar entorno virtual
& c:/espacioDeTrabajo/HipicaAntigracity/venv/Scripts/Activate.ps1

# Ejecutar automatización completa
python automatizacion.py
```

Este comando ejecutará:
1. ✅ Scraping de datos actualizados
2. ✅ Entrenamiento del modelo ML
3. ✅ Generación de predicciones para la jornada

### Automatización con Programador de Tareas (Windows)

1. Abrir "Programador de tareas" de Windows
2. Crear nueva tarea básica
3. Configurar:
   - **Nombre**: Pista Inteligente - Actualización Diaria
   - **Desencadenador**: Diariamente a las 6:00 AM
   - **Acción**: Iniciar programa
   - **Programa**: `C:\espacioDeTrabajo\HipicaAntigracity\venv\Scripts\python.exe`
   - **Argumentos**: `automatizacion.py`
   - **Iniciar en**: `C:\espacioDeTrabajo\HipicaAntigracity`

## 📊 Estructura de Datos

### Tabla `predicciones`

```sql
CREATE TABLE predicciones (
    fecha TEXT,
    hipodromo TEXT,
    nro_carrera INTEGER,
    caballo TEXT,
    prob_1ro REAL,        -- Probabilidad de ganar (%)
    prob_2do REAL,        -- Probabilidad de segundo (%)
    prob_3ro REAL,        -- Probabilidad de tercero (%)
    prob_figuracion REAL  -- Probabilidad de top 3 (%)
)
```

## 🤖 Modelo de Machine Learning

### Algoritmo
- **Random Forest Classifier**
- 3 modelos independientes (1º, 2º, 3º lugar)
- 100 árboles de decisión
- Profundidad máxima: 10

### Features (Características)
1. Hipódromo (codificado)
2. Número de carrera
3. Día de la semana
4. Mes del año

### Entrenamiento
- Datos: Últimas 500 carreras históricas
- Actualización: Cada vez que se ejecuta `automatizacion.py`
- Modelos guardados: `modelo_primero.pkl`, `modelo_segundo.pkl`, `modelo_tercero.pkl`

## 📈 Mejoras Futuras

### Corto Plazo
- [ ] Agregar más features (condición de pista, distancia, peso)
- [ ] Implementar validación cruzada
- [ ] Métricas de precisión del modelo

### Mediano Plazo
- [ ] Integrar datos de jinetes y entrenadores
- [ ] Análisis de tendencias temporales
- [ ] API REST para predicciones

### Largo Plazo
- [ ] Deep Learning (LSTM para series temporales)
- [ ] Ensemble de múltiples modelos
- [ ] Sistema de apuestas automatizado

## 🔧 Troubleshooting

### Error: "No hay suficientes datos"
**Solución**: Ejecutar `python scraper.py` varias veces para acumular datos históricos.

### Error: "Modelos no encontrados"
**Solución**: Ejecutar `python predictor_ml.py` para entrenar los modelos.

### Error en scraping
**Solución**: Verificar conexión a internet y que los sitios web estén accesibles.

## 📝 Logs

Los logs de automatización se muestran en consola con timestamps:
```
[2024-11-27 19:00:00] 🔄 Iniciando scraping de datos...
[2024-11-27 19:02:15] ✅ Scraping completado exitosamente
[2024-11-27 19:02:16] 🤖 Generando predicciones con Machine Learning...
[2024-11-27 19:03:45] ✅ Predicciones generadas exitosamente
```

## 🎓 Recursos de Aprendizaje

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Random Forest Explained](https://www.youtube.com/watch?v=J4Wdy0Wc_xQ)
- [Machine Learning for Betting](https://towardsdatascience.com/tagged/sports-betting)
