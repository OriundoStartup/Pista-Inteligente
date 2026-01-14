import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Production optimizations
  output: 'standalone',

  // Image optimization
  images: {
    unoptimized: true, // For static export compatibility
  },

  // Disable x-powered-by header
  poweredByHeader: false,

  // Enable strict mode for better debugging
  reactStrictMode: true,
};

export default nextConfig;
