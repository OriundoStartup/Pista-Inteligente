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
                className={`fixed bottom-4 left-4 z-50 w-full max-w-sm rounded-2xl shadow-2xl transition-all duration-500 transform translate-y-0 backdrop-blur-md border ${isMegaJackpot
                        ? "bg-yellow-900/40 border-yellow-500/50 text-yellow-100"
                        : "bg-[#0f172a]/90 border-white/10 text-slate-100"
                    }`}
                style={{
                    boxShadow: isMegaJackpot ? '0 0 40px rgba(234, 179, 8, 0.2)' : '0 10px 30px -10px rgba(0,0,0,0.5)'
                }}
            >
                <div className="p-5 relative">
                    <button
                        onClick={() => setIsVisible(false)}
                        className="absolute top-2 right-2 p-1.5 hover:bg-white/10 rounded-full transition-colors text-white/60 hover:text-white"
                        aria-label="Cerrar alerta"
                    >
                        <X size={16} />
                    </button>

                    <div className="flex items-start gap-4">
                        <div
                            className={`p-3 rounded-xl shadow-lg ${isMegaJackpot
                                    ? "bg-gradient-to-br from-yellow-500 to-orange-600 text-white animate-pulse"
                                    : "bg-gradient-to-br from-violet-600 to-indigo-600 text-white"
                                }`}
                        >
                            {isMegaJackpot ? <Flame size={28} /> : <DollarSign size={28} />}
                        </div>

                        <div className="flex-1">
                            <h3 className={`font-bold text-lg leading-tight mb-1 ${isMegaJackpot ? "text-yellow-200" : "text-violet-200"}`}>
                                {isMegaJackpot ? "¡MEGA POZO VACANTE!" : "Pozo Acumulado"}
                            </h3>

                            <p className="text-3xl font-black tracking-tight text-white drop-shadow-sm">
                                {formatMoney(topPozo.monto_estimado)}
                            </p>

                            <div className="mt-3 flex flex-col gap-1.5 text-sm">
                                <div className="flex items-center gap-2 text-white/80">
                                    <span className="bg-white/5 px-2 py-0.5 rounded text-xs font-medium border border-white/10">📍 {topPozo.hipodromo}</span>
                                </div>
                                <div className="flex items-center gap-2 text-white/90 font-medium">
                                    🎰 {topPozo.tipo_apuesta}
                                </div>
                                {topPozo.mensaje_marketing && (
                                    <span className="text-xs italic text-white/60 mt-0.5 block">
                                        "{topPozo.mensaje_marketing}"
                                    </span>
                                )}
                            </div>

                            {/* Botón de Jugada Inteligente */}
                            {topPozo.ticket_sugerido && (
                                <button
                                    onClick={handleOpenTicket}
                                    className={`mt-4 w-full py-2 px-4 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all hover:scale-[1.02] shadow-lg ${isMegaJackpot
                                            ? "bg-gradient-to-r from-yellow-400 to-yellow-600 text-black hover:shadow-yellow-500/30"
                                            : "bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:shadow-cyan-500/30"
                                        }`}
                                >
                                    <Lightbulb size={16} strokeWidth={2.5} />
                                    Ver Jugada Inteligente
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Shimmer effect for mega jackpot */}
                {isMegaJackpot && (
                    <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden rounded-2xl">
                        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-[shimmer_3s_infinite]"></div>
                    </div>
                )}
            </div>

            {/* Modal de Ticket Sugerido */}
            {showModal && selectedTicket && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
                    <div className="bg-[#1e293b] border border-white/10 rounded-2xl shadow-2xl max-w-md w-full overflow-hidden relative">

                        {/* Background Decoration */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2"></div>

                        {/* Header del Modal */}
                        <div className="bg-[#0f172a] p-5 border-b border-white/5 flex justify-between items-center relative z-10">
                            <div className="flex items-center gap-3">
                                <div className="bg-yellow-500/20 p-2 rounded-lg text-yellow-400">
                                    <Ticket size={20} />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white text-lg leading-none">{selectedTicket.titulo}</h3>
                                    <span className="text-xs text-slate-400">Sugerencia basada en IA</span>
                                </div>
                            </div>
                            <button
                                onClick={() => setShowModal(false)}
                                className="p-2 hover:bg-white/5 rounded-full transition-colors text-slate-400 hover:text-white"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* Contenido del Modal */}
                        <div className="p-6 relative z-10">
                            <div className="space-y-4">
                                {selectedTicket.detalle.map((item, idx) => (
                                    <div key={idx} className="flex gap-4 items-start bg-white/5 p-3 rounded-xl border border-white/5">
                                        <div className="bg-violet-600/20 text-violet-300 rounded-lg px-2.5 py-1.5 font-bold text-sm min-w-[3.5rem] text-center flex flex-col items-center justify-center">
                                            <span className="text-[10px] uppercase opacity-70">Carrera</span>
                                            <span className="text-lg leading-none">{item.carrera}</span>
                                        </div>
                                        <div className="flex-1">
                                            {item.caballos.map((cab, cIdx) => (
                                                <div key={cIdx} className="text-slate-200 font-medium mb-1.5 last:mb-0 flex items-center gap-2">
                                                    <span className="text-yellow-500">Video</span> {/* Using a fake icon concept or just simple unicode */}
                                                    <span>🐴 {cab}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-6 flex justify-between items-center bg-black/20 p-4 rounded-xl border border-white/5">
                                <div className="flex flex-col">
                                    <span className="text-slate-400 text-xs uppercase font-bold tracking-wider">Costo Estimado</span>
                                    <span className="text-white font-bold text-xl">{formatMoney(selectedTicket.costo_estimado)}</span>
                                </div>
                                <div className="text-right">
                                    <span className="text-slate-400 text-xs uppercase font-bold tracking-wider block">Combinaciones</span>
                                    <span className="text-white font-medium">{selectedTicket.combinaciones}</span>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-[#0f172a] border-t border-white/5 text-center">
                            <button
                                onClick={() => setShowModal(false)}
                                className="text-violet-400 font-semibold text-sm hover:text-violet-300 transition-colors"
                            >
                                Cerrar ventana
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
