import LoginWithGoogleButton from '@/components/LoginWithGoogleButton'
import type { Metadata, Viewport } from 'next'

export const metadata: Metadata = {
    title: 'Regístrate Gratis | Pista Inteligente - Predicciones Hípicas con IA',
    description: 'Accede GRATIS a predicciones profesionales de carreras hípicas potenciadas por Inteligencia Artificial. Estadísticas en tiempo real, chatbot experto y más.',
}

export const viewport: Viewport = {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
}

export default function LoginPage() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#0f172a] text-white p-4 sm:p-6 md:p-8 relative overflow-hidden">
            {/* Background Gradients - Enhanced */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-[-15%] left-[-15%] w-[50%] h-[50%] rounded-full bg-purple-600/25 blur-[120px]" />
                <div className="absolute bottom-[-15%] right-[-15%] w-[50%] h-[50%] rounded-full bg-blue-600/25 blur-[120px]" />
                <div className="absolute top-[40%] left-[30%] w-[30%] h-[30%] rounded-full bg-cyan-500/10 blur-[80px]" />
            </div>

            <div className="relative z-10 w-full max-w-md px-2">
                {/* Main Card */}
                <div className="login-card bg-white/5 backdrop-blur-xl border border-white/10 p-6 sm:p-8 rounded-3xl shadow-2xl">

                    {/* FREE Badge */}
                    <div className="text-center mb-5 login-card-delay-1">
                        <span className="free-badge">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            100% GRATIS
                        </span>
                    </div>

                    {/* Header */}
                    <div className="text-center mb-6 login-card-delay-1">
                        <h1 className="text-2xl sm:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 mb-3">
                            🏇 Pista Inteligente
                        </h1>
                        <p className="text-gray-300 text-sm sm:text-base leading-relaxed">
                            Únete a la comunidad de apostadores que <strong className="text-white">ganan con datos</strong>, no con suerte.
                        </p>
                    </div>

                    {/* Benefits List */}
                    <div className="space-y-3 mb-6 login-card-delay-2">
                        <div className="benefit-item">
                            <span className="benefit-icon">🤖</span>
                            <div>
                                <p className="text-sm font-medium text-white">Predicciones con IA</p>
                                <p className="text-xs text-gray-400">Algoritmos que analizan miles de carreras</p>
                            </div>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">📊</span>
                            <div>
                                <p className="text-sm font-medium text-white">Estadísticas en Tiempo Real</p>
                                <p className="text-xs text-gray-400">Datos de jinetes, caballos y pistas actualizados</p>
                            </div>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">💬</span>
                            <div>
                                <p className="text-sm font-medium text-white">Chatbot Experto 24/7</p>
                                <p className="text-xs text-gray-400">Pregúntale cualquier duda sobre carreras</p>
                            </div>
                        </div>
                    </div>

                    {/* Mini Stats */}
                    <div className="stats-mini mb-6 login-card-delay-2">
                        <div className="stat-mini-item">
                            <div className="stat-mini-number">+2,500</div>
                            <div className="stat-mini-label">Usuarios activos</div>
                        </div>
                        <div className="stat-mini-item">
                            <div className="stat-mini-number">85%</div>
                            <div className="stat-mini-label">Precisión promedio</div>
                        </div>
                    </div>

                    {/* Google Button */}
                    <div className="login-card-delay-3">
                        <LoginWithGoogleButton />
                    </div>

                    {/* Security Text */}
                    <div className="security-text login-card-delay-3">
                        <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                        </svg>
                        <span>Tus datos están protegidos por Google</span>
                    </div>

                    {/* Live Races Indicator */}
                    <div className="mt-5 flex justify-center login-card-delay-3">
                        <div className="live-indicator">
                            <span className="live-dot"></span>
                            <span>Carreras en vivo hoy</span>
                        </div>
                    </div>
                </div>

                {/* Trust Badges Below Card */}
                <div className="mt-4 flex flex-wrap justify-center gap-3 login-card-delay-3">
                    <div className="trust-badge">
                        <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-xs text-gray-400">Sin spam</span>
                    </div>
                    <div className="trust-badge">
                        <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-xs text-gray-400">Cancela cuando quieras</span>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-6 text-center">
                    <p className="text-xs text-gray-500">
                        Al registrarte aceptas nuestros términos de servicio
                    </p>
                </div>
            </div>
        </div>
    )
}
