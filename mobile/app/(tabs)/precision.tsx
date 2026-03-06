import React, { useCallback, useState, useMemo } from 'react';
import {
    View,
    FlatList,
    RefreshControl,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
    LayoutAnimation,
    Platform,
    UIManager,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '../../components/ThemedText';
import { GradientText } from '../../components/GradientText';
import { SectionTitle } from '../../components/SectionTitle';
import { StatCard } from '../../components/StatCard';
import { RaceResultCard } from '../../components/RaceResultCard';
import { Colors } from '../../constants/Colors';
import { Spacing, BorderRadius, Typography } from '../../constants/Theme';
import { useSupabaseQuery } from '../../hooks/useSupabase';
import { supabase } from '../../lib/supabase';
import { MaterialCommunityIcons } from '@expo/vector-icons';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
    UIManager.setLayoutAnimationEnabledExperimental(true);
}

const PAGE_SIZE = 30;

interface StatsData {
    total_carreras: number;
    ganador_pct: number;
    quiniela_pct: number;
    trifecta_pct: number;
    superfecta_pct: number;
    ganador_count: number;
    quiniela_count: number;
    trifecta_count: number;
    superfecta_count: number;
}

interface RaceResult {
    fecha: string;
    hipodromo: string;
    nro_carrera: number;
    acierto_ganador: boolean;
    acierto_quiniela: boolean;
    acierto_trifecta: boolean;
    acierto_superfecta: boolean;
    prediccion_top4: string[];
    resultado_top4: string[];
}

const getHipodromoIcon = (hip: string) => {
    if (hip.includes('Chile')) return '🏇';
    if (hip.includes('Club')) return '🏛️';
    if (hip.includes('Valparaíso')) return '🌊';
    if (hip.includes('Concepción')) return '🌲';
    return '🏇';
};

function HipodromoStatsCard({ name, stats }: { name: string; stats: StatsData }) {
    const [open, setOpen] = useState(false);

    const toggleOpen = useCallback(() => {
        LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
        setOpen((prev) => !prev);
    }, []);

    return (
        <View style={styles.hipCard}>
            <TouchableOpacity
                style={styles.hipHeader}
                onPress={toggleOpen}
                activeOpacity={0.7}
            >
                <ThemedText style={{ fontSize: 22 }}>{getHipodromoIcon(name)}</ThemedText>
                <View style={{ flex: 1 }}>
                    <ThemedText variant="body" weight="semibold" numberOfLines={1}>{name}</ThemedText>
                    <ThemedText variant="caption">{stats.total_carreras} carreras</ThemedText>
                </View>
                <MaterialCommunityIcons name={open ? 'chevron-up' : 'chevron-down'} size={20} color={Colors.textMuted} />
            </TouchableOpacity>
            {open && (
                <View style={styles.hipStats}>
                    {[
                        { label: '🥇 Ganador', value: stats.ganador_pct, color: Colors.gold },
                        { label: '🎯 Quiniela', value: stats.quiniela_pct, color: Colors.silver },
                        { label: '🏆 Trifecta', value: stats.trifecta_pct, color: Colors.bronze },
                        { label: '⭐ Super', value: stats.superfecta_pct, color: Colors.primary },
                    ].map((s) => (
                        <View key={s.label} style={styles.hipStatItem}>
                            <ThemedText variant="caption" style={{ fontSize: 10 }}>{s.label}</ThemedText>
                            <ThemedText variant="h3" weight="extrabold" color={s.color}>{s.value}%</ThemedText>
                        </View>
                    ))}
                </View>
            )}
        </View>
    );
}

