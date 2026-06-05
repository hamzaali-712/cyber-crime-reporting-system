'use client';

export const dynamic = 'force-dynamic';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldAlert, Mail, Lock, User, UserPlus, Phone, CreditCard, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

import { signUpSchema, type SignUpFormData } from '@/lib/validations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';

export default function CitizenSignUpPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
  });

  const onSubmit = async (data: SignUpFormData) => {
    setIsLoading(true);
    setConnectionError(false);
    try {
      const { data: authData, error } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
        options: {
          data: {
            full_name: data.full_name,
            role: 'citizen',
            cnic: data.cnic,
            phone: data.phone,
          },
        },
      });

      if (error) {
        // Check for database trigger errors (shows as 500 from Supabase)
        if (error.message?.includes('Database error') || error.status === 500) {
          setConnectionError(true);
          toast.error('Database Configuration Error', {
            description: 'The user profile trigger failed. Please contact the administrator to fix the database trigger.',
            duration: 8000,
          });
        } else {
          toast.error('Registration Failed', {
            description: error.message,
          });
        }
        return;
      }

      toast.success('Registration successful!', {
        description: 'Please check your email for a verification link.',
      });
      router.push('/citizen/auth/sign-in');
    } catch (error: any) {
      // "Failed to fetch" often means a 500 from Supabase Auth (database trigger crash)
      const msg = error?.message || '';
      if (msg.includes('fetch') || msg.includes('network') || error?.name === 'TypeError') {
        setConnectionError(true);
        toast.error('Server Error', {
          description: 'The authentication server returned an error. This is usually caused by a database trigger issue. Please run the fix SQL in Supabase SQL Editor.',
          duration: 10000,
        });
      } else {
        toast.error('Something went wrong', {
          description: msg || 'An unexpected error occurred.',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50/50 p-4 py-12">
      <div className="w-full max-w-xl">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-blue-600 shadow-xl shadow-blue-200 mb-4">
            <ShieldAlert className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Create Account</h1>
          <p className="text-gray-500 mt-2">Join the National Cyber Crime Reporting System</p>
        </div>

        {/* Connection Error Banner */}
        {connectionError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3 animate-in fade-in duration-300">
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-bold text-red-800">Server Connection Failed</p>
              <p className="text-xs text-red-600 mt-1 leading-relaxed">
                Cannot reach the authentication server. This usually means the Supabase URL or API Key 
                in <code className="bg-red-100 px-1 rounded">web/.env.local</code> is incorrect.
                Please verify your <strong>NEXT_PUBLIC_SUPABASE_URL</strong> and <strong>NEXT_PUBLIC_SUPABASE_ANON_KEY</strong>.
              </p>
            </div>
          </div>
        )}

        <Card className="shadow-xl border-gray-200/50">
          <CardHeader>
            <CardTitle>Sign Up</CardTitle>
            <CardDescription>Fill in your details to create a secure citizen account</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <Input
                    label="Full Name"
                    placeholder="John Doe"
                    {...register('full_name')}
                    error={errors.full_name?.message}
                    className="pl-10"
                  />
                  <User className="absolute left-3 top-[34px] h-4 w-4 text-gray-400" />
                </div>

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
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <Input
                    label="CNIC (Format: 00000-0000000-0)"
                    placeholder="12345-6789012-3"
                    {...register('cnic')}
                    error={errors.cnic?.message}
                    className="pl-10"
                  />
                  <CreditCard className="absolute left-3 top-[34px] h-4 w-4 text-gray-400" />
                </div>

                <div className="relative">
                  <Input
                    label="Phone Number"
                    placeholder="+923001234567"
                    {...register('phone')}
                    error={errors.phone?.message}
                    className="pl-10"
                  />
                  <Phone className="absolute left-3 top-[34px] h-4 w-4 text-gray-400" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

                <div className="relative">
                  <Input
                    label="Confirm Password"
                    placeholder="••••••••"
                    type="password"
                    {...register('confirm_password')}
                    error={errors.confirm_password?.message}
                    className="pl-10"
                  />
                  <Lock className="absolute left-3 top-[34px] h-4 w-4 text-gray-400" />
                </div>
              </div>

              <p className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg border border-gray-100 italic">
                By creating an account, you agree to provide truthful information under PECA 2016. 
                Providing false information to a law enforcement agency is a punishable offense.
              </p>

              <Button type="submit" className="w-full group" loading={isLoading}>
                Create Account
                <UserPlus className="ml-2 h-4 w-4 transition-transform group-hover:scale-110" />
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-4 border-t border-gray-100 mt-2 pt-6">
            <p className="text-sm text-center text-gray-600">
              Already have an account?{' '}
              <Link 
                href="/citizen/auth/sign-in" 
                className="font-bold text-blue-600 hover:text-blue-700 transition-colors"
              >
                Sign in instead
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
