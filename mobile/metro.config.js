// @ts-nocheck
const { getDefaultConfig } = require('expo/metro-config');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);

// Configurar opciones de minificación agresivas para ofuscar mejor el código
config.transformer.minifierConfig = {
    compress: {
        // Apply more aggressive compression
        drop_console: true,
    },
    mangle: {
        toplevel: true, // Mangle top-level variable names
        keep_classnames: false,
        keep_fnames: false,
    },
};

module.exports = config;
