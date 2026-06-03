import React from 'react';
import { 
  Users, 
  FileText, 
  Activity, 
  ShieldCheck, 
  AlertTriangle,
  History,
  ArrowUpRight,
  ArrowDownRight,
  Cpu,
  Database,
  Cloud,
  Terminal
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDateTime, cn } from '@/lib/utils';

export default async function AdminDashboardPage() {
  const supabase = await createClient();
  
  // Fetch system-wide stats
  const { count: usersCount } = await supabase.from('profiles').select('*', { count: 'exact', head: true });
  const { count: casesCount } = await supabase.from('complaints').select('*', { count: 'exact', head: true });
  const { count: securityAlerts } = await supabase.from('audit_logs').select('*', { count: 'exact', head: true }).eq('action', 'SECURITY_ALERT');

  const { data: recentLogs } = await supabase
    .from('audit_logs')
    .select('*, profiles(full_name)')
    .order('created_at', { ascending: false })
    .limit(8);

  const mainStats = [
    { label: 'Cloud Infrastructure', value: 'OPTIMAL', icon: Cloud, color: 'text-emerald-500', sub: '99.99% Uptime' },
    { label: 'Registered Entities', value: usersCount || 0, icon: Users, color: 'text-blue-500', sub: '+124 this month', trend: 'up' },
    { label: 'Active Dossiers', value: casesCount || 0, icon: FileText, color: 'text-purple-500', sub: '14 waiting review', trend: 'down' },
    { label: 'Security Protocols', value: 'LEVEL 4', icon: ShieldCheck, color: 'text-red-500', sub: 'Last scan 2m ago' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-1000">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-4xl font-black text-white tracking-tight">Control Center</h1>
          <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Real-time system health and entity monitoring.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="bg-slate-900 border-slate-800 text-slate-300 font-bold px-6 h-12 rounded-2xl hover:bg-slate-800">
             Open Terminal
          </Button>
          <Button className="bg-blue-600 hover:bg-blue-700 text-white font-bold h-12 px-8 rounded-2xl shadow-2xl shadow-blue-900/40">
             System Re-Sync
          </Button>
        </div>
      </div>

      {/* Infrastructure Heatmap Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
         {mainStats.map((stat, i) => (
           <Card key={i} className="bg-slate-900/50 border-slate-800/50 backdrop-blur-sm p-6 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                 <stat.icon className="h-20 w-20" />
              </div>
              <div className="relative z-10">
                 <div className="flex items-center justify-between mb-4">
                    <div className={cn("p-2 rounded-xl bg-slate-950 border border-slate-800 shadow-inner", stat.color)}>
                       <stat.icon className="h-5 w-5" />
                    </div>
                    {stat.trend && (
                       <Badge variant="outline" className={cn("bg-slate-950 border-none font-bold text-[9px]", stat.trend === 'up' ? 'text-emerald-500' : 'text-red-500')}>
                          {stat.trend === 'up' ? <ArrowUpRight className="h-3 w-3 mr-1" /> : <ArrowDownRight className="h-3 w-3 mr-1" />}
                          {stat.trend === 'up' ? 'GROWTH' : 'DECAY'}
                       </Badge>
                    )}
                 </div>
                 <p className="text-3xl font-black text-white">{stat.value}</p>
                 <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-2">{stat.label}</p>
                 <p className="text-[9px] font-bold text-slate-600 mt-1">{stat.sub}</p>
              </div>
           </Card>
         ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
         {/* Live Audit Stream */}
         <div className="xl:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
               <h2 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-blue-500" /> Administrative Audit Stream
               </h2>
               <Button variant="ghost" className="text-xs font-black text-slate-500 hover:text-white">Full Logs</Button>
            </div>
            
            <Card className="bg-slate-950 border-slate-800/50 overflow-hidden shadow-2xl">
               <div className="p-0 divide-y divide-slate-800/50">
                  {recentLogs && recentLogs.length > 0 ? (
                    recentLogs.map((log: any) => (
                      <div key={log.id} className="p-4 flex items-start gap-4 hover:bg-slate-900/30 transition-colors group">
                         <div className="mt-1 h-8 w-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 font-mono text-[10px] shrink-0 group-hover:text-blue-500 group-hover:border-blue-500/30 transition-all">
                            ID: {log.id.slice(0, 2)}
                         </div>
                         <div className="flex-1 overflow-hidden">
                            <div className="flex items-center justify-between">
                               <p className="text-xs font-bold text-slate-200">{log.action.replace('_', ' ')}</p>
                               <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">{formatDateTime(log.created_at)}</span>
                            </div>
                            <p className="text-[10px] text-slate-500 mt-1 truncate">
                               Executed by <span className="text-slate-300 font-bold">{log.profiles?.full_name || 'System Root'}</span> 
                               {log.entity_id && ` on scope [${log.entity_id.slice(0, 8)}]`}
                            </p>
                         </div>
                         <Badge variant="outline" className="text-[8px] font-black border-slate-800 text-slate-600 group-hover:text-blue-400">SUCCESS</Badge>
                      </div>
                    ))
                  ) : (
                    <div className="p-12 text-center text-slate-500 text-xs italic">
                       Standby: Waiting for system events...
                    </div>
                  )}
               </div>
            </Card>
         </div>

         {/* System Load & Services */}
         <div className="space-y-8">
            <Card className="bg-[#020617] border-slate-800/50 rounded-3xl p-8 relative overflow-hidden ring-1 ring-slate-800/50">
               <h3 className="text-sm font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2">
                  <Activity className="h-4 w-4 text-emerald-500" /> Core Services
               </h3>
               <div className="space-y-6">
                  {[
                     { name: 'Database Relay', health: 98, color: 'bg-emerald-500' },
                     { name: 'Auth Node', health: 100, color: 'bg-emerald-500' },
                     { name: 'AI Processing (Groq)', health: 12, color: 'bg-blue-500', load: true },
                     { name: 'SMTP Gateway', health: 100, color: 'bg-emerald-500' },
                  ].map((service, i) => (
                    <div key={i} className="space-y-2">
                       <div className="flex justify-between text-[10px] font-black uppercase tracking-tighter">
                          <span className="text-slate-400">{service.name}</span>
                          <span className={service.load ? 'text-blue-400' : 'text-emerald-400'}>{service.health}% {service.load ? 'LOAD' : 'NOMINAL'}</span>
                       </div>
                       <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                          <div className={cn("h-full rounded-full transition-all duration-1000", service.color)} style={{ width: `${service.health}%` }} />
                       </div>
                    </div>
                  ))}
               </div>
               
               <div className="mt-12 pt-8 border-t border-slate-800 flex gap-4">
                  <div className="flex-1 bg-slate-900/50 p-4 rounded-2xl border border-slate-800/50 text-center">
                     <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Latency</p>
                     <p className="text-xl font-black text-white mt-1">42ms</p>
                  </div>
                  <div className="flex-1 bg-slate-900/50 p-4 rounded-2xl border border-slate-800/50 text-center">
                     <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Active Ops</p>
                     <p className="text-xl font-black text-white mt-1">1,248</p>
                  </div>
               </div>
               
               <div className="absolute -bottom-8 -right-8 opacity-5">
                  <Database className="h-32 w-32" />
               </div>
            </Card>

            {/* Alert Panel */}
            <Card className="bg-red-950/20 border-red-500/20 rounded-3xl p-6 border group hover:bg-red-950/30 transition-all">
               <div className="flex items-center gap-3 mb-4">
                  <div className="h-10 w-10 rounded-xl bg-red-950 border border-red-950 flex items-center justify-center text-red-500">
                     <AlertTriangle className="h-5 w-5" />
                  </div>
                  <h3 className="font-black text-white text-sm uppercase tracking-widest">Security Alert</h3>
               </div>
               <p className="text-xs text-red-400 leading-relaxed font-bold">
                  DDoS mitigation currently active on public API routes. 
                  Rate-limiting strictly enforced for non-verified citizens.
               </p>
            </Card>
         </div>
      </div>
    </div>
  );
}
