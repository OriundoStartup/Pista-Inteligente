import React, { useMemo } from 'react';
import { View, StyleSheet } from 'react-native';
import { ThemedText } from './ThemedText';
import { ScoreBar } from './ScoreBar';
import { ShareButton } from './ShareButton';
import { Colors } from '../constants/Colors';
import { BorderRadius, Spacing } from '../constants/Theme';

interface Prediccion {
    numero: number;
    caballo: string;
    jinete: string;
    puntaje_ia: number;
}

interface RaceCardProps {
    carrera: number;
    hora: string;
    distancia: number;
    predicciones: Prediccion[];
    hipodromo?: string;
}

export const RaceCard = React.memo<RaceCardProps>(({
    carrera,
    hora,
    distancia,
    predicciones,
    hipodromo = '',
}) => {
    const shareData = useMemo(() => {
        const topPick = predicciones[0];
        if (!topPick) return null;
        return {
            title: `Predicción Carrera ${carrera}`,
            message:
                `🏇 ${hipodromo || 'Hipódromo'} — Carrera ${carrera}: ` +
                `Mi pick es ${topPick.caballo} (${topPick.jinete})\n` +
                `Predicción de Pista Inteligente 🎯`,
            url: 'https://pista-inteligente.vercel.app/programa',
        };
    }, [carrera, hipodromo, predicciones]);

    return (
        <View style={styles.card}>
            {/* Header */}
            <View style={styles.header}>
                <View style={styles.headerLeft}>
                    <ThemedText variant="h3" weight="semibold">
                        Carrera {carrera}
                    </ThemedText>
                    <ThemedText variant="caption">
                        {hora} • {distancia.toLocaleString('es-CL')}m
                    </ThemedText>
                </View>
                {shareData && (
                    <ShareButton
                        title={shareData.title}
                        message={shareData.message}
                        url={shareData.url}
                        size={18}
                    />
                )}
            </View>

            {/* Table Header */}
            <View style={styles.tableHeader}>
                <ThemedText variant="label" style={styles.colNum}>#</ThemedText>
                <ThemedText variant="label" style={styles.colCaballo}>Caballo</ThemedText>
                <ThemedText variant="label" style={styles.colJinete}>Jinete</ThemedText>
                <ThemedText variant="label" style={styles.colScore}>Score IA</ThemedText>
            </View>

            {/* Predictions */}
            {predicciones.map((p, index) => (
                <View
                    key={`${p.numero}-${index}`}
                    style={[
                        styles.row,
                        index === 0 && styles.topRow,
                        index < predicciones.length - 1 && styles.rowBorder,
                    ]}
                >
                    <ThemedText
                        variant="body"
                        weight={index === 0 ? 'extrabold' : 'regular'}
                        color={index === 0 ? Colors.primary : Colors.textMuted}
                        style={styles.colNum}
                    >
                        {p.numero}
                    </ThemedText>
                    <View style={styles.colCaballo}>
                        <ThemedText
                            variant="body"
                            weight={index === 0 ? 'semibold' : 'regular'}
                            numberOfLines={1}
                        >
                            {p.caballo}
                        </ThemedText>
                    </View>
                    <ThemedText
                        variant="caption"
                        numberOfLines={1}
                        style={styles.colJinete}
                    >
                        {p.jinete}
                    </ThemedText>
                    <View style={styles.colScore}>
                        <ScoreBar score={p.puntaje_ia} rank={index + 1} />
                    </View>
                </View>
            ))}
        </View>
    );
});

RaceCard.displayName = 'RaceCard';

const styles = StyleSheet.create({
    card: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        overflow: 'hidden',
        marginBottom: Spacing.md,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: Spacing.lg,
        borderBottomWidth: 1,
        borderBottomColor: Colors.borderGlass,
    },
    headerLeft: {
        gap: 2,
    },
    tableHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: Spacing.lg,
        paddingVertical: Spacing.sm,
        backgroundColor: 'rgba(0,0,0,0.2)',
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: Spacing.lg,
        paddingVertical: Spacing.md,
    },
    topRow: {
        backgroundColor: 'rgba(139, 92, 246, 0.08)',
    },
    rowBorder: {
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.04)',
    },
    colNum: {
        width: 30,
    },
    colCaballo: {
        flex: 1.5,
        paddingRight: Spacing.sm,
    },
    colJinete: {
        flex: 1,
        paddingRight: Spacing.sm,
    },
    colScore: {
        flex: 1.2,
    },
});
