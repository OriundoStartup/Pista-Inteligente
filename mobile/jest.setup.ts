/// <reference types="jest" />
/**
 * Jest global setup — mocks for native modules that don't exist in test env.
 *
 * Only mock modules that ARE installed as dependencies.
 */

// React Native requires __DEV__ global
(global as any).__DEV__ = true;
(global as any).__TEST__ = true;

// ─── @expo/vector-icons ───
jest.mock('@expo/vector-icons', () => {
    const React = require('react');
    const MockIcon = (props: any) => React.createElement('div', props);
    return {
        Ionicons: MockIcon,
        MaterialIcons: MockIcon,
        FontAwesome: MockIcon,
    };
});
jest.mock('expo-router', () => ({
    useRouter: () => ({
        push: jest.fn(),
        replace: jest.fn(),
        back: jest.fn(),
    }),
    usePathname: () => '/',
    useSegments: () => [],
    Stack: { Screen: () => null },
    Tabs: { Screen: () => null },
    Link: ({ children }: any) => children,
}));

// ─── @react-native-async-storage/async-storage ───
jest.mock('expo-modules-core', () => {
    return {
        NativeModulesProxy: {},
        EventEmitter: jest.fn(() => ({
            addListener: jest.fn(),
            removeListeners: jest.fn(),
        })),
        requireOptionalNativeModule: jest.fn(() => null),
        requireNativeModule: jest.fn(() => null),
    };
});

jest.mock('@react-native-async-storage/async-storage', () => ({
    __esModule: true,
    default: {
        getItem: jest.fn(() => Promise.resolve(null)),
        setItem: jest.fn(() => Promise.resolve()),
        removeItem: jest.fn(() => Promise.resolve()),
        clear: jest.fn(() => Promise.resolve()),
        getAllKeys: jest.fn(() => Promise.resolve([])),
    },
}));

// ─── @react-native-community/netinfo ───
jest.mock('@react-native-community/netinfo', () => ({
    __esModule: true,
    default: {
        addEventListener: jest.fn(() => jest.fn()),
        fetch: jest.fn(() =>
            Promise.resolve({ isConnected: true, isInternetReachable: true, type: 'wifi' })
        ),
    },
}));

// ─── expo-constants ───
jest.mock('expo-constants', () => ({
    __esModule: true,
    default: {
        expoConfig: {
            extra: { eas: { projectId: 'test-project-id' } },
        },
    },
}));

// ─── expo-notifications ───
jest.mock('expo-notifications', () => ({
    getPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
    requestPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
    getExpoPushTokenAsync: jest.fn(() => Promise.resolve({ data: 'ExponentPushToken[test]' })),
    setNotificationHandler: jest.fn(),
    setNotificationChannelAsync: jest.fn(),
    addNotificationReceivedListener: jest.fn(() => ({ remove: jest.fn() })),
    addNotificationResponseReceivedListener: jest.fn(() => ({ remove: jest.fn() })),
    AndroidImportance: { HIGH: 4 },
}));

// ─── expo-linear-gradient ───
jest.mock('expo-linear-gradient', () => ({
    LinearGradient: ({ children }: any) => children,
}));

// ─── @react-native-masked-view/masked-view ───
jest.mock('@react-native-masked-view/masked-view', () => ({
    __esModule: true,
    default: ({ children }: any) => children,
}));

// ─── react-native-reanimated ───
jest.mock('react-native-reanimated', () => ({
    __esModule: true,
    default: {
        View: 'Animated.View',
        createAnimatedComponent: (c: any) => c,
    },
    useSharedValue: (init: any) => ({ value: init }),
    useAnimatedStyle: (fn: () => any) => fn(),
    withTiming: (val: any) => val,
    Easing: { out: () => () => 0, cubic: () => 0 },
}));

// ─── Supabase client ───
jest.mock('./lib/supabase', () => ({
    supabase: {
        from: jest.fn(() => ({
            select: jest.fn().mockReturnThis(),
            upsert: jest.fn(() => ({ error: null })),
            eq: jest.fn().mockReturnThis(),
            order: jest.fn().mockReturnThis(),
            limit: jest.fn().mockReturnThis(),
        })),
        auth: {
            getUser: jest.fn(() => Promise.resolve({ data: { user: null } })),
            onAuthStateChange: jest.fn(() => ({
                data: { subscription: { unsubscribe: jest.fn() } },
            })),
            signInWithOAuth: jest.fn(),
            signOut: jest.fn(),
        },
        rpc: jest.fn(),
    },
}));
