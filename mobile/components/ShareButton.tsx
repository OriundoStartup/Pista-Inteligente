import React, { useCallback } from 'react';
import { TouchableOpacity, Share, StyleSheet, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';

interface ShareButtonProps {
    /** Share dialog title (iOS only) */
    title: string;
    /** Message to share */
    message: string;
    /** Optional URL to attach (iOS appends separately, Android gets appended to message) */
    url?: string;
    /** Icon size, default 20 */
    size?: number;
}

/**
 * Generic share button using the native Share API.
 *
 * iOS:  Share.share({ message, url }) — url appears as separate attachment
 * Android: Share.share({ message: message + url }) — combined into one string
 */
export const ShareButton = React.memo<ShareButtonProps>(function ShareButton({
    title,
    message,
    url,
    size = 20,
}) {
    const handleShare = useCallback(async () => {
        try {
            if (Platform.OS === 'ios') {
                await Share.share({
                    message,
                    url: url || undefined,
                });
            } else {
                // Android: combine message + url into one string
                const fullMessage = url ? `${message}\n${url}` : message;
                await Share.share({ message: fullMessage, title });
            }
        } catch (err: any) {
            // User dismissed — silently ignore
            if (err?.message !== 'User did not share') {
                console.error('[ShareButton] Share error:', err);
            }
        }
    }, [title, message, url]);

    return (
        <TouchableOpacity
            style={styles.button}
            onPress={handleShare}
            activeOpacity={0.7}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
            <Ionicons name="share-outline" size={size} color={Colors.primary} />
        </TouchableOpacity>
    );
});

ShareButton.displayName = 'ShareButton';

const styles = StyleSheet.create({
    button: {
        padding: Spacing.sm,
        borderRadius: BorderRadius.full,
        backgroundColor: Colors.primaryMuted,
    },
});
