"use client";

import { useEffect, useState } from 'react';

interface DetallePatron {
    fecha: string;
    hipodromo: string;
    nro_carrera: number;
    resultado: number[];
}

interface Patron {
    tipo: string;
    numeros: number[];
    veces: number;
    detalle: DetallePatron[];
}

export default function PatronesList() {
    const [patrones, setPatrones] = useState<Patron[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchPatrones = async () => {
            try {
                const res = await fetch('/api/analisis/patrones');
                if (!res.ok) throw new Error('Error al cargar patrones');
                const data = await res.json();
                setPatrones(data.patrones || []);
            } catch (err) {
                console.error(err);
                setError('No se pudieron cargar los patrones numéricos en este momento.');
            } finally {
                setLoading(false);
            }
        };

        fetchPatrones();
    }, []);

    if (loading) {
        return (
            <div className="glass-card text-center p-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-4"></div>
                <p className="text-gray-400">Analizando últimas 60 días de carreras...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="glass-card p-6 border-l-4 border-red-500">
                <p className="text-red-400">{error}</p>
            </div>
        );
    }

    if (patrones.length === 0) {
        return (
            <div className="glass-card p-6 text-center">
                <p className="text-gray-400">No se encontraron patrones numéricos repetidos recientemente.</p>
            </div>
        );
    }

    return (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {patrones.map((patron, idx) => (
                <div key={idx} className="glass-card p-6 relative overflow-hidden group hover:bg-white/5 transition-all">
                    {/* Badge Impacto */}
                    <div className="absolute top-4 right-4 bg-purple-500/20 text-purple-300 text-xs px-2 py-1 rounded-full font-bold">
                        {patron.veces} Repeticiones
                    </div>

                    <h3 className="text-xl font-bold text-white mb-2">{patron.tipo}</h3>

                    {/* Números Grandes */}
                    <div className="flex gap-2 my-4 justify-center">
                        {patron.numeros.map((num, i) => (
                            <div key={i} className="w-12 h-12 flex items-center justify-center rounded-full bg-gradient-to-br from-yellow-500 to-amber-700 text-white font-black text-xl shadow-lg border-2 border-yellow-300/30">
                                {num}
                            </div>
                        ))}
                    </div>

                    <p className="text-sm text-gray-300 mb-4 text-center">
                        La combinación <span className="text-yellow-400 font-bold">{patron.numeros.join('-')}</span> se ha repetido {patron.veces} veces.
                    </p>

                    {/* Detalle Historial */}
                    <div className="bg-black/20 rounded-lg p-3 text-xs space-y-2">
                        <p className="font-semibold text-gray-400 mb-1">Últimas apariciones:</p>
                        {patron.detalle.slice(0, 3).map((d, i) => (
                            <div key={i} className="flex justify-between items-center text-gray-300 border-b border-white/5 pb-1 last:border-0">
                                <span>{new Date(d.fecha).toLocaleDateString('es-CL', { day: 'numeric', month: 'short' })}</span>
                                <span className="truncate max-w-[120px]" title={d.hipodromo}>{d.hipodromo}</span>
                                <span className="bg-white/10 px-1.5 rounded">#{d.nro_carrera}</span>
                            </div>
                        ))}
                        {patron.detalle.length > 3 && (
                            <div className="text-center text-gray-500 italic">
                                (+{patron.detalle.length - 3} más)
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
