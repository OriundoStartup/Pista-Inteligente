import React from 'react';
import { TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';

interface GradientButtonProps {
    onPress: () => void;
    label: string;
    style?: ViewStyle;
    disabled?: boolean;
}

/**
 * CTA button matching web's `.cta-button`:
 * `background: linear-gradient(135deg, var(--primary), var(--secondary))`
 * `border-radius: 50px; box-shadow: 0 10px 20px -5px var(--primary-glow);`
 *
 * ⚠️ Parent must wrap `onPress` with useCallback to benefit from memo.
 */
export const GradientButton = React.memo<GradientButtonProps>(function GradientButton({
    onPress,
    label,
    style,
    disabled = false,
}: GradientButtonProps) {
    return (
        <TouchableOpacity
            onPress={onPress}
            activeOpacity={0.85}
            disabled={disabled}
            style={[styles.wrapper, style]}
        >
            <LinearGradient
                colors={[Colors.primary, Colors.secondary]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.gradient}
            >
                <ThemedText variant="body" weight="semibold" color="#fff" align="center">
                    {label}
                </ThemedText>
            </LinearGradient>
        </TouchableOpacity>
    );
});

GradientButton.displayName = 'GradientButton';

const styles = StyleSheet.create({
    wrapper: {
        borderRadius: 50, // pill shape like web
        overflow: 'hidden',
        shadowColor: Colors.primary,
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.35,
        shadowRadius: 20,
        elevation: 8,
    },
    gradient: {
        paddingVertical: Spacing.lg,
        paddingHorizontal: Spacing.xxxl,
        borderRadius: 50,
        alignItems: 'center',
    },
});
