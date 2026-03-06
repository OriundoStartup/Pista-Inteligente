import { DarkTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import {
  Outfit_300Light,
  Outfit_400Regular,
  Outfit_600SemiBold,
  Outfit_800ExtraBold,
} from '@expo-google-fonts/outfit';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { Platform, View } from 'react-native';
import 'react-native-reanimated';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as NavigationBar from 'expo-navigation-bar';
import { Colors } from '../constants/Colors';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { OfflineBanner } from '../components/OfflineBanner';
import { ChatFAB } from '../components/ChatFAB';
import { useNotifications } from '../hooks/useNotifications';
import { validateEnv } from '../utils/validateEnv';

// ─── Top-level validation (runs before any component mounts) ───
console.log('=== APP STARTING ===');
try {
  validateEnv();
  console.log('=== AFTER validateEnv (OK) ===');
} catch (e: any) {
  console.error('[RootLayout] Environment validation failed:', e?.message ?? e);
  console.log('=== AFTER validateEnv (CAUGHT ERROR) ===');
  // Don't re-throw: let the app render so ErrorBoundary / UI can show a message
}

// Prevent the splash screen from auto-hiding before asset loading is complete.
console.log('=== BEFORE SplashScreen.preventAutoHideAsync ===');
SplashScreen.preventAutoHideAsync();
console.log('=== AFTER SplashScreen.preventAutoHideAsync ===');

const CustomDarkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: Colors.primary,
    background: Colors.bgDark,
    card: Colors.bgDark,
    text: Colors.textMain,
    border: Colors.borderGlass,
    notification: Colors.accent,
  },
};

export default function RootLayout() {
  const [loaded] = useFonts({
    Outfit_300Light,
    Outfit_400Regular,
    Outfit_600SemiBold,
    Outfit_800ExtraBold,
  });

  // Initialize push notifications (hook is always called; internally no-ops on web)
  useNotifications();

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  // Configure Android navigation bar to match app theme
  useEffect(() => {
    if (Platform.OS === 'android') {
      NavigationBar.setBackgroundColorAsync(Colors.bgDark);
      NavigationBar.setButtonStyleAsync('light');
    }
  }, []);

  if (!loaded) {
    return null;
  }

  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <ThemeProvider value={CustomDarkTheme}>
          <View style={{ flex: 1 }}>
            <OfflineBanner />
            <Stack>
              <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
              <Stack.Screen
                name="auth/callback"
                options={{
                  headerShown: false,
                  animation: 'fade',
                }}
              />
              <Stack.Screen
                name="guia"
                options={{
                  headerShown: true,
                  title: 'Guía de Uso',
                  headerStyle: { backgroundColor: Colors.bgDark },
                  headerTintColor: Colors.textMain,
                }}
              />
              <Stack.Screen
                name="analisis"
                options={{
                  headerShown: true,
                  title: 'Análisis',
                  headerStyle: { backgroundColor: Colors.bgDark },
                  headerTintColor: Colors.textMain,
                }}
              />
              <Stack.Screen name="+not-found" />
            </Stack>
            <ChatFAB />
          </View>
          <StatusBar style="light" />
        </ThemeProvider>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
