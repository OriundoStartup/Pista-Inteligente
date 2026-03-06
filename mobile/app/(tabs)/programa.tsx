import React, { useCallback, useState, useMemo } from 'react';
import {
    View,
    FlatList,
    RefreshControl,
    StyleSheet,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '../../components/ThemedText';
import { GradientText } from '../../components/GradientText';
import { HipodromoAccordion } from '../../components/HipodromoAccordion';
import { Colors } from '../../constants/Colors';
import { Spacing, BorderRadius, Typography } from '../../constants/Theme';
import { useSupabaseQuery } from '../../hooks/useSupabase';
import { supabase } from '../../lib/supabase';

interface Prediccion {
    numero: number;
    caballo: string;
    jinete: string;
    puntaje_ia: number;
}

interface Carrera {
    id: string;
    hipodromo: string;
    carrera: number;
    fecha: string;
    hora: string;
    distancia: number;
    predicciones: Prediccion[];
}

/**
 * Fetches predictions using Promise.allSettled for independent queries.
 *
 * Query dependency graph:
 *   1. jornadas (independent)
 *   2. hipodromos + carreras (depend on jornadas, parallel to each other)
 *   3. participaciones + predicciones (depend on carreras, parallel to each other)
 */
async function getPredicciones(): Promise<{
    carreras: Carrera[];
    stats: { total_carreras: number; total_caballos: number; fecha_principal: string };
    partialError: string | null;
}> {
    const today = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Santiago' });
    const warnings: string[] = [];

    try {
        // ─── Step 1: Get upcoming jornadas (independent) ───
        const { data: jornadas } = await supabase
            .from('jornadas')
            .select('id, fecha, hipodromo_id')
            .gte('fecha', today)
            .order('fecha', { ascending: true })
            .order('hipodromo_id', { ascending: true })
            .limit(10);

        if (!jornadas || jornadas.length === 0) {
            return {
                carreras: [],
                stats: { total_carreras: 0, total_caballos: 0, fecha_principal: today },
                partialError: null,
            };
        }

        // ─── Step 2: hipodromos + carreras in parallel (both depend only on jornadas) ───
        const hipodromoIds = [...new Set(jornadas.map((j: any) => j.hipodromo_id))];
        const jornadaIds = jornadas.map((j: any) => j.id);

        const [hipodromosResult, carrerasResult] = await Promise.allSettled([
            supabase.from('hipodromos').select('id, nombre').in('id', hipodromoIds),
            supabase.from('carreras')
                .select('id, numero, hora, distancia, jornada_id')
                .in('jornada_id', jornadaIds)
                .order('numero', { ascending: true }),
        ]);

        // Extract hipódromo map (tolerate failure)
        const hipodromoMap = new Map<string | number, string>();
        if (hipodromosResult.status === 'fulfilled') {
            for (const h of hipodromosResult.value.data || []) {
                hipodromoMap.set(h.id, h.nombre);
                hipodromoMap.set(String(h.id), h.nombre);
                hipodromoMap.set(Number(h.id), h.nombre);
            }
        } else {
            warnings.push('No se pudieron cargar los nombres de hipódromos');
        }

        // Extract carreras (critical — if this fails, we can't continue)
        if (carrerasResult.status === 'rejected') {
            throw new Error('Error al cargar las carreras');
        }
        const carreras = carrerasResult.value.data || [];

        // ─── Step 3: participaciones + predicciones in parallel ───
        const allCarreraIds = carreras.map((c: any) => c.id);

        const [resultsResult, prediccionesResult] = await Promise.allSettled([
            supabase.from('participaciones').select('carrera_id').in('carrera_id', allCarreraIds),
            // We'll filter active carreras inline — fetch predictions for all
            supabase.from('predicciones')
                .select('*')
                .in('carrera_id', allCarreraIds)
                .order('rank_predicho', { ascending: true }),
        ]);

        // Completed races set (tolerate failure — just show all races)
        const completedRaceSet = new Set<any>();
        if (resultsResult.status === 'fulfilled') {
            for (const r of resultsResult.value.data || []) {
                completedRaceSet.add(r.carrera_id);
            }
        } else {
            warnings.push('No se pudo verificar carreras completadas');
        }

        // Predicciones (tolerate failure — show placeholder)
        let predicciones: any[] = [];
        if (prediccionesResult.status === 'fulfilled') {
            predicciones = prediccionesResult.value.data || [];
        } else {
            warnings.push('No se pudieron cargar las predicciones');
        }

        // ─── Step 4: Build response ───
        const activeCarreras = carreras.filter((c: any) => {
            if (completedRaceSet.has(c.id)) return false;
            const jornada = jornadas.find((j: any) => j.id === c.jornada_id);
            if (jornada && (jornada as any).fecha < today) return false;
            return true;
        });

        const carrerasConPredicciones: Carrera[] = activeCarreras
            .map((carrera: any) => {
                const jornada = jornadas.find((j: any) => j.id === carrera.jornada_id);
                const hipodromoNombre = jornada
                    ? hipodromoMap.get((jornada as any).hipodromo_id) ||
                    hipodromoMap.get(String((jornada as any).hipodromo_id))
                    : undefined;

                const preds = predicciones
                    .filter((p: any) => p.carrera_id === carrera.id)
                    .slice(0, 4)
                    .map((p: any) => ({
                        numero: p.numero_caballo || 0,
                        caballo: p.caballo || 'N/A',
                        jinete: p.jinete || 'N/A',
                        puntaje_ia: p.probabilidad ? p.probabilidad * 100 : 50,
                    }));

                return {
                    id: carrera.id,
                    hipodromo: hipodromoNombre || 'Hipódromo Chile',
                    carrera: carrera.numero,
                    fecha: (jornada as any)?.fecha || today,
                    hora: carrera.hora || '00:00',
                    distancia: carrera.distancia || 1000,
                    predicciones:
                        preds.length > 0
                            ? preds
                            : [{ numero: 1, caballo: 'Datos pendientes', jinete: '-', puntaje_ia: 0 }],
                };
            })
            .filter((c: Carrera) => {
                if (!c.carrera || c.carrera <= 0) return false;
                if (!c.predicciones || c.predicciones.length === 0) return false;
                if (c.predicciones[0]?.caballo === 'Datos pendientes') return false;
                if (c.predicciones[0]?.caballo === 'N/A') return false;
                return true;
            });

        return {
            carreras: carrerasConPredicciones,
            stats: {
                total_carreras: carrerasConPredicciones.length,
                total_caballos: carrerasConPredicciones.reduce((sum, c) => sum + c.predicciones.length, 0),
                fecha_principal: jornadas[0]?.fecha || today,
            },
            partialError: warnings.length > 0 ? warnings.join('. ') : null,
        };
    } catch (error) {
        console.error('Error fetching predictions:', error);
        return {
            carreras: [],
            stats: { total_carreras: 0, total_caballos: 0, fecha_principal: today },
            partialError: 'Error al cargar datos',
        };
    }
}

export default function ProgramaScreen() {
    const today = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Santiago' });

    const { data, loading, error, refresh } = useSupabaseQuery(
        getPredicciones,
        'predicciones_data'
    );

    const [refreshing, setRefreshing] = useState(false);
    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await refresh();
        setRefreshing(false);
    }, [refresh]);

    // Group carreras by hipódromo + fecha
    const hipodromoGroups = useMemo(() => {
        if (!data?.carreras) return [];
        const groups: Record<string, Carrera[]> = {};
        data.carreras.forEach((carrera) => {
            const key = `${carrera.hipodromo}|${carrera.fecha}`;
            if (!groups[key]) groups[key] = [];
            groups[key].push(carrera);
        });
        return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
    }, [data?.carreras]);

    const renderHeader = useCallback(() => (
        <View>
            {/* Header */}
            <View style={styles.header}>
                <ThemedText variant="h2" weight="extrabold" align="center">
                    🔮 Predicciones IA
                </ThemedText>
                <ThemedText variant="muted" align="center">
                    {new Date().toLocaleDateString('es-CL', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                        timeZone: 'America/Santiago',
                    })}
                </ThemedText>
            </View>

            {/* Partial error banner */}
            {data?.partialError && (
                <View style={styles.warningBanner}>
                    <ThemedText variant="caption" weight="semibold" color="#92400e">
                        ⚠️ {data.partialError}
                    </ThemedText>
                </View>
            )}

            {/* Stats Row */}
            {data && (
                <View style={styles.statsRow}>
                    <View style={styles.statItem}>
                        <ThemedText variant="h2" weight="extrabold" color={Colors.secondary}>
                            {data.stats.total_carreras}
                        </ThemedText>
                        <ThemedText variant="caption">Carreras</ThemedText>
                    </View>
                    <View style={styles.statDivider} />
                    <View style={styles.statItem}>
                        <ThemedText variant="h2" weight="extrabold" color={Colors.primary}>
                            {data.stats.total_caballos}
                        </ThemedText>
                        <ThemedText variant="caption">Caballos</ThemedText>
                    </View>
                    <View style={styles.statDivider} />
                    <View style={styles.statItem}>
                        <ThemedText variant="h2" weight="extrabold" color={Colors.accent}>
                            📅
                        </ThemedText>
                        <ThemedText variant="caption">{data.stats.fecha_principal}</ThemedText>
                    </View>
                </View>
            )}

            {/* Loading or Empty State */}
            {loading && !data && (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator color={Colors.primary} size="large" />
                    <ThemedText variant="muted" align="center" style={{ marginTop: Spacing.md }}>
                        Cargando predicciones...
                    </ThemedText>
                </View>
            )}

            {!loading && hipodromoGroups.length === 0 && (
                <View style={styles.emptyState}>
                    <ThemedText style={{ fontSize: 64 }} align="center">🏇</ThemedText>
                    <ThemedText variant="h2" align="center" style={{ marginVertical: Spacing.md }}>
                        No hay carreras programadas
                    </ThemedText>
                    <ThemedText variant="muted" align="center" style={{ maxWidth: 300 }}>
                        Las predicciones se actualizan diariamente cuando hay jornadas programadas.
                    </ThemedText>
                </View>
            )}
        </View>
    ), [data, loading, hipodromoGroups.length]);

    const renderItem = useCallback(({ item: [key, carreras] }: { item: [string, Carrera[]] }) => (
        <HipodromoAccordion
            hipodromoKey={key}
            carreras={carreras}
            today={today}
            defaultOpen={true}
        />
    ), [today]);

    const keyExtractor = useCallback(([key]: [string, Carrera[]]) => key, []);

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <FlatList
                data={hipodromoGroups}
                keyExtractor={keyExtractor}
                ListHeaderComponent={renderHeader}
                contentContainerStyle={styles.content}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={onRefresh}
                        tintColor={Colors.primary}
                        colors={[Colors.primary]}
                    />
                }
                renderItem={renderItem}
            />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
    },
    content: {
        padding: Spacing.lg,
        paddingBottom: Spacing.xxxl,
    },
    header: {
        paddingVertical: Spacing.xl,
        gap: Spacing.xs,
        marginBottom: Spacing.lg,
    },
    warningBanner: {
        backgroundColor: '#fef3c7',
        borderRadius: BorderRadius.md,
        paddingVertical: Spacing.sm,
        paddingHorizontal: Spacing.lg,
        marginBottom: Spacing.lg,
        borderWidth: 1,
        borderColor: '#f59e0b',
    },
    statsRow: {
        flexDirection: 'row',
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        padding: Spacing.lg,
        marginBottom: Spacing.xl,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        alignItems: 'center',
        justifyContent: 'space-around',
    },
    statItem: {
        alignItems: 'center',
        gap: 2,
    },
    statDivider: {
        width: 1,
        height: 40,
        backgroundColor: Colors.borderGlass,
    },
    loadingContainer: {
        paddingVertical: Spacing.xxxl * 2,
        alignItems: 'center',
    },
    emptyState: {
        paddingVertical: Spacing.xxxl * 2,
        alignItems: 'center',
    },
});
