# Prompts Optimizados para Generación de CSVs - Pista Inteligente

Este documento contiene los prompts exactos para el agente que extrae datos de PDFs/documentos de programas y resultados hípicos. Cada CSV debe seguir estas especificaciones para un volcado óptimo a la base de datos.

---

## 📋 REGLAS GENERALES (Todos los CSVs)

1. **Nombre del archivo:**
   - Programas: `PROGRAMA_[CODIGO]_[YYYY-MM-DD].csv`
   - Resultados: `RESULTADO_[CODIGO]_[YYYY-MM-DD].csv`
   
2. **Códigos de hipódromo:** `HC`, `CHC`, `VSC`, `CONCE`

3. **Formato obligatorio:**
   - Codificación: UTF-8
   - Separador: coma `,`
   - Decimales: punto `.`
   - Fechas: YYYY-MM-DD

---

## 🏇 PROMPT PARA PROGRAMAS - HIPÓDROMO CHILE (HC)

```
Actúa como Ingeniero de Datos experto. Extrae los datos del programa de carreras del Hipódromo Chile y genera un CSV con estas columnas EXACTAS en este orden:

carrera,numero,caballo,jinete,peso,distancia,hora,fecha,condicion,stud

REGLAS:
1. Nombre archivo: PROGRAMA_HC_[FECHA].csv (ej: PROGRAMA_HC_2026-01-16.csv)
2. carrera: número entero (1, 2, 3...)
3. numero: número del caballo/mandil (entero)
4. caballo: nombre limpio SIN sufijos (Arg), (USA), etc.
5. jinete: nombre completo del jinete
6. peso: decimal con punto (ej: 56.5)
7. distancia: metros como entero (ej: 1100, 1200)
8. hora: formato HH:MM sin "APROX" (ej: 14:30, 15:00)
9. fecha: YYYY-MM-DD
10. condicion: tipo de carrera (Handicap, Condicional, etc.)
11. stud: nombre del stud/haras

Ejemplo:
carrera,numero,caballo,jinete,peso,distancia,hora,fecha,condicion,stud
1,1,STORM RUNNER,J. MEDINA,56,1100,14:30,2026-01-16,Handicap,DOÑA ELIANA
1,2,BIG DADDY,B. SANCHO,57.5,1100,14:30,2026-01-16,Handicap,VIEJO PERRO
```

---

## 🏇 PROMPT PARA PROGRAMAS - CLUB HÍPICO DE SANTIAGO (CHC)

```
Actúa como Ingeniero de Datos experto. Extrae los datos del programa de carreras del Club Hípico de Santiago y genera un CSV con estas columnas EXACTAS en este orden:

carrera,numero,caballo,jinete,peso,distancia,hora,fecha,condicion,stud

REGLAS:
1. Nombre archivo: PROGRAMA_CHC_[FECHA].csv (ej: PROGRAMA_CHC_2026-01-16.csv)
2. carrera: número entero (1, 2, 3...)
3. numero: número del caballo/mandil (entero)
4. caballo: nombre limpio SIN sufijos (Arg), (USA), etc.
5. jinete: nombre completo del jinete
6. peso: decimal con punto (ej: 56.5)
7. distancia: metros como entero (ej: 1000, 1200, 1400)
8. hora: formato HH:MM sin "APROX" (ej: 14:00, 15:30)
9. fecha: YYYY-MM-DD
10. condicion: tipo de carrera
11. stud: nombre del stud/haras

IMPORTANTE: Si el documento tiene "Cab. N°" usar ese valor para la columna numero.
```

---

## 🏇 PROMPT PARA PROGRAMAS - VALPARAÍSO SPORTING (VSC)

