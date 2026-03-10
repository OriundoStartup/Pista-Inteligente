import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
    View,
    TextInput,
    FlatList,
    TouchableOpacity,
    StyleSheet,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
    Modal,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { ThemedText } from './ThemedText';
import { Colors } from '../constants/Colors';
import { Spacing, BorderRadius } from '../constants/Theme';
import { getEnv } from '../utils/validateEnv';

// ─── Types ───

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

interface ChatbotSheetProps {
    visible: boolean;
    onClose: () => void;
}

// ─── Helpers ───

let messageCounter = 0;

function createMessage(role: 'user' | 'assistant', content: string): ChatMessage {
    return {
        id: `msg_${Date.now()}_${++messageCounter}`,
        role,
        content,
        timestamp: Date.now(),
    };
}

const WELCOME_MESSAGE = createMessage(
    'assistant',
    '¡Hola! 🏇 Soy el asistente de Pista Inteligente.\n\nPuedo ayudarte con:\n• Predicciones de carreras\n• Información sobre jinetes y caballos\n• Cómo funciona nuestro modelo de IA\n\n¿Qué te gustaría saber?'
);

function getApiUrl(): string {
    const env = getEnv();
    const base = env.API_BASE_URL || 'https://pista-inteligente.vercel.app';
    if (!env.API_BASE_URL) {
        console.warn('[ChatbotSheet] API_BASE_URL no definida, usando fallback:', base);
    }
    return `${base}/api/chat`;
}

// ─── Typing indicator ───

function TypingIndicator() {
    return (
        <View style={[styles.messageBubble, styles.assistantBubble]}>
            <View style={styles.typingRow}>
                <View style={[styles.typingDot, styles.typingDot1]} />
                <View style={[styles.typingDot, styles.typingDot2]} />
                <View style={[styles.typingDot, styles.typingDot3]} />
            </View>
        </View>
    );
}

// ─── Message bubble ───

const MessageBubble = React.memo(function MessageBubble({ message }: { message: ChatMessage }) {
    const isUser = message.role === 'user';
    const time = new Date(message.timestamp).toLocaleTimeString('es-CL', {
        hour: '2-digit',
        minute: '2-digit',
    });

    return (
        <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.assistantBubble]}>
            <ThemedText
                variant="body"
                color={isUser ? '#fff' : Colors.textMain}
                style={styles.messageText}
            >
                {message.content}
            </ThemedText>
            <ThemedText
                variant="caption"
                color={isUser ? 'rgba(255,255,255,0.6)' : Colors.textMuted}
                style={styles.messageTime}
            >
                {time}
            </ThemedText>
        </View>
    );
});

MessageBubble.displayName = 'MessageBubble';

// ─── Main component ───

export function ChatbotSheet({ visible, onClose }: ChatbotSheetProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const flatListRef = useRef<FlatList>(null);
    const insets = useSafeAreaInsets();

    const sendMessage = useCallback(async () => {
        const trimmed = input.trim();
        if (!trimmed || isLoading) return;

        const userMsg = createMessage('user', trimmed);
        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch(getApiUrl(), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: trimmed }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            const botMsg = createMessage('assistant', data.response || 'Sin respuesta del servidor.');
            setMessages((prev) => [...prev, botMsg]);
        } catch (err: any) {
            console.error('[ChatbotSheet] API error:', err);
            const errorMsg = createMessage(
                'assistant',
                '⚠️ No pude conectar con el servidor. Revisa tu conexión e intenta de nuevo.'
            );
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading]);

    const handleSend = useCallback(() => {
        sendMessage();
    }, [sendMessage]);

    const renderMessage = useCallback(
        ({ item }: { item: ChatMessage }) => <MessageBubble message={item} />,
        []
    );

    const keyExtractor = useCallback((item: ChatMessage) => item.id, []);

    // Inverted FlatList shows newest at bottom — data must be reversed
    const invertedMessages = React.useMemo(
        () => [...messages].reverse(),
        [messages]
    );

    return (
        <Modal
            visible={visible}
            onRequestClose={onClose}
            animationType="slide"
            presentationStyle={Platform.OS === 'ios' ? 'pageSheet' : 'fullScreen'}
            transparent={false}
        >
            <View style={styles.container}>
                <KeyboardAvoidingView
                    behavior={Platform.OS === 'ios' ? 'padding' : undefined}
                    style={styles.keyboardView}
                    keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
                >
                    {/* ─── Header ─── */}
                    <View style={[styles.header, { paddingTop: Math.max(Spacing.lg, insets.top) }]}>
                        <View style={styles.headerLeft}>
                            <ThemedText style={{ fontSize: 24 }}>🤖</ThemedText>
                            <View>
                                <ThemedText variant="body" weight="semibold">
                                    Asistente Hípico
                                </ThemedText>
                                <ThemedText
                                    variant="caption"
                                    color={isLoading ? Colors.accent : Colors.success}
                                >
                                    {isLoading ? 'Escribiendo...' : 'En línea'}
                                </ThemedText>
                            </View>
                        </View>
                        <TouchableOpacity
                            onPress={onClose}
                            hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
                            style={styles.closeButton}
                        >
                            <Ionicons name="close" size={22} color={Colors.textMuted} />
                        </TouchableOpacity>
                    </View>

                    {/* ─── Messages (inverted FlatList) ─── */}
                    <FlatList
                        ref={flatListRef}
                        data={invertedMessages}
                        keyExtractor={keyExtractor}
                        renderItem={renderMessage}
                        inverted
                        style={styles.messagesList}
                        contentContainerStyle={styles.messagesContent}
                        keyboardDismissMode="interactive"
                        keyboardShouldPersistTaps="handled"
                        showsVerticalScrollIndicator={false}
                        ListHeaderComponent={isLoading ? <TypingIndicator /> : null}
                    />

                    {/* ─── Input footer ─── */}
                    <View style={[
                        styles.inputRow,
                        { paddingBottom: Math.max(Spacing.md, insets.bottom + (Platform.OS === 'android' ? 4 : 0)) }
                    ]}>
                        <TextInput
                            style={styles.textInput}
                            value={input}
                            onChangeText={setInput}
                            placeholder="Pregunta sobre una carrera..."
                            placeholderTextColor={Colors.textMuted}
                            editable={!isLoading}
                            returnKeyType="send"
                            onSubmitEditing={handleSend}
                            multiline
                            maxLength={500}
                            blurOnSubmit={false}
                        />
                        <TouchableOpacity
                            style={[
                                styles.sendButton,
                                (!input.trim() || isLoading) && styles.sendButtonDisabled,
                            ]}
                            onPress={handleSend}
                            disabled={!input.trim() || isLoading}
                            activeOpacity={0.7}
                        >
                            <Ionicons
                                name="send"
                                size={18}
                                color={!input.trim() || isLoading ? 'rgba(255,255,255,0.3)' : '#fff'}
                            />
                        </TouchableOpacity>
                    </View>
                </KeyboardAvoidingView>
            </View>
        </Modal>
    );
}

