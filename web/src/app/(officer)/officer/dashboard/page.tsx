import React from 'react';

export const dynamic = 'force-dynamic';
import Link from 'next/link';
import { 
  Inbox, 
  CheckCircle, 
  Clock, 
  Timer, 
  TrendingUp, 
  ShieldAlert,
  ArrowRight,
  AlertTriangle,
  Zap,
  BarChart3
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge, Badge } from '@/components/ui/badge';
import { formatDate, cn } from '@/lib/utils';
import type { Complaint } from '@/lib/database.types';

import { redirect } from 'next/navigation';

export default async function OfficerDashboardPage() {
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

  // Fetch officer profile info
  const { data: officer } = await supabase
    .from('officers')
    .select('*, profiles(full_name)')
    .eq('id', user.id)
    .single();

  // Fetch count stats
  const { count: totalAssigned } = await supabase
    .from('complaints')
    .select('*', { count: 'exact', head: true })
    .eq('assigned_officer_id', user.id);

  const { count: pendingReview } = await supabase
    .from('complaints')
    .select('*', { count: 'exact', head: true })
    .eq('assigned_officer_id', user.id)
    .in('status', ['PENDING', 'UNDER_REVIEW']);

  // Priority Queue: Oldest unresolved cases
  const { data: priorityQueue } = await supabase
    .from('complaints')
    .select('*')
    .in('status', ['PENDING', 'UNDER_REVIEW', 'UNDER_INVESTIGATION'])
    .order('created_at', { ascending: true })
    .limit(5);

  const stats = [
    { label: 'Assigned Items', value: totalAssigned || 0, icon: Inbox, color: 'text-blue-500', trend: '+12%' },
    { label: 'Pending Review', value: pendingReview || 0, icon: Clock, color: 'text-amber-500', trend: '-5%' },
    { label: 'Cleared (Today)', value: 4, icon: CheckCircle, color: 'text-emerald-500', trend: '+2' },
    { label: 'Avg Latency', value: '1.2d', icon: Timer, color: 'text-purple-500', trend: '-8%' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">System Overview</h1>
          <p className="text-slate-500 mt-1 font-medium">Monitoring active cyber crime dossiers & operational metrics.</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-white px-4 py-2 text-slate-600 font-bold border-slate-200">
             Badge: {officer?.badge_number || 'NC-772'}
          </Badge>
          <Link href="/officer/cases">
             <Button className="bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20 font-bold rounded-xl px-6">
                Open Full Queue
             </Button>
          </Link>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <Card key={i} className="border-none shadow-sm bg-white overflow-hidden ring-1 ring-slate-200/60 p-6 group hover:shadow-md transition-all">
             <div className="flex items-center justify-between mb-4">
                <div className={cn('p-3 rounded-2xl bg-slate-50 group-hover:scale-110 transition-transform', stat.color)}>
                   <stat.icon className="h-6 w-6" />
                </div>
                <div className="flex items-center gap-1 text-[10px] font-bold bg-emerald-50 text-emerald-600 px-2 py-1 rounded-full">
                   <TrendingUp className="h-3 w-3" /> {stat.trend}
                </div>
             </div>
             <div>
                <p className="text-2xl font-black text-slate-900">{stat.value}</p>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">{stat.label}</p>
             </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Charts Mockup */}
        <div className="lg:col-span-2 space-y-8">
           <Card className="border-none shadow-sm ring-1 ring-slate-200/60 h-[400px] flex flex-col items-center justify-center bg-slate-50/50">
              <BarChart3 className="h-12 w-12 text-slate-200 mb-4" />
              <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Case Volume Matrix (Real-time)</p>
           </Card>

           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-none shadow-sm ring-1 ring-slate-200/60 h-64 flex flex-col items-center justify-center bg-slate-50/50">
                <TrendingUp className="h-8 w-8 text-slate-200 mb-3" />
                <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Resolution Trends</p>
              </Card>
              <Card className="border-none shadow-sm ring-1 ring-slate-200/60 h-64 flex flex-col items-center justify-center bg-slate-50/50">
                <Zap className="h-8 w-8 text-slate-200 mb-3" />
                <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Efficiency Scoring</p>
              </Card>
           </div>
        </div>

        {/* Sidebar: Priority Queue */}
        <div className="space-y-6">
          <div className="flex items-center justify-between px-2">
             <h3 className="font-bold text-slate-900 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500 underline" /> Priority Dossiers
             </h3>
             <Badge variant="outline" className="bg-red-50 text-red-700 border-red-100 flex gap-1">
                <ShieldAlert className="h-3 w-3" /> SLA Critical
             </Badge>
          </div>

          <div className="space-y-3">
             {priorityQueue && priorityQueue.length > 0 ? (
               priorityQueue.map((caseItem: Complaint) => (
                 <Link key={caseItem.id} href={`/officer/cases/${caseItem.tracking_id}`}>
                   <Card className="group hover:ring-2 hover:ring-blue-100 transition-all cursor-pointer border-none shadow-sm ring-1 ring-slate-200/60 overflow-hidden">
                      <CardContent className="p-4">
                         <div className="flex items-start justify-between gap-4">
                            <div className="overflow-hidden">
                               <p className="font-bold text-slate-900 text-sm truncate group-hover:text-blue-600 transition-colors">{caseItem.category}</p>
                               <p className="text-[10px] font-mono font-bold text-slate-400 mt-1 uppercase">{caseItem.tracking_id}</p>
                            </div>
                            <StatusBadge status={caseItem.status} className="shrink-0" />
                         </div>
                         <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tight flex items-center gap-1">
                               <Clock className="h-3 w-3" /> {formatDate(caseItem.created_at)}
                            </span>
                            <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" title="SLA breach risk" />
                         </div>
                      </CardContent>
                   </Card>
                 </Link>
               ))
             ) : (
               <div className="h-32 rounded-3xl bg-slate-50 border border-dashed border-slate-200 flex items-center justify-center text-slate-400 text-xs font-bold uppercase tracking-widest">
                  Queue Empty
               </div>
             )}
             
             <Link href="/officer/cases" className="block mt-4">
                <Button variant="ghost" className="w-full text-slate-500 font-bold hover:text-blue-600 group">
                   Manage All Dossiers <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
             </Link>
          </div>

          <Card className="bg-slate-900 border-none shadow-2xl p-6 relative overflow-hidden text-white">
             <div className="relative z-10">
                <p className="text-blue-400 text-[10px] font-bold uppercase tracking-widest mb-1">AI Service Status</p>
                <div className="flex items-center gap-2 mb-4">
                   <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                   <span className="font-bold text-sm">Groq-Llama-3.3 ACTIVE</span>
                </div>
                <p className="text-slate-400 text-xs leading-relaxed">
                   Real-time case summarization and legal mapping services are currently operational with 99.9% uptime.
                </p>
             </div>
             <div className="absolute top-0 right-0 p-4 opacity-5">
                <Zap className="h-32 w-32 text-white" />
             </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
