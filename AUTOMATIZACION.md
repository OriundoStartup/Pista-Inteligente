# 🤖 Automatización y Optimización del Sistema

## 1. Tarea Programada (Windows)

Para configurar la recolección automática de datos todos los días a las 05:00 AM, ejecuta el siguiente bloque de código en una terminal de **PowerShell** (ejecutar como Administrador es recomendado pero no siempre estrictamente necesario si es para tu propio usuario):

```powershell
$taskName = "HipicaScraperDiario"
$pythonPath = "c:\espacioDeTrabajo\HipicaAntigracity\venv\Scripts\python.exe"
$scriptPath = "scraper.py"
$workDir = "c:\espacioDeTrabajo\HipicaAntigracity"

# Crear la acción (ejecutar python con el script)
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory $workDir

# Crear el disparador (diariamente a las 05:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At "05:00"

# Registrar la tarea
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $taskName -Description "Ejecuta el scraper de hípica diariamente a las 5 AM para actualizar resultados y programas."

Write-Host "✅ Tarea programada '$taskName' creada exitosamente."
```

### Verificación
Para verificar que la tarea se creó correctamente, puedes abrir el "Programador de tareas" de Windows y buscar "HipicaScraperDiario" en la biblioteca, o ejecutar:
```powershell
Get-ScheduledTask -TaskName "HipicaScraperDiario"
```

## 2. Optimización del Frontend (Caché)

Se ha modificado el archivo `app_frontend.py` para incluir el sistema de caché inteligente de Streamlit.

### Cambios realizados:
- Se aplicó el decorador `@st.cache_data(ttl=86400)` a la función `cargar_datos`.
- **TTL (Time To Live)**: 86400 segundos (24 horas).

### Comportamiento esperado:
1. La primera vez que un usuario entre en el día, la app cargará los datos desde la base de datos (tardará unos segundos).
2. Para cualquier acceso posterior (del mismo u otros usuarios) durante las próximas 24 horas, la app usará los datos en memoria (carga instantánea).
3. La caché se invalidará automáticamente después de 24 horas, forzando una recarga fresca justo después de que tu scraper matutino haya actualizado la base de datos.
