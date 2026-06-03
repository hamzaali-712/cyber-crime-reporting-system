'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldAlert, BadgeInfo, Lock, ArrowRight, ShieldCheck, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

const officerSignInSchema = z.object({
  officer_id: z.string().min(5, 'Valid Officer ID required'),
  password: z.string().min(1, 'Password is required'),
});

type OfficerSignInData = z.infer<typeof officerSignInSchema>;

export default function OfficerSignInPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<OfficerSignInData>({
    resolver: zodResolver(officerSignInSchema),
  });

  const onSubmit = async (data: OfficerSignInData) => {
    setIsLoading(true);
    setConnectionError(false);
    try {
      // Find the email associated with this Officer ID first
      const { data: officer, error: findError } = await supabase
        .from('officers')
        .select('id, profiles(email)')
        .eq('officer_id', data.officer_id)
        .single();

      if (findError || !officer?.profiles) {
        // Check if it's a connection error vs actual "not found"
        if (findError?.message?.includes('fetch') || findError?.message?.includes('Failed') || findError?.code === 'PGRST301') {
          setConnectionError(true);
          toast.error('Connection Error', {
            description: 'Cannot connect to the database. Please check your Supabase configuration.',
            duration: 8000,
          });
        } else {
          toast.error('Access Denied', { description: 'Officer ID not found in system. Make sure the officer account exists in the database.' });
        }
        return;
      }

      // Sign in with the found email
      const { error } = await supabase.auth.signInWithPassword({
        email: (officer.profiles as any).email,
        password: data.password,
      });

      if (error) {
        toast.error('Authentication Failed', { description: error.message });
        return;
      }

      toast.success('System Access Granted', { description: 'Authenticated with officer privileges.' });
      router.push('/officer/dashboard');
      router.refresh();
    } catch (error: any) {
      if (error?.message?.includes('fetch') || error?.message?.includes('network') || error?.name === 'TypeError') {
        setConnectionError(true);
        toast.error('Connection Error', {
          description: 'Cannot connect to the authentication server. Check your Supabase configuration.',
          duration: 8000,
        });
      } else {
        toast.error('Secure Link Failure', { description: 'Connection to NCIA servers interrupted.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a] p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-blue-500/5 blur-[120px] rounded-full" />
      <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-indigo-500/5 blur-[120px] rounded-full" />
      
      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center h-20 w-20 rounded-3xl bg-blue-600 shadow-2xl shadow-blue-500/30 mb-6 border border-blue-400/20">
            <ShieldAlert className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight">Officer Portal</h1>
          <p className="text-slate-400 mt-3 font-semibold uppercase tracking-widest text-[10px]">NCIA Secure Operations Gateway</p>
        </div>

        {/* Connection Error Banner */}
        {connectionError && (
          <div className="mb-6 p-4 bg-red-950/50 border border-red-800/50 rounded-xl flex items-start gap-3 animate-in fade-in duration-300">
            <AlertTriangle className="h-5 w-5 text-red-400 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-bold text-red-300">Server Connection Failed</p>
              <p className="text-xs text-red-400 mt-1 leading-relaxed">
                Cannot reach the database server. Verify your Supabase credentials in 
                <code className="bg-red-900/50 px-1 rounded mx-1">web/.env.local</code>. 
                Also ensure the <strong>officers</strong> table exists with seed data.
              </p>
            </div>
          </div>
        )}

        <Card className="bg-[#1e293b]/90 border-slate-700/50 backdrop-blur-xl shadow-3xl ring-1 ring-white/5">
          <CardHeader className="pb-8 border-b border-slate-700/30">
            <CardTitle className="text-white flex items-center gap-2">
               Access Control <ShieldCheck className="h-5 w-5 text-emerald-400" />
            </CardTitle>
            <CardDescription className="text-slate-400">Restricted to authorized law enforcement personnel only.</CardDescription>
          </CardHeader>
          <CardContent className="pt-8">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="relative">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 block">Official Officer ID</label>
                <Input
                  placeholder="e.g. CYBER2024AHME001"
                  {...register('officer_id')}
                  error={errors.officer_id?.message}
                  className="bg-slate-900/50 border-slate-700 text-slate-200 pl-10 h-12 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-inner"
                />
                <BadgeInfo className="absolute left-3 top-[37px] h-4 w-4 text-slate-500" />
              </div>

              <div className="relative">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 block">Security Password</label>
                <Input
                  placeholder="••••••••"
                  type="password"
                  {...register('password')}
                  error={errors.password?.message}
                  className="bg-slate-900/50 border-slate-700 text-slate-200 pl-10 h-12 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-inner"
                />
                <Lock className="absolute left-3 top-[37px] h-4 w-4 text-slate-500" />
              </div>

              <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-500 h-12 text-base font-bold shadow-lg shadow-blue-900/20 group" loading={isLoading}>
                Authorize Access
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-4 border-t border-slate-700/30 mt-4 pt-6 text-center">
            <p className="text-[10px] text-slate-500 font-medium leading-relaxed max-w-[280px]">
              Access to this system is logged and monitored. Unauthorized attempts are punishable under Section 3 of PECA 2016.
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
