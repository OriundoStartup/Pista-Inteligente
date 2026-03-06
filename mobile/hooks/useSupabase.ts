import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { Platform } from 'react-native';
import { supabase } from '../lib/supabase';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface CachedData<T> {
    data: T;
    timestamp: number;
}

interface UseSupabaseResult<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
    lastUpdated: Date | null;
    isStale: boolean;
    refresh: () => Promise<void>;
}

const DEFAULT_TTL_MINUTES = 10;

export function useSupabaseQuery<T>(
    queryFn: () => Promise<T>,
    cacheKey?: string,
    deps: any[] = [],
    ttlMinutes: number = DEFAULT_TTL_MINUTES
): UseSupabaseResult<T> {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isStale, setIsStale] = useState(false);

    const isMounted = useRef(true);
    const abortControllerRef = useRef<AbortController | null>(null);

    useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    const fetchData = useCallback(async () => {
        if (!isMounted.current) return;

        // Abort previous requests
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        abortControllerRef.current = new AbortController();

        try {
            setLoading(true);
            setError(null);

            if (cacheKey && Platform.OS !== 'web') {
                try {
                    const cached = await AsyncStorage.getItem(cacheKey);
                    if (cached && isMounted.current) {
                        const parsed: CachedData<T> = JSON.parse(cached);
                        const age = Date.now() - parsed.timestamp;
                        const ttlMs = ttlMinutes * 60 * 1000;

                        setData(parsed.data);
                        setLastUpdated(new Date(parsed.timestamp));
                        setIsStale(age > ttlMs);
                        setLoading(false);
                    }
                } catch { }
            }

            const result = await queryFn();
            const now = Date.now();

            if (isMounted.current) {
                setData(result);
                setLastUpdated(new Date(now));
                setIsStale(false);
            }

            if (cacheKey && result && Platform.OS !== 'web') {
                try {
                    const cacheEntry: CachedData<T> = {
                        data: result,
                        timestamp: now,
                    };
                    await AsyncStorage.setItem(cacheKey, JSON.stringify(cacheEntry));
                } catch { }
            }
        } catch (e: any) {
            if (isMounted.current && e.name !== 'AbortError') {
                setError(e?.message || 'Error al cargar datos');
            }
        } finally {
            if (isMounted.current) {
                setLoading(false);
            }
        }
    }, deps);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // PREVENIR re-creación eterna del return literal:
    return useMemo(() => ({
        data,
        loading,
        error,
        lastUpdated,
        isStale,
        refresh: fetchData
    }), [data, loading, error, lastUpdated, isStale, fetchData]);
}

export function useSupabaseCount(table: string, cacheKey?: string) {
    return useSupabaseQuery(async () => {
        const { count, error } = await supabase
            .from(table)
            .select('*', { count: 'exact', head: true });
        if (error) throw error;
        return count || 0;
    }, cacheKey || `count_${table}`);
}

export { supabase };

