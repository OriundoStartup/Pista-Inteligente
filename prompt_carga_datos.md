# Prompt de Instrucción para Generación de CSVs (ETL Hípica)

Este documento define las especificaciones exactas para crear archivos CSV compatibles con el sistema de carga ("SmartLoader") de la base de datos hípica.

---

## Instrucción para el Agente/Sistema:

"Actúa como un Ingeniero de Datos experto. Tu tarea es extraer información tabular de documentos (PDFs, imágenes o texto) y estructurarla en un archivo CSV **estrictamente formateado** para su ingesta automática en una base de datos SQL. Sigue estas reglas al pie de la letra:"

### 1. Naming Convention (Nombre del Archivo)
El nombre del archivo CSV **DEBE** seguir este formato para ser detectado y clasificado correctamente:
- **Para Programas (Futuros):** `PROGRAMA_[CODIGO]_[YYYY-MM-DD].csv`
- **Para Resultados (Pasados):** `RESULTADO_[CODIGO]_[YYYY-MM-DD].csv`

**Códigos de Hipódromo permitidos:**
- `VSC`: Valparaíso Sporting
- `CHS`: Club Hípico de Santiago
- `HC`: Hipódromo Chile
- `CONCE`: Club Hípico de Concepción

*Ejemplos:* `PROGRAMA_VSC_2025-12-25.csv`, `RESULTADO_CHS_2025-12-20.csv`

---

### 2. Estructura de Columnas (Headers)
El CSV debe contener las siguientes columnas. Los nombres deben ser exactos (case-insensitive, pero preferiblemente en minúsculas):

| Nombre Columna | Descripción | Formato / Ejemplo | Obligatorio |
| :--- | :--- | :--- | :--- |
| **carrera** | Número de la carrera | Entero (1, 2, 3...) | ✅ SÍ |
| **numero** | Número del caballo (mandil) | Entero (1, 2, 3...) | ✅ SÍ (Crítico) |
| **caballo** | Nombre del ejemplar | Texto (ej. "BIG DADDY") | ✅ SÍ |
| **jinete** | Nombre del jinete | Texto (ej. "JOAQUIN HERRERA") | ✅ SÍ |
| **peso** | Peso del jinete | Decimal (55, 56.5) | ✅ SÍ |
| **distancia** | Metros de la carrera | Entero (1000, 1200) | ✅ SÍ |
| **fecha** | Fecha de la jornada | YYYY-MM-DD | ✅ SÍ |
| **stud** | Stud o Haras | Texto | ⚠️ Opcional |
| **condicion** | Condición de carrera | Texto (ej. "Handicap") | ⚠️ Opcional |
| **posicion** | Lugar de llegada (SOLO RESULTADOS) | Entero (1, 2, 3...) | ✅ SÍ (Solo Resultados) |
| **dividendo** | Pago a ganador (SOLO RESULTADOS) | Decimal (2.5, 10.1) | ⚠️ Opcional |

---

### 3. Reglas de Formato de Datos
1.  **Fechas:** SIEMPRE usar formato ISO `YYYY-MM-DD` (ej. `2025-12-25`). Nunca usar `25/12/2025`.
2.  **Decimales:** Usar punto `.` como separador decimal (ej. `56.5`), aunque el sistema tolera comas.
3.  **Limpieza de Texto:**
    *   Eliminar tildes en nombres de caballos si es posible (ej. "Valparaíso" -> "Valparaiso" es aceptable, pero mantener consistencia).
    *   **Nombres de Caballos:** Deben estar limpios, sin sufijos entre paréntesis como `(Arg)` o `(USA)` a menos que sean parte oficial del nombre.
4.  **Codificación:** Guardar el archivo siempre como **UTF-8**.
5.  **Separador:** Usar coma `,` como delimitador de columnas.

### 4. Ejemplo de Contenido CSV Válido

```csv
carrera,numero,caballo,jinete,peso,distancia,fecha,condicion,stud
1,1,STORM RITAN,F. HENRIQUEZ,56,1100,2025-12-25,Indice 1,DOÑA ELIANA
1,2,BIG DADDY,J. HERRERA,58,1100,2025-12-25,Indice 1,VIEJO PERRO
2,1,EL COIGUE,B. SANCHO,55,1000,2025-12-25,Condicional,MAMMA
```

---

**Nota Final:** Si un campo obligatorio no está disponible en la fuente, intenta inferirlo (ej. la fecha suele estar en el título del documento) o déjalo vacío, pero mantén la columna.
