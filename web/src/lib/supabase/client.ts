import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    if (typeof window !== 'undefined') {
      console.error('CRITICAL: Supabase environment variables are missing in the browser!');
    }
    // Return a dummy client during build to prevent prerender crash
    return createBrowserClient('https://placeholder.supabase.co', 'placeholder');
  }

  return createBrowserClient(url, key);
}
