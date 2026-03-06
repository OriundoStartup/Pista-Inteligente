/**
 * Tests for utils/validateEnv.ts
 *
 * Validates that environment variable checking works correctly:
 * - Throws on missing/invalid critical vars
 * - Warns on missing optional vars
 */

describe('validateEnv', () => {
    const originalEnv = process.env;

    beforeEach(() => {
        // Reset modules so validateEnv re-reads process.env each time
        jest.resetModules();
        process.env = { ...originalEnv };
    });

    afterAll(() => {
        process.env = originalEnv;
    });

    function loadValidateEnv() {
        return require('../utils/validateEnv').validateEnv;
    }

    it('throws if EXPO_PUBLIC_SUPABASE_URL is missing', () => {
        delete process.env.EXPO_PUBLIC_SUPABASE_URL;
        process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY = 'a-valid-key-that-is-longer-than-20-chars';

        const validateEnv = loadValidateEnv();
        expect(() => validateEnv()).toThrow('EXPO_PUBLIC_SUPABASE_URL is missing');
    });

    it('throws if EXPO_PUBLIC_SUPABASE_URL is not a valid https URL', () => {
        process.env.EXPO_PUBLIC_SUPABASE_URL = 'http://not-https.example.com';
        process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY = 'a-valid-key-that-is-longer-than-20-chars';

        const validateEnv = loadValidateEnv();
        expect(() => validateEnv()).toThrow('must start with https://');
    });

    it('throws if EXPO_PUBLIC_SUPABASE_ANON_KEY is missing', () => {
        process.env.EXPO_PUBLIC_SUPABASE_URL = 'https://test.supabase.co';
        delete process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

        const validateEnv = loadValidateEnv();
        expect(() => validateEnv()).toThrow('EXPO_PUBLIC_SUPABASE_ANON_KEY is missing');
    });

    it('throws if EXPO_PUBLIC_SUPABASE_ANON_KEY is too short', () => {
        process.env.EXPO_PUBLIC_SUPABASE_URL = 'https://test.supabase.co';
        process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY = 'short';

        const validateEnv = loadValidateEnv();
        expect(() => validateEnv()).toThrow('looks invalid');
    });

    it('does NOT throw when both required vars are valid', () => {
        process.env.EXPO_PUBLIC_SUPABASE_URL = 'https://test.supabase.co';
        process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY = 'a-valid-key-that-is-longer-than-20-chars';
        process.env.EXPO_PUBLIC_API_BASE_URL = 'https://example.com';

        const validateEnv = loadValidateEnv();
        expect(() => validateEnv()).not.toThrow();
    });

    it('does NOT warn if EXPO_PUBLIC_API_BASE_URL is missing (secureConfig provides fallback)', () => {
        process.env.EXPO_PUBLIC_SUPABASE_URL = 'https://test.supabase.co';
        process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY = 'a-valid-key-that-is-longer-than-20-chars';
        delete process.env.EXPO_PUBLIC_API_BASE_URL;

        const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => { });

        const validateEnv = loadValidateEnv();
        expect(() => validateEnv()).not.toThrow();
        // secureConfig.ts now provides a default fallback for API_BASE_URL,
        // so validateEnv will see a non-empty value and NOT warn.
        expect(warnSpy).not.toHaveBeenCalledWith(
            expect.stringContaining('EXPO_PUBLIC_API_BASE_URL')
        );

        warnSpy.mockRestore();
    });
});

describe('getEnv', () => {
    it('returns typed environment variables', () => {
        process.env.EXPO_PUBLIC_SUPABASE_URL = 'https://test.supabase.co';
        process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY = 'test-key-123456789012345';
        process.env.EXPO_PUBLIC_API_BASE_URL = 'https://pista.vercel.app';

        jest.resetModules();
        const { getEnv } = require('../utils/validateEnv');
        const env = getEnv();

        expect(env.SUPABASE_URL).toBe('https://test.supabase.co');
        expect(env.SUPABASE_ANON_KEY).toBe('test-key-123456789012345');
        expect(env.API_BASE_URL).toBe('https://pista.vercel.app');
    });
});
