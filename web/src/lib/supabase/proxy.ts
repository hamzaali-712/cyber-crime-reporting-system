import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  // GUARD: If env vars are missing or clearly invalid, skip all Supabase calls
  // This prevents the middleware from hanging on unreachable servers
  if (!supabaseUrl || !supabaseKey || supabaseUrl.includes('placeholder')) {
    return supabaseResponse;
  }

  const supabase = createServerClient(
    supabaseUrl,
    supabaseKey,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  const { pathname } = request.nextUrl;

  // Public paths that don't require authentication
  const publicPaths = ['/citizen/auth', '/officer/auth', '/admin/auth', '/', '/citizen/laws'];
  
  const isPublicPath = publicPaths.some((p) => {
    if (p === '/') return pathname === '/';
    return pathname === p || pathname.startsWith(p + '/');
  });

  // For public paths, no auth check needed — return immediately (FAST)
  if (isPublicPath) {
    return supabaseResponse;
  }

  // For protected paths, try to get the user
  let user = null;
  try {
    const { data } = await supabase.auth.getUser();
    user = data?.user ?? null;
  } catch (error) {
    // If Supabase is unreachable, redirect to login instead of hanging
    console.log('[NCIA Middleware] Session verification failed. Redirecting to login.');
    user = null;
  }

  // Not logged in -> redirect to appropriate login page
  if (!user) {
    let loginUrl = '/citizen/auth/sign-in';
    if (pathname.startsWith('/officer')) {
      loginUrl = '/officer/auth/sign-in';
    } else if (pathname.startsWith('/admin')) {
      loginUrl = '/admin/auth/sign-in';
    }
    const url = request.nextUrl.clone();
    url.pathname = loginUrl;
    return NextResponse.redirect(url);
  }

  // Role-based access control
  if (!user) {
    return supabaseResponse;
  }

  try {
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user?.id)
      .single();

    if (profile) {
      if (pathname.startsWith('/officer') && profile.role === 'citizen') {
        return NextResponse.redirect(new URL('/citizen/dashboard', request.url));
      }
      if (pathname.startsWith('/admin') && profile.role !== 'admin') {
        return NextResponse.redirect(new URL('/citizen/dashboard', request.url));
      }
    }
  } catch (error) {
    // If profile check fails, allow access (auth already verified above)
    console.log('[NCIA Middleware] Profile check bypassed.');
  }

  return supabaseResponse;
}
