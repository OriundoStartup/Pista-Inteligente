const { createClient } = require('@supabase/supabase-js');
const supabase = createClient('https://bxdxztbdsxyyvvavvtoo.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4ZHh6dGJkc3h5eXZ2YXZ2dG9vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgzNTQxNzcsImV4cCI6MjA4MzkzMDE3N30.J6hbXS2bAcqMy0ZGdnZw-HxDJMX4QtdUAyJuwgP7Bm4');
(async () => {
    const todayStr = new Date().toISOString().split('T')[0];
    const { data: future1 } = await supabase.from('predicciones').select('carrera_id, carreras!inner(jornadas!inner(fecha))').gte('carreras.jornadas.fecha', todayStr);
    console.log('UTC todayStr:', todayStr, '=>', future1?.length || 0);

    const chileDate = new Date();
    chileDate.setHours(chileDate.getHours() - 12);
    const chileTodayStr = chileDate.toISOString().split('T')[0];
    const { data: future2 } = await supabase.from('predicciones').select('carrera_id, carreras!inner(jornadas!inner(fecha))').gte('carreras.jornadas.fecha', chileTodayStr);
    console.log('Chile todayStr:', chileTodayStr, '=>', future2?.length || 0);
})();
