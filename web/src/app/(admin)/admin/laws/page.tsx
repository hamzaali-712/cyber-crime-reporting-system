import React from 'react';
import { 
  ShieldCheck, 
  Plus, 
  Edit3, 
  Trash2, 
  Gavel, 
  CheckCircle2, 
  XCircle,
  ArrowUpDown,
  Search,
  Eye,
  EyeOff
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import type { Law } from '@/lib/database.types';

export default async function AdminLawsPage() {
  const supabase = await createClient();
  
  const { data: laws } = await supabase
    .from('laws')
    .select('*')
    .order('sort_order', { ascending: true });

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
             <ShieldCheck className="h-8 w-8 text-blue-500" /> Law Repository
          </h1>
          <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Managing PECA 2016 sections and judicial mappings.</p>
        </div>
        <div className="flex gap-3">
          <Button className="bg-blue-600 hover:bg-blue-700 text-white font-black h-12 px-6 rounded-2xl shadow-xl shadow-blue-900/20">
             <Plus className="h-4 w-4 mr-2" /> Add New Section
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
         <Card className="bg-slate-900/50 border-slate-800/50 p-6 flex flex-col justify-center text-center">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Total Sections</p>
            <p className="text-3xl font-black text-white mt-1">{laws?.length || 0}</p>
         </Card>
         <Card className="bg-slate-900/50 border-slate-800/50 p-6 flex flex-col justify-center text-center">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Published</p>
            <p className="text-3xl font-black text-emerald-500 mt-1">{laws?.filter(l => l.is_published).length || 0}</p>
         </Card>
      </div>

      {/* Main Laws List */}
      <Card className="bg-slate-950 border border-slate-800/50 rounded-3xl overflow-hidden shadow-2xl ring-1 ring-slate-800/50">
         <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[1000px]">
               <thead>
                  <tr className="bg-slate-900/40 border-b border-slate-800/50">
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest w-16 text-center h-4">Order</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Section Info</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Punishment Overview</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Category</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Visibility</th>
                     <th className="px-6 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Actions</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-slate-800/30">
                  {laws && laws.length > 0 ? (
                    laws.map((law: Law) => (
                      <tr key={law.id} className="hover:bg-slate-900/40 transition-all group border-b border-slate-800/10">
                         <td className="px-6 py-5 text-center">
                            <span className="text-xs font-mono font-black text-slate-600 group-hover:text-blue-500 transition-colors">#{law.sort_order}</span>
                         </td>
                         <td className="px-6 py-5">
                            <div className="flex items-start gap-4">
                               <div className="h-10 w-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 font-black shrink-0">
                                  {law.section_number}
                               </div>
                               <div>
                                  <p className="text-sm font-black text-white leading-none tracking-tight">{law.title}</p>
                                  <p className="text-[10px] font-bold text-slate-500 mt-2 line-clamp-1 max-w-xs">{law.short_description}</p>
                               </div>
                            </div>
                         </td>
                         <td className="px-6 py-5">
                            <p className="text-[10px] font-bold text-red-500/80 leading-relaxed max-w-xs">{law.punishment}</p>
                         </td>
                         <td className="px-6 py-5">
                            <Badge variant="outline" className="border-slate-800 text-[9px] font-black text-slate-400 uppercase tracking-widest px-3">
                               {law.category}
                            </Badge>
                         </td>
                         <td className="px-6 py-5">
                            <div className="flex items-center gap-2">
                               {law.is_published ? (
                                  <div className="flex items-center gap-2 text-emerald-500">
                                     <CheckCircle2 className="h-3 w-3" />
                                     <span className="text-[9px] font-black uppercase tracking-widest">Public</span>
                                  </div>
                               ) : (
                                  <div className="flex items-center gap-2 text-red-500/50">
                                     <XCircle className="h-3 w-3" />
                                     <span className="text-[9px] font-black uppercase tracking-widest">Draft</span>
                                  </div>
                               )}
                            </div>
                         </td>
                         <td className="px-6 py-5 text-right">
                            <div className="flex items-center justify-end gap-2">
                               <Button variant="ghost" size="icon" className="h-9 w-9 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 text-slate-400">
                                  <Edit3 className="h-4 w-4" />
                               </Button>
                               <Button variant="ghost" size="icon" className="h-9 w-9 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 text-slate-400">
                                  {law.is_published ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                               </Button>
                               <Button variant="ghost" size="icon" className="h-9 w-9 bg-slate-900 border border-slate-800 rounded-xl hover:bg-red-950/20 hover:text-red-500">
                                  <Trash2 className="h-4 w-4" />
                               </Button>
                            </div>
                         </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                       <td colSpan={6} className="py-24 text-center">
                          <Gavel className="h-12 w-12 text-slate-800 mx-auto mb-4" />
                          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">No laws in the repository.</p>
                       </td>
                    </tr>
                  )}
               </tbody>
            </table>
         </div>
      </Card>
    </div>
  );
}
