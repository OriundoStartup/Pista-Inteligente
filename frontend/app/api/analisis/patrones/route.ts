import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic'; // No caching, real-time analysis

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

interface Participation {
    carrera_id: number;
    posicion: number;
    numero: number; // Mandil
    hipodromo: string;
    fecha: string;
    nro_carrera: number;
}

interface Pattern {
    tipo: string;
    numeros: number[];
    veces: number;
    detalle: {
        fecha: string;
        hipodromo: string;
        nro_carrera: number;
        resultado: number[];
    }[];
}

export async function GET() {
    try {
        // 1. Calculate date 60 days ago
        const today = new Date();
        const pastDate = new Date();
        pastDate.setDate(today.getDate() - 60);
        const fechaMin = pastDate.toISOString().split('T')[0];
        const todayStr = new Date().toISOString().split('T')[0];

        // 2a. Fetch Future Program (Predicciones for today/tomorrow) to check availability
        const { data: futureData, error: futureError } = await supabase
            .from('predicciones')
            .select(`
                carrera_id,
                numero_caballo,
                carreras!inner (
                    id,
                    jornadas!inner (
                        fecha
                    )
                )
            `)
            .gte('carreras.jornadas.fecha', todayStr);

        const futureRaces = new Map<number, Set<number>>();
        if (futureData) {
            futureData.forEach((row: any) => {
                const cId = row.carrera_id;
                if (!futureRaces.has(cId)) futureRaces.set(cId, new Set());
                futureRaces.get(cId)?.add(row.numero_caballo);
            });
        }

        // 2b. Fetch results from Supabase
        const { data, error } = await supabase
            .from('participaciones')
            .select(`
                carrera_id,
                posicion,
                numero_mandil,
                carreras!inner (
                    id,
                    numero,
                    jornadas!inner (
                        fecha,
                        hipodromos!inner (
                            nombre
                        )
                    )
                )
            `)
            .gte('carreras.jornadas.fecha', fechaMin)
            .lte('posicion', 4) // Only interested in top 4
            .order('carrera_id', { ascending: true })
            .order('posicion', { ascending: true });

        if (error) {
            console.error('Supabase Error:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        if (!data || data.length === 0) {
            return NextResponse.json({ patrones: [] });
        }

        // 3. Process Data
        // Group by Race
        const races: { [key: number]: Participation[] } = {};

        data.forEach((row: any) => {
            const carreraId = row.carrera_id;
            if (!races[carreraId]) {
                races[carreraId] = [];
            }
            // Normalize data structure
            races[carreraId].push({
                carrera_id: carreraId,
                posicion: row.posicion,
                numero: row.numero_mandil,
                hipodromo: row.carreras.jornadas.hipodromos.nombre,
                fecha: row.carreras.jornadas.fecha,
                nro_carrera: row.carreras.numero
            });
        });

        // 4. Find Patterns
        const patternCounts: { [key: string]: Pattern } = {};

        Object.values(races).forEach(raceParticipants => {
            // Sort by position to ensure order (1st, 2nd, 3rd, 4th)
            raceParticipants.sort((a, b) => a.posicion - b.posicion);

            const numeros = raceParticipants.map(p => p.numero);

            // Need at least 2 for Quinela
            if (numeros.length < 2) return;

            const baseInfo = {
                fecha: raceParticipants[0].fecha,
                hipodromo: raceParticipants[0].hipodromo,
                nro_carrera: raceParticipants[0].nro_carrera,
                resultado: numeros
            };

            // Quinela (First 2)
            const quinelaSig = [...numeros.slice(0, 2)].sort((a, b) => a - b).join('-');
            const quinelaKey = `Q:${quinelaSig}`;

            if (!patternCounts[quinelaKey]) {
                patternCounts[quinelaKey] = { tipo: 'Quinela (2 Números)', numeros: numeros.slice(0, 2).sort((a, b) => a - b), veces: 0, detalle: [] };
            }
            patternCounts[quinelaKey].veces++;
            patternCounts[quinelaKey].detalle.push(baseInfo);

            // Trifecta (First 3)
            if (numeros.length >= 3) {
                const trifectaSig = [...numeros.slice(0, 3)].sort((a, b) => a - b).join('-');
                const trifectaKey = `T:${trifectaSig}`;
                if (!patternCounts[trifectaKey]) {
                    patternCounts[trifectaKey] = { tipo: 'Trifecta (3 Números)', numeros: numeros.slice(0, 3).sort((a, b) => a - b), veces: 0, detalle: [] };
                }
                patternCounts[trifectaKey].veces++;
                patternCounts[trifectaKey].detalle.push(baseInfo);
            }

            // Superfecta (First 4)
            if (numeros.length >= 4) {
                const superSig = [...numeros.slice(0, 4)].sort((a, b) => a - b).join('-');
                const superKey = `S:${superSig}`;
                if (!patternCounts[superKey]) {
                    patternCounts[superKey] = { tipo: 'Superfecta (4 Números)', numeros: numeros.slice(0, 4).sort((a, b) => a - b), veces: 0, detalle: [] };
                }
                patternCounts[superKey].veces++;
                patternCounts[superKey].detalle.push(baseInfo);
            }
        });

        // 5. Filter and Sort
        const result = Object.values(patternCounts)
            .filter(p => {
                // Condition 1: Repeated exactly twice (as per user request: "solo las que se han repetido dos veces")
                if (p.veces !== 2) return false;

                // Condition 2: Must likely repeat active ("que se pueden repetir por una 3 vez")
                // Check if this pattern is a SUBSET of any FUTURE race
                // Optimization: Convert pattern numbers to Set once
                const pSet = new Set(p.numeros);
                
                // Iterate all future races
                for (const raceHorses of futureRaces.values()) {
                    let match = true;
                    for (const num of pSet) {
                        if (!raceHorses.has(num)) {
                            match = false;
                            break;
                        }
                    }
                    if (match) return true; // Found a race where it can happen!
                }
                return false;
            }) 
            .sort((a, b) => b.veces - a.veces); // Most frequent first (though all are 2 now)

        // Limit results to prevent lag
        return NextResponse.json({ patrones: result.slice(0, 50) });

    } catch (error: any) {
        console.error('API Error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