// ─── Styles ───

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: Colors.bgDark,
    },
    keyboardView: {
        flex: 1,
    },

    // Header
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: Spacing.lg,
        borderBottomWidth: 1,
        borderBottomColor: Colors.borderGlass,
        backgroundColor: Colors.bgCardSolid,
    },
    headerLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: Spacing.md,
    },
    closeButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: 'rgba(255,255,255,0.08)',
        justifyContent: 'center',
        alignItems: 'center',
    },

    // Messages
    messagesList: {
        flex: 1,
    },
    messagesContent: {
        padding: Spacing.lg,
        gap: Spacing.sm,
    },
    messageBubble: {
        maxWidth: '82%',
        padding: Spacing.md,
        borderRadius: BorderRadius.lg,
        marginBottom: Spacing.xs,
    },
    userBubble: {
        alignSelf: 'flex-end',
        backgroundColor: Colors.primary,
        borderBottomRightRadius: 4,
    },
    assistantBubble: {
        alignSelf: 'flex-start',
        backgroundColor: Colors.bgCardSolid,
        borderBottomLeftRadius: 4,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
    },
    messageText: {
        lineHeight: 20,
    },
    messageTime: {
        fontSize: 10,
        marginTop: 4,
        textAlign: 'right',
    },

    // Typing indicator
    typingRow: {
        flexDirection: 'row',
        gap: 4,
        paddingVertical: 4,
        paddingHorizontal: 2,
    },
    typingDot: {
        width: 8,
        height: 8,
        borderRadius: 4,
        backgroundColor: Colors.textMuted,
        opacity: 0.5,
    },
    typingDot1: { opacity: 0.3 },
    typingDot2: { opacity: 0.5 },
    typingDot3: { opacity: 0.7 },

    // Input
    inputRow: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        padding: Spacing.md,
        gap: Spacing.sm,
        borderTopWidth: 1,
        borderTopColor: Colors.borderGlass,
        backgroundColor: Colors.bgCardSolid,
    },
    textInput: {
        flex: 1,
        backgroundColor: Colors.bgDark,
        borderRadius: BorderRadius.md,
        paddingVertical: Platform.OS === 'ios' ? Spacing.md : Spacing.sm,
        paddingHorizontal: Spacing.lg,
        color: Colors.textMain,
        fontFamily: 'Outfit_400Regular',
        fontSize: 14,
        borderWidth: 1,
        borderColor: Colors.borderGlass,
        maxHeight: 100,
        minHeight: 40,
    },
    sendButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: Colors.primary,
        justifyContent: 'center',
        alignItems: 'center',
    },
    sendButtonDisabled: {
        backgroundColor: 'rgba(139, 92, 246, 0.3)',
    },
});
