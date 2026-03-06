import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';
import { ThemedText } from '../components/ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';

const sections = [
    {
        title: '🏟️ Hipódromos de Chile',
        items: [
            {
                name: '🏇 Hipódromo Chile',
                desc: 'Santiago (Independencia) — El hipódromo con mayor actividad del país. Pista de arena de 1.500 metros con jornadas regulares de lunes a viernes.',
                color: Colors.primary,
            },
            {
                name: '🏛️ Club Hípico de Santiago',
                desc: 'Santiago (Blanco Encalada) — Fundado en 1869, el recinto más antiguo de Chile. Pista de pasto de 2.000m, sede de los clásicos más prestigiosos.',
                color: Colors.secondary,
            },
            {
                name: '🌊 Valparaíso Sporting',
                desc: 'Viña del Mar — Cuna de la hípica chilena, sede del Derby. Pista de pasto con recorrido técnico costero.',
                color: Colors.hipValpo,
            },
            {
                name: '🌲 Club Hípico de Concepción',
                desc: 'Hualpén (Biobío) — Principal recinto del sur, jornadas regulares con carreras especiales para la zona.',
                color: Colors.hipConce,
            },
        ],
    },
    {
        title: '🇦🇷 Hipódromos de Argentina',
        items: [
            {
                name: '🏇 Hipódromo de La Plata',
                desc: 'Buenos Aires — Uno de los recintos más activos de Argentina. Pista de arena y césped con jornadas frecuentes.',
                color: Colors.secondary,
            },
            {
                name: '🏛️ Hipódromo de Palermo',
                desc: 'Buenos Aires (Capital) — El recinto más emblemático del turf argentino. Sede del Gran Premio Nacional y los clásicos más importantes.',
                color: Colors.primary,
            },
            {
                name: '🌳 Hipódromo de San Isidro',
                desc: 'San Isidro, Buenos Aires — Pista de césped de alto nivel técnico. Sede del Gran Premio Carlos Pellegrini.',
                color: Colors.accent,
            },
        ],
    },
    {
        title: '🎰 Tipos de Apuestas',
        items: [
            {
                name: '🥇 Ganador',
                desc: 'Apostar al caballo que cruza primero la meta. La apuesta más simple y directa.',
                color: Colors.gold,
            },
            {
                name: '🥈 Placé',
                desc: 'El caballo elegido debe llegar 1° o 2°. Menor riesgo, menor pago.',
                color: Colors.silver,
            },
            {
                name: '🎯 Exacta',
                desc: 'Acertar los dos primeros lugares en orden exacto. Mayor dificultad que la Quiniela.',
                color: Colors.secondary,
            },
            {
                name: '🔄 Imperfecta',
                desc: 'Acertar los dos primeros lugares sin importar el orden. Más fácil que la Exacta, menor pago.',
                color: Colors.hipValpo,
            },
            {
                name: '🎲 Quintela',
                desc: 'Seleccionar un grupo de caballos que deben llegar en los primeros puestos, sin orden específico.',
                color: Colors.hipConce,
            },
            {
                name: '🏆 Trifecta',
                desc: 'Acertar los tres primeros lugares en orden exacto. Alta dificultad, alto pago.',
                color: Colors.bronze,
            },
            {
                name: '⭐ Superfecta',
                desc: 'Acertar los cuatro primeros lugares en orden exacto. La apuesta más difícil.',
                color: Colors.primary,
            },
        ],
    },
    {
        title: '📋 Cómo Leer el Programa',
        items: [
            {
                name: '📊 Número y Nombre',
                desc: 'Cada caballo tiene un número de partida y su nombre registrado. El número indica su puesto en la partida.',
                color: Colors.textMuted,
            },
            {
                name: '🏇 Jinete y Preparador',
                desc: 'El jinete monta al caballo en la carrera. El preparador (entrenador) lo entrena. Ambos influyen en el rendimiento.',
                color: Colors.textMuted,
            },
            {
                name: '⚖️ Peso y Distancia',
                desc: 'El peso asignado equilibra las chances. La distancia determina si favorece a velocistas o fondistas.',
                color: Colors.textMuted,
            },
            {
                name: '📈 Puntaje IA',
                desc: 'Nuestro modelo asigna un puntaje de probabilidad basado en historial, condiciones y variables estadísticas.',
                color: Colors.primary,
            },
        ],
    },
    {
        title: '📖 Terminología Hípica',
        items: [
            { name: 'Cuerpo', desc: 'Unidad de distancia entre caballos (~2.4 metros).', color: Colors.textMuted },
            { name: 'Handicap', desc: 'Peso extra asignado para equilibrar las chances.', color: Colors.textMuted },
            { name: 'Stud', desc: 'Grupo propietario de caballos de carrera.', color: Colors.textMuted },
            { name: 'Haras', desc: 'Criadero donde nacen y se crían los ejemplares.', color: Colors.textMuted },
            { name: 'Gateras', desc: 'Compartimentos de partida donde se ubican los caballos.', color: Colors.textMuted },
            { name: 'Pozo', desc: 'Total de dinero apostado en un tipo de apuesta.', color: Colors.textMuted },
            { name: 'Dividendo', desc: 'Lo que paga una apuesta ganadora. Ej: $1.850 por $100.', color: Colors.textMuted },
        ],
    },
];

