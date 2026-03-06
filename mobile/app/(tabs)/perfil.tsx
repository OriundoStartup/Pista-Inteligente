import React from 'react';
import {
    View,
    ScrollView,
    StyleSheet,
    TouchableOpacity,
    Image,
    ActivityIndicator,
    Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { ThemedText } from '../../components/ThemedText';
import { Colors } from '../../constants/Colors';
import { Spacing, BorderRadius } from '../../constants/Theme';
import { useAuth } from '../../hooks/useAuth';

const links = [
    { icon: 'compass-outline' as const, label: 'Metodología', url: 'https://pista-inteligente.vercel.app/metodologia' },
    { icon: 'book-outline' as const, label: 'Guía de Uso', url: '', route: '/guia' },
    { icon: 'people-outline' as const, label: 'Quiénes Somos', url: 'https://pista-inteligente.vercel.app/quienes-somos' },
    { icon: 'shield-checkmark-outline' as const, label: 'Política de Privacidad', url: 'https://pista-inteligente.vercel.app/politica-de-privacidad' },
    { icon: 'document-text-outline' as const, label: 'Términos y Condiciones', url: 'https://pista-inteligente.vercel.app/terminos-y-condiciones' },
];

export default function PerfilScreen() {
    const { user, isLoading, signInWithGoogle, signOut } = useAuth();
    const router = useRouter();

    if (isLoading) {
        return (
            <SafeAreaView style={styles.container} edges={['top']}>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator color={Colors.primary} size="large" />
                </View>
            </SafeAreaView>
        );
    }

    // Not authenticated — Login screen
    if (!user) {
        return (
            <SafeAreaView style={styles.container} edges={['top']}>
                <ScrollView contentContainerStyle={styles.loginContent}>
                    <View style={styles.loginHero}>
                        <ThemedText style={{ fontSize: 64 }}>🏇</ThemedText>
                        <ThemedText variant="h1" align="center" style={{ marginTop: Spacing.lg }}>
                            Pista Inteligente
                        </ThemedText>
                        <ThemedText variant="muted" align="center" style={{ lineHeight: 22, maxWidth: 280, marginTop: Spacing.sm }}>
                            Accede a predicciones hípicas con IA y lleva las carreras contigo
                        </ThemedText>
                    </View>

                    {/* Benefits */}
                    <View style={styles.benefitsCard}>
                        <ThemedText variant="h3" weight="semibold" style={{ marginBottom: Spacing.lg }}>
                            ✨ Beneficios de registrarte
                        </ThemedText>
                        {[
                            '🔮 Predicciones de IA en tiempo real',
                            '📊 Estadísticas detalladas por hipódromo',
                            '🏆 Historial de rendimiento verificable',
                            '🔔 Notificaciones de nuevas jornadas',
                        ].map((benefit) => (
                            <View key={benefit} style={styles.benefitRow}>
                                <ThemedText variant="body">{benefit}</ThemedText>
                            </View>
                        ))}
                    </View>

                    {/* Google Sign In */}
                    <TouchableOpacity style={styles.googleBtn} onPress={signInWithGoogle} activeOpacity={0.85}>
                        <MaterialCommunityIcons name="google" size={22} color="#fff" />
                        <ThemedText variant="body" weight="semibold" color="#fff">
                            Continuar con Google
                        </ThemedText>
                    </TouchableOpacity>

                    {/* Badge */}
                    <View style={styles.badgeRow}>
                        <View style={styles.freeBadge}>
                            <ThemedText variant="caption" weight="semibold" color={Colors.success}>
                                100% GRATIS
                            </ThemedText>
                        </View>
                    </View>

                    {/* Trust */}
                    <View style={styles.trustRow}>
                        <ThemedText variant="caption">🔒 Sin spam</ThemedText>
                        <ThemedText variant="caption">🛡️ Protección SSL</ThemedText>
                        <ThemedText variant="caption">✅ Google OAuth</ThemedText>
                    </View>
                </ScrollView>
            </SafeAreaView>
        );
    }

    // Authenticated — Profile screen
    const avatarUrl = user.user_metadata?.avatar_url;
    const fullName = user.user_metadata?.full_name || user.email;

    return (
        <SafeAreaView style={styles.container} edges={['top']}>
            <ScrollView contentContainerStyle={styles.content}>
                {/* Profile Header */}
                <View style={styles.profileHeader}>
                    {avatarUrl ? (
                        <Image source={{ uri: avatarUrl }} style={styles.avatar} />
                    ) : (
                        <View style={[styles.avatar, styles.avatarPlaceholder]}>
                            <Ionicons name="person" size={40} color={Colors.textMuted} />
                        </View>
                    )}
                    <ThemedText variant="h2" weight="extrabold" align="center">
                        {fullName}
                    </ThemedText>
                    <ThemedText variant="muted" align="center">
                        {user.email}
                    </ThemedText>
                </View>

                {/* Links */}
                <View style={styles.linksCard}>
                    {links.map((link, i) => (
                        <TouchableOpacity
                            key={link.label}
                            style={[styles.linkRow, i < links.length - 1 && styles.linkBorder]}
                            onPress={() => {
                                if (link.route) {
                                    router.push(link.route as any);
                                } else {
                                    Linking.openURL(link.url);
                                }
                            }}
                            activeOpacity={0.7}
                        >
                            <Ionicons name={link.icon} size={20} color={Colors.primary} />
                            <ThemedText variant="body" style={{ flex: 1 }}>{link.label}</ThemedText>
                            <Ionicons name="chevron-forward" size={18} color={Colors.textMuted} />
                        </TouchableOpacity>
                    ))}
                </View>

                {/* Sign Out */}
                <TouchableOpacity style={styles.signOutBtn} onPress={signOut} activeOpacity={0.85}>
                    <Ionicons name="log-out-outline" size={20} color={Colors.accent} />
                    <ThemedText variant="body" weight="semibold" color={Colors.accent}>
                        Cerrar Sesión
                    </ThemedText>
                </TouchableOpacity>

                {/* Version */}
                <ThemedText variant="caption" align="center" style={{ marginTop: Spacing.xl }}>
                    Pista Inteligente v1.0.0 • Hecho con ❤️ en Chile
                </ThemedText>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loginContent: {
        padding: Spacing.xl,
        paddingBottom: Spacing.xxxl,
        alignItems: 'center',
    },
    loginHero: {
        alignItems: 'center',
        paddingVertical: Spacing.xxxl,
    },
    benefitsCard: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        padding: Spacing.xl,
        width: '100%',
        marginBottom: Spacing.xl,
    },
    benefitRow: {
        paddingVertical: Spacing.sm,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
    },
    googleBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.md,
        backgroundColor: '#4285F4',
        paddingVertical: Spacing.lg,
        paddingHorizontal: Spacing.xxl,
        borderRadius: BorderRadius.full,
        width: '100%',
        justifyContent: 'center',
        shadowColor: '#4285F4',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 6,
    },
    badgeRow: {
        marginTop: Spacing.lg,
        alignItems: 'center',
    },
    freeBadge: {
        backgroundColor: Colors.successBg,
        paddingVertical: Spacing.xs,
        paddingHorizontal: Spacing.lg,
        borderRadius: BorderRadius.full,
        borderWidth: 1,
        borderColor: Colors.success,
    },
    trustRow: {
        flexDirection: 'row',
        gap: Spacing.lg,
        marginTop: Spacing.lg,
    },
    content: {
        padding: Spacing.xl,
        paddingBottom: Spacing.xxxl,
    },
    profileHeader: {
        alignItems: 'center',
        paddingVertical: Spacing.xxl,
        gap: Spacing.sm,
    },
    avatar: {
        width: 80,
        height: 80,
        borderRadius: 40,
        marginBottom: Spacing.md,
    },
    avatarPlaceholder: {
        backgroundColor: Colors.bgCardSolid,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 2,
        borderColor: Colors.borderGlass,
    },
    linksCard: {
        backgroundColor: Colors.bgCardSolid,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        overflow: 'hidden',
    },
    linkRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.md,
        padding: Spacing.lg,
    },
    linkBorder: {
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
    },
    signOutBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: Spacing.sm,
        paddingVertical: Spacing.lg,
        marginTop: Spacing.xl,
        backgroundColor: Colors.accentMuted,
        borderRadius: BorderRadius.lg,
        borderWidth: 1,
        borderColor: Colors.accent,
    },
});
