import { NextRequest, NextResponse } from 'next/server';

/**
 * Health check endpoint for Kubernetes probes.
 *
 * - GET /api/health: Basic liveness check (just returns healthy status)
 * - GET /api/health?full=1: Full readiness check (includes backend connectivity)
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const full = searchParams.get('full');

  const response: {
    status: string;
    version: string;
    timestamp: string;
    checks?: Record<string, string>;
  } = {
    status: 'healthy',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  };

  // If full check requested, verify backend connectivity
  if (full === '1') {
    const checks: Record<string, string> = {};

    try {
      // Check backend API connectivity
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

      const backendResponse = await fetch(`${backendUrl}/health`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (backendResponse.ok) {
        checks.backend = 'reachable';
      } else {
        checks.backend = 'unhealthy';
        response.status = 'unhealthy';
      }
    } catch (error) {
      checks.backend = 'unreachable';
      response.status = 'unhealthy';
    }

    response.checks = checks;

    // Return 503 if unhealthy for readiness probe
    if (response.status === 'unhealthy') {
      return NextResponse.json(response, { status: 503 });
    }
  }

  return NextResponse.json(response);
}
