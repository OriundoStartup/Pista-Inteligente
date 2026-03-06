/** @type {import('jest').Config} */
module.exports = {
    preset: 'react-native',
    // Use babel-jest with Expo's babel preset directly
    // (bypasses jest-expo preset which has ESM parsing issues in v55)
    transform: {
        '^.+\\.[jt]sx?$': [
            'babel-jest',
            {
                presets: ['babel-preset-expo'],
            },
        ],
    },

    setupFiles: ['./jest.setup.ts'],
    setupFilesAfterEnv: ['@testing-library/jest-native/extend-expect'],

    // Whitelist ALL expo/react-native modules for transformation
    transformIgnorePatterns: [
        'node_modules/(?!(' +
        '(jest-)?react-native' +
        '|@react-native(-community)?' +
        '|expo(nent)?' +
        '|@expo(nent)?/.*' +
        '|@expo-google-fonts/.*' +
        '|expo-asset' +
        '|expo-font' +
        '|expo-modules-core' +
        '|react-navigation' +
        '|@react-navigation/.*' +
        '|@supabase/.*' +
        '|react-native-reanimated' +
        '|react-native-url-polyfill' +
        '|@react-native-masked-view' +
        '|react-native-worklets' +
        ')/)',
    ],

    // We use node environment. The Invalid hook call was with jest-expo which defaults to jsdom, 
    // or when the environment is undefined. React Native testing library actually recommends 
    // nothing or node. Let's explicitly define it:
    // testEnvironment: 'node',

    moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],

    // Ensure single React instance to prevent Invalid Hook Call
    moduleNameMapper: {
        '^react$': '<rootDir>/node_modules/react',
        '^react-native$': '<rootDir>/node_modules/react-native',
        '^@/(.*)$': '<rootDir>/$1',
    },

    testPathIgnorePatterns: ['/node_modules/', '/android/', '/ios/'],
};
