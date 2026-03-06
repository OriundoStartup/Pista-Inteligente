import React, { useCallback } from 'react';
import {
  View,
  ScrollView,
  RefreshControl,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { ThemedText } from '../../components/ThemedText';
import { GradientText } from '../../components/GradientText';
import { SectionTitle } from '../../components/SectionTitle';
import { GradientButton } from '../../components/GradientButton';
import { StatCard } from '../../components/StatCard';
import { JackpotAlert } from '../../components/JackpotAlert';
import { DonationButton } from '../../components/DonationButton';
import { Colors } from '../../constants/Colors';
import { Spacing, BorderRadius, Typography } from '../../constants/Theme';
import { useSupabaseQuery } from '../../hooks/useSupabase';
import { supabase } from '../../lib/supabase';

interface JineteStat {
  jinete: string;
  ganadas: number;
  eficiencia: string;
}

export default function HomeScreen() {
  const router = useRouter();

  // Fetch counts
  const stats = useSupabaseQuery(async () => {
    const [carreras, caballos, jinetes, jornadas] = await Promise.all([
      supabase.from('carreras').select('*', { count: 'exact', head: true }),
      supabase.from('caballos').select('*', { count: 'exact', head: true }),
      supabase.from('jinetes').select('*', { count: 'exact', head: true }),
      supabase.from('jornadas').select('*', { count: 'exact', head: true }),
    ]);
    return {
      total_carreras: carreras.count || 0,
      total_caballos: caballos.count || 0,
      total_jinetes: jinetes.count || 0,
      total_jornadas: jornadas.count || 0,
    };
  }, 'home_stats');

  // Fetch top jinetes
  const jinetes = useSupabaseQuery<JineteStat[]>(async () => {
    try {
      const { data, error } = await supabase.rpc('get_top_jinetes_2026');
      if (!error && data && data.length > 0) {
        return data.map((j: any) => ({
          jinete: j.jinete,
          ganadas: Number(j.ganadas),
          eficiencia: j.eficiencia,
        }));
      }
    } catch { }
    return [
      { jinete: 'Cargando...', ganadas: 0, eficiencia: '0.0' },
    ];
  }, 'home_jinetes');

  // Fetch pozos acumulados
  const pozos = useSupabaseQuery(async () => {
    const { data } = await supabase
      .from('pozos_acumulados')
      .select('*')
      .order('fecha_evento', { ascending: false })
      .limit(5);
    return data || [];
  }, 'home_pozos');

  const [refreshing, setRefreshing] = React.useState(false);
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([stats.refresh(), jinetes.refresh(), pozos.refresh()]);
    setRefreshing(false);
  }, []);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={Colors.primary}
            colors={[Colors.primary]}
          />
        }
      >
        {/* Hero Section — matches web's gradient h1 */}
        <View style={styles.hero}>
          <GradientText
            fontSize={Typography.sizes.hero}
            fontFamily={Typography.fontFamily.extrabold}
          >
            Pista Inteligente
          </GradientText>
          <ThemedText variant="muted" align="center" style={styles.heroSubtitle}>
            🏇 Predicciones Hípicas con IA para Chile
          </ThemedText>
        </View>

        {/* Stats Cards */}
        <View style={styles.section}>
          <SectionTitle emoji="📊">Nuestra Base de Datos</SectionTitle>
          {stats.loading && !stats.data ? (
            <ActivityIndicator color={Colors.primary} size="large" />
          ) : (
            <View style={styles.statsGrid}>
              <StatCard
                label="🏁 Carreras"
                value={stats.data?.total_carreras ?? 0}
                color={Colors.secondary}
              />
              <StatCard
                label="🐴 Caballos"
                value={stats.data?.total_caballos ?? 0}
                color={Colors.primary}
              />
              <StatCard
                label="🏇 Jinetes"
                value={stats.data?.total_jinetes ?? 0}
                color={Colors.accent}
              />
              <StatCard
                label="📅 Jornadas"
                value={stats.data?.total_jornadas ?? 0}
                color={Colors.gold}
              />
            </View>
          )}
        </View>

        {/* Top Jinetes */}
        <View style={styles.card}>
          <SectionTitle emoji="🏆">Top Jinetes 2026</SectionTitle>
          {jinetes.data && jinetes.data.length > 0 ? (
            <View>
              <View style={[styles.tableRow, styles.tableHeader]}>
                <ThemedText variant="label" color={Colors.secondary} style={{ flex: 2 }}>Jinete</ThemedText>
                <ThemedText variant="label" color={Colors.secondary} style={{ flex: 1, textAlign: 'center' }}>Triunfos</ThemedText>
                <ThemedText variant="label" color={Colors.secondary} style={{ flex: 1, textAlign: 'right' }}>Eficiencia</ThemedText>
              </View>
              {jinetes.data.map((j, i) => (
                <View key={i} style={[styles.tableRow, i === 0 && styles.topRowHighlight]}>
                  <ThemedText variant="body" weight={i === 0 ? 'semibold' : 'regular'} style={{ flex: 2 }}>
                    {i === 0 ? '🥇 ' : i === 1 ? '🥈 ' : i === 2 ? '🥉 ' : ''}{j.jinete}
                  </ThemedText>
                  <ThemedText variant="body" color={Colors.primary} align="center" style={{ flex: 1 }}>
                    {j.ganadas}
                  </ThemedText>
                  <ThemedText variant="body" color={Colors.secondary} style={{ flex: 1, textAlign: 'right' }}>
                    {j.eficiencia}%
                  </ThemedText>
                </View>
              ))}
            </View>
          ) : (
            <ActivityIndicator color={Colors.primary} />
          )}
        </View>

        {/* Jackpot */}
        {pozos.data && pozos.data.length > 0 && (
          <JackpotAlert pozos={pozos.data} />
        )}

        {/* CTA Button — pill shape like web */}
        <GradientButton
          label="🔮 Ver Predicciones de Hoy"
          onPress={() => router.push('/(tabs)/programa')}
          style={{ marginTop: Spacing.lg, alignSelf: 'center' }}
        />

        {/* Donation */}
        <DonationButton />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bgDark,
  },
  scroll: {
    flex: 1,
  },
  content: {
    padding: Spacing.lg,
    paddingBottom: Spacing.xxxl,
  },
  hero: {
    paddingVertical: Spacing.xxxl,
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  heroSubtitle: {
    maxWidth: 300,
    lineHeight: 22,
    marginTop: Spacing.sm,
  },
  section: {
    marginBottom: Spacing.xl,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
  },
  card: {
    backgroundColor: Colors.bgCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.borderGlass,
    marginBottom: Spacing.xl,
  },
  tableRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.borderGlass,
  },
  tableHeader: {
    borderBottomWidth: 2,
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: Spacing.sm,
    borderRadius: BorderRadius.sm,
  },
  topRowHighlight: {
    backgroundColor: Colors.primaryMuted,
    borderRadius: BorderRadius.sm,
    paddingHorizontal: Spacing.sm,
  },
});
