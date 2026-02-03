"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/utils/supabase/client";
import { AlertCircle, Flame, DollarSign, X, Lightbulb, Ticket } from "lucide-react";

type TicketSugerido = {
    titulo: string;
    detalle: {
        carrera: number;
        caballos: string[];
    }[];
    combinaciones: number;
    costo_estimado: number;
};

type Pozo = {
    id: number;
    hipodromo: string;
    fecha_evento: string;
    nro_carrera: number;
    tipo_apuesta: string;
    monto_estimado: number;
    mensaje_marketing: string | null;
    ticket_sugerido: TicketSugerido | null;
};

export default function JackpotAlert() {
    const [pozos, setPozos] = useState<Pozo[]>([]);
    const [isVisible, setIsVisible] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [selectedTicket, setSelectedTicket] = useState<TicketSugerido | null>(null);

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

    const handleOpenTicket = () => {
        if (topPozo.ticket_sugerido) {
            setSelectedTicket(topPozo.ticket_sugerido);
            setShowModal(true);
        }
    };

    return (
        <>
            <div
                className={`fixed bottom-4 left-4 z-50 w-full max-w-sm rounded-lg shadow-xl transition-all duration-500 transform translate-y-0 ${isMegaJackpot
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

                            {/* Botón de Jugada Inteligente */}
                            {topPozo.ticket_sugerido && (
                                <button
                                    onClick={handleOpenTicket}
                                    className={`mt-3 w-full py-1.5 px-3 rounded text-sm font-bold flex items-center justify-center gap-2 transition-transform hover:scale-105 ${isMegaJackpot
                                            ? "bg-black text-yellow-400 hover:bg-zinc-800"
                                            : "bg-blue-600 text-white hover:bg-blue-700"
                                        }`}
                                >
                                    <Lightbulb size={16} />
                                    Ver Jugada IA
                                </button>
                            )}

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

            {/* Modal de Ticket Sugerido */}
            {showModal && selectedTicket && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-md w-full overflow-hidden border border-zinc-200 dark:border-zinc-700">
                        {/* Header del Modal */}
                        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4 text-white flex justify-between items-center">
                            <div className="flex items-center gap-2">
                                <Ticket className="text-yellow-300" />
                                <h3 className="font-bold text-lg">{selectedTicket.titulo}</h3>
                            </div>
                            <button
                                onClick={() => setShowModal(false)}
                                className="p-1 hover:bg-white/20 rounded-full transition-colors"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* Contenido del Modal */}
                        <div className="p-6">
                            <p className="text-sm text-zinc-500 mb-4 text-center">
                                Basado en nuestros modelos de IA (LightGBM + XGBoost)
                            </p>

                            <div className="space-y-4">
                                {selectedTicket.detalle.map((item, idx) => (
                                    <div key={idx} className="flex gap-3 items-start border-b border-zinc-100 dark:border-zinc-800 pb-3 last:border-0">
                                        <div className="bg-zinc-100 dark:bg-zinc-800 rounded px-2 py-1 font-bold text-sm min-w-[5rem] text-center">
                                            Carrera {item.carrera}
                                        </div>
                                        <div className="flex-1">
                                            {item.caballos.map((cab, cIdx) => (
                                                <div key={cIdx} className="text-sm font-medium mb-1 flex items-center gap-1">
                                                    🐴 {cab}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-6 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex justify-between items-center text-sm">
                                <span className="text-zinc-500">Costo Estimado:</span>
                                <span className="font-bold text-lg">{formatMoney(selectedTicket.costo_estimado)}</span>
                            </div>
                        </div>

                        <div className="p-4 bg-zinc-50 dark:bg-zinc-950/50 text-center">
                            <button
                                onClick={() => setShowModal(false)}
                                className="text-indigo-600 font-semibold text-sm hover:underline"
                            >
                                Cerrar y volver
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
