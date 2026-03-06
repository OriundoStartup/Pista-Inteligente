import { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import * as Linking from 'expo-linking';
import { supabase } from '../../lib/supabase';
import { ThemedText } from '../../components/ThemedText';
import { Colors } from '../../constants/Colors';
import { Spacing, BorderRadius } from '../../constants/Theme';

type CallbackStatus = 'loading' | 'success' | 'error';

/**
 * Parses OAuth tokens from a callback URL.
 *
 * Supabase sends tokens in either:
 *   - Hash fragment:  pistainteligente://auth/callback#access_token=...&refresh_token=...
 *   - Query params:   pistainteligente://auth/callback?access_token=...&refresh_token=...
 *
 * This function handles both cases.
 */
function extractTokens(url: string): { accessToken: string | null; refreshToken: string | null } {
    // Try hash fragment first (most common with Supabase PKCE/implicit)
    const hashIndex = url.indexOf('#');
    if (hashIndex !== -1) {
        const fragment = url.substring(hashIndex + 1);
        const params = new URLSearchParams(fragment);
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        if (accessToken && refreshToken) {
            return { accessToken, refreshToken };
        }
    }

    // Fallback to query params
    const queryIndex = url.indexOf('?');
    if (queryIndex !== -1) {
        const query = url.substring(queryIndex + 1);
        const params = new URLSearchParams(query);
        return {
            accessToken: params.get('access_token'),
            refreshToken: params.get('refresh_token'),
        };
    }

    return { accessToken: null, refreshToken: null };
}

/**
 * Auth callback screen — handles the OAuth redirect from Supabase/Google.
 *
 * Flow:
 * 1. User taps "Sign in with Google" → opens browser
 * 2. Google auth completes → redirects to pistainteligente://auth/callback#tokens
 * 3. This screen parses tokens → calls supabase.auth.setSession()
 * 4. On success → navigates to tabs. On error → shows retry UI.
 */
export default function AuthCallbackScreen() {
    const router = useRouter();
    const [status, setStatus] = useState<CallbackStatus>('loading');
    const [errorMessage, setErrorMessage] = useState<string>('');

    const handleDeepLink = async (url: string): Promise<void> => {
        try {
            console.log('[AuthCallback] Processing URL:', url.substring(0, 80) + '...');

            const { accessToken, refreshToken } = extractTokens(url);

            if (!accessToken || !refreshToken) {
                throw new Error(
                    'No se encontraron tokens en la URL de callback.\n' +
                    'Verifica que el Redirect URI esté configurado en Supabase.'
                );
            }

            const { error } = await supabase.auth.setSession({
                access_token: accessToken,
                refresh_token: refreshToken,
            });

            if (error) {
                throw new Error(error.message);
            }

            console.log('[AuthCallback] Session set successfully');
            setStatus('success');

            // Brief delay so the user sees the success state
            setTimeout(() => {
                router.replace('/(tabs)');
            }, 500);
        } catch (e: any) {
            console.error('[AuthCallback] Error:', e);
            setErrorMessage(e?.message || 'Error desconocido al procesar la autenticación.');
            setStatus('error');
        }
    };

    useEffect(() => {
        let isMounted = true;

        // Case 1: Cold start — app was closed, opened via deep link
        const checkInitialURL = async () => {
            const initialUrl = await Linking.getInitialURL();
            if (initialUrl && isMounted) {
                await handleDeepLink(initialUrl);
            } else if (isMounted) {
                // No URL — user navigated here directly (shouldn't happen)
                setErrorMessage('No se recibió URL de callback.');
                setStatus('error');
            }
        };

        checkInitialURL();

        // Case 2: App in background/foreground — receives deep link while running
        const subscription = Linking.addEventListener('url', (event) => {
            if (isMounted) {
                handleDeepLink(event.url);
            }
        });

        return () => {
            isMounted = false;
            subscription.remove();
        };
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // ─── Loading state ───
    if (status === 'loading') {
        return (
            <View style={styles.container}>
                <ActivityIndicator color={Colors.primary} size="large" />
                <ThemedText variant="muted" align="center" style={styles.text}>
                    Completando inicio de sesión...
                </ThemedText>
            </View>
        );
    }

    // ─── Error state ───
    if (status === 'error') {
        return (
            <View style={styles.container}>
                <ThemedText style={styles.icon}>❌</ThemedText>
                <ThemedText variant="h3" weight="semibold" align="center">
                    Error de autenticación
                </ThemedText>
                <ThemedText variant="muted" align="center" style={styles.text}>
                    {errorMessage}
                </ThemedText>
                <TouchableOpacity
                    style={styles.button}
                    onPress={() => router.replace('/(tabs)')}
                    activeOpacity={0.85}
                >
                    <ThemedText variant="body" weight="semibold" color="#fff">
                        ← Volver al inicio
                    </ThemedText>
                </TouchableOpacity>
            </View>
        );
    }

    // ─── Success state (brief flash before redirect) ───
    return (
        <View style={styles.container}>
            <ThemedText style={styles.icon}>✅</ThemedText>
            <ThemedText variant="h3" weight="semibold" align="center" color={Colors.success}>
                ¡Bienvenido!
            </ThemedText>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
        justifyContent: 'center',
        alignItems: 'center',
        padding: Spacing.xl,
        gap: Spacing.lg,
    },
    icon: {
        fontSize: 48,
        marginBottom: Spacing.sm,
    },
    text: {
        maxWidth: 300,
        lineHeight: 20,
    },
    button: {
        backgroundColor: Colors.primary,
        paddingVertical: Spacing.md,
        paddingHorizontal: Spacing.xxl,
        borderRadius: 50,
        marginTop: Spacing.lg,
        shadowColor: Colors.primary,
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.35,
        shadowRadius: 12,
        elevation: 6,
    },
});
