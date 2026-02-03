-- Migration: Add ticket_sugerido to pozos_alertas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'pozos_alertas'
        AND column_name = 'ticket_sugerido'
    ) THEN
        ALTER TABLE public.pozos_alertas ADD COLUMN ticket_sugerido JSONB;
        COMMENT ON COLUMN public.pozos_alertas.ticket_sugerido IS 'Estructura JSON con la sugerencia de apuesta basada en IA';
    END IF;
END $$;
