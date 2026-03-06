import { Link, Stack } from 'expo-router';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '../components/ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ title: 'Página no encontrada' }} />
      <View style={styles.container}>
        <ThemedText style={{ fontSize: 64 }}>🏇</ThemedText>
        <ThemedText variant="h2" align="center">
          Página no encontrada
        </ThemedText>
        <ThemedText variant="muted" align="center">
          La página que buscas no existe
        </ThemedText>
        <Link href="/" style={styles.link}>
          <ThemedText variant="body" color={Colors.primary}>
            Volver al inicio
          </ThemedText>
        </Link>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.xl,
    backgroundColor: Colors.bgDark,
    gap: Spacing.md,
  },
  link: {
    marginTop: Spacing.lg,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.xl,
    backgroundColor: Colors.primaryMuted,
    borderRadius: BorderRadius.full,
  },
});
