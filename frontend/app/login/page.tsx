import LoginWithGoogleButton from '@/components/LoginWithGoogleButton'

export default function LoginPage() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-[#0f172a] text-white p-4 relative overflow-hidden">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[100px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/20 blur-[100px]" />
            </div>

            <div className="relative z-10 w-full max-w-sm">
                <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
                            Pista Inteligente
                        </h1>
                        <p className="text-gray-400 text-sm">
                            Inicia sesión para acceder a las predicciones y estadísticas.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <LoginWithGoogleButton />
                    </div>

                    <div className="mt-8 text-center">
                        <p className="text-xs text-gray-500">
                            Versión 4.0 - Fase 1
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
