import React from 'react';
import Link from 'next/link';
import { 
  Inbox, 
  Search, 
  Filter, 
  Download, 
  ChevronRight, 
  MoreHorizontal,
  ArrowUpDown,
  History,
  FileText,
  User,
  AlertCircle
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { StatusBadge, Badge } from '@/components/ui/badge';
import { formatDate, formatDateTime, maskCNIC } from '@/lib/utils';
import type { Complaint } from '@/lib/database.types';

import { redirect } from 'next/navigation';

export default async function OfficerCasesPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string; search?: string; category?: string }>;
}) {
  const { status, search, category } = await searchParams;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    redirect('/officer/auth/sign-in');
  }

  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', user.id)
    .single();

  if (profile?.role !== 'officer' && profile?.role !== 'admin') {
    redirect('/');
  }

  let query = supabase
    .from('complaints')
    .select(`
      *,
      citizen:profiles(full_name, cnic)
    `)
    .order('created_at', { ascending: false });

  if (status) {
    query = query.eq('status', status);
  }

  if (search) {
    query = query.or(`tracking_id.ilike.%${search}%, description.ilike.%${search}%`);
  }

  if (category) {
    query = query.eq('category', category);
  }

  const { data: cases, error } = await query;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
             <Inbox className="h-8 w-8 text-blue-600" /> Operational Queue
          </h1>
          <p className="text-slate-500 font-medium mt-1">Master list of all reported cyber crime dossiers in the system.</p>
        </div>
        <div className="flex items-center gap-2">
           <Button variant="outline" className="bg-white rounded-xl font-bold gap-2">
             <Download className="h-4 w-4" /> Export CSV
           </Button>
           <Button className="bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20 rounded-xl font-bold">
             New Manual Dossier
           </Button>
        </div>
      </div>

      {/* Advanced Filter Bar */}
      <Card className="border-none shadow-sm ring-1 ring-slate-200/60 p-4 bg-white rounded-2xl">
         <div className="flex flex-col lg:flex-row items-center gap-4">
            <div className="relative flex-1 w-full">
               <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
               <Input 
                 placeholder="Search tracking ID or case details..." 
                 className="pl-10 h-12 bg-slate-50/50 border-slate-200 rounded-xl focus:ring-blue-500/20"
                 defaultValue={search}
               />
            </div>
            <div className="flex items-center gap-3 w-full lg:w-auto">
               <select className="h-12 px-4 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-600 flex-1 lg:w-40 appearance-none">
                  <option value="">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="UNDER_REVIEW">Under Review</option>
                  <option value="APPROVED">Approved</option>
                  <option value="REJECTED">Rejected</option>
               </select>
               <select className="h-12 px-4 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-slate-600 flex-1 lg:w-48 appearance-none">
                  <option value="">All Categories</option>
                  <option value="Cyber Stalking">Cyber Stalking</option>
                  <option value="Financial Fraud">Financial Fraud</option>
               </select>
               <Button variant="outline" size="icon" className="h-12 w-12 rounded-xl text-slate-500">
                  <Filter className="h-4 w-4" />
               </Button>
            </div>
         </div>
      </Card>

      {/* Main Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden shadow-slate-200/20">
         <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[1000px]">
               <thead>
                  <tr className="bg-slate-50/50 border-b border-slate-200">
                     <th className="px-6 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-center h-4"># Status</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Case Dossier</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Complainant</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Incident Category</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest">Submission Date</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Dossier Access</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-slate-100">
                  {cases && cases.length > 0 ? (
                    cases.map((c: any) => (
                      <tr key={c.id} className="hover:bg-slate-50/70 transition-all group cursor-pointer">
                         <td className="px-6 py-5">
                            <div className="flex justify-center">
                               <StatusBadge status={c.status} />
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <div>
                               <p className="font-mono text-xs font-black text-blue-600 tracking-tighter">{c.tracking_id}</p>
                               <p className="text-[10px] font-bold text-slate-400 mt-0.5 flex items-center gap-1">
                                  <History className="h-3 w-3" /> Updated {formatDate(c.updated_at)}
                               </p>
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <div className="flex items-center gap-3">
                               <div className="h-8 w-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-xs ring-1 ring-slate-200">
                                  {c.is_anonymous ? 'A' : (c.citizen?.full_name?.charAt(0) || 'U')}
                               </div>
                               <div>
                                  <p className="text-sm font-bold text-slate-900 leading-none">
                                     {c.is_anonymous ? <Badge variant="secondary" className="bg-slate-100 text-[10px]">ANONYMOUS</Badge> : (c.citizen?.full_name || 'System User')}
                                  </p>
                                  {!c.is_anonymous && (
                                    <p className="text-[10px] text-slate-500 font-mono mt-1 font-bold">{maskCNIC(c.citizen?.cnic)}</p>
                                  )}
                               </div>
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <Badge variant="outline" className="border-slate-200 text-slate-600 font-bold bg-white text-[10px] px-3">
                               {c.category}
                            </Badge>
                         </td>
                         <td className="px-6 py-5">
                            <div className="text-xs font-bold text-slate-600">
                               {formatDate(c.created_at)}
                            </div>
                         </td>
                         <td className="px-6 py-5 text-right">
                            <Link href={`/officer/cases/${c.tracking_id}`}>
                               <Button variant="ghost" size="sm" className="rounded-xl hover:bg-blue-50 hover:text-blue-600 font-black text-[10px] uppercase tracking-widest border border-transparent hover:border-blue-100">
                                  Access Dossier <ChevronRight className="ml-1 h-3 w-3" />
                               </Button>
                            </Link>
                         </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                       <td colSpan={6} className="py-20 text-center">
                          <div className="flex flex-col items-center">
                             <div className="h-20 w-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                                <Search className="h-10 w-10 text-slate-200" />
                             </div>
                             <h4 className="font-bold text-slate-900">No Dossiers Found</h4>
                             <p className="text-sm text-slate-500 mt-1 max-w-xs mx-auto">Either no reports match your current filters or the system queue is empty.</p>
                             <Button variant="outline" className="mt-8 rounded-xl font-bold">Clear All Filters</Button>
                          </div>
                       </td>
                    </tr>
                  )}
               </tbody>
            </table>
         </div>
         
         {/* Simple Pagination */}
         <div className="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Showing 1 to {cases?.length || 0} of {cases?.length || 0} dossiers</p>
            <div className="flex items-center gap-2">
               <Button variant="ghost" disabled size="sm" className="font-bold text-xs rounded-lg">Previous</Button>
               <Button variant="ghost" disabled size="sm" className="font-bold text-xs rounded-lg">Next</Button>
            </div>
         </div>
      </div>
    </div>
  );
}
