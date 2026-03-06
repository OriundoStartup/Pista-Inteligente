import React from 'react';
import { View, StyleSheet, Text } from 'react-native';
import MaskedView from '@react-native-masked-view/masked-view';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors } from '../constants/Colors';
import { Typography } from '../constants/Theme';

interface GradientTextProps {
    children: React.ReactNode;
    fontSize?: number;
    fontFamily?: string;
    colors?: readonly [string, string, ...string[]];
    style?: any;
}

/**
 * Gradient text component that matches the web's
 * `background: linear-gradient(to right, var(--primary), var(--secondary))`
 * text effect. Falls back to primary color if MaskedView is unavailable.
 */
export const GradientText = React.memo<GradientTextProps>(function GradientText({
    children,
    fontSize = Typography.sizes.xxl,
    fontFamily = Typography.fontFamily.extrabold,
    colors = [Colors.primary, Colors.secondary] as const,
    style,
}: GradientTextProps) {
    // Fallback for platforms where MaskedView isn't available
    try {
        return (
            <MaskedView
                maskElement={
                    <Text
                        style={[
                            {
                                fontSize,
                                fontFamily,
                                color: 'black', // Required for mask
                            },
                            style,
                        ]}
                    >
                        {children}
                    </Text>
                }
            >
                <LinearGradient
                    colors={colors}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                >
                    <Text
                        style={[
                            {
                                fontSize,
                                fontFamily,
                                opacity: 0, // Hidden — gradient shows through mask
                            },
                            style,
                        ]}
                    >
                        {children}
                    </Text>
                </LinearGradient>
            </MaskedView>
        );
    } catch {
        // Fallback: plain colored text
        return (
            <Text
                style={[
                    {
                        fontSize,
                        fontFamily,
                        color: Colors.primary,
                    },
                    style,
                ]}
            >
                {children}
            </Text>
        );
    }
});

GradientText.displayName = 'GradientText';
