import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';

interface PatternCardProps {
    tipo: string;
    numeros: number[];
    veces: number;
    detalle: {
        fecha: string;
        hipodromo: string;
        nro_carrera: number;
    }[];
}

/**
 * Card displaying a numeric pattern from race results.
 */
export const PatternCard = React.memo(function PatternCard({
    tipo,
    numeros,
    veces,
    detalle,
}: PatternCardProps) {
    return (
        <View style={styles.card}>
            {/* Badge */}
            <View style={styles.badge}>
                <ThemedText variant="caption" weight="semibold" color={Colors.primary}>
                    {veces} repeticiones
                </ThemedText>
            </View>

            {/* Title */}
            <ThemedText variant="body" weight="semibold" style={styles.title}>
                {tipo}
            </ThemedText>

            {/* Numbers */}
            <View style={styles.numbersRow}>
                {numeros.map((num, i) => (
                    <View key={i} style={styles.numberCircle}>
                        <ThemedText variant="h3" weight="extrabold" color="#fff">
                            {num}
                        </ThemedText>
                    </View>
                ))}
            </View>

            {/* Description */}
            <ThemedText variant="muted" align="center" style={styles.desc}>
                La combinación{' '}
                <ThemedText variant="body" weight="semibold" color={Colors.gold}>
                    {numeros.join('-')}
                </ThemedText>{' '}
                se ha repetido {veces} veces.
            </ThemedText>

            {/* Recent appearances */}
            {detalle.length > 0 && (
                <View style={styles.detailBox}>
                    <ThemedText variant="caption" style={styles.detailTitle}>
                        Últimas apariciones:
                    </ThemedText>
                    {detalle.slice(0, 3).map((d, i) => (
                        <View key={i} style={styles.detailRow}>
                            <ThemedText variant="caption">
                                {new Date(d.fecha).toLocaleDateString('es-CL', {
                                    day: 'numeric',
                                    month: 'short',
                                })}
                            </ThemedText>
                            <ThemedText
                                variant="caption"
                                numberOfLines={1}
                                style={styles.detailHip}
                            >
                                {d.hipodromo}
                            </ThemedText>
                            <View style={styles.detailBadge}>
                                <ThemedText variant="caption">#{d.nro_carrera}</ThemedText>
                            </View>
                        </View>
                    ))}
                    {detalle.length > 3 && (
                        <ThemedText
                            variant="caption"
                            color={Colors.textMuted}
                            align="center"
                            style={{ marginTop: Spacing.xs }}
                        >
                            (+{detalle.length - 3} más)
                        </ThemedText>
                    )}
                </View>
            )}
        </View>
    );
});

const styles = StyleSheet.create({
    card: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        padding: Spacing.lg,
        marginBottom: Spacing.lg,
    },
    badge: {
        position: 'absolute',
        top: Spacing.md,
        right: Spacing.md,
        backgroundColor: Colors.primaryMuted,
        paddingVertical: 2,
        paddingHorizontal: Spacing.sm,
        borderRadius: BorderRadius.full,
    },
    title: {
        marginBottom: Spacing.md,
    },
    numbersRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        gap: Spacing.sm,
        marginVertical: Spacing.lg,
    },
    numberCircle: {
        width: 48,
        height: 48,
        borderRadius: 24,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: Colors.gold,
        shadowColor: Colors.gold,
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.4,
        shadowRadius: 8,
        elevation: 4,
    },
    desc: {
        lineHeight: 20,
        marginBottom: Spacing.md,
    },
    detailBox: {
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: BorderRadius.md,
        padding: Spacing.md,
    },
    detailTitle: {
        color: Colors.textMuted,
        marginBottom: Spacing.xs,
    },
    detailRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: Spacing.xs,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
    },
    detailHip: {
        flex: 1,
        marginHorizontal: Spacing.sm,
        textAlign: 'center',
    },
    detailBadge: {
        backgroundColor: 'rgba(255,255,255,0.1)',
        paddingHorizontal: Spacing.xs,
        borderRadius: 4,
    },
});
