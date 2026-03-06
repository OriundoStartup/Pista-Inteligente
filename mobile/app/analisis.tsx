import React, { useCallback } from 'react';
import {
    View,
    FlatList,
    RefreshControl,
    StyleSheet,
    ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';
import { ThemedText } from '../components/ThemedText';
import { PatternCard } from '../components/PatternCard';
import { Colors } from '../constants/Colors';
import { Spacing } from '../constants/Theme';

import { API_BASE_URL } from '../utils/secureConfig';

const API_BASE = API_BASE_URL ?? 'https://pista-inteligente.vercel.app';
const API_URL = `${API_BASE}/api/analisis/patrones`;

if (!API_BASE_URL) {
    console.warn('[analisis] API_BASE_URL no definida, usando fallback:', API_BASE);
}

interface Patron {
    tipo: string;
    numeros: number[];
    veces: number;
    detalle: {
        fecha: string;
        hipodromo: string;
        nro_carrera: number;
        resultado: number[];
    }[];
}

export default function AnalisisScreen() {
    const [patrones, setPatrones] = React.useState<Patron[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<string | null>(null);
    const [refreshing, setRefreshing] = React.useState(false);

    const fetchPatrones = React.useCallback(async () => {
        try {
            setError(null);
            const res = await fetch(API_URL);

            if (!res.ok) {
                throw new Error(
                    res.status === 404
                        ? 'Endpoint no encontrado. Verifica que la API esté desplegada.'
                        : `Error del servidor (HTTP ${res.status})`
                );
            }

            const contentType = res.headers.get('content-type');
            if (!contentType?.includes('application/json')) {
                throw new Error(
                    'La API no devolvió JSON válido. Es posible que el servidor esté caído o la URL sea incorrecta.'
                );
            }

            const data = await res.json();
            setPatrones(data.patrones || []);
        } catch (err: any) {
            console.warn('[analisis] Fetch error:', err?.message);
            setError(err?.message || 'No se pudieron cargar los patrones');
        } finally {
            setLoading(false);
        }
    }, []);

    React.useEffect(() => {
        fetchPatrones();
    }, [fetchPatrones]);

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await fetchPatrones();
        setRefreshing(false);
    }, [fetchPatrones]);

    const renderHeader = () => (
        <View style={styles.header}>
            <ThemedText variant="h2" weight="extrabold" align="center">
                🔢 Patrones Numéricos
            </ThemedText>
            <ThemedText variant="muted" align="center" style={styles.subtitle}>
                Combinaciones que se han repetido en las últimas carreras
            </ThemedText>
        </View>
    );

    if (loading) {
        return (
            <>
                <Stack.Screen
                    options={{
                        title: 'Análisis',
                        headerStyle: { backgroundColor: Colors.bgDark },
                        headerTintColor: Colors.textMain,
                        headerTitleStyle: { fontFamily: 'Outfit_600SemiBold' },
                    }}
                />
                <SafeAreaView style={styles.container} edges={['bottom']}>
                    <View style={styles.loadingContainer}>
                        <ActivityIndicator color={Colors.primary} size="large" />
                        <ThemedText variant="muted" align="center" style={{ marginTop: Spacing.md }}>
                            Analizando últimos 60 días de carreras...
                        </ThemedText>
                    </View>
                </SafeAreaView>
            </>
        );
    }

    if (error) {
        return (
            <>
                <Stack.Screen
                    options={{
                        title: 'Análisis',
                        headerStyle: { backgroundColor: Colors.bgDark },
                        headerTintColor: Colors.textMain,
                    }}
                />
                <SafeAreaView style={styles.container} edges={['bottom']}>
                    <View style={styles.loadingContainer}>
                        <ThemedText variant="h3" color={Colors.accent} align="center">
                            ⚠️ {error}
                        </ThemedText>
                    </View>
                </SafeAreaView>
            </>
        );
    }

    return (
        <>
            <Stack.Screen
                options={{
                    title: 'Análisis',
                    headerStyle: { backgroundColor: Colors.bgDark },
                    headerTintColor: Colors.textMain,
                    headerTitleStyle: { fontFamily: 'Outfit_600SemiBold' },
                }}
            />
            <SafeAreaView style={styles.container} edges={['bottom']}>
                <FlatList
                    data={patrones}
                    keyExtractor={(item, i) => `${item.tipo}-${i}`}
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
                    renderItem={({ item }) => (
                        <PatternCard
                            tipo={item.tipo}
                            numeros={item.numeros}
                            veces={item.veces}
                            detalle={item.detalle}
                        />
                    )}
                    ListEmptyComponent={
                        <View style={styles.loadingContainer}>
                            <ThemedText variant="muted" align="center">
                                No se encontraron patrones numéricos repetidos recientemente.
                            </ThemedText>
                        </View>
                    }
                />
            </SafeAreaView>
        </>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
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
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: Spacing.xxxl * 2,
    },
});
