# Prompts para Generar CSVs Compatibles con Pista Inteligente

Este documento contiene los prompts exactos para pedirle a Gemini que genere los CSVs en el formato correcto para el sistema ETL.

---

## 📁 Convención de Nombres de Archivos

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| Programa | `PROGRAMA_[CODIGO]_[YYYY-MM-DD].csv` | `PROGRAMA_HC_2026-01-20.csv` |
| Resultados | `RESULTADOS_[CODIGO]_[YYYY-MM-DD].csv` | `RESULTADOS_CHC_2026-01-18.csv` |

### Códigos de Hipódromos:
- **HC** = Hipódromo Chile
- **CHC** = Club Hípico de Santiago (Chile)
- **VAL** = Valparaíso Sporting
- **CONCE** = Club Hípico de Concepción

---

## 🏇 PROMPT PARA PROGRAMAS (Carreras Futuras)

```
Genera un archivo CSV para el programa de carreras del [HIPÓDROMO] del día [FECHA] con el siguiente formato exacto:

FORMATO DEL ARCHIVO:
- Nombre: PROGRAMA_[CODIGO]_[FECHA].csv
- Separador: coma (,)
- Encoding: UTF-8

COLUMNAS REQUERIDAS (en este orden exacto):
Carrera,Hora,Premio,Distancia,Superficie,Numero,Caballo,Peso,Jinete,Preparador

DESCRIPCIÓN DE COLUMNAS:
- Carrera: Número de carrera (1, 2, 3, etc.)
- Hora: Hora de la carrera en formato HH:MM (ej: 12:30)
- Premio: Nombre o condición del premio
- Distancia: En metros con punto como separador de miles (ej: 1.000, 1.200, 1.400)
- Superficie: "Arena" o "Pasto"
- Numero: Número de partida/mandil del caballo (1, 2, 3, etc.)
- Caballo: Nombre en MAYÚSCULAS (ej: TATA MONCHO)
- Peso: Peso en kg (ej: 56, 58)
- Jinete: Nombre abreviado (ej: P.Zuniga, N.Venegas)
- Preparador: Nombre abreviado del preparador/entrenador

EJEMPLO DE PRIMERAS LÍNEAS:
Carrera,Hora,Premio,Distancia,Superficie,Numero,Caballo,Peso,Jinete,Preparador
1,12:30,Compicado,1.000,Arena,1,TATA MONCHO,58,P.Zuniga,R.QuirozS.
1,12:30,Compicado,1.000,Arena,2,DON'T STOP ME NOW,56,N.Venegas,E.SwittV.
1,12:30,Compicado,1.000,Arena,3,INDIA TERCA,55,L.Valdivia,E.SwittV.
2,13:00,Especial,1.200,Arena,1,OTRO CABALLO,54,J.Eyzaguirre,P.ValderramaC.

NOTAS IMPORTANTES:
- Cada fila representa UN caballo en UNA carrera
- Para una carrera con 12 caballos, habrá 12 filas con el mismo número de Carrera
- Los nombres de caballos van en MAYÚSCULAS
- No usar comillas a menos que el texto contenga comas
```

---

## 🏆 PROMPT PARA RESULTADOS (Carreras Ya Corridas)

```
Genera un archivo CSV con los resultados de las carreras del [HIPÓDROMO] del día [FECHA] con el siguiente formato exacto:

FORMATO DEL ARCHIVO:
- Nombre: RESULTADOS_[CODIGO]_[FECHA].csv
- Separador: coma (,)
- Encoding: UTF-8

COLUMNAS REQUERIDAS (en este orden exacto):
Reunion,Carrera,Hora,Distancia,Lugar,Numero,Ejemplar,Padrillo,Peso_Fisico,Peso_Jinete,Jinete,Preparador,Stud,Dividendo

DESCRIPCIÓN DE COLUMNAS:
- Reunion: Nombre completo del hipódromo y fecha (ej: "Hipódromo Chile 03-01-2026")
- Carrera: Número de carrera (1, 2, 3, etc.)
- Hora: Hora de la carrera en formato HH:MM (ej: 11:45)
- Distancia: Con unidad (ej: 1200m, 1400m)
- Lugar: Posición de llegada (1, 2, 3, etc.)
- Numero: Número de partida/mandil del caballo
- Ejemplar: Nombre del caballo (ej: "Indy Jets")
- Padrillo: Nombre del padre del caballo (ej: "Get Jets")
- Peso_Fisico: Peso físico del caballo en kg (ej: 442)
- Peso_Jinete: Peso del jinete en kg (ej: 55)
- Jinete: Nombre abreviado (ej: "L. González")
- Preparador: Nombre completo del preparador (ej: "Rodrigo Muñoz M.")
- Stud: Nombre del stud/haras (ej: "Savka Hermanos")
- Dividendo: Pago del caballo si ganó/colocó (ej: 5.50). Usar punto decimal.

EJEMPLO DE PRIMERAS LÍNEAS:
Reunion,Carrera,Hora,Distancia,Lugar,Numero,Ejemplar,Padrillo,Peso_Fisico,Peso_Jinete,Jinete,Preparador,Stud,Dividendo
"Hipódromo Chile 03-01-2026",1,"11:45",1200m,1,12,"Indy Jets","Get Jets",442,55,"L. González","Rodrigo Muñoz M.","Savka Hermanos",5.50
"Hipódromo Chile 03-01-2026",1,"11:45",1200m,2,6,"Marrakech","El Milagrito",454,54,"B. González","Genaro J. Covarrubias E.","La Corina",2.60
"Hipódromo Chile 03-01-2026",1,"11:45",1200m,3,10,"Me Veras Caer","Iron Clad",418,55,"F. Henríquez","Julio Castillo D.","Carlos Cavieres",15.40

NOTAS IMPORTANTES:
- El campo Reunion debe ir entre comillas porque contiene espacios
- Lugar = 1 es el ganador, 2 es el segundo, etc.
- Dividendo: Solo los primeros puestos tienen dividendo significativo
- Ordenar por Carrera ASC, luego por Lugar ASC
- Para una carrera con 12 caballos, habrá 12 filas ordenadas por posición de llegada
```

---

## 📋 RESUMEN RÁPIDO

### Para PROGRAMAS:
```
Columnas: Carrera,Hora,Premio,Distancia,Superficie,Numero,Caballo,Peso,Jinete,Preparador
Archivo: PROGRAMA_[CODIGO]_YYYY-MM-DD.csv
```

### Para RESULTADOS:
```
Columnas: Reunion,Carrera,Hora,Distancia,Lugar,Numero,Ejemplar,Padrillo,Peso_Fisico,Peso_Jinete,Jinete,Preparador,Stud,Dividendo
Archivo: RESULTADOS_[CODIGO]_YYYY-MM-DD.csv
```

---

## 🔄 Después de Generar el CSV

1. Guardar el archivo en: `exports/`
2. Ejecutar: `python sync_system.py`
3. El sistema procesará automáticamente los nuevos archivos
