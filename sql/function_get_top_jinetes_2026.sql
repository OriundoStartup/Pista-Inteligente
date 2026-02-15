-- Function to get Top Jinetes for 2026
-- Returns: jinete name, wins, efficiency %
-- Logic: Same as frontend but runs on DB to avoid 1000 row limit on REST API
create or replace function get_top_jinetes_2026()
returns table (
  jinete text,
  ganadas bigint,
  eficiencia text
)
language plpgsql
security definer -- Allows function to bypass RLS if needed, or use 'invoker'
as $$
begin
  return query
  select
    j.nombre as jinete,
    count(*) filter (where p.posicion = 1) as ganadas,
    to_char((count(*) filter (where p.posicion = 1)::float / count(*)::float) * 100, 'FM999.0') as eficiencia
  from participaciones p
  join carreras c on p.carrera_id = c.id
  join jornadas jor on c.jornada_id = jor.id
  join jinetes j on p.jinete_id = j.id
  where jor.fecha >= '2026-01-01' and jor.fecha <= '2026-12-31'
  group by j.nombre
  having count(*) >= 5 -- Minimo 5 carreras para evitar 100% con 1 carrera
  order by ganadas desc
  limit 10;
end;
$$;
