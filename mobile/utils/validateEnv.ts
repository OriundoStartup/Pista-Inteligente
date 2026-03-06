/**
 * Environment variable validation and typed access.
 *
 * Call validateEnv() at app startup (top-level, outside components).
 * Use getEnv() anywhere to access typed environment variables.
 */

interface AppEnv {
    SUPABASE_URL: string;
    SUPABASE_ANON_KEY: string;
    API_BASE_URL: string | undefined;
}

import {
    SUPABASE_URL as SECURE_SUPABASE_URL,
    SUPABASE_ANON_KEY as SECURE_ANON_KEY,
    API_BASE_URL as SECURE_API_BASE_URL
} from './secureConfig';

/**
 * Validates required environment variables.
 *
 * - EXPO_PUBLIC_SUPABASE_URL — must exist and start with https://
 * - EXPO_PUBLIC_SUPABASE_ANON_KEY — must exist and length > 20
 * - EXPO_PUBLIC_API_BASE_URL — optional, warns if missing
 *
 * @throws Error if any critical variable is missing or invalid
 */
export function validateEnv(): void {
    const errors: string[] = [];
    const warnings: string[] = [];

    // --- EXPO_PUBLIC_SUPABASE_URL ---
    const supabaseUrl = SECURE_SUPABASE_URL;
    if (!supabaseUrl || supabaseUrl.trim() === '') {
        errors.push('EXPO_PUBLIC_SUPABASE_URL is missing.');
    } else if (!supabaseUrl.startsWith('https://')) {
        errors.push(
            `EXPO_PUBLIC_SUPABASE_URL must start with https:// (got: "${supabaseUrl.slice(0, 30)}...")`
        );
    }

    // --- EXPO_PUBLIC_SUPABASE_ANON_KEY ---
    const anonKey = SECURE_ANON_KEY;
    if (!anonKey || anonKey.trim() === '') {
        errors.push('EXPO_PUBLIC_SUPABASE_ANON_KEY is missing.');
    } else if (anonKey.length <= 20) {
        errors.push(
            `EXPO_PUBLIC_SUPABASE_ANON_KEY looks invalid (length: ${anonKey.length}, expected > 20).`
        );
    }

    // --- EXPO_PUBLIC_API_BASE_URL (warning only) ---
    const apiBaseUrl = SECURE_API_BASE_URL;
    if (!apiBaseUrl || apiBaseUrl.trim() === '') {
        warnings.push(
            'EXPO_PUBLIC_API_BASE_URL is not set. Chatbot and analysis features may not work.'
        );
    }

    // Emit warnings
    for (const w of warnings) {
        console.warn(`[validateEnv] ⚠️  ${w}`);
    }

    // Throw on critical errors
    if (errors.length > 0) {
        const message = [
            '❌ Environment validation failed:',
            '',
            ...errors.map((e, i) => `  ${i + 1}. ${e}`),
            '',
            'Create a .env file in the mobile/ directory with:',
            '  EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co',
            '  EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key',
            '  EXPO_PUBLIC_API_BASE_URL=https://pista-inteligente.vercel.app  (optional)',
        ].join('\n');

        throw new Error(message);
    }
}

/**
 * Returns typed environment variables.
 * Should only be called after validateEnv() succeeds.
 */
export function getEnv(): AppEnv {
    return {
        SUPABASE_URL: SECURE_SUPABASE_URL,
        SUPABASE_ANON_KEY: SECURE_ANON_KEY,
        API_BASE_URL: SECURE_API_BASE_URL || undefined,
    };
}
