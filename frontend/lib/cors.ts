import { NextResponse } from 'next/server';

/**
 * CORS headers for API routes.
 *
 * Allows requests from the mobile app and any configured origins.
 * Configurable via ALLOWED_ORIGINS env var (comma-separated).
 * Defaults to '*' (allow all origins) if not set.
 */
function getCorsHeaders(): Record<string, string> {
    const allowedOrigins = process.env.ALLOWED_ORIGINS || '*';

    return {
        'Access-Control-Allow-Origin': allowedOrigins,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };
}

/**
 * Handle CORS preflight OPTIONS request.
 * Export this as `OPTIONS` in any route.ts that needs CORS.
 */
export function corsOptionsResponse(): NextResponse {
    return new NextResponse(null, {
        status: 200,
        headers: getCorsHeaders(),
    });
}

/**
 * Add CORS headers to a NextResponse.
 * Use this to wrap your existing response.
 *
 * @example
 * ```ts
 * import { withCors, corsOptionsResponse } from '@/lib/cors';
 *
 * export const OPTIONS = corsOptionsResponse;
 *
 * export async function GET() {
 *   return withCors(NextResponse.json({ data: 'hello' }));
 * }
 * ```
 */
export function withCors(response: NextResponse): NextResponse {
    const headers = getCorsHeaders();
    for (const [key, value] of Object.entries(headers)) {
        response.headers.set(key, value);
    }
    return response;
}
