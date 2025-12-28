# 🏇 Pista Inteligente

> Sistema de predicción hípica impulsado por Inteligencia Artificial y Machine Learning

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura](#-arquitectura)
- [API](#-api)
- [Deploy](#-deploy)
- [Contribución](#-contribución)

## 🎯 Descripción

**Pista Inteligente** es un sistema avanzado de predicción de carreras de caballos que utiliza técnicas de Machine Learning de última generación. El sistema procesa datos históricos de carreras, características de caballos, jinetes y preparadores para generar predicciones precisas y calibradas.

### ¿Qué hace especial a Pista Inteligente?

- **Ensemble de 3 Modelos GBDT**: Combina LightGBM, XGBoost y CatBoost con un meta-learner Ridge
- **Calibración Profesional**: Probabilidades diferenciadas que reflejan verdaderas chances de victoria
- **Arquitectura Escalable**: Diseñado para Cloud Run con sincronización automática a Firestore
- **Pipeline Automatizado**: ETL, entrenamiento, inferencia y deploy completamente automatizados

## ✨ Características

### Core del Sistema

- 🤖 **Ensemble v4.0**: 3 modelos GBDT + meta-learner con mejora de +5-15% NDCG vs baseline
- 📊 **Feature Engineering Avanzado**: 
  - Estadísticas históricas por caballo, jinete y preparador
  - Features temporales (lags, rolling stats)
  - Encoding inteligente de variables categóricas
- 🎯 **Calibración de Probabilidades**: Temperature scaling + amplification para probabilidades realistas
- ♻️ **Reentrenamiento Automático**: El sistema se actualiza con cada nueva carrera
- ☁️ **Sincronización Cloud**: Migración incremental a Firestore con retry logic

### Web Application

- 🌐 **Interfaz Responsive**: Diseño adaptable para desktop y mobile
- 📱 **Progressive Web App**: Funciona offline después de primera carga
- 📈 **Visualización de Precisión**: Gráficos interactivos de accuracy histórico
- 🏆 **Top 4 Predicciones**: Muestra los 4 caballos más probables por carrera
- 🔄 **Actualización Automática**: Las predicciones se actualizan diariamente

## 🛠️ Tecnologías

### Backend
- **Python 3.8+**: Lenguaje principal
- **Flask 2.0+**: Framework web
- **SQLite**: Base de datos local
- **Firestore**: Base de datos en la nube
- **Pandas & NumPy**: Procesamiento de datos

### Machine Learning
- **LightGBM**: Modelo base principal
- **XGBoost**: Segundo modelo del ensemble
- **CatBoost**: Tercer modelo del ensemble
- **scikit-learn**: Preprocessing y meta-learning

### Frontend
- **HTML5 & CSS3**: Estructura y diseño
- **JavaScript (Vanilla)**: Interactividad
- **Chart.js**: Visualizaciones

### DevOps & Cloud
- **Docker**: Containerización
- **Google Cloud Run**: Hosting serverless
- **Firebase**: Hosting estático y Firestore
- **GitHub Actions**: CI/CD (opcional)

## 📦 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/pista-inteligente.git
cd pista-inteligente
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**
```bash
# La base de datos se crea automáticamente en la primera ejecución
```

## 🚀 Uso

### Ejecutar Localmente

```bash
# Iniciar la aplicación web
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Sistema de Sincronización

```bash
# Sincronización completa (ETL + Training + Inference + Firebase)
python sync_system.py

# Forzar reentrenamiento completo
python sync_system.py --force

# Usar modelo baseline en lugar de ensemble
python sync_system.py --baseline
```

### Entrenar Modelos

```bash
# Entrenar ensemble v4 (LightGBM + XGBoost + CatBoost)
python -m src.models.train_v4_ensemble

# Entrenar baseline v2 (solo LightGBM)
python -m src.models.train_v2
```

### Scripts de Utilidad

```bash
# Verificar estado del sistema
python Scripts/verification/verify_system_v4.py

# Analizar predicciones
python Scripts/analysis/analizar_predicciones.py

# Limpiar datos en Firestore
python Scripts/maintenance/cleanup_firestore.py
```

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                     SYNC SYSTEM v4.0                    │
└─────────────────────────────────────────────────────────┘
                           ▼
        ┌──────────────────┬──────────────────┐
        ▼                  ▼                  ▼
  ┌─────────┐        ┌─────────┐       ┌──────────┐
  │   ETL   │───────▶│ TRAINING│──────▶│INFERENCE │
  │Pipeline │        │Ensemble │       │ Pipeline │
  └─────────┘        └─────────┘       └──────────┘
        │                  │                  │
        │                  │                  │
        ▼                  ▼                  ▼
  ┌──────────────────────────────────────────────┐
  │           SQLite (Local Database)            │
  └──────────────────────────────────────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   FIREBASE   │
                   │   MIGRATION  │
                   └──────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────┐
  │      Firestore (Cloud Database)              │
  └──────────────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────┐
  │         Flask Web Application                │
  │    (Cloud Run + Firebase Hosting)            │
  └──────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. ETL Pipeline (`src/etl/`)
- Scraping/importación de programas de carreras
- Procesamiento de resultados históricos
- Limpieza y normalización de datos
- Actualización de base de datos

#### 2. ML Models (`src/models/`)
- **Ensemble Ranker**: Combina 3 modelos GBDT
- **Feature Engineering**: Genera características predictivas
- **Inference Pipeline**: Aplica modelos a nuevos datos
- **Training Scripts**: Entrenan y evalúan modelos

#### 3. Data Manager (`src/models/data_manager.py`)
- Interfaz unificada para acceso a datos
- Integración SQLite + Firestore
- Cálculo de estadísticas y métricas
- Gestión de predicciones activas

#### 4. Web Application (`app.py`)
- Rutas Flask para navegación
- Renderizado de predicciones
- Visualización de estadísticas
- API endpoints

## 📡 API

### Endpoints Principales

#### `GET /`
Página principal con predicciones del día

#### `GET /programa`
Programa completo de carreras futuras

#### `GET /precision`
Métricas de precisión del modelo

#### `GET /patrones`
Patrones detectados en resultados históricos

#### `POST /api/cron/update-predictions`
Endpoint protegido para actualización automática (Cloud Scheduler)

## 🌐 Deploy

### Deploy a Cloud Run

1. **Configurar Google Cloud**
```bash
gcloud config set project pista-inteligente
```

2. **Build y Deploy**
```bash
gcloud run deploy pista-inteligente \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

3. **Configurar Cloud Scheduler**
```bash
gcloud scheduler jobs create http update-predictions \
  --schedule="0 9 * * *" \
  --time-zone="America/Santiago" \
  --uri="https://pista-inteligente.run.app/api/cron/update-predictions" \
  --oidc-service-account-email=scheduler@pista-inteligente.iam.gserviceaccount.com
```

### Deploy Frontend a Firebase

```bash
firebase deploy --only hosting
```

## 📊 Performance

| Métrica | Valor |
|---------|-------|
| **Ensemble NDCG** | ~0.82 |
| **Baseline NDCG** | ~0.78 |
| **Mejora vs Baseline** | +5-15% |
| **Tiempo de Inferencia** | ~2-3s |
| **Latencia Web (p95)** | <500ms |
| **Precisión Top-1 (último mes)** | Variable por hipódromo |

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/

# Test específico
python tests/test_inference_basic.py

# Con coverage
python -m pytest --cov=src tests/
```

## 🤝 Contribución

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guidelines

- Seguir PEP 8 para código Python
- Agregar tests para nuevas funcionalidades
- Actualizar documentación según sea necesario
- Mantener commits atómicos y descriptivos

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **ML Engineering Team** - *Desarrollo del sistema de predicción*
- **Oriundo Startup** - *Desarrollo de aplicación web*

## 🙏 Agradecimientos

- Hipódromos de Chile por los datos públicos
- Comunidad de ML y Data Science
- Usuarios que confían en nuestras predicciones

## 📞 Contacto

- Website: [pista-inteligente.web.app](https://pista-inteligente.web.app)
- Email: contacto@oriundo.cl

---

⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub!

**Versión**: 4.0  
**Última actualización**: Diciembre 2025
