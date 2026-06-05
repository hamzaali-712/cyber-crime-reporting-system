import { jwtVerify } from 'jose';
import { type NextRequest } from 'next/server';

/**
 * Pure Edge JWT validation for NCIA Portal.
 * Zero Supabase SDK dependencies.
 */
export async function getEdgeSession(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const projectId = supabaseUrl.split('.')[0].split('//')[1];
  const cookieName = `sb-${projectId}-auth-token`;
  const cookie = request.cookies.get(cookieName);

  if (!cookie?.value) return null;

  try {
    const sessionData = JSON.parse(cookie.value);
    const token = sessionData?.access_token;

    if (!token) return null;

    // Use JWT_SECRET_KEY as the Supabase JWT Secret
    // Note: In production, ensure this is the actual Supabase JWT Secret from dashboard
    const secret = new TextEncoder().encode(process.env.JWT_SECRET_KEY || '');
    
    const { payload } = await jwtVerify(token, secret);
    
    return {
      user: payload,
      role: (payload as any)?.app_metadata?.role || 'citizen',
      userId: payload.sub
    };
  } catch (error) {
    // Decoding without verification if secret is missing or invalid in dev
    // But we prioritize security for prod-ready stance
    return null;
  }
}

export const publicPaths = ['/citizen/auth', '/officer/auth', '/admin/auth', '/', '/citizen/laws'];

export function isPublicPath(pathname: string) {
  return publicPaths.some((p) => {
    if (p === '/') return pathname === '/';
    return pathname === p || pathname.startsWith(p + '/');
  });
}
