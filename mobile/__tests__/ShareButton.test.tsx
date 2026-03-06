/**
 * Tests for components/ShareButton.tsx
 *
 * - Renders the share icon button
 * - Calls Share.share with the correct message on press
 * - Handles user dismissal gracefully (no error thrown)
 */

import React from 'react';
import { TouchableOpacity, Share, StyleSheet, Platform } from 'react-native';
import { render, fireEvent, waitFor } from '@testing-library/react-native';

// Import component after mocks
import { ShareButton } from '../components/ShareButton';

describe('ShareButton', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders the share button', () => {
        const { getByRole, toJSON } = render(
            <ShareButton
                title="Test Title"
                message="Test message"
            />
        );

        // Should render without crashing
        expect(toJSON()).toBeTruthy();
    });

    it('calls Share.share with correct message on press', async () => {
        const shareSpy = jest.spyOn(Share, 'share').mockResolvedValue({
            action: Share.sharedAction,
            activityType: undefined,
        });

        const { root } = render(
            <ShareButton
                title="Predicción"
                message="🏇 Hipódromo Chile — Carrera 3: Mi pick es Tornado"
                url="https://pista-inteligente.vercel.app/programa"
            />
        );

        // Find and press the touchable
        const touchable = root;
        await waitFor(() => {
            fireEvent.press(touchable);
        });

        expect(shareSpy).toHaveBeenCalledTimes(1);

        const shareCall = shareSpy.mock.calls[0][0];
        expect(shareCall.message).toContain('Tornado');

        shareSpy.mockRestore();
    });

    it('handles user dismissal silently (no error thrown)', async () => {
        const shareSpy = jest.spyOn(Share, 'share').mockRejectedValue(
            new Error('User did not share')
        );

        const { root } = render(
            <ShareButton
                title="Test"
                message="Test message"
            />
        );

        // Press should not throw even though Share.share rejects
        await waitFor(() => {
            fireEvent.press(root);
        });

        // No error should have been thrown — component handles it silently
        expect(shareSpy).toHaveBeenCalledTimes(1);

        shareSpy.mockRestore();
    });

    it('handles unexpected Share errors without crashing', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });
        const shareSpy = jest.spyOn(Share, 'share').mockRejectedValue(
            new Error('Unexpected platform error')
        );

        const { root } = render(
            <ShareButton
                title="Test"
                message="Test message"
            />
        );

        await waitFor(() => {
            fireEvent.press(root);
        });

        expect(consoleSpy).toHaveBeenCalledWith(
            expect.stringContaining('[ShareButton]'),
            expect.any(Error)
        );

        shareSpy.mockRestore();
        consoleSpy.mockRestore();
    });
});
