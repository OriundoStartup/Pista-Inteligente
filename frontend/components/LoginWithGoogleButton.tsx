'use client'

import { createClient } from '../utils/supabase/client'

export default function LoginWithGoogleButton() {
    const handleLogin = async () => {
        const supabase = createClient()

        // Determinar la URL de redirección
        // En producción, usar la URL de Vercel; en desarrollo, usar localhost
        const getRedirectUrl = () => {
            if (typeof window === 'undefined') return '/auth/callback'

            // Si estamos en localhost, usar localhost
            if (window.location.hostname === 'localhost') {
                return `${window.location.origin}/auth/callback`
            }

            // En producción, usar la URL actual del sitio
            return `${window.location.origin}/auth/callback`
        }

        const redirectUrl = getRedirectUrl()

        await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: redirectUrl,
            },
        })
    }

    return (
        <div className="space-y-2">
            <button
                onClick={handleLogin}
                className="google-btn-enhanced flex items-center justify-center gap-3 bg-white text-gray-700 font-semibold px-6 py-4 rounded-xl shadow-lg hover:shadow-xl active:scale-[0.98] transition-all duration-300 w-full touch-manipulation group"
            >
                {/* Google SVG Icon */}
                <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                    <path
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        fill="#4285F4"
                    />
                    <path
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        fill="#34A853"
                    />
                    <path
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z"
                        fill="#FBBC05"
                    />
                    <path
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                        fill="#EA4335"
                    />
                </svg>
                <span className="text-base">Registrarme con Google</span>
                <svg className="w-4 h-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
            </button>
            <p className="text-center text-xs text-gray-500">
                Solo toma 3 segundos • Sin tarjeta de crédito
            </p>
        </div>
    )
}
