const { createClient } = require('@supabase/supabase-js');
const supabase = createClient('https://bxdxztbdsxyyvvavvtoo.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4ZHh6dGJkc3h5eXZ2YXZ2dG9vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgzNTQxNzcsImV4cCI6MjA4MzkzMDE3N30.J6hbXS2bAcqMy0ZGdnZw-HxDJMX4QtdUAyJuwgP7Bm4');
(async () => {
    try {
        const now = new Date();
        now.setHours(now.getHours() - 12);
        const todayStr = now.toISOString().split('T')[0];

        const pastDate = new Date();
        pastDate.setDate(pastDate.getDate() - 60);
        const fechaMin = pastDate.toISOString().split('T')[0];

        const { data: futureData } = await supabase.from('predicciones').select('carrera_id, numero_caballo, carreras!inner(jornadas!inner(fecha))').gte('carreras.jornadas.fecha', todayStr);
        const futureRaces = new Map();
        if (futureData) {
            futureData.forEach((row) => {
                const cId = row.carrera_id;
                if (!futureRaces.has(cId)) futureRaces.set(cId, new Set());
                futureRaces.get(cId).add(row.numero_caballo);
            });
        }
        
        console.log('Future Races:', futureRaces.size);

        const { data } = await supabase.from('participaciones').select('carrera_id, posicion, numero_mandil, carreras!inner(id, numero, jornadas!inner(fecha, hipodromos!inner(nombre)))').gte('carreras.jornadas.fecha', fechaMin).lte('posicion', 4).order('carrera_id').order('posicion');
        
        const races = {};
        data.forEach((row) => {
            const carreraId = row.carrera_id;
            if (!races[carreraId]) races[carreraId] = [];
            races[carreraId].push({ carrera_id: carreraId, posicion: row.posicion, numero: row.numero_mandil });
        });

        const patternCounts = {};
        Object.values(races).forEach(raceParticipants => {
            raceParticipants.sort((a, b) => a.posicion - b.posicion);
            const numeros = raceParticipants.map(p => p.numero);
            if (numeros.length < 2) return;
            const quinelaSig = [...numeros.slice(0, 2)].sort((a, b) => a - b).join('-');
            const quinelaKey = 'Q:' + quinelaSig;
            if (!patternCounts[quinelaKey]) patternCounts[quinelaKey] = { tipo: 'Quinela', numeros: numeros.slice(0, 2).sort((a, b) => a - b), veces: 0 };
            patternCounts[quinelaKey].veces++;
        });

        const beforeFilter = Object.values(patternCounts).filter(p => p.veces === 2).length;
        console.log('Patterns exactly 2 times (Before Future Filter):', beforeFilter);

        const afterFilter = Object.values(patternCounts).filter(p => {
            if (p.veces !== 2) return false;
            const pSet = new Set(p.numeros);
            for (const raceHorses of futureRaces.values()) {
                let match = true;
                for (const num of pSet) {
                    if (!raceHorses.has(num)) { match = false; break; }
                }
                if (match) return true;
            }
            return false;
        }).length;
        console.log('Patterns exactly 2 times (After Future Filter):', afterFilter);
    } catch (e) {
        console.error(e);
    }
})();
