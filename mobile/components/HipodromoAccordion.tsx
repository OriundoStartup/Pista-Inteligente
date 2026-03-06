import React, { useState, useCallback } from 'react';
import { View, TouchableOpacity, StyleSheet, LayoutAnimation, Platform, UIManager } from 'react-native';
import { ThemedText } from './ThemedText';
import { RaceCard } from './RaceCard';
import { Colors } from '../constants/Colors';
import { BorderRadius, Spacing } from '../constants/Theme';
import { MaterialCommunityIcons } from '@expo/vector-icons';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
    UIManager.setLayoutAnimationEnabledExperimental(true);
}

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

interface HipodromoAccordionProps {
    hipodromoKey: string; // "hipódromo|fecha"
    carreras: Carrera[];
    today: string;
    defaultOpen?: boolean;
}

const getHipodromoIcon = (name: string) => {
    if (name.includes('Chile')) return '🏇';
    if (name.includes('Club Hípico de Santiago') || name.includes('Club Hípico')) return '🏛️';
    if (name.includes('Valparaíso')) return '🌊';
    if (name.includes('Concepción')) return '🌲';
    return '🏇';
};

export const HipodromoAccordion = React.memo(function HipodromoAccordion({
    hipodromoKey,
    carreras,
    today,
    defaultOpen = true,
}: HipodromoAccordionProps) {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    const [hipodromo, fecha] = hipodromoKey.split('|');
    const isToday = fecha === today;

    const toggleOpen = useCallback(() => {
        LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
        setIsOpen((prev) => !prev);
    }, []);

    const formatFecha = (f: string) => {
        const d = new Date(f + 'T12:00:00');
        return d.toLocaleDateString('es-CL', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
        });
    };

    return (
        <View style={styles.container}>
            <TouchableOpacity
                style={styles.header}
                onPress={toggleOpen}
                activeOpacity={0.7}
            >
                <ThemedText style={styles.icon}>{getHipodromoIcon(hipodromo)}</ThemedText>
                <View style={styles.headerText}>
                    <ThemedText variant="h3" weight="semibold" numberOfLines={1}>
                        {hipodromo}
                    </ThemedText>
                    <View style={styles.badges}>
                        {isToday ? (
                            <View style={styles.todayBadge}>
                                <ThemedText variant="caption" weight="semibold" color={Colors.bgDark}>
                                    HOY
                                </ThemedText>
                            </View>
                        ) : (
                            <ThemedText variant="caption">{formatFecha(fecha)}</ThemedText>
                        )}
                        <ThemedText variant="caption" color={Colors.primary}>
                            {carreras.length} carrera{carreras.length !== 1 ? 's' : ''}
                        </ThemedText>
                    </View>
                </View>
                <MaterialCommunityIcons
                    name={isOpen ? 'chevron-up' : 'chevron-down'}
                    size={24}
                    color={Colors.textMuted}
                />
            </TouchableOpacity>

            {isOpen && (
                <View style={styles.content}>
                    {carreras
                        .sort((a, b) => a.carrera - b.carrera)
                        .map((carrera) => (
                            <RaceCard
                                key={carrera.id}
                                carrera={carrera.carrera}
                                hora={carrera.hora}
                                distancia={carrera.distancia}
                                predicciones={carrera.predicciones}
                                hipodromo={hipodromo}
                            />
                        ))}
                </View>
            )}
        </View>
    );
});

HipodromoAccordion.displayName = 'HipodromoAccordion';

const styles = StyleSheet.create({
    container: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        overflow: 'hidden',
        marginBottom: Spacing.lg,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: Spacing.lg,
        gap: Spacing.md,
    },
    icon: {
        fontSize: 28,
    },
    headerText: {
        flex: 1,
        gap: 4,
    },
    badges: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.sm,
    },
    todayBadge: {
        backgroundColor: Colors.success,
        paddingHorizontal: Spacing.sm,
        paddingVertical: 2,
        borderRadius: BorderRadius.full,
    },
    content: {
        padding: Spacing.md,
        paddingTop: 0,
    },
});
