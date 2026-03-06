import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, Typography } from '../constants/Theme';

interface SectionTitleProps {
    children: React.ReactNode;
    emoji?: string;
    borderColor?: string;
}

/**
 * Section title matching web's `.section-title`:
 * `border-left: 4px solid var(--secondary); padding-left: 1rem;`
 */
export const SectionTitle = React.memo<SectionTitleProps>(function SectionTitle({
    children,
    emoji,
    borderColor = Colors.secondary,
}: SectionTitleProps) {
    return (
        <View style={[styles.container, { borderLeftColor: borderColor }]}>
            <ThemedText
                variant="h2"
                weight="semibold"
                style={{ lineHeight: 28 }}
            >
                {emoji ? `${emoji} ` : ''}{children}
            </ThemedText>
        </View>
    );
});

SectionTitle.displayName = 'SectionTitle';

const styles = StyleSheet.create({
    container: {
        borderLeftWidth: 4,
        paddingLeft: Spacing.lg,
        marginBottom: Spacing.lg,
    },
});
