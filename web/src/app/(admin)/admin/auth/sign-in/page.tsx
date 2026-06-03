'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldAlert, Lock, ArrowRight, Settings, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

const adminSignInSchema = z.object({
  email: z.string().email('Valid Admin Email required'),
  password: z.string().min(1, 'Password is required'),
  security_token: z.string().min(1, 'Security Token required'),
});

type AdminSignInData = z.infer<typeof adminSignInSchema>;

export default function AdminSignInPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AdminSignInData>({
    resolver: zodResolver(adminSignInSchema),
  });

  const onSubmit = async (data: AdminSignInData) => {
    setIsLoading(true);
    setConnectionError(false);
    try {
      const { data: authData, error } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      });

      if (error) {
        toast.error('Authentication Failed', { description: error.message });
        return;
      }

      // Verify if user is actually an admin
      const { data: profile, error: profileError } = await supabase
        .from('profiles')
        .select('role')
        .eq('id', authData.user.id)
        .single();

      if (profileError || profile?.role !== 'admin') {
        await supabase.auth.signOut();
        toast.error('Access Denied', { description: 'This account does not have administrative privileges.' });
        return;
      }

      toast.success('Root Access Granted', { description: 'Authenticated with system administrator privileges.' });
      router.push('/admin/dashboard');
      router.refresh();
    } catch (error: any) {
      if (error?.message?.includes('fetch') || error?.message?.includes('network') || error?.name === 'TypeError') {
        setConnectionError(true);
        toast.error('Connection Error', {
          description: 'Cannot connect to the authentication server. Check your Supabase configuration.',
          duration: 8000,
        });
      } else {
        toast.error('Secure Link Failure', { description: 'Connection to NCIA root servers interrupted.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-red-500/5 blur-[120px] rounded-full" />
      <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-blue-500/5 blur-[120px] rounded-full" />
      
      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center h-20 w-20 rounded-3xl bg-red-600 shadow-2xl shadow-red-500/30 mb-6 border border-red-400/20 animate-pulse">
            <Lock className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight italic">ADMIN <span className="text-red-600">ROOT</span></h1>
          <p className="text-slate-400 mt-3 font-semibold uppercase tracking-widest text-[10px]">NCIA Master Control Protocol</p>
        </div>

        {/* Connection Error Banner */}
        {connectionError && (
          <div className="mb-6 p-4 bg-red-950/50 border border-red-800/50 rounded-xl flex items-start gap-3 animate-in fade-in duration-300">
            <AlertTriangle className="h-5 w-5 text-red-400 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-bold text-red-300">Server Connection Failed</p>
              <p className="text-xs text-red-400 mt-1 leading-relaxed">
                Cannot reach the authentication server. Verify your Supabase credentials in 
                <code className="bg-red-900/50 px-1 rounded mx-1">web/.env.local</code>. 
                Ensure <strong>NEXT_PUBLIC_SUPABASE_URL</strong> and <strong>NEXT_PUBLIC_SUPABASE_ANON_KEY</strong> are correct.
              </p>
            </div>
          </div>
        )}

        <Card className="bg-[#0f172a]/90 border-red-900/30 backdrop-blur-xl shadow-3xl ring-1 ring-white/5 border-t-2 border-t-red-600">
          <CardHeader className="pb-8 border-b border-slate-700/30">
            <CardTitle className="text-white flex items-center gap-2">
               System Authentication <Settings className="h-5 w-5 text-red-500" />
            </CardTitle>
            <CardDescription className="text-slate-400">Master access for global system administration.</CardDescription>
          </CardHeader>
          <CardContent className="pt-8">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="relative">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 block">Root Email</label>
                <Input
                  placeholder="admin@ncia.gov.pk"
                  {...register('email')}
                  error={errors.email?.message}
                  className="bg-slate-900/50 border-slate-700 text-slate-200 pl-10 h-12 focus:ring-red-500/20 focus:border-red-500 transition-all shadow-inner"
                />
                <ShieldAlert className="absolute left-3 top-[37px] h-4 w-4 text-slate-500" />
              </div>

              <div className="relative">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 block">Master Password</label>
                <Input
                  placeholder="••••••••"
                  type="password"
                  {...register('password')}
                  error={errors.password?.message}
                  className="bg-slate-900/50 border-slate-700 text-slate-200 pl-10 h-12 focus:ring-red-500/20 focus:border-red-500 transition-all shadow-inner"
                />
                <Lock className="absolute left-3 top-[37px] h-4 w-4 text-slate-500" />
              </div>

              <div className="relative">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 block">2FA Security Token</label>
                <Input
                  placeholder="X-772-BASE-9"
                  {...register('security_token')}
                  error={errors.security_token?.message}
                  className="bg-slate-900/50 border-slate-700 text-slate-200 pl-10 h-12 focus:ring-red-500/20 focus:border-red-500 transition-all shadow-inner"
                />
                <AlertTriangle className="absolute left-3 top-[37px] h-4 w-4 text-slate-500" />
              </div>

              <Button type="submit" className="w-full bg-red-600 hover:bg-red-500 h-12 text-base font-bold shadow-lg shadow-red-900/20 group" loading={isLoading}>
                Initialize Root Access
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-4 border-t border-slate-700/30 mt-4 pt-6 text-center">
            <p className="text-[10px] text-red-500/50 font-black leading-relaxed uppercase tracking-tighter">
              UNAUTHORIZED ACCESS TO ROOT IS A CAPITAL OFFENSE UNDER PECA 2016 SECTION 3.
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
