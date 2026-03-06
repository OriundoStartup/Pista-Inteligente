import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, Text } from 'react-native';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

const BANNER_HEIGHT = 36;

/**
 * Offline indicator banner.
 *
 * - Slides in from the top with Animated.timing when offline
 * - Slides out when connection is restored
 * - position: absolute, top: 0 — does NOT displace content
 * - Yellow (#f59e0b) background with dark text
 */
export const OfflineBanner = React.memo(function OfflineBanner() {
    const { isConnected } = useNetworkStatus();
    const translateY = useRef(new Animated.Value(-BANNER_HEIGHT)).current;

    useEffect(() => {
        Animated.timing(translateY, {
            toValue: isConnected ? -BANNER_HEIGHT : 0,
            duration: 300,
            useNativeDriver: true,
        }).start();
    }, [isConnected, translateY]);

    return (
        <Animated.View
            style={[styles.container, { transform: [{ translateY }] }]}
            pointerEvents={isConnected ? 'none' : 'auto'}
        >
            <Text style={styles.text}>
                📡 Sin conexión — mostrando datos en caché
            </Text>
        </Animated.View>
    );
});

OfflineBanner.displayName = 'OfflineBanner';

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: BANNER_HEIGHT,
        backgroundColor: '#f59e0b',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 4,
        elevation: 6,
    },
    text: {
        color: '#1c1917',
        fontSize: 13,
        fontWeight: '600',
        letterSpacing: 0.2,
    },
});
