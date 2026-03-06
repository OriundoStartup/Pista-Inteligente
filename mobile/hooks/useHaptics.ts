import { Platform } from 'react-native';

/**
 * Cross-platform haptic feedback utilities.
 * Uses expo-haptics on native, no-ops on web.
 *
 * Note: expo-haptics must be installed separately:
 *   npx expo install expo-haptics
 *
 * Since expo-haptics is optional, we use dynamic import
 * with a graceful fallback if not installed.
 */

let Haptics: any = null;

// Try to load expo-haptics dynamically
try {
    Haptics = require('expo-haptics');
} catch {
    // expo-haptics not installed — all functions are no-ops
}

export const haptics = {
    /** Light tap — tab changes, selections */
    light: () => {
        if (Platform.OS === 'web' || !Haptics) return;
        try {
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        } catch { }
    },

    /** Medium tap — button presses, toggles */
    medium: () => {
        if (Platform.OS === 'web' || !Haptics) return;
        try {
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        } catch { }
    },

    /** Heavy tap — destructive actions, important events */
    heavy: () => {
        if (Platform.OS === 'web' || !Haptics) return;
        try {
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
        } catch { }
    },

    /** Success feedback — completed action */
    success: () => {
        if (Platform.OS === 'web' || !Haptics) return;
        try {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        } catch { }
    },

    /** Selection change — picker, toggle */
    selection: () => {
        if (Platform.OS === 'web' || !Haptics) return;
        try {
            Haptics.selectionAsync();
        } catch { }
    },
};
