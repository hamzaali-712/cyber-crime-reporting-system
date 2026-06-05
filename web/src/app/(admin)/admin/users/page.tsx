import React from 'react';

export const dynamic = 'force-dynamic';
import { 
  Users, 
  Search, 
  Filter, 
  Shield, 
  UserPlus, 
  MoreVertical,
  UserCheck,
  UserX,
  CreditCard,
  Mail,
  MoreHorizontal,
  Plus
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { formatDate, maskCNIC, cn } from '@/lib/utils';

import { redirect } from 'next/navigation';

export default async function UserManagementPage({
  searchParams,
}: {
  searchParams: Promise<{ role?: string; q?: string }>;
}) {
  const { role, q } = await searchParams;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    redirect('/admin/auth/sign-in');
  }

  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', user.id)
    .single();

  if (profile?.role !== 'admin') {
    redirect('/');
  }
  
  let query = supabase
    .from('profiles')
    .select(`
      *,
      officer_details:officers(officer_id, badge_number)
    `)
    .order('created_at', { ascending: false });

  if (role) {
    query = query.eq('role', role);
  }

  if (q) {
    query = query.or(`full_name.ilike.%${q}%,email.ilike.%${q}%,cnic.ilike.%${q}%`);
  }

  const { data: users } = await query;

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
             <Users className="h-8 w-8 text-blue-500" /> User Entities
          </h1>
          <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Managing registry of citizens, officers and administrators.</p>
        </div>
        <div className="flex gap-3">
          <Button className="bg-blue-600 hover:bg-blue-700 text-white font-black h-12 px-6 rounded-2xl shadow-xl shadow-blue-900/20">
             <Plus className="h-4 w-4 mr-2" /> Provision New Officer
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
         {/* Stats mini-cards */}
         {[
           { label: 'Total Citizens', count: 1240, color: 'text-blue-500' },
           { label: 'Active Officers', count: 42, color: 'text-emerald-500' },
           { label: 'Suspended Entities', count: 5, color: 'text-red-500' },
           { label: 'Admin Root Nodes', count: 2, color: 'text-purple-500' },
         ].map((stat, i) => (
           <Card key={i} className="bg-slate-900/30 border-slate-800/50 p-4">
              <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{stat.label}</p>
              <p className={cn("text-xl font-black mt-1", stat.color)}>{stat.count}</p>
           </Card>
         ))}
      </div>

      {/* Filter Bar */}
      <Card className="bg-slate-900/50 border-slate-800/50 backdrop-blur-xl p-3 rounded-2xl ring-1 ring-slate-800/50">
         <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
               <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
               <Input 
                 placeholder="Search registry by name, email, or CNIC..." 
                 className="pl-10 h-11 bg-slate-950 border-slate-800 text-slate-300 rounded-xl focus:ring-blue-500/20"
                 defaultValue={q}
               />
            </div>
            <div className="flex gap-2">
               <select className="h-11 px-4 bg-slate-950 border border-slate-800 rounded-xl text-xs font-bold text-slate-400 appearance-none min-w-[140px]">
                  <option value="">All Roles</option>
                  <option value="citizen">Citizen</option>
                  <option value="officer">Officer</option>
                  <option value="admin">Admin</option>
               </select>
               <Button variant="outline" className="h-11 bg-slate-950 border-slate-800 text-slate-400 font-bold px-4 rounded-xl">
                  <Filter className="h-4 w-4 mr-2" /> Filter
               </Button>
            </div>
         </div>
      </Card>

      {/* Users Registry Table */}
      <div className="bg-slate-950 border border-slate-800/50 rounded-3xl overflow-hidden shadow-2xl">
         <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[900px]">
               <thead>
                  <tr className="bg-slate-900/40 border-b border-slate-800/50">
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Entity Signature</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Access Role</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Identity Info</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Status</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Last Synced</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Actions</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-slate-800/30">
                  {users && users.length > 0 ? (
                    users.map((u: any) => (
                      <tr key={u.id} className="hover:bg-slate-900/40 transition-all group border-b border-slate-800/10">
                         <td className="px-6 py-5">
                            <div className="flex items-center gap-4">
                               <div className="h-10 w-10 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 font-black relative shadow-inner group-hover:border-blue-500/50 group-hover:text-blue-500 transition-all">
                                  {u.full_name?.charAt(0)}
                                  {u.role === 'admin' && (
                                    <div className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full border-2 border-slate-950" />
                                  )}
                               </div>
                               <div>
                                  <p className="text-sm font-black text-white leading-none tracking-tight">{u.full_name}</p>
                                  <p className="text-[10px] font-bold text-slate-500 mt-1 flex items-center gap-1">
                                     <Mail className="h-3 w-3" /> {u.email}
                                  </p>
                               </div>
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <Badge className={cn(
                               "text-[9px] font-black uppercase px-3 py-1 border-none",
                               u.role === 'admin' ? "bg-red-500/10 text-red-500" :
                               u.role === 'officer' ? "bg-blue-500/10 text-blue-500" : "bg-emerald-500/10 text-emerald-500"
                            )}>
                               {u.role}
                            </Badge>
                         </td>
                         <td className="px-6 py-5">
                            <div className="space-y-1">
                               <div className="flex items-center gap-2">
                                  <CreditCard className="h-3.5 w-3.5 text-slate-600" />
                                  <p className="text-xs font-mono font-bold text-slate-400">{u.cnic ? maskCNIC(u.cnic) : 'NOT_RECORDED'}</p>
                               </div>
                               {u.officer_details?.[0] && (
                                 <p className="text-[9px] font-black text-blue-500/80 uppercase tracking-widest pl-5">BADGE: {u.officer_details[0].badge_number}</p>
                               )}
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <div className="flex items-center gap-2">
                               <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                               <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">ACTIVE</span>
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <p className="text-xs font-bold text-slate-500">{formatDate(u.updated_at)}</p>
                         </td>
                         <td className="px-6 py-5 text-right">
                            <div className="flex items-center justify-end gap-2">
                               <Button variant="ghost" size="icon" className="h-9 w-9 bg-slate-900 border border-slate-800 rounded-xl hover:bg-red-950/20 hover:text-red-500 transition-all">
                                  <UserX className="h-4 w-4" />
                               </Button>
                               <Button variant="ghost" size="icon" className="h-9 w-9 bg-slate-900 border border-slate-800 rounded-xl hover:bg-blue-900/20 hover:text-blue-500 transition-all">
                                  <Shield className="h-4 w-4" />
                               </Button>
                               <Button variant="ghost" size="icon" className="h-9 w-9 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 text-slate-400">
                                  <MoreHorizontal className="h-4 w-4" />
                               </Button>
                            </div>
                         </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                       <td colSpan={6} className="py-24 text-center">
                          <Users className="h-12 w-12 text-slate-800 mx-auto mb-4" />
                          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Registry Empty or Filters Too Strict</p>
                       </td>
                    </tr>
                  )}
               </tbody>
            </table>
         </div>
      </div>
    </div>
  );
}
