import React from 'react';
import { Text, TextProps, StyleSheet } from 'react-native';
import { Colors } from '../constants/Colors';
import { Typography } from '../constants/Theme';

interface ThemedTextProps extends TextProps {
    variant?: 'hero' | 'h1' | 'h2' | 'h3' | 'body' | 'caption' | 'muted' | 'label';
    color?: string;
    weight?: 'light' | 'regular' | 'semibold' | 'extrabold';
    align?: 'left' | 'center' | 'right';
}

export const ThemedText: React.FC<ThemedTextProps> = ({
    variant = 'body',
    color,
    weight,
    align,
    style,
    children,
    ...props
}) => {
    const variantStyles = {
        hero: { fontSize: Typography.sizes.hero, fontFamily: Typography.fontFamily.extrabold, color: Colors.textMain },
        h1: { fontSize: Typography.sizes.xxxl, fontFamily: Typography.fontFamily.extrabold, color: Colors.textMain },
        h2: { fontSize: Typography.sizes.xxl, fontFamily: Typography.fontFamily.semibold, color: Colors.textMain },
        h3: { fontSize: Typography.sizes.xl, fontFamily: Typography.fontFamily.semibold, color: Colors.textMain },
        body: { fontSize: Typography.sizes.md, fontFamily: Typography.fontFamily.regular, color: Colors.textMain },
        caption: { fontSize: Typography.sizes.sm, fontFamily: Typography.fontFamily.regular, color: Colors.textMuted },
        muted: { fontSize: Typography.sizes.md, fontFamily: Typography.fontFamily.regular, color: Colors.textMuted },
        label: { fontSize: Typography.sizes.xs, fontFamily: Typography.fontFamily.semibold, color: Colors.textMuted, textTransform: 'uppercase' as const, letterSpacing: 1 },
    };

    const weightMap = weight ? { fontFamily: Typography.fontFamily[weight] } : {};

    return (
        <Text
            style={[
                variantStyles[variant],
                weightMap,
                color ? { color } : {},
                align ? { textAlign: align } : {},
                style,
            ]}
            {...props}
        >
            {children}
        </Text>
    );
};
