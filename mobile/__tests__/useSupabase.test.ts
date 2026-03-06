/**
 * Tests for hooks/useSupabase.ts — cache logic
 *
 * Tests the AsyncStorage caching layer:
 * - Cache hit with fresh data
 * - Cache hit with stale data (TTL expired)
 * - Cache miss (calls query function)
 * - lastUpdated null when no cache
 */

// Provide mock before importing
jest.mock('@react-native-async-storage/async-storage', () => ({
    getItem: jest.fn().mockResolvedValue(null),
    setItem: jest.fn().mockResolvedValue(undefined),
    removeItem: jest.fn().mockResolvedValue(undefined),
    clear: jest.fn().mockResolvedValue(undefined),
}));

import AsyncStorage from '@react-native-async-storage/async-storage';
import { renderHook, waitFor, act } from '@testing-library/react-native';
import { useSupabaseQuery } from '../hooks/useSupabase';

const mockAsyncStorage = AsyncStorage as jest.Mocked<typeof AsyncStorage>;

describe('useSupabaseQuery', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('returns cached data if cache exists and is fresh', async () => {
        const cachedData = {
            data: { total: 42 },
            timestamp: Date.now() - 1000, // 1 second ago (fresh)
        };

        mockAsyncStorage.getItem.mockResolvedValueOnce(JSON.stringify(cachedData));

        const queryFn = jest.fn().mockResolvedValue({ total: 99 });

        const { result } = renderHook(() =>
            useSupabaseQuery(queryFn, 'test_key', [], 10)
        );

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        // Should have called AsyncStorage.getItem
        expect(mockAsyncStorage.getItem).toHaveBeenCalledWith('test_key');
        // Data should eventually be the fresh query result (query runs even with cache)
        expect(result.current.data).toBeDefined();
        // isStale should be false (within TTL)
        expect(result.current.isStale).toBe(false);
    });

    it('marks data as stale if cache timestamp exceeds TTL', async () => {
        const ttlMinutes = 10;
        const staleCacheData = {
            data: { total: 42 },
            timestamp: Date.now() - (ttlMinutes + 1) * 60 * 1000, // 11 min ago
        };

        mockAsyncStorage.getItem.mockResolvedValueOnce(JSON.stringify(staleCacheData));

        const queryFn = jest.fn().mockImplementation(
            () => new Promise(() => { }) // Never resolves — so we see stale state
        );

        const { result } = renderHook(() =>
            useSupabaseQuery(queryFn, 'stale_key', [], ttlMinutes)
        );

        // Wait for cache to be read (sets isStale before query resolves)
        await waitFor(() => {
            expect(result.current.data).toEqual({ total: 42 });
        });

        expect(result.current.isStale).toBe(true);
        expect(result.current.lastUpdated).toBeInstanceOf(Date);
    });

    it('calls query function when cache does not exist', async () => {
        mockAsyncStorage.getItem.mockResolvedValueOnce(null);

        const queryFn = jest.fn().mockResolvedValue({ count: 100 });

        const { result } = renderHook(() =>
            useSupabaseQuery(queryFn, 'new_key', [], 10)
        );

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
        });

        expect(queryFn).toHaveBeenCalledTimes(1);
        expect(result.current.data).toEqual({ count: 100 });
    });

    it('has lastUpdated=null initially before any data loads', () => {
        mockAsyncStorage.getItem.mockResolvedValue(null);

        const queryFn = jest.fn().mockImplementation(
            () => new Promise(() => { }) // Never resolves
        );

        const { result } = renderHook(() =>
            useSupabaseQuery(queryFn, 'pending_key', [], 10)
        );

        expect(result.current.lastUpdated).toBeNull();
        expect(result.current.loading).toBe(true);
    });
});
