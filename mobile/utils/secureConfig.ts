/**
 * Secure Config — Simplified version.
 *
 * Reads environment variables directly from process.env.
 * The obfuscation layer (split/reconstruct + domain hash)
 * will be re-added once the app is confirmed working.
 *
 * EXPO_PUBLIC_* vars are inlined at build time by Metro.
 */

console.log('=== secureConfig: module loading ===');

export const SUPABASE_URL =
    process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';

export const SUPABASE_ANON_KEY =
    process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

export const API_BASE_URL =
    process.env.EXPO_PUBLIC_API_BASE_URL ??
    'https://pista-inteligente.vercel.app';

console.log('=== secureConfig: module loaded ===');
console.log('  SUPABASE_URL length:', SUPABASE_URL.length);
console.log('  SUPABASE_ANON_KEY length:', SUPABASE_ANON_KEY.length);
console.log('  API_BASE_URL:', API_BASE_URL);
