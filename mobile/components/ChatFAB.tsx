import React, { useState, useRef, useCallback } from 'react';
import {
    TouchableOpacity,
    StyleSheet,
    Animated,
} from 'react-native';
import { usePathname } from 'expo-router';
import { ThemedText } from './ThemedText';
import { ChatbotSheet } from './ChatbotSheet';
import { Colors } from '../constants/Colors';

/**
 * Routes where the FAB should NOT be visible.
 */
const HIDDEN_ROUTES = [
    '/auth',              // Auth screens
    '/auth/callback',     // OAuth callback
];

/**
 * Floating Action Button for the chatbot.
 *
 * - 56×56 circle, absolute position bottom-right
 * - Animated.spring press effect
 * - Opens ChatbotSheet modal on press
 * - Hidden on auth screens
 */
export function ChatFAB() {
    const [isOpen, setIsOpen] = useState(false);
    const scaleAnim = useRef(new Animated.Value(1)).current;
    const pathname = usePathname();

    // ─── Route-based visibility ───
    const shouldHide = HIDDEN_ROUTES.some((route) =>
        pathname.startsWith(route)
    );

    const handlePressIn = useCallback(() => {
        Animated.spring(scaleAnim, {
            toValue: 0.85,
            useNativeDriver: true,
            friction: 5,
            tension: 80,
        }).start();
    }, [scaleAnim]);

    const handlePressOut = useCallback(() => {
        Animated.spring(scaleAnim, {
            toValue: 1,
            useNativeDriver: true,
            friction: 3,
            tension: 40,
        }).start();
    }, [scaleAnim]);

    const handlePress = useCallback(() => {
        setIsOpen(true);
    }, []);

    const handleClose = useCallback(() => {
        setIsOpen(false);
    }, []);

    if (shouldHide) return null;

    return (
        <>
            {/* FAB button */}
            <Animated.View
                style={[styles.fab, { transform: [{ scale: scaleAnim }] }]}
            >
                <TouchableOpacity
                    style={styles.fabButton}
                    onPress={handlePress}
                    onPressIn={handlePressIn}
                    onPressOut={handlePressOut}
                    activeOpacity={1}
                >
                    <ThemedText style={styles.fabIcon}>🤖</ThemedText>
                </TouchableOpacity>
            </Animated.View>

            {/* Chatbot modal */}
            <ChatbotSheet visible={isOpen} onClose={handleClose} />
        </>
    );
}
ChatFAB.displayName = 'ChatFAB';

const styles = StyleSheet.create({
    fab: {
        position: 'absolute',
        bottom: 90,
        right: 16,
        zIndex: 100,
    },
    fabButton: {
        width: 56,
        height: 56,
        borderRadius: 28,
        backgroundColor: Colors.primary,
        justifyContent: 'center',
        alignItems: 'center',
        shadowColor: Colors.primary,
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.5,
        shadowRadius: 12,
        elevation: 8,
    },
    fabIcon: {
        fontSize: 28,
    },
});
