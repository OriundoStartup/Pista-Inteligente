---
title: Pista Inteligente
emoji: 🐎
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: app_frontend.py
pinned: false
license: mit
---

# 🐎 Pista Inteligente: Análisis Hípico

Este proyecto es una aplicación de análisis hípico diseñada para detectar patrones de llegada (trifectas) repetidos y ofrecer proyecciones estadísticas.

## Descripción
El sistema analiza resultados históricos de carreras para identificar combinaciones de llegada (1°-2°-3°) frecuentes y alertar sobre patrones repetidos en próximas jornadas.

## Características
*   **Detección de Patrones:** Identifica trifectas que se han repetido históricamente.
*   **Alertas de Jornada:** Cruza los patrones históricos con la programación de la próxima jornada.
*   **Proyecciones Estadísticas:** Genera las combinaciones más probables basadas en el rendimiento histórico de los caballos.
*   **Interfaz Interactiva:** Construida con Streamlit para una experiencia de usuario fluida.

## Stack Tecnológico
*   **Frontend:** Streamlit
*   **Lenguaje:** Python
*   **Análisis de Datos:** Pandas
*   **Base de Datos:** SQLite

## Ejecución Local
1.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
2.  Ejecutar la aplicación:
    ```bash
    streamlit run app_frontend.py
    ```

## Despliegue en Hugging Face Spaces
Este repositorio está configurado para desplegarse automáticamente en Hugging Face Spaces usando Docker.
- **SDK:** Docker
- **Puerto:** 7860
