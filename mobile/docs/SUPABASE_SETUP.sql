-- ============================================================
-- Pista Inteligente — Push Tokens Table
-- ============================================================
-- Run this SQL in: Supabase Dashboard → SQL Editor → New Query
-- This creates the push_tokens table needed for server-side
-- push notifications via Expo.
-- ============================================================

-- 1. Create the table
CREATE TABLE IF NOT EXISTS public.push_tokens (
    id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token       text NOT NULL,
    platform    text NOT NULL CHECK (platform IN ('ios', 'android')),
    created_at  timestamptz DEFAULT now() NOT NULL,
    updated_at  timestamptz DEFAULT now() NOT NULL
);

-- 2. Add comment for documentation
COMMENT ON TABLE public.push_tokens IS 
    'Stores Expo push tokens for each user/platform for server-side notifications.';

-- 3. Unique constraint for upsert (one token per user+platform)
CREATE UNIQUE INDEX IF NOT EXISTS push_tokens_user_platform_idx 
    ON public.push_tokens (user_id, platform);

-- 4. Index for querying by token (useful when sending batch notifications)
CREATE INDEX IF NOT EXISTS push_tokens_token_idx 
    ON public.push_tokens (token);

-- 5. Auto-update the updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_push_tokens_updated_at ON public.push_tokens;
CREATE TRIGGER set_push_tokens_updated_at
    BEFORE UPDATE ON public.push_tokens
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- 6. Enable Row Level Security
ALTER TABLE public.push_tokens ENABLE ROW LEVEL SECURITY;

-- 7. RLS Policies

-- Users can view their own tokens
CREATE POLICY "Users can view own push tokens"
    ON public.push_tokens
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own tokens
CREATE POLICY "Users can insert own push tokens"
    ON public.push_tokens
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own tokens
CREATE POLICY "Users can update own push tokens"
    ON public.push_tokens
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own tokens (e.g. on sign out)
CREATE POLICY "Users can delete own push tokens"
    ON public.push_tokens
    FOR DELETE
    USING (auth.uid() = user_id);

-- Service role can read all tokens (for server-side notification dispatch)
-- Note: service_role bypasses RLS by default, but this makes it explicit.
CREATE POLICY "Service role can read all push tokens"
    ON public.push_tokens
    FOR SELECT
    TO service_role
    USING (true);

-- ============================================================
-- Verification: Run after creating the table
-- ============================================================
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'push_tokens' 
-- ORDER BY ordinal_position;
