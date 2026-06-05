import { NextResponse, type NextRequest } from 'next/server';
import { getEdgeSession, isPublicPath } from '@/lib/auth-edge';

/**
 * NCIA GLOBAL PROTECTION LAYER
 * ----------------------------
 * Pure Edge implementation using JWT verification.
 * Zero Supabase SDK leakage. No Node.js APIs.
 */
export default async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Skip if public path
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  // 2. Extract and verify session using Edge JWT
  const session = await getEdgeSession(request);

  // 3. Handle unauthenticated access
  if (!session) {
    let loginUrl = '/citizen/auth/sign-in';
    if (pathname.startsWith('/officer')) loginUrl = '/officer/auth/sign-in';
    if (pathname.startsWith('/admin')) loginUrl = '/admin/auth/sign-in';
    
    const url = request.nextUrl.clone();
    url.pathname = loginUrl;
    return NextResponse.redirect(url);
  }

  // 4. Role-Based Access Control (RBAC)
  const { role } = session;

  if (pathname.startsWith('/officer') && role === 'citizen') {
    return NextResponse.redirect(new URL('/citizen/dashboard', request.url));
  }
  
  if (pathname.startsWith('/admin') && role !== 'admin') {
    return NextResponse.redirect(new URL('/citizen/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - api (API routes)
     * - public assets
     */
    '/((?!_next/static|_next/image|favicon\\.ico|api|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