export default function PrecisionScreen() {
    const { data, loading, refresh } = useSupabaseQuery(async () => {
        // 1. Fetch global stats
        const { data: statsRow, error } = await supabase
            .from('rendimiento_stats')
            .select('data')
            .eq('id', 'global_stats')
            .single();

        if (error || !statsRow) return null;

        const statsData = typeof statsRow.data === 'string'
            ? JSON.parse(statsRow.data)
            : statsRow.data;

        // 2. Fetch ALL recent race results (we paginate client-side)
        const { data: recentRaces } = await supabase
            .from('rendimiento_historico')
            .select('*')
            .gte('fecha', '2025-11-01')
            .or('acierto_ganador.eq.true,acierto_quiniela.eq.true,acierto_trifecta.eq.true,acierto_superfecta.eq.true')
            .order('fecha', { ascending: false })
            .limit(300);

        // Deduplicate
        const seenKeys = new Set<string>();
        const races: RaceResult[] = (recentRaces || [])
            .filter((r: any) => r.fecha && r.hipodromo && r.nro_carrera > 0)
            .filter((r: any) => {
                const key = `${r.fecha}-${r.hipodromo}-${r.nro_carrera}`;
                if (seenKeys.has(key)) return false;
                seenKeys.add(key);
                return true;
            })
            .map((r: any) => ({
                fecha: r.fecha,
                hipodromo: r.hipodromo,
                nro_carrera: r.nro_carrera,
                acierto_ganador: r.acierto_ganador,
                acierto_quiniela: r.acierto_quiniela,
                acierto_trifecta: r.acierto_trifecta,
                acierto_superfecta: r.acierto_superfecta,
                prediccion_top4: typeof r.prediccion_top4 === 'string' ? JSON.parse(r.prediccion_top4) : r.prediccion_top4 || [],
                resultado_top4: typeof r.resultado_top4 === 'string' ? JSON.parse(r.resultado_top4) : r.resultado_top4 || [],
            }));

        const emptyStats: StatsData = { total_carreras: 0, ganador_pct: 0, quiniela_pct: 0, trifecta_pct: 0, superfecta_pct: 0, ganador_count: 0, quiniela_count: 0, trifecta_count: 0, superfecta_count: 0 };

        return {
            all_time: statsData.all_time || emptyStats,
            by_hipodromo: statsData.by_hipodromo || {},
            recent_races: races,
        };
    }, 'precision_data');

    // ─── Pagination state ───
    const [page, setPage] = useState(1);
    const allRaces = data?.recent_races || [];
    const totalItems = allRaces.length;

    const items = useMemo(
        () => allRaces.slice(0, page * PAGE_SIZE),
        [allRaces, page]
    );
    const hasMore = items.length < totalItems;
    const [loadingMore, setLoadingMore] = useState(false);

    const onEndReached = useCallback(() => {
        if (loadingMore || !hasMore) return;
        setLoadingMore(true);
        // Small delay to show the spinner for UX feedback
        setTimeout(() => {
            setPage((prev) => prev + 1);
            setLoadingMore(false);
        }, 200);
    }, [loadingMore, hasMore]);

    const [refreshing, setRefreshing] = useState(false);
    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        setPage(1); // Reset pagination on refresh
        await refresh();
        setRefreshing(false);
    }, [refresh]);

    const allTime = data?.all_time;
    const hipodromos = useMemo(
        () => data ? Object.entries(data.by_hipodromo).sort((a, b) => (b[1] as StatsData).total_carreras - (a[1] as StatsData).total_carreras) : [],
        [data]
    );

    const renderHeader = useCallback(() => (
        <View>
            <View style={styles.header}>
                <ThemedText variant="h2" weight="extrabold" align="center">
                    📊 Rendimiento
                </ThemedText>
                <ThemedText variant="muted" align="center">
                    Transparencia total: datos verificables
                </ThemedText>
            </View>

            {loading && !data && (
                <ActivityIndicator color={Colors.primary} size="large" style={{ marginVertical: Spacing.xxxl }} />
            )}

            {/* Global Stats */}
            {allTime && (
                <View style={styles.section}>
                    <SectionTitle emoji="🎯" borderColor={Colors.gold}>Precisión Global ({allTime.total_carreras} carreras)</SectionTitle>
                    <View style={styles.statsGrid}>
                        <StatCard label="🥇 GANADOR" value={`${allTime.ganador_pct}%`} color={Colors.gold} count={allTime.ganador_count} total={allTime.total_carreras} />
                        <StatCard label="🎯 QUINIELA" value={`${allTime.quiniela_pct}%`} color={Colors.silver} count={allTime.quiniela_count} total={allTime.total_carreras} />
                        <StatCard label="🏆 TRIFECTA" value={`${allTime.trifecta_pct}%`} color={Colors.bronze} count={allTime.trifecta_count} total={allTime.total_carreras} />
                        <StatCard label="⭐ SUPERFECTA" value={`${allTime.superfecta_pct}%`} color={Colors.primary} count={allTime.superfecta_count} total={allTime.total_carreras} />
                    </View>
                </View>
            )}

            {/* By Hipódromo */}
            {hipodromos.length > 0 && (
                <View style={styles.section}>
                    <SectionTitle emoji="🏇">Por Hipódromo</SectionTitle>
                    {hipodromos.map(([name, stats]) => (
                        <HipodromoStatsCard key={name} name={name} stats={stats as StatsData} />
                    ))}
                </View>
            )}

            {/* Section title for race results */}
            {items.length > 0 && (
                <SectionTitle emoji="📋">Últimas Carreras Verificadas ({totalItems})</SectionTitle>
            )}
        </View>
    ), [data, loading, allTime, hipodromos, items.length, totalItems]);

    // ─── Footer: loading spinner or "no more" text ───
    const renderFooter = useCallback(() => {
        if (loadingMore) {
            return (
                <ActivityIndicator
                    color={Colors.primary}
                    size="small"
                    style={{ paddingVertical: Spacing.lg }}
                />
            );
        }
        if (!hasMore && items.length > 0) {
            return (
                <ThemedText
                    variant="muted"
                    align="center"
                    style={{ paddingVertical: Spacing.xl }}
                >
                    No hay más resultados
                </ThemedText>
            );
        }
        return null;
    }, [loadingMore, hasMore, items.length]);

    const renderItem = useCallback(
        ({ item }: { item: RaceResult }) => <RaceResultCard race={item} />,
        []
    );

    const keyExtractor = useCallback(
        (item: RaceResult) => `${item.fecha}-${item.hipodromo}-${item.nro_carrera}`,
        []
    );

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <FlatList
                data={items}
                keyExtractor={keyExtractor}
                ListHeaderComponent={renderHeader}
                ListFooterComponent={renderFooter}
                contentContainerStyle={styles.content}
                onEndReached={onEndReached}
                onEndReachedThreshold={0.3}
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
    section: {
        marginBottom: Spacing.xl,
    },
    sectionTitle: {
        marginBottom: Spacing.lg,
    },
    statsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: Spacing.md,
    },
    hipCard: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        overflow: 'hidden',
        marginBottom: Spacing.md,
    },
    hipHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: Spacing.lg,
        gap: Spacing.md,
    },
    hipStats: {
        flexDirection: 'row',
        paddingHorizontal: Spacing.lg,
        paddingBottom: Spacing.lg,
        gap: Spacing.sm,
    },
    hipStatItem: {
        flex: 1,
        alignItems: 'center',
        gap: 2,
    },
});
