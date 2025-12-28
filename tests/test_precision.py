"""
Script para probar el cálculo de precisión del modelo
"""
import sys
sys.path.append('.')

from src.models.data_manager import calcular_precision_modelo, obtener_predicciones_historicas

print("=" * 70)
print("PRUEBA DE PRECISIÓN DEL MODELO")
print("=" * 70)

# Calcular precisión global
print("\n📊 Calculando precisión global...")
precision = calcular_precision_modelo()

print("\n✅ RESULTADOS:")
print(f"  • Total de predicciones analizadas: {precision.get('total_predicciones', 0)}")
print(f"  • Total de carreras analizadas: {precision.get('total_carreras', 0)}")
print(f"  • Rango de fechas: {precision.get('rango_fechas', 'N/A')}")
print(f"\n🎯 PRECISIÓN:")
print(f"  • Top 1 Accuracy: {precision.get('top1_accuracy', 0)}% ({precision.get('top1_correct', 0)}/{precision.get('top1_total', 0)})")
print(f"  • Top 3 Accuracy: {precision.get('top3_accuracy', 0)}% ({precision.get('top3_correct', 0)}/{precision.get('top3_total', 0)})")
print(f"  • Top 4 Accuracy: {precision.get('top4_accuracy', 0)}% ({precision.get('top4_correct', 0)}/{precision.get('top4_total', 0)})")

if 'mensaje' in precision:
    print(f"\n⚠️ {precision['mensaje']}")

# Obtener predicciones históricas
print("\n" + "=" * 70)
print("PREDICCIONES HISTÓRICAS")
print("=" * 70)

predicciones_df = obtener_predicciones_historicas(limite=20)
if not predicciones_df.empty:
    print(f"\n📋 Últimas {len(predicciones_df)} predicciones:")
    print(predicciones_df.to_string(index=False))
else:
    print("\n⚠️ No hay predicciones históricas disponibles")

print("\n" + "=" * 70)
