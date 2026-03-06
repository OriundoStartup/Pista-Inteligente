import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { BorderRadius, Spacing } from '../constants/Theme';

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

interface RaceResultCardProps {
    race: RaceResult;
}

const getHipodromoIcon = (hip: string) => {
    if (hip.includes('Chile')) return '🏇';
    if (hip.includes('Club')) return '🏛️';
    if (hip.includes('Valparaíso')) return '🌊';
    if (hip.includes('Concepción')) return '🌲';
    return '🏇';
};

const getBestMatch = (race: RaceResult) => {
    if (race.acierto_superfecta) return { color: Colors.primary, label: '⭐ SUPERFECTA' };
    if (race.acierto_trifecta) return { color: Colors.bronze, label: '🏆 TRIFECTA' };
    if (race.acierto_quiniela) return { color: Colors.silver, label: '🎯 QUINIELA' };
    if (race.acierto_ganador) return { color: Colors.gold, label: '🥇 GANADOR' };
    return null;
};

export const RaceResultCard = React.memo(function RaceResultCard({ race }: RaceResultCardProps) {
    const bestMatch = getBestMatch(race);
    const formatDate = (fecha: string) => {
        const d = new Date(fecha + 'T12:00:00');
        return d.toLocaleDateString('es-CL', { day: '2-digit', month: 'short' });
    };

    return (
        <View style={[styles.card, { borderLeftColor: bestMatch?.color || 'transparent' }]}>
            {/* Header */}
            <View style={styles.header}>
                <View style={styles.headerLeft}>
                    <ThemedText style={{ fontSize: 18 }}>{getHipodromoIcon(race.hipodromo)}</ThemedText>
                    <View>
                        <ThemedText variant="body" weight="semibold" numberOfLines={1}>
                            {race.hipodromo}
                        </ThemedText>
                        <ThemedText variant="caption">
                            {formatDate(race.fecha)} • Carrera {race.nro_carrera}
                        </ThemedText>
                    </View>
                </View>
                <View style={styles.badgeRow}>
                    {race.acierto_ganador && <View style={[styles.badge, { backgroundColor: Colors.goldBg, borderColor: Colors.goldBorder }]}><ThemedText style={{ fontSize: 12 }}>🥇</ThemedText></View>}
                    {race.acierto_quiniela && <View style={[styles.badge, { backgroundColor: Colors.silverBg, borderColor: Colors.silverBorder }]}><ThemedText style={{ fontSize: 12 }}>🎯</ThemedText></View>}
                    {race.acierto_trifecta && <View style={[styles.badge, { backgroundColor: Colors.bronzeBg, borderColor: Colors.bronzeBorder }]}><ThemedText style={{ fontSize: 12 }}>🏆</ThemedText></View>}
                    {race.acierto_superfecta && <View style={[styles.badge, { backgroundColor: Colors.primaryMuted, borderColor: Colors.primary }]}><ThemedText style={{ fontSize: 12 }}>⭐</ThemedText></View>}
                </View>
            </View>

            {/* Hit Grid */}
            <View style={styles.hitGrid}>
                {[
                    { label: 'Ganador', hit: race.acierto_ganador, color: Colors.gold },
                    { label: 'Quiniela', hit: race.acierto_quiniela, color: Colors.silver },
                    { label: 'Trifecta', hit: race.acierto_trifecta, color: Colors.bronze },
                    { label: 'Super', hit: race.acierto_superfecta, color: Colors.primary },
                ].map((item) => (
                    <View key={item.label} style={[styles.hitBox, item.hit && { backgroundColor: `${item.color}15`, borderColor: `${item.color}40` }]}>
                        <ThemedText variant="caption" style={{ fontSize: 10 }}>{item.label}</ThemedText>
                        <ThemedText style={{ fontSize: 16 }}>{item.hit ? '✅' : '❌'}</ThemedText>
                    </View>
                ))}
            </View>

            {/* Comparison */}
            <View style={styles.comparison}>
                <View style={styles.compCol}>
                    <ThemedText variant="label" color={Colors.primary}>🤖 IA Predice</ThemedText>
                    {(race.prediccion_top4 || []).slice(0, 4).map((p, i) => (
                        <View key={i} style={[styles.compRow, i === 0 && { backgroundColor: Colors.primaryMuted }]}>
                            <ThemedText variant="caption" weight={i === 0 ? 'semibold' : 'regular'} color={i === 0 ? Colors.primary : Colors.textMuted} style={{ width: 18 }}>
                                {i + 1}.
                            </ThemedText>
                            <ThemedText variant="caption" weight={i === 0 ? 'semibold' : 'regular'} color={Colors.textMain} numberOfLines={1} style={{ flex: 1 }}>
                                {p}
                            </ThemedText>
                        </View>
                    ))}
                </View>
                <View style={styles.compCol}>
                    <ThemedText variant="label" color={Colors.secondary}>🏁 Resultado</ThemedText>
                    {(race.resultado_top4 || []).slice(0, 4).map((r, i) => (
                        <View key={i} style={[styles.compRow, i === 0 && { backgroundColor: Colors.secondaryMuted }]}>
                            <ThemedText variant="caption" weight={i === 0 ? 'semibold' : 'regular'} color={i === 0 ? Colors.secondary : Colors.textMuted} style={{ width: 18 }}>
                                {i + 1}.
                            </ThemedText>
                            <ThemedText variant="caption" weight={i === 0 ? 'semibold' : 'regular'} color={Colors.textMain} numberOfLines={1} style={{ flex: 1 }}>
                                {r}
                            </ThemedText>
                        </View>
                    ))}
                </View>
            </View>
        </View>
    );
});

RaceResultCard.displayName = 'RaceResultCard';

const styles = StyleSheet.create({
    card: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        borderLeftWidth: 4,
        overflow: 'hidden',
        marginBottom: Spacing.md,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: Spacing.md,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
    },
    headerLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.sm,
        flex: 1,
    },
    badgeRow: {
        flexDirection: 'row',
        gap: 4,
    },
    badge: {
        paddingHorizontal: 6,
        paddingVertical: 2,
        borderRadius: 4,
        borderWidth: 1,
    },
    hitGrid: {
        flexDirection: 'row',
        gap: Spacing.sm,
        padding: Spacing.md,
    },
    hitBox: {
        flex: 1,
        alignItems: 'center',
        padding: Spacing.sm,
        borderRadius: BorderRadius.sm,
        backgroundColor: 'rgba(255,255,255,0.02)',
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.05)',
        gap: 2,
    },
    comparison: {
        flexDirection: 'row',
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: BorderRadius.sm,
        margin: Spacing.md,
        marginTop: 0,
        padding: Spacing.md,
        gap: Spacing.md,
    },
    compCol: {
        flex: 1,
        gap: 4,
    },
    compRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 2,
        paddingHorizontal: 4,
        borderRadius: 4,
        gap: 4,
    },
});