```
Actúa como Ingeniero de Datos experto. Extrae los datos del programa de carreras de Valparaíso Sporting y genera un CSV con estas columnas EXACTAS en este orden:

carrera,numero,caballo,jinete,peso,distancia,hora,fecha,condicion,stud

REGLAS:
1. Nombre archivo: PROGRAMA_VSC_[FECHA].csv (ej: PROGRAMA_VSC_2026-01-16.csv)
2. carrera: número entero
3. numero: número del caballo/mandil (entero)
4. caballo: nombre limpio SIN sufijos
5. jinete: nombre completo
6. peso: decimal con punto
7. distancia: metros como entero
8. hora: formato HH:MM (sin APROX, sin texto adicional)
9. fecha: YYYY-MM-DD
10. condicion: tipo de carrera
11. stud: nombre del stud

NOTA: El formato de Valparaíso suele usar "Hora" con texto como "14:00 APROX." - extraer solo "14:00".
```

---

## 🏆 PROMPT PARA RESULTADOS - HIPÓDROMO CHILE (HC)

```
Actúa como Ingeniero de Datos experto. Extrae los RESULTADOS de carreras del Hipódromo Chile y genera un CSV con estas columnas EXACTAS en este orden:

carrera,numero,caballo,jinete,posicion,dividendo,tiempo,peso,distancia,fecha

REGLAS:
1. Nombre archivo: RESULTADO_HC_[FECHA].csv
2. carrera: número de la carrera (entero)
3. numero: número del caballo participante (mandil)
4. caballo: nombre del ejemplar limpio
5. jinete: nombre del jinete
6. posicion: lugar de llegada (1, 2, 3... usar "RET" si retirado, "DESC" si descalificado)
7. dividendo: pago al ganador/placé como decimal (ej: 2.50, 15.30). Vacío si no pagó.
8. tiempo: tiempo de la carrera en formato M:SS.CC (ej: 1:12.45)
9. peso: peso del jinete (decimal)
10. distancia: metros de la carrera (entero)
11. fecha: YYYY-MM-DD

IMPORTANTE: Solo los caballos en posición 1-4 suelen tener dividendo.
```

---

## 🏆 PROMPT PARA RESULTADOS - CLUB HÍPICO (CHC)

```
Actúa como Ingeniero de Datos experto. Extrae los RESULTADOS de carreras del Club Hípico de Santiago y genera un CSV con estas columnas EXACTAS:

carrera,numero,caballo,jinete,posicion,dividendo,tiempo,peso,distancia,fecha

REGLAS:
1. Nombre archivo: RESULTADO_CHC_[FECHA].csv
2. posicion: puede venir como "Puesto" o "Lugar" en el documento - normalizar a entero
3. dividendo: usar punto decimal (2.50 no 2,50)
4. tiempo: formato M:SS.CC
5. Limpiar nombres de caballos de sufijos (Arg), (Chi), etc.
```

---

## 🏆 PROMPT PARA RESULTADOS - VALPARAÍSO (VSC)

```
Actúa como Ingeniero de Datos experto. Extrae los RESULTADOS de Valparaíso Sporting y genera un CSV:

carrera,numero,caballo,jinete,posicion,dividendo,tiempo,peso,distancia,fecha

REGLAS:
1. Nombre archivo: RESULTADO_VSC_[FECHA].csv
2. Todos los campos numéricos como números (sin texto adicional)
3. Posición como entero (1, 2, 3...)
4. Tiempo exacto en formato M:SS.CC
5. Fecha en formato YYYY-MM-DD
```

---

## ⚠️ CAMPOS CRÍTICOS (NUNCA OMITIR)

| Campo | Por qué es crítico |
|-------|-------------------|
| `numero` | Identifica al caballo en la carrera. Sin esto no se puede vincular predicción con resultado. |
| `hora` | Se muestra en el frontend. Si falta, aparece "00:00". |
| `distancia` | Se muestra en frontend como "XXXXm". Si falta, aparece 1000m por defecto. |
| `jinete` | Se muestra en predicciones. Si falta aparece "N/A". |

---

## ✅ VALIDACIÓN ANTES DE GUARDAR

Antes de guardar el CSV, verificar:
1. [ ] ¿Todas las carreras tienen número?
2. [ ] ¿Todos los caballos tienen número de mandil?
3. [ ] ¿La fecha está en formato YYYY-MM-DD?
4. [ ] ¿La hora está limpia (sin APROX)?
5. [ ] ¿La distancia es un número entero?
6. [ ] ¿El archivo se nombró correctamente?
