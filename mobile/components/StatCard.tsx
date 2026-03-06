import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { BorderRadius, Spacing } from '../constants/Theme';

interface StatCardProps {
    label: string;
    value: string | number;
    color: string;
    count?: number;
    total?: number;
    subtitle?: string;
    icon?: string;
}

/**
 * Stat card used in grid layouts (index.tsx, estadisticas.tsx).
 * Rendered inside map() — memo prevents re-renders when sibling data changes.
 * All props are primitives → default shallow comparison is sufficient.
 */
export const StatCard = React.memo<StatCardProps>(function StatCard({
    label,
    value,
    color,
    count,
    total,
    subtitle,
    icon,
}) {
    return (
        <View style={[styles.card, { borderLeftColor: color }]}>
            {icon && <ThemedText style={styles.icon}>{icon}</ThemedText>}
            <ThemedText variant="caption" align="center">{label}</ThemedText>
            <ThemedText
                variant="h1"
                align="center"
                style={[styles.value, { color }]}
            >
                {typeof value === 'number' ? value.toLocaleString('es-CL') : value}
            </ThemedText>
            {count !== undefined && total !== undefined && (
                <ThemedText variant="caption" align="center">
                    {count} de {total}
                </ThemedText>
            )}
            {subtitle && (
                <ThemedText variant="caption" align="center">{subtitle}</ThemedText>
            )}
        </View>
    );
});

StatCard.displayName = 'StatCard';

const styles = StyleSheet.create({
    card: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        padding: Spacing.lg,
        borderLeftWidth: 4,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        alignItems: 'center',
        flex: 1,
        minWidth: 140,
    },
    value: {
        marginVertical: Spacing.xs,
    },
    icon: {
        fontSize: 24,
        marginBottom: Spacing.xs,
    },
});
