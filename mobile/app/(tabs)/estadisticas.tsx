import React, { useCallback } from 'react';
import {
    View,
    ScrollView,
    RefreshControl,
    StyleSheet,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { ThemedText } from '../../components/ThemedText';
import { GradientText } from '../../components/GradientText';
import { SectionTitle } from '../../components/SectionTitle';
import { GradientButton } from '../../components/GradientButton';
import { StatCard } from '../../components/StatCard';
import { Colors } from '../../constants/Colors';
import { Spacing, BorderRadius, Typography } from '../../constants/Theme';
import { useSupabaseQuery } from '../../hooks/useSupabase';
import { supabase } from '../../lib/supabase';

const hipodromosInfo = [
    {
        name: '🏇 Hipódromo Chile',
        color: Colors.primary,
        desc: 'Santiago (Independencia) — El hipódromo con mayor actividad del país. Pista de arena de 1.500 metros con jornadas regulares de lunes a viernes.',
    },
    {
        name: '🏛️ Club Hípico de Santiago',
        color: Colors.secondary,
        desc: 'Santiago (Blanco Encalada) — Fundado en 1869, el recinto más antiguo de Chile. Pista de pasto de 2.000m, sede de los clásicos más prestigiosos.',
    },
    {
        name: '🌊 Valparaíso Sporting',
        color: Colors.hipValpo,
        desc: 'Viña del Mar — Cuna de la hípica chilena, sede del Derby. Pista de pasto con recorrido técnico costero.',
    },
    {
        name: '🌲 Club Hípico de Concepción',
        color: Colors.hipConce,
        desc: 'Hualpén (Biobío) — Principal recinto del sur, jornadas regulares con carreras especiales para la zona.',
    },
];

const techStack = [
    { component: 'Modelo Principal', tech: 'LightGBM', color: Colors.primary, desc: 'Gradient Boosting optimizado para ranking' },
    { component: 'Modelo Secundario', tech: 'XGBoost', color: Colors.secondary, desc: 'Regularización avanzada contra sobreajuste' },
    { component: 'Modelo Terciario', tech: 'CatBoost', color: Colors.accent, desc: 'Especializado en variables categóricas' },
    { component: 'Meta-Learner', tech: 'Ridge Regression', color: Colors.gold, desc: 'Combina predicciones de los 3 modelos' },
];

export default function EstadisticasScreen() {
    const router = useRouter();

    const stats = useSupabaseQuery(async () => {
        const [carreras, caballos, jinetes, jornadas] = await Promise.all([
            supabase.from('carreras').select('*', { count: 'exact', head: true }),
            supabase.from('caballos').select('*', { count: 'exact', head: true }),
            supabase.from('jinetes').select('*', { count: 'exact', head: true }),
            supabase.from('jornadas').select('*', { count: 'exact', head: true }),
        ]);
        return {
            total_carreras: carreras.count || 0,
            total_caballos: caballos.count || 0,
            total_jinetes: jinetes.count || 0,
            total_jornadas: jornadas.count || 0,
        };
    }, 'estadisticas_counts');

    const [refreshing, setRefreshing] = React.useState(false);
    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await stats.refresh();
        setRefreshing(false);
    }, []);

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <ScrollView
                style={styles.scroll}
                contentContainerStyle={styles.content}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} colors={[Colors.primary]} />
                }
            >
                {/* Header */}
                <View style={styles.header}>
                    <GradientText
                        fontSize={Typography.sizes.xxl}
                        fontFamily={Typography.fontFamily.extrabold}
                    >
                        Estadísticas del Sistema
                    </GradientText>
                    <ThemedText variant="muted" align="center" style={{ maxWidth: 320, lineHeight: 20 }}>
                        Datos reales de nuestra base de datos
                    </ThemedText>
                </View>

                {/* Stats Grid */}
                <View style={styles.section}>
                    <SectionTitle emoji="🗄️">Base de Datos</SectionTitle>
                    {stats.loading && !stats.data ? (
                        <ActivityIndicator color={Colors.primary} size="large" />
                    ) : (
                        <View style={styles.statsGrid}>
                            <StatCard label="🏁 Carreras" value={stats.data?.total_carreras ?? 0} color={Colors.primary} subtitle="Registradas" />
                            <StatCard label="🐴 Caballos" value={stats.data?.total_caballos ?? 0} color={Colors.secondary} subtitle="En base de datos" />
                            <StatCard label="🏇 Jinetes" value={stats.data?.total_jinetes ?? 0} color={Colors.accent} subtitle="Registrados" />
                            <StatCard label="📅 Jornadas" value={stats.data?.total_jornadas ?? 0} color={Colors.gold} subtitle="Procesadas" />
                        </View>
                    )}
                </View>

                {/* CTA to Rendimiento */}
                <GradientButton
                    label="📊 Ver Rendimiento Detallado"
                    onPress={() => router.push('/(tabs)/precision')}
                    style={{ alignSelf: 'center', marginBottom: Spacing.xl }}
                />

                {/* Hipódromos */}
                <View style={styles.section}>
                    <SectionTitle emoji="🏟️">Hipódromos Cubiertos</SectionTitle>
                    {hipodromosInfo.map((h) => (
                        <View key={h.name} style={[styles.hipCard, { borderLeftColor: h.color }]}>
                            <ThemedText variant="h3" weight="semibold" color={h.color} style={{ marginBottom: Spacing.sm }}>
                                {h.name}
                            </ThemedText>
                            <ThemedText variant="muted" style={{ lineHeight: 20 }}>
                                {h.desc}
                            </ThemedText>
                        </View>
                    ))}
                </View>

                {/* Technology */}
                <View style={styles.section}>
                    <SectionTitle emoji="🤖">Tecnología IA</SectionTitle>
                    <ThemedText variant="muted" style={{ lineHeight: 20, marginBottom: Spacing.lg }}>
                        Ensemble de tres modelos de Gradient Boosting combinados mediante un meta-learner.
                    </ThemedText>
                    {techStack.map((item) => (
                        <View key={item.tech} style={styles.techRow}>
                            <View style={[styles.techDot, { backgroundColor: item.color }]} />
                            <View style={{ flex: 1 }}>
                                <ThemedText variant="body" weight="semibold" color={item.color}>
                                    {item.tech}
                                </ThemedText>
                                <ThemedText variant="caption">{item.desc}</ThemedText>
                            </View>
                            <ThemedText variant="caption" style={{ opacity: 0.7 }}>{item.component}</ThemedText>
                        </View>
                    ))}
                </View>

                {/* CTA to Análisis */}
                <GradientButton
                    label="🔢 Ver Patrones Numéricos"
                    onPress={() => router.push('/analisis' as any)}
                    style={{ alignSelf: 'center', marginBottom: Spacing.xl }}
                />
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
    },
    scroll: {
        flex: 1,
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
    ctaCard: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        padding: Spacing.xl,
        alignItems: 'center',
        gap: Spacing.sm,
        marginBottom: Spacing.xl,
    },
    ctaBtn: {
        backgroundColor: Colors.primary,
        paddingVertical: Spacing.md,
        paddingHorizontal: Spacing.xl,
        borderRadius: BorderRadius.full,
        marginTop: Spacing.sm,
    },
    hipCard: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        borderLeftWidth: 4,
        padding: Spacing.lg,
        marginBottom: Spacing.md,
    },
    techRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.md,
        paddingVertical: Spacing.md,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
    },
    techDot: {
        width: 10,
        height: 10,
        borderRadius: 5,
    },
});
