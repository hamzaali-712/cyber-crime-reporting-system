'use client';

import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  CreditCard, 
  MapPin, 
  Shield, 
  Bell, 
  Trash2, 
  Save,
  Lock,
  Camera,
  CheckCircle2
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';

import { profileUpdateSchema, type ProfileUpdateFormData } from '@/lib/validations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { createClient } from '@/lib/supabase/client';
import { Skeleton } from '@/components/ui/skeleton';

export default function CitizenProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileUpdateFormData>({
    resolver: zodResolver(profileUpdateSchema),
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();

      if (data) {
        setProfile({ ...data, email: user.email });
        reset({
          full_name: data.full_name,
          cnic: data.cnic || '',
          phone: data.phone || '',
          address: data.address || '',
        });
      }
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: ProfileUpdateFormData) => {
    setIsSaving(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { error } = await supabase
        .from('profiles')
        .update(data)
        .eq('id', user.id);

      if (error) throw error;

      toast.success('Profile updated', { description: 'Your personal information has been saved.' });
      fetchProfile();
    } catch (error: any) {
      toast.error('Update Failed', { description: error.message });
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) return (
    <div className="space-y-8 max-w-4xl mx-auto py-6">
       <Skeleton className="h-10 w-48" />
       <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Skeleton className="h-64 rounded-3xl" />
          <Skeleton className="h-64 md:col-span-2 rounded-3xl" />
       </div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500 py-6">
      <header>
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Account Settings</h1>
        <p className="text-gray-500 mt-1">Manage your identity, security, and portal preferences.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Avatar & Quick Info */}
        <div className="space-y-6">
          <Card className="border-none shadow-xl ring-1 ring-gray-100 overflow-hidden text-center p-8">
             <div className="relative inline-block group mb-6">
                <div className="h-32 w-32 rounded-full bg-blue-100 border-4 border-white shadow-xl flex items-center justify-center text-blue-600 text-4xl font-bold overflow-hidden ring-1 ring-blue-50">
                   {profile?.full_name?.charAt(0) || 'U'}
                </div>
                <button className="absolute bottom-0 right-0 p-2 bg-blue-600 text-white rounded-full shadow-lg border-2 border-white hover:bg-blue-700 transition-colors opacity-0 group-hover:opacity-100 scale-90 group-hover:scale-100 transition-all">
                   <Camera className="h-4 w-4" />
                </button>
             </div>
             <h2 className="text-xl font-bold text-gray-900">{profile?.full_name}</h2>
             <p className="text-sm text-gray-500">{profile?.email}</p>
             <Badge className="mt-4 bg-emerald-50 text-emerald-700 border-emerald-100 px-4 py-1">
               Verified Citizen
             </Badge>

             <div className="mt-8 space-y-2 text-left bg-gray-50 p-4 rounded-2xl border border-gray-100">
                <div className="flex items-center gap-3 text-gray-600">
                   <Shield className="h-4 w-4 text-blue-600" />
                   <span className="text-xs font-semibold uppercase tracking-widest">Account Status</span>
                </div>
                <p className="text-sm font-bold text-gray-900 truncate">Active & SECURED</p>
             </div>
          </Card>

          <Card className="border-none shadow-sm ring-1 ring-gray-100">
             <CardHeader>
                <CardTitle className="text-base">Identity Documents</CardTitle>
             </CardHeader>
             <CardContent className="space-y-4">
                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
                   <div className="flex items-center gap-3">
                      <CreditCard className="h-4 w-4 text-gray-400" />
                      <span className="text-xs font-bold text-gray-500 uppercase">CNIC</span>
                   </div>
                   <span className="text-sm font-mono font-bold text-gray-900">
                     {profile?.cnic ? `*****-*******-${profile.cnic.slice(-1)}` : 'Not provided'}
                   </span>
                </div>
                <div className="bg-amber-50 p-3 rounded-xl border border-amber-100">
                   <p className="text-[10px] text-amber-700 font-bold uppercase tracking-widest">Verification</p>
                   <p className="text-xs text-amber-900 mt-1 leading-relaxed">
                     Your identity is verified against NADRA records for legal compliance.
                   </p>
                </div>
             </CardContent>
          </Card>
        </div>

        {/* Right Column: Edit Forms */}
        <div className="lg:col-span-2 space-y-8">
           <Card className="border-none shadow-xl ring-1 ring-gray-100 overflow-hidden">
             <CardHeader className="border-b border-gray-50 pb-6">
                <CardTitle className="text-xl flex items-center gap-2">
                   <User className="h-5 w-5 text-blue-600" /> Personal Information
                </CardTitle>
                <CardDescription>Update your public identity and contact details.</CardDescription>
             </CardHeader>
             <form onSubmit={handleSubmit(onSubmit)}>
                <CardContent className="pt-8 space-y-6">
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Input 
                        label="Full Legal Name" 
                        {...register('full_name')} 
                        error={errors.full_name?.message}
                      />
                      <Input 
                        label="CNIC (National ID)" 
                        placeholder="12345-6789012-3"
                        {...register('cnic')} 
                        error={errors.cnic?.message}
                      />
                   </div>

                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <Input 
                        label="Phone Number" 
                        placeholder="+923001234567"
                        {...register('phone')} 
                        error={errors.phone?.message}
                      />
                      <div className="space-y-1.5 opacity-60">
                         <label className="block text-sm font-medium text-gray-700">Email Address (Immutable)</label>
                         <Input value={profile?.email} disabled className="bg-gray-50 cursor-not-allowed" />
                      </div>
                   </div>

                   <Textarea 
                      label="Residential Address" 
                      placeholder="Street, City, Province"
                      rows={3}
                      {...register('address')}
                      error={errors.address?.message}
                   />
                </CardContent>
                <CardFooter className="bg-gray-50/50 border-t border-gray-100 px-8 py-4 flex justify-end">
                   <Button type="submit" loading={isSaving} disabled={!isDirty} className="bg-blue-600 hover:bg-blue-700 font-bold px-8">
                      <Save className="h-4 w-4 mr-2" /> Save Changes
                   </Button>
                </CardFooter>
             </form>
           </Card>

           {/* Security Settings */}
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <Card className="border-none shadow-sm ring-1 ring-gray-100">
                 <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                       <Lock className="h-4 w-4 text-blue-600" /> Security
                    </CardTitle>
                 </CardHeader>
                 <CardContent>
                    <p className="text-xs text-gray-500 leading-relaxed mb-6">
                       Change your account password. We recommend choosing a strong, unique password.
                    </p>
                    <Button variant="outline" className="w-full font-bold">Update Password</Button>
                 </CardContent>
              </Card>

              <Card className="border-none shadow-sm ring-1 ring-gray-100">
                 <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                       <Bell className="h-4 w-4 text-blue-600" /> Notifications
                    </CardTitle>
                 </CardHeader>
                 <CardContent>
                    <div className="space-y-4">
                       <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">Case status updates</span>
                          <div className="h-5 w-10 bg-blue-600 rounded-full relative p-1 cursor-pointer">
                             <div className="h-3 w-3 bg-white rounded-full absolute right-1" />
                          </div>
                       </div>
                       <div className="flex items-center justify-between opacity-50">
                          <span className="text-sm font-medium text-gray-700">Legal awareness tips</span>
                          <div className="h-5 w-10 bg-gray-200 rounded-full relative p-1 cursor-not-allowed">
                             <div className="h-3 w-3 bg-white rounded-full absolute left-1" />
                          </div>
                       </div>
                    </div>
                 </CardContent>
              </Card>
           </div>

           {/* Destructive Actions */}
           <Card className="border-none shadow-sm ring-1 ring-red-100 bg-red-50/20">
              <CardHeader>
                 <CardTitle className="text-base text-red-900 flex items-center gap-2">
                    <Trash2 className="h-4 w-4 text-red-600" /> Data Deletion
                 </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col md:flex-row items-center justify-between gap-4">
                 <p className="text-xs text-red-700 max-w-md">
                    Permanently delete your citizen account and all associated data. This action is irreversible.
                    Any active complaints will be archived for legal purposes.
                 </p>
                 <Button variant="destructive" className="bg-red-600 hover:bg-red-700 font-bold px-6">Delete Account</Button>
              </CardContent>
           </Card>
        </div>
      </div>
    </div>
  );
}