export default function GuiaScreen() {
    return (
        <>
            <Stack.Screen
                options={{
                    title: 'Guía de Uso',
                    headerStyle: { backgroundColor: Colors.bgDark },
                    headerTintColor: Colors.textMain,
                    headerTitleStyle: { fontFamily: 'Outfit_600SemiBold' },
                }}
            />
            <SafeAreaView style={styles.container} edges={['bottom']}>
                <ScrollView
                    style={styles.scroll}
                    contentContainerStyle={styles.content}
                    showsVerticalScrollIndicator={false}
                >
                    {/* Header */}
                    <View style={styles.header}>
                        <ThemedText variant="h2" weight="extrabold" align="center">
                            📖 Guía Completa
                        </ThemedText>
                        <ThemedText variant="muted" align="center" style={styles.subtitle}>
                            Todo lo que necesitas saber sobre las carreras de caballos en Chile
                        </ThemedText>
                    </View>

                    {/* Sections */}
                    {sections.map((section) => (
                        <View key={section.title} style={styles.section}>
                            <ThemedText variant="h3" weight="semibold" style={styles.sectionTitle}>
                                {section.title}
                            </ThemedText>
                            {section.items.map((item) => (
                                <View
                                    key={item.name}
                                    style={[styles.card, { borderLeftColor: item.color }]}
                                >
                                    <ThemedText variant="body" weight="semibold" color={item.color}>
                                        {item.name}
                                    </ThemedText>
                                    <ThemedText variant="muted" style={styles.cardDesc}>
                                        {item.desc}
                                    </ThemedText>
                                </View>
                            ))}
                        </View>
                    ))}

                    {/* Footer */}
                    <View style={styles.footer}>
                        <ThemedText variant="caption" align="center">
                            🏇 Pista Inteligente — Hecho con ❤️ en Chile
                        </ThemedText>
                    </View>
                </ScrollView>
            </SafeAreaView>
        </>
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
        paddingBottom: Spacing.xxxl * 2,
    },
    header: {
        paddingVertical: Spacing.xl,
        gap: Spacing.xs,
        marginBottom: Spacing.lg,
    },
    subtitle: {
        maxWidth: 300,
        lineHeight: 20,
        alignSelf: 'center',
    },
    section: {
        marginBottom: Spacing.xl,
    },
    sectionTitle: {
        marginBottom: Spacing.lg,
    },
    card: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        borderLeftWidth: 4,
        padding: Spacing.lg,
        marginBottom: Spacing.md,
    },
    cardDesc: {
        lineHeight: 20,
        marginTop: Spacing.xs,
    },
    footer: {
        paddingVertical: Spacing.xl,
        opacity: 0.6,
    },
});
