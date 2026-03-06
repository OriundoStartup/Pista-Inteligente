import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { BorderRadius, Spacing } from '../constants/Theme';
import { LinearGradient } from 'expo-linear-gradient';

interface Pozo {
    id: string;
    hipodromo: string;
    fecha_evento: string;
    nro_carrera: number;
    tipo_apuesta: string;
    monto_estimado: number;
    mensaje_marketing: string;
    ticket_sugerido?: any;
}

interface JackpotAlertProps {
    pozos: Pozo[];
}

/**
 * Custom comparator for JackpotAlert.
 * Pozos is an array of objects — shallow compare by length + first/last ids.
 */
function arePropsEqual(prev: JackpotAlertProps, next: JackpotAlertProps): boolean {
    if (prev.pozos === next.pozos) return true;
    if (prev.pozos.length !== next.pozos.length) return false;
    if (prev.pozos.length === 0) return true;
    // Compare first and last item ids as a fast heuristic
    return (
        prev.pozos[0].id === next.pozos[0].id &&
        prev.pozos[prev.pozos.length - 1].id === next.pozos[next.pozos.length - 1].id
    );
}

export const JackpotAlert = React.memo<JackpotAlertProps>(function JackpotAlert({ pozos }) {
    if (!pozos || pozos.length === 0) return null;

    const formatCLP = (monto: number) => {
        return '$' + monto.toLocaleString('es-CL');
    };

    return (
        <View style={styles.container}>
            <LinearGradient
                colors={['rgba(139, 92, 246, 0.15)', 'rgba(244, 63, 94, 0.1)']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.gradient}
            >
                <ThemedText variant="h3" align="center" style={styles.title}>
                    💰 Pozos Acumulados
                </ThemedText>

                {pozos.map((pozo) => (
                    <View key={pozo.id} style={styles.pozoCard}>
                        <View style={styles.pozoHeader}>
                            <ThemedText variant="body" weight="semibold">
                                {pozo.hipodromo}
                            </ThemedText>
                            <ThemedText variant="caption">
                                Carrera {pozo.nro_carrera} • {pozo.tipo_apuesta}
                            </ThemedText>
                        </View>
                        <ThemedText
                            variant="h2"
                            weight="extrabold"
                            color={Colors.accent}
                            align="center"
                            style={styles.monto}
                        >
                            {formatCLP(pozo.monto_estimado)}
                        </ThemedText>
                        {pozo.mensaje_marketing && (
                            <ThemedText variant="caption" align="center">
                                {pozo.mensaje_marketing}
                            </ThemedText>
                        )}
                    </View>
                ))}
            </LinearGradient>
        </View>
    );
}, arePropsEqual);

JackpotAlert.displayName = 'JackpotAlert';

const styles = StyleSheet.create({
    container: {
        borderRadius: BorderRadius.lg,
        overflow: 'hidden',
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        marginBottom: Spacing.lg,
    },
    gradient: {
        padding: Spacing.lg,
    },
    title: {
        marginBottom: Spacing.lg,
    },
    pozoCard: {
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: BorderRadius.md,
        padding: Spacing.lg,
        marginBottom: Spacing.md,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
    },
    pozoHeader: {
        gap: 2,
        marginBottom: Spacing.sm,
    },
    monto: {
        marginVertical: Spacing.sm,
    },
});
