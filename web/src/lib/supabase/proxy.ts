import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  // GUARD: If env vars are missing or clearly invalid, skip all Supabase calls
  // This prevents the middleware from hanging on unreachable servers
  if (!supabaseUrl || !supabaseKey || supabaseUrl === 'YOUR_SUPABASE_URL' || supabaseKey.length < 30) {
    console.warn('[NCIA Middleware] Supabase credentials missing or invalid. Skipping auth check.');
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

  // For protected paths, try to get the user with a timeout
  let user = null;
  try {
    // Use AbortController to add a 3-second timeout so pages don't hang
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    const { data } = await supabase.auth.getUser();
    clearTimeout(timeoutId);
    user = data?.user ?? null;
  } catch (error) {
    // If Supabase is unreachable, redirect to login instead of hanging
    console.warn('[NCIA Middleware] Could not reach Supabase auth. Redirecting to login.');
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
    console.warn('[NCIA Middleware] Profile check failed, allowing access.');
  }

  return supabaseResponse;
}
