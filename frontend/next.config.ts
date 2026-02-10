import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Production optimizations
  output: 'standalone',
  compress: true, // Enable gzip compression for better performance

  // Image optimization
  images: {
    unoptimized: true, // For static export compatibility
  },

  // Disable x-powered-by header for security
  poweredByHeader: false,

  // Enable strict mode for better debugging
  reactStrictMode: true,

  // Experimental features for performance
  experimental: {
    optimizePackageImports: ['lucide-react', 'date-fns', 'lodash'], // Optimize common heavy libraries
  },

  // Security Headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://va.vercel-scripts.com; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data: https:; font-src 'self' data:; connect-src 'self' https://bxdxztbdsxyyvvavvtoo.supabase.co https://vitals.vercel-insights.com;",
          },
        ],
      },
    ];
  },

  // Ignore build errors for faster deployment
  // TODO: Remove this once technical debt is cleared to ensure type safety
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
