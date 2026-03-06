import 'react-native-url-polyfill/auto';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from '../utils/secureConfig';

console.log('=== supabase: module loading ===');
console.log('  Creating client with URL length:', SUPABASE_URL.length);

// Use fallback values so createClient never receives empty strings
// (which would crash with an invalid URL error)
const url = SUPABASE_URL || 'https://placeholder.supabase.co';
const key = SUPABASE_ANON_KEY || 'placeholder-key';

// AsyncStorage only works on native platforms (iOS/Android).
// On web/SSR the `window` object may not exist, causing a crash.
const storage = Platform.OS === 'web' ? undefined : AsyncStorage;

export const supabase = createClient(url, key, {
    auth: {
        storage: storage,
        autoRefreshToken: true,
        persistSession: Platform.OS !== 'web',
        detectSessionInUrl: false,
    },
});

console.log('=== supabase: client created ===');
