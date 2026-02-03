"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/utils/supabase/client";
import { AlertCircle, Flame, DollarSign, X } from "lucide-react";

type Pozo = {
    id: number;
    hipodromo: string;
    fecha_evento: string;
    nro_carrera: number;
    tipo_apuesta: string;
    monto_estimado: number;
    mensaje_marketing: string | null;
};

export default function JackpotAlert() {
    const [pozos, setPozos] = useState<Pozo[]>([]);
    const [isVisible, setIsVisible] = useState(true);
    const supabase = createClient();

    useEffect(() => {
        async function fetchPozos() {
            const today = new Date().toISOString().split("T")[0];

            const { data, error } = await supabase
                .from("pozos_alertas")
                .select("*")
                .gte("fecha_evento", today)
                .order("monto_estimado", { ascending: false });

            if (error) {
                console.error("Error fetching jackpots:", error);
            } else if (data) {
                setPozos(data);
            }
        }

        fetchPozos();
    }, []);

    if (!isVisible || pozos.length === 0) return null;

    // Show the highest jackpot
    const topPozo = pozos[0];
    const isMegaJackpot = topPozo.monto_estimado >= 50000000; // 50M

    const formatMoney = (amount: number) => {
        return new Intl.NumberFormat("es-CL", {
            style: "currency",
            currency: "CLP",
            maximumFractionDigits: 0,
        }).format(amount);
    };

    return (
        <div
            className={`fixed bottom-4 right-4 z-50 w-full max-w-sm rounded-lg shadow-xl transition-all duration-500 transform translate-y-0 ${isMegaJackpot
                    ? "bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500 text-black border-2 border-yellow-200"
                    : "bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100"
                }`}
        >
            <div className="p-4 relative">
                <button
                    onClick={() => setIsVisible(false)}
                    className="absolute top-2 right-2 p-1 hover:bg-black/10 rounded-full transition-colors"
                    aria-label="Cerrar alerta"
                >
                    <X size={16} />
                </button>

                <div className="flex items-start gap-3">
                    <div
                        className={`p-2 rounded-full ${isMegaJackpot ? "bg-red-600 text-white animate-pulse" : "bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300"
                            }`}
                    >
                        {isMegaJackpot ? <Flame size={24} /> : <DollarSign size={24} />}
                    </div>

                    <div className="flex-1">
                        <h3 className={`font-bold text-lg leading-tight ${isMegaJackpot ? "text-red-900" : ""}`}>
                            {isMegaJackpot ? "¡MEGA POZO VACANTE!" : "Posible Pozo Acumulado"}
                        </h3>

                        <p className={`mt-1 text-2xl font-black tracking-tight ${isMegaJackpot ? "text-black" : "text-green-600 dark:text-green-400"}`}>
                            {formatMoney(topPozo.monto_estimado)}
                        </p>

                        <div className="mt-2 flex flex-col gap-1 text-sm opacity-90">
                            <span className="font-semibold flex items-center gap-1">
                                📍 {topPozo.hipodromo}
                            </span>
                            <span className="flex items-center gap-1">
                                🎰 {topPozo.tipo_apuesta}
                            </span>
                            {topPozo.mensaje_marketing && (
                                <span className="italic text-xs mt-1 block">
                                    "{topPozo.mensaje_marketing}"
                                </span>
                            )}
                        </div>

                        <p className="mt-3 text-xs opacity-75">
                            Solo para la jornada de hoy/próxima.
                        </p>
                    </div>
                </div>
            </div>

            {/* Shimmer effect for mega jackpot */}
            {isMegaJackpot && (
                <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden rounded-lg">
                    <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                </div>
            )}
        </div>
    );
}
