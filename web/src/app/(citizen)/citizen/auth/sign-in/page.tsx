'use client';

export const dynamic = 'force-dynamic';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldAlert, Mail, Lock, ArrowRight, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

import { signInSchema, type SignInFormData } from '@/lib/validations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

export default function CitizenSignInPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignInFormData>({
    resolver: zodResolver(signInSchema),
  });

  const onSubmit = async (data: SignInFormData) => {
    setIsLoading(true);
    setConnectionError(false);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      });

      if (error) {
        toast.error('Authentication Failed', {
          description: error.message,
        });
        return;
      }

      toast.success('Welcome back!', {
        description: 'You have successfully signed in.',
      });
      router.push('/citizen/dashboard');
      router.refresh();
    } catch (error: any) {
      if (error?.message?.includes('fetch') || error?.message?.includes('network') || error?.name === 'TypeError') {
        setConnectionError(true);
        toast.error('Connection Error', {
          description: 'Cannot connect to the authentication server. Check your Supabase configuration.',
          duration: 8000,
        });
      } else {
        toast.error('Something went wrong', {
          description: error?.message || 'An unexpected error occurred.',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50/50 p-4">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-blue-600 shadow-xl shadow-blue-200 mb-4">
            <ShieldAlert className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Citizen Portal</h1>
          <p className="text-gray-500 mt-2">National Cyber Crime Reporting System</p>
        </div>

        {/* Connection Error Banner */}
        {connectionError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3 animate-in fade-in duration-300">
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-bold text-red-800">Server Connection Failed</p>
              <p className="text-xs text-red-600 mt-1 leading-relaxed">
                Cannot reach the authentication server. Please verify your 
                <code className="bg-red-100 px-1 rounded mx-1">NEXT_PUBLIC_SUPABASE_URL</code> and 
                <code className="bg-red-100 px-1 rounded mx-1">NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in 
                <code className="bg-red-100 px-1 rounded ml-1">web/.env.local</code>.
              </p>
            </div>
          </div>
        )}

        <Card className="shadow-xl border-gray-200/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>Enter your credentials to access your account</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="relative">
                <Input
                  label="Email Address"
                  placeholder="name@example.com"
                  type="email"
                  {...register('email')}
                  error={errors.email?.message}
                  className="pl-10"
                />
                <Mail className="absolute left-3 top-[34px] h-4 w-4 text-gray-400" />
              </div>

              <div className="relative">
                <Input
                  label="Password"
                  placeholder="••••••••"
                  type="password"
                  {...register('password')}
                  error={errors.password?.message}
                  className="pl-10"
                />
                <Lock className="absolute left-3 top-[34px] h-4 w-4 text-gray-400" />
              </div>

              <div className="flex justify-end">
                <Link 
                  href="/citizen/auth/forgot-password" 
                  className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" className="w-full group" loading={isLoading}>
                Sign In
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-4 border-t border-gray-100 mt-2 pt-6">
            <p className="text-sm text-center text-gray-600">
              Don't have an account?{' '}
              <Link 
                href="/citizen/auth/sign-up" 
                className="font-bold text-blue-600 hover:text-blue-700 transition-colors"
              >
                Create an account
              </Link>
            </p>
          </CardFooter>
        </Card>

        {/* Legal Disclaimer */}
        <p className="text-center text-xs text-gray-400 mt-8 leading-relaxed">
          Official platform of the National Cyber Investigation Agency.
          Protected by PECA 2016. Unauthorized access is strictly prohibited.
        </p>
      </div>
    </div>
  );
}
