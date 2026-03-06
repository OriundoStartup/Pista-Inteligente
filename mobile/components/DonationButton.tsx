import React, { useCallback } from 'react';
import { TouchableOpacity, Linking, StyleSheet, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { ThemedText } from './ThemedText';
import { Spacing, BorderRadius } from '../constants/Theme';

/**
 * Reads the donation URL from env vars.
 * Returns null if not configured — component won't render.
 */
function getDonationUrl(): string | null {
    const url = process.env.EXPO_PUBLIC_DONATION_URL;
    if (!url || url.trim() === '') return null;
    return url;
}

/**
 * "Invítanos una Quinela" donation button.
 *
 * - Opens payment link via native browser (Linking.openURL)
 * - URL from EXPO_PUBLIC_DONATION_URL env var
 * - Returns null if env var is not set (button hidden)
 * - Green gradient background (expo-linear-gradient)
 */
export const DonationButton = React.memo(function DonationButton() {
    const donationUrl = getDonationUrl();

    const handlePress = useCallback(() => {
        if (donationUrl) {
            Linking.openURL(donationUrl);
        }
    }, [donationUrl]);

    // Don't render if env var is not configured
    if (!donationUrl) return null;

    return (
        <TouchableOpacity
            style={styles.container}
            onPress={handlePress}
            activeOpacity={0.85}
        >
            <LinearGradient
                colors={['#16a34a', '#15803d', '#166534']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.gradient}
            >
                <View style={styles.content}>
                    <ThemedText style={styles.icon}>☕</ThemedText>
                    <View style={styles.textColumn}>
                        <ThemedText variant="caption" color="rgba(255,255,255,0.85)">
                            ¿Te sirvió el dato?
                        </ThemedText>
                        <ThemedText variant="body" weight="semibold" color="#fff">
                            Invítanos una Quinela 🏇
                        </ThemedText>
                    </View>
                </View>
            </LinearGradient>
        </TouchableOpacity>
    );
});

DonationButton.displayName = 'DonationButton';

const styles = StyleSheet.create({
    container: {
        borderRadius: BorderRadius.lg,
        overflow: 'hidden',
        marginTop: Spacing.lg,
        shadowColor: '#16a34a',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 6,
    },
    gradient: {
        paddingVertical: Spacing.lg,
        paddingHorizontal: Spacing.xl,
    },
    content: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        gap: Spacing.md,
    },
    icon: {
        fontSize: 28,
    },
    textColumn: {
        gap: 2,
    },
});
