# 🏇 Pista Inteligente - Plataforma de Predicciones Hípicas Pro

**Pista Inteligente** es una plataforma avanzada de análisis de datos y predicciones para la hípica chilena. Combina el poder de **Machine Learning (Ensemble Models)** con una arquitectura moderna de **Next.js** y **Supabase** para ofrecer proyecciones de alta precisión en tiempo real.

---

## 🚀 Características Principales

- **🧠 Modelos de IA Ensemble:** Sistema de inferencia optimizado que analiza historiales de jinetes, preparadores y caballos para predecir ganadores.
- **📊 Dashboard en Vivo:** Visualización de estadísticas de jinetes, rendimientos por hipódromo y programas de carreras actualizados vía Supabase.
- **🤖 Chatbot Analyst (RAG):** Asistente inteligente con memoria conversacional que integra datos internos (SQL) y búsquedas web externas (Serper API) para responder dudas técnicas y hípicas.
- **⚡ Arquitectura de Alto Rendimiento:** Implementación de ISR (Incremental Static Regeneration) para un frontend ultrarrápido sin comprometer la frescura de los datos.
- **📱 App Mobile Integrada:** Ecosistema completo con versión móvil desarrollada en React Native / Expo.

---

## 🛠️ Stack Tecnológico

- **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router), TypeScript, Tailwind CSS.
- **Backend/DB:** [Supabase](https://supabase.com/) (PostgreSQL + Auth + RPC).
- **Inteligencia Artificial:** 
  - Modelos Python (Scikit-Learn, Pandas).
  - LLMs: [Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/) & [Llama 3.3 (Groq)](https://groq.com/).
- **Web Scraping & RAG:** Cheerio, Serper.dev API.

---

## 🏗️ Estructura del Proyecto

```text
├── frontend/             # Aplicación Web (Next.js)
├── mobile/               # Aplicación Móvil (Expo/React Native)
├── src/
│   ├── models/           # Lógica de Inferencia y ML
│   ├── scripts/          # Procesamiento de datos y performance
│   └── utils/            # Utilidades de carga a Supabase
├── data/                 # Almacenamiento local de DB y predicciones
└── sync_system.py        # Orquestador del pipeline de datos
```

---

## ⚙️ Configuración y Despliegue

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- Instalar dependencias:
  ```bash
  pip install -r requirements.txt
  cd frontend && npm install
  ```

### Variables de Entorno
Crea archivos `.env` con las siguientes llaves:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `GEMINI_API_KEY` / `GROQ_API_KEY`
- `SERPER_API_KEY` (Para búsqueda web)

---

## 🛡️ Seguridad y Robustez
El sistema implementa:
- **Rate Limiting & Token Caps:** Control de costos en el uso de LLMs.
- **Sanitización de Inputs:** Protección contra Prompt Injection.
- **Robust Scraper:** Manejo de timeouts y rotación de headers para acceso a fuentes externas.

---

## 📧 Contacto y Soporte
Desarrollado por **Oriundo Startup**. Impulsando la tecnología en el deporte hípico.

---
*Optimizado para hípica chilena (Club Hípico de Santiago, Hipódromo Chile, Valparaíso Sporting).*
