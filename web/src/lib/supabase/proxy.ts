import { NextResponse, type NextRequest } from 'next/server';
import { decodeJwt } from 'jose';

export async function updateSession(request: NextRequest) {
  const supabaseResponse = NextResponse.next({ request });
  const { pathname } = request.nextUrl;

  // 1. PUBLIC PATH GUARD
  const publicPaths = ['/citizen/auth', '/officer/auth', '/admin/auth', '/', '/citizen/laws'];
  const isPublicPath = publicPaths.some((p) => {
    if (p === '/') return pathname === '/';
    return pathname === p || pathname.startsWith(p + '/');
  });

  if (isPublicPath) {
    return supabaseResponse;
  }

  // 2. JWT EXTRACTION (SDK-FREE)
  // Supabase SSR uses a cookie naming convention: sb-[project-id]-auth-token
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const projectId = supabaseUrl.split('.')[0].split('//')[1];
  const cookieName = `sb-${projectId}-auth-token`;
  const cookie = request.cookies.get(cookieName);

  let sessionData = null;
  let accessToken = null;

  if (cookie?.value) {
    try {
      // Supabase SSR cookies are often encoded JSON or chunks
      // This is a simplified check for the presence of a session
      sessionData = JSON.parse(cookie.value);
      accessToken = sessionData?.access_token;
    } catch {
      // Handle cases where cookie might be chunked or different format
      accessToken = null;
    }
  }

  // 3. SECURE REDIRECTS
  if (!accessToken) {
    let loginUrl = '/citizen/auth/sign-in';
    if (pathname.startsWith('/officer')) loginUrl = '/officer/auth/sign-in';
    if (pathname.startsWith('/admin')) loginUrl = '/admin/auth/sign-in';
    
    const url = request.nextUrl.clone();
    url.pathname = loginUrl;
    return NextResponse.redirect(url);
  }

  // 4. RBAC (DECODING ONLY)
  try {
    const payload: any = decodeJwt(accessToken);
    const userRole = payload?.app_metadata?.role || 'citizen';

    // Enforce role-based routing
    if (pathname.startsWith('/officer') && userRole === 'citizen') {
      return NextResponse.redirect(new URL('/citizen/dashboard', request.url));
    }
    if (pathname.startsWith('/admin') && userRole !== 'admin') {
      return NextResponse.redirect(new URL('/citizen/dashboard', request.url));
    }
  } catch (e) {
    console.log('[NCIA Middleware] JWT Decode Error:', e);
    // On decode error, we fall back to letting the Server Component verify
  }

  return supabaseResponse;
}
