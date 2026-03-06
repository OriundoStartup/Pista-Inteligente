import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withTiming,
    Easing,
} from 'react-native-reanimated';
import { Colors } from '../constants/Colors';
import { BorderRadius, Spacing } from '../constants/Theme';
import { ThemedText } from './ThemedText';
import { LinearGradient } from 'expo-linear-gradient';

interface ScoreBarProps {
    score: number; // 0–100
    rank: number;
}

export const ScoreBar = React.memo<ScoreBarProps>(function ScoreBar({ score, rank }) {
    const width = useSharedValue(0);

    useEffect(() => {
        width.value = withTiming(Math.min(score, 100), {
            duration: 800,
            easing: Easing.out(Easing.cubic),
        });
    }, [score]);

    const animatedStyle = useAnimatedStyle(() => ({
        width: `${width.value}%`,
    }));

    return (
        <View style={styles.container}>
            <View style={styles.barBg}>
                <Animated.View style={[styles.barFill, animatedStyle]}>
                    <LinearGradient
                        colors={[Colors.primary, Colors.secondary]}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 0 }}
                        style={StyleSheet.absoluteFill}
                    />
                </Animated.View>
            </View>
            <ThemedText
                variant="caption"
                weight="semibold"
                color={rank === 1 ? Colors.primary : Colors.textMuted}
                style={styles.scoreText}
            >
                {score.toFixed(1)}
            </ThemedText>
        </View>
    );
});

ScoreBar.displayName = 'ScoreBar';

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.sm,
    },
    barBg: {
        flex: 1,
        height: 8,
        backgroundColor: 'rgba(255,255,255,0.08)',
        borderRadius: BorderRadius.full,
        overflow: 'hidden',
    },
    barFill: {
        height: '100%',
        borderRadius: BorderRadius.full,
        overflow: 'hidden',
    },
    scoreText: {
        minWidth: 36,
        textAlign: 'right',
    },
});
