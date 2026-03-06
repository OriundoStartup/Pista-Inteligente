import { useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import { Session, User, AuthChangeEvent } from '@supabase/supabase-js';
import * as WebBrowser from 'expo-web-browser';
import * as AuthSession from 'expo-auth-session';
import { Alert } from 'react-native';

// Completes the web browser auth session if one was pending
WebBrowser.maybeCompleteAuthSession();

interface UseAuthResult {
    user: User | null;
    session: Session | null;
    isLoading: boolean;
    signInWithGoogle: () => Promise<void>;
    signOut: () => Promise<void>;
}

/**
 * Authentication hook for Supabase + Google OAuth.
 *
 * - Manages session state and auth state changes
 * - Handles Google OAuth via expo-web-browser
 * - Exports `isLoading` for UI loading indicators
 * - Cleans up auth listener on unmount
 */
export function useAuth(): UseAuthResult {
    const [session, setSession] = useState<Session | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // 1. Fetch the existing session (persisted in AsyncStorage)
        supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
            setSession(currentSession);
            setUser(currentSession?.user ?? null);
            setIsLoading(false);
        });

        // 2. Subscribe to auth state changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (event: AuthChangeEvent, newSession: Session | null) => {
                console.log('[useAuth] Auth event:', event);
                setSession(newSession);
                setUser(newSession?.user ?? null);

                // Stop loading on any auth event
                setIsLoading(false);
            }
        );

        // 3. Cleanup: unsubscribe on unmount
        return () => {
            subscription.unsubscribe();
        };
    }, []);

    /**
     * Initiates Google OAuth flow.
     *
     * Flow:
     * 1. Request OAuth URL from Supabase (skipBrowserRedirect: true)
     * 2. Open in-app browser via expo-web-browser
     * 3. Browser redirects to pistainteligente://auth/callback#tokens
     * 4. auth/callback.tsx handles the token parsing and session setting
     * 5. onAuthStateChange fires → this hook updates session/user
     */
    const signInWithGoogle = useCallback(async () => {
        try {
            setIsLoading(true);

            const redirectUrl = AuthSession.makeRedirectUri({
                scheme: 'pistainteligente',
                path: 'auth/callback',
            });

            console.log('[useAuth] Redirect URL:', redirectUrl);

            const { data, error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: redirectUrl,
                    skipBrowserRedirect: true,
                },
            });

            if (error) throw error;

            if (data?.url) {
                const result = await WebBrowser.openAuthSessionAsync(
                    data.url,
                    redirectUrl
                );

                if (result.type === 'success' && result.url) {
                    // Token parsing happens in auth/callback.tsx
                    // The deep link handler there will call setSession
                    // which triggers onAuthStateChange above.
                    console.log('[useAuth] Browser returned successfully');
                } else if (result.type === 'cancel') {
                    console.log('[useAuth] User cancelled auth');
                    setIsLoading(false);
                }
            }
        } catch (e: any) {
            console.error('[useAuth] Sign in error:', e);
            Alert.alert(
                'Error de autenticación',
                e?.message || 'No se pudo iniciar sesión con Google.'
            );
            setIsLoading(false);
        }
    }, []);

    /**
     * Signs the user out and clears the session.
     */
    const signOut = useCallback(async () => {
        try {
            const { error } = await supabase.auth.signOut();
            if (error) throw error;

            setSession(null);
            setUser(null);
        } catch (e: any) {
            console.error('[useAuth] Sign out error:', e);
            Alert.alert(
                'Error',
                e?.message || 'No se pudo cerrar sesión.'
            );
        }
    }, []);

    return { user, session, isLoading, signInWithGoogle, signOut };
}
