import { useState, useEffect, useRef } from 'react';
import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { supabase } from '../lib/supabase';

const PUSH_TOKEN_KEY = 'push_token';

// Configure notification behavior (native only)
if (Platform.OS !== 'web') {
    Notifications.setNotificationHandler({
        handleNotification: async () => ({
            shouldShowAlert: true,
            shouldPlaySound: true,
            shouldSetBadge: true,
            shouldShowBanner: true,
            shouldShowList: true,
        }),
    });
}

/**
 * Registers the device for push notifications.
 * Returns the Expo push token or null if registration fails.
 */
export async function registerForPushNotificationsAsync(): Promise<string | null> {
    if (Platform.OS === 'web') return null;

    try {
        // Check existing permissions
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        // Request permission if not already granted
        if (existingStatus !== 'granted') {
            const { status } = await Notifications.requestPermissionsAsync();
            finalStatus = status;
        }

        if (finalStatus !== 'granted') {
            console.log('[Notifications] Permission not granted');
            return null;
        }

        // Get token — requires a physical device
        const tokenData = await Notifications.getExpoPushTokenAsync({
            projectId: Device.default.expoConfig?.extra?.eas?.projectId || undefined,
        });

        const token = tokenData.data;

        // Save locally
        await AsyncStorage.setItem(PUSH_TOKEN_KEY, token);

        // Android notification channel
        if (Platform.OS === 'android') {
            await Notifications.setNotificationChannelAsync('default', {
                name: 'Pista Inteligente',
                importance: Notifications.AndroidImportance.HIGH,
                vibrationPattern: [0, 250, 250, 250],
                lightColor: '#8b5cf6',
            });
        }

        return token;
    } catch (error) {
        console.error('[Notifications] Registration error:', error);
        return null;
    }
}

/**
 * Hook to manage push notifications lifecycle.
 * Registers for push, listens for incoming notifications,
 * and handles notification responses (taps).
 */
export function useNotifications() {
    const [expoPushToken, setExpoPushToken] = useState<string | null>(null);
    const [notification, setNotification] =
        useState<Notifications.Notification | null>(null);
    const notificationListener = useRef<Notifications.EventSubscription | undefined>(undefined);
    const responseListener = useRef<Notifications.EventSubscription | undefined>(undefined);

    useEffect(() => {
        // Skip all notification work on web (expo-notifications is native-only)
        if (Platform.OS === 'web') return;

        // Register on mount
        registerForPushNotificationsAsync().then((token) => {
            if (token) {
                setExpoPushToken(token);
                savePushTokenToSupabase(token);
            }
        });

        // Listen for incoming notifications (while app is open)
        notificationListener.current =
            Notifications.addNotificationReceivedListener((notification: Notifications.Notification) => {
                setNotification(notification);
            });

        // Listen for notification taps
        responseListener.current =
            Notifications.addNotificationResponseReceivedListener((response: Notifications.NotificationResponse) => {
                const data = response.notification.request.content.data;
                // Navigation based on notification data could be added here
                console.log('[Notifications] Tapped:', data);
            });

        return () => {
            if (notificationListener.current) {
                notificationListener.current.remove();
            }
            if (responseListener.current) {
                responseListener.current.remove();
            }
        };
    }, []);

    return { expoPushToken, notification };
}

/**
 * Save push token to Supabase for server-side notifications.
 * Uses upsert on (user_id, platform) to avoid duplicates.
 *
 * Error handling:
 * - 42P01 (table not found) → clear console.warn with SQL instructions
 * - Other errors → logged but never crash the app
 * - Token is ALWAYS saved in AsyncStorage regardless of Supabase result
 */
async function savePushTokenToSupabase(token: string) {
    try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
            // Not authenticated — token is still saved locally in AsyncStorage
            return;
        }

        const { error } = await supabase
            .from('push_tokens')
            .upsert(
                {
                    user_id: user.id,
                    token,
                    platform: Platform.OS,
                    updated_at: new Date().toISOString(),
                },
                { onConflict: 'user_id,platform' }
            );

        if (error) {
            // Check for "relation does not exist" (PostgreSQL error 42P01)
            const isTableMissing =
                error.code === '42P01' ||
                error.message?.includes('relation') && error.message?.includes('does not exist');

            if (isTableMissing) {
                console.warn(
                    '[Notifications] ⚠️ La tabla "push_tokens" no existe en Supabase.\n' +
                    '  Las push notifications server-side NO funcionarán hasta que la crees.\n' +
                    '  → Ejecuta el SQL en: /mobile/docs/SUPABASE_SETUP.sql\n' +
                    '  → O copia y pégalo en: Supabase Dashboard → SQL Editor\n' +
                    '  El token se guardó localmente en AsyncStorage.'
                );
            } else {
                console.warn('[Notifications] Error al guardar token en Supabase:', error.message);
            }
        } else {
            console.log('[Notifications] Token guardado en Supabase ✅');
        }
    } catch (err: any) {
        // Never crash the app for push token errors
        console.warn('[Notifications] Error inesperado al guardar token:', err?.message || err);
    }
}

