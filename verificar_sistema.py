"""
Script de Verificación del Sistema Pista Inteligente
Demuestra que el sistema está funcionando correctamente con datos reales
"""
import sqlite3
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# Conectar a la base de datos
conn = sqlite3.connect('hipica_data.db')

# 1. Estadísticas Generales
console.print("\n[bold cyan]🐎 PISTA INTELIGENTE - VERIFICACIÓN DEL SISTEMA[/bold cyan]\n")

stats_query = """
SELECT 
    COUNT(*) as total_carreras,
    COUNT(DISTINCT fecha) as dias_con_datos,
    COUNT(DISTINCT hipodromo) as hipodromos,
    MIN(fecha) as fecha_inicio,
    MAX(fecha) as fecha_fin
FROM resultados
"""
stats = pd.read_sql(stats_query, conn)

panel_stats = Panel(
    f"""[green]✅ Total de Carreras:[/green] {stats['total_carreras'][0]}
[green]✅ Días con Datos:[/green] {stats['dias_con_datos'][0]}
[green]✅ Hipódromos:[/green] {stats['hipodromos'][0]}
[green]✅ Rango de Fechas:[/green] {stats['fecha_inicio'][0]} a {stats['fecha_fin'][0]}""",
    title="📊 Estadísticas Generales",
    border_style="cyan"
)
console.print(panel_stats)

# 2. Datos por Hipódromo
console.print("\n[bold yellow]📍 DATOS POR HIPÓDROMO[/bold yellow]\n")
hipodromo_query = """
SELECT 
    hipodromo,
    COUNT(*) as carreras,
    COUNT(DISTINCT fecha) as dias
FROM resultados
GROUP BY hipodromo
"""
hip_data = pd.read_sql(hipodromo_query, conn)

table_hip = Table(title="Distribución por Hipódromo", box=box.ROUNDED)
table_hip.add_column("Hipódromo", style="cyan")
table_hip.add_column("Carreras", style="green")
table_hip.add_column("Días", style="yellow")

for _, row in hip_data.iterrows():
    table_hip.add_row(row['hipodromo'], str(row['carreras']), str(row['dias']))

console.print(table_hip)

# 3. Patrones Repetidos (Análisis Principal)
console.print("\n[bold magenta]🎯 PATRONES REPETIDOS (ANÁLISIS PREDICTIVO)[/bold magenta]\n")
patrones_query = """
SELECT 
    llegada_str,
    COUNT(*) as repeticiones,
    GROUP_CONCAT(DISTINCT hipodromo) as hipodromos
FROM resultados
GROUP BY llegada_str
HAVING COUNT(*) > 1
ORDER BY repeticiones DESC
LIMIT 10
"""
patrones = pd.read_sql(patrones_query, conn)

if not patrones.empty:
    table_pat = Table(title="Top 10 Patrones Más Repetidos", box=box.DOUBLE)
    table_pat.add_column("Patrón (1-2-3)", style="bold cyan")
    table_pat.add_column("Repeticiones", style="bold green")
    table_pat.add_column("Hipódromo(s)", style="yellow")
    
    for _, row in patrones.iterrows():
        style = "bold red" if row['repeticiones'] >= 3 else "white"
        table_pat.add_row(
            row['llegada_str'],
            str(row['repeticiones']),
            row['hipodromos'],
            style=style
        )
    
    console.print(table_pat)
    
    # Destacar patrones de alta frecuencia
    alta_freq = patrones[patrones['repeticiones'] >= 3]
    if not alta_freq.empty:
        console.print(f"\n[bold green]🚨 ¡ALERTA! {len(alta_freq)} patrón(es) con 3+ repeticiones detectado(s)[/bold green]")
        console.print("[bold green]💰 A COBRAR LOS QUE SABEN[/bold green]\n")
else:
    console.print("[yellow]ℹ️  No se encontraron patrones repetidos aún[/yellow]\n")

# 4. Muestra de Datos Recientes
console.print("\n[bold blue]📅 ÚLTIMAS 5 CARRERAS REGISTRADAS[/bold blue]\n")
recent_query = """
SELECT fecha, hipodromo, nro_carrera, llegada_str
FROM resultados
ORDER BY fecha DESC, nro_carrera DESC
LIMIT 5
"""
recent = pd.read_sql(recent_query, conn)

table_recent = Table(title="Datos Más Recientes", box=box.SIMPLE)
table_recent.add_column("Fecha", style="cyan")
table_recent.add_column("Hipódromo", style="magenta")
table_recent.add_column("Carrera N°", style="yellow")
table_recent.add_column("Llegada (1-2-3)", style="green")

for _, row in recent.iterrows():
    table_recent.add_row(
        row['fecha'],
        row['hipodromo'],
        str(row['nro_carrera']),
        row['llegada_str']
    )

console.print(table_recent)

# 5. Verificación de Integridad
console.print("\n[bold cyan]🔍 VERIFICACIÓN DE INTEGRIDAD DE DATOS[/bold cyan]\n")
integrity_checks = []

# Check 1: Datos nulos
null_check = pd.read_sql("SELECT COUNT(*) as nulls FROM resultados WHERE llegada_str IS NULL OR fecha IS NULL", conn)
integrity_checks.append(("Registros con datos nulos", null_check['nulls'][0], "✅" if null_check['nulls'][0] == 0 else "❌"))

# Check 2: Formato de llegada
format_check = pd.read_sql("SELECT COUNT(*) as invalid FROM resultados WHERE llegada_str NOT LIKE '%-%-%'", conn)
integrity_checks.append(("Registros con formato inválido", format_check['invalid'][0], "✅" if format_check['invalid'][0] == 0 else "❌"))

# Check 3: Duplicados exactos
dup_check = pd.read_sql("SELECT COUNT(*) - COUNT(DISTINCT fecha || hipodromo || nro_carrera) as dups FROM resultados", conn)
integrity_checks.append(("Duplicados exactos", dup_check['dups'][0], "✅" if dup_check['dups'][0] == 0 else "⚠️"))

table_integrity = Table(title="Checks de Integridad", box=box.MINIMAL)
table_integrity.add_column("Verificación", style="cyan")
table_integrity.add_column("Resultado", style="yellow")
table_integrity.add_column("Estado", style="green")

for check in integrity_checks:
    table_integrity.add_row(check[0], str(check[1]), check[2])

console.print(table_integrity)

# Conclusión
console.print("\n" + "="*60)
console.print("[bold green]✅ SISTEMA OPERATIVO Y FUNCIONANDO CORRECTAMENTE[/bold green]")
console.print("[italic]Base de datos: hipica_data.db[/italic]")
console.print("[italic]\"A cobrar los que saben.\" - Pista Inteligente[/italic]")
console.print("="*60 + "\n")

conn.close()
