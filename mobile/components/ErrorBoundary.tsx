import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, StyleSheet, TouchableOpacity, ScrollView, Text } from 'react-native';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

/**
 * Global Error Boundary — class component (required by React).
 *
 * Catches unhandled JS errors in the component tree and shows
 * either a custom fallback or a built-in recovery screen.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <App />
 *   </ErrorBoundary>
 *
 *   <ErrorBoundary fallback={<MyCustomError />}>
 *     <RiskyComponent />
 *   </ErrorBoundary>
 */
export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        this.setState({ errorInfo });
        console.error('[ErrorBoundary] Uncaught error:', error);
        console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);
    }

    handleRetry = (): void => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render(): ReactNode {
        if (!this.state.hasError) {
            return this.props.children;
        }

        // Custom fallback takes priority
        if (this.props.fallback) {
            return this.props.fallback;
        }

        const isDev = process.env.NODE_ENV === 'development';

        return (
            <View style={styles.container}>
                <View style={styles.content}>
                    {/* Warning icon */}
                    <Text style={styles.icon}>⚠️</Text>

                    <ThemedText variant="h2" weight="extrabold" align="center">
                        ¡Algo salió mal!
                    </ThemedText>

                    <ThemedText
                        variant="muted"
                        align="center"
                        style={styles.description}
                    >
                        La aplicación encontró un error inesperado.{'\n'}
                        Puedes intentar recargar o reiniciar la app.
                    </ThemedText>

                    {/* Stack trace — only in development */}
                    {isDev && this.state.error && (
                        <ScrollView
                            style={styles.errorBox}
                            showsVerticalScrollIndicator
                        >
                            <Text style={styles.errorTitle}>
                                {this.state.error.name}: {this.state.error.message}
                            </Text>
                            {this.state.error.stack && (
                                <Text style={styles.stackText}>
                                    {this.state.error.stack.slice(0, 600)}
                                </Text>
                            )}
                            {this.state.errorInfo?.componentStack && (
                                <Text style={styles.stackText}>
                                    {'\n'}Component Stack:
                                    {this.state.errorInfo.componentStack.slice(0, 400)}
                                </Text>
                            )}
                        </ScrollView>
                    )}

                    {/* Retry button */}
                    <TouchableOpacity
                        style={styles.retryButton}
                        onPress={this.handleRetry}
                        activeOpacity={0.85}
                    >
                        <ThemedText variant="body" weight="semibold" color="#fff">
                            🔄 Reintentar
                        </ThemedText>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
        justifyContent: 'center',
        alignItems: 'center',
        padding: Spacing.xl,
    },
    content: {
        alignItems: 'center',
        maxWidth: 360,
        gap: Spacing.md,
    },
    icon: {
        fontSize: 56,
        marginBottom: Spacing.sm,
    },
    description: {
        lineHeight: 22,
        maxWidth: 300,
    },
    errorBox: {
        maxHeight: 180,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        borderRadius: BorderRadius.md,
        borderWidth: 1,
        borderColor: 'rgba(239, 68, 68, 0.3)',
        padding: Spacing.md,
        width: '100%',
        marginTop: Spacing.sm,
    },
    errorTitle: {
        color: Colors.accent,
        fontFamily: 'monospace',
        fontSize: 12,
        fontWeight: '700',
        marginBottom: 6,
    },
    stackText: {
        color: Colors.textMuted,
        fontFamily: 'monospace',
        fontSize: 10,
        lineHeight: 15,
    },
    retryButton: {
        backgroundColor: Colors.primary,
        paddingVertical: Spacing.lg,
        paddingHorizontal: Spacing.xxl,
        borderRadius: 50,
        marginTop: Spacing.xl,
        shadowColor: Colors.primary,
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.4,
        shadowRadius: 16,
        elevation: 8,
    },
});
