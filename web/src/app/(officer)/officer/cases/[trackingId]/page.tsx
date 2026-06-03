import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { 
  ArrowLeft, 
  Shield, 
  User, 
  FileText, 
  History, 
  Download, 
  ExternalLink,
  Sparkles,
  Search,
  Scale,
  Mail,
  CheckCircle2,
  AlertTriangle,
  Send,
  Zap,
  MapPin,
  Star
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge, Badge } from '@/components/ui/badge';
import { formatDate, formatDateTime, formatFileSize, maskCNIC, cn } from '@/lib/utils';
import type { ComplaintWithRelations, EvidenceFile } from '@/lib/database.types';

// Strategic Intelligence Panels
import CaseDecisionPanel from "./CaseDecisionPanel";
import AIAnalysisPanel from "./AIAnalysisPanel";
import EmailDispatchPanel from "./EmailDispatchPanel";

export default async function OfficerCaseReviewPage({
  params,
}: {
  params: Promise<{ trackingId: string }>;
}) {
  const { trackingId } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  const { data: caseData, error } = await supabase
    .from('complaints')
    .select(`
      *,
      citizen:profiles(full_name, cnic, phone, address, email),
      evidence_files (*),
      ai_reports (*),
      status_history:complaint_status_history (
        *,
        changer:profiles(full_name)
      )
    `)
    .eq('tracking_id', trackingId)
    .single();

  if (!caseData || error) {
    return notFound();
  }

  const complaint = caseData as ComplaintWithRelations;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      {/* Header Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <Link href="/officer/cases" className="inline-flex items-center text-xs font-bold text-slate-400 hover:text-blue-600 transition-colors uppercase tracking-widest mb-2">
            <ArrowLeft className="mr-2 h-3 w-3" /> Back to Operational Queue
          </Link>
          <div className="flex items-center gap-3">
             <h1 className="text-3xl font-black text-slate-900 tracking-tight">{complaint.tracking_id}</h1>
             <StatusBadge status={complaint.status} className="scale-110" />
          </div>
          <p className="text-slate-500 font-medium flex items-center gap-2">
             Dossier Type: <Badge variant="outline" className="text-[10px] font-bold border-slate-200">{complaint.category}</Badge>
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="rounded-xl border-slate-200 font-bold gap-2 bg-white">
            <Download className="h-4 w-4" /> Export Dossier
          </Button>
          <Button className="rounded-xl bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20 font-bold">
            Flag as Critical
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
        {/* Left Columns: Main Dossier View (Content) */}
        <div className="xl:col-span-8 space-y-8">
          
          {/* 1. Complainant Intelligence */}
          <Card className="border-none shadow-sm ring-1 ring-slate-200/60 rounded-2xl">
             <CardHeader className="bg-slate-50 border-b border-slate-100 py-6">
                <CardTitle className="text-sm font-black uppercase tracking-widest text-slate-900 flex items-center gap-2">
                   <User className="h-4 w-4 text-blue-600" /> Complainant Intelligence
                </CardTitle>
             </CardHeader>
             <CardContent className="p-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                   <div className="space-y-6">
                      <div className="flex items-center gap-4">
                         <div className="h-16 w-16 rounded-2xl bg-blue-100 flex items-center justify-center text-blue-600 text-2xl font-black ring-4 ring-blue-50">
                            {complaint.is_anonymous ? 'A' : (complaint.citizen?.full_name?.charAt(0) || 'U')}
                         </div>
                         <div>
                            <p className="text-lg font-black text-slate-900 leading-none">
                               {complaint.is_anonymous ? 'Anonymous Petitioner' : (complaint.citizen?.full_name || 'System User')}
                            </p>
                            <p className="text-xs font-bold text-slate-400 mt-2 uppercase tracking-tight">Identity: {complaint.is_anonymous ? 'Masked' : 'Verified'}</p>
                         </div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-3">
                         <div className="flex justify-between items-center">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">National ID</span>
                            <span className="text-xs font-mono font-bold text-slate-900">{maskCNIC(complaint.citizen?.cnic || '')}</span>
                         </div>
                         <div className="flex justify-between items-center">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">Phone No.</span>
                            <span className="text-xs font-bold text-slate-900">{complaint.is_anonymous ? 'REDACTED' : (complaint.citizen?.phone || '—')}</span>
                         </div>
                      </div>
                   </div>
                   
                   <div className="md:col-span-2">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                         <div className="space-y-1">
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Digital Mail</p>
                            <p className="text-sm font-bold text-slate-900 flex items-center gap-2 truncate">
                               <Mail className="h-3 w-3 text-slate-300" /> {complaint.citizen?.email || 'N/A'}
                            </p>
                         </div>
                         <div className="space-y-1">
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Resident Address</p>
                            <p className="text-sm font-bold text-slate-900 flex items-center gap-2">
                               <MapPin className="h-3 w-3 text-slate-300" /> {complaint.is_anonymous ? 'REDACTED' : (complaint.citizen?.address || 'Pakistan')}
                            </p>
                         </div>
                      </div>
                      <div className="mt-8 pt-8 border-t border-slate-100">
                         <div className="flex items-center justify-between mb-4">
                            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Submission Context</h4>
                            <Badge variant="outline" className="bg-white border-slate-200 text-slate-500 text-[10px] font-bold">Priority High</Badge>
                         </div>
                         <div className="grid grid-cols-2 gap-4">
                            <div className="bg-blue-50/50 p-3 rounded-xl border border-blue-100">
                               <p className="text-[10px] font-bold text-blue-600 uppercase">Filed Date</p>
                               <p className="text-xs font-bold text-blue-900 mt-1">{formatDateTime(complaint.created_at)}</p>
                            </div>
                            <div className="bg-amber-50/50 p-3 rounded-xl border border-amber-100">
                               <p className="text-[10px] font-bold text-amber-600 uppercase">Incident Date</p>
                               <p className="text-xs font-bold text-amber-900 mt-1">{formatDate(complaint.incident_date)}</p>
                            </div>
                         </div>
                      </div>
                   </div>
                </div>
             </CardContent>
          </Card>

          {/* 2. Incident Brief & Description */}
          <Card className="border-none shadow-sm ring-1 ring-slate-200/60 rounded-2xl overflow-hidden">
             <CardHeader className="bg-slate-900 py-6">
                <div className="flex items-center justify-between">
                   <CardTitle className="text-sm font-black uppercase tracking-widest text-white flex items-center gap-2">
                      <FileText className="h-4 w-4 text-blue-400" /> Complaint Statement
                   </CardTitle>
                   <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg h-8 text-[10px] font-bold uppercase tracking-tighter">
                      Translate to English
                   </Button>
                </div>
             </CardHeader>
             <CardContent className="p-8">
                <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 relative group">
                   <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button variant="outline" size="sm" className="h-8 rounded-lg text-xs bg-white">Copy Text</Button>
                   </div>
                   <p className="text-sm text-slate-800 leading-relaxed font-medium whitespace-pre-wrap">
                      {complaint.description}
                   </p>
                </div>
                
                {complaint.incident_location && (
                  <div className="mt-6 flex items-center gap-2 p-4 bg-indigo-50/50 rounded-xl border border-indigo-100/50">
                     <Search className="h-4 w-4 text-indigo-500" />
                     <p className="text-xs font-bold text-indigo-900">Virtual Location/URL: <span className="font-medium underline ml-2 cursor-pointer">{complaint.incident_location}</span></p>
                  </div>
                )}
             </CardContent>
          </Card>

          {/* 3. Evidence Repository */}
          <Card className="border-none shadow-sm ring-1 ring-slate-200/60 rounded-2xl">
             <CardHeader className="bg-white border-b border-slate-100 py-6">
                <div className="flex items-center justify-between">
                   <CardTitle className="text-sm font-black uppercase tracking-widest text-slate-900 flex items-center gap-2">
                      <Shield className="h-4 w-4 text-blue-600" /> Evidence Repository
                   </CardTitle>
                   <Badge variant="secondary" className="bg-slate-100 text-slate-500 font-bold">{complaint.evidence_files?.length || 0} Artifacts</Badge>
                </div>
             </CardHeader>
             <CardContent className="p-8">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                   {complaint.evidence_files && complaint.evidence_files.length > 0 ? (
                      complaint.evidence_files.map((file: EvidenceFile) => (
                         <div key={file.id} className="group border border-slate-200 rounded-2xl overflow-hidden hover:shadow-xl hover:ring-2 hover:ring-blue-100 transition-all bg-white relative">
                            <div className="aspect-square bg-slate-50 flex items-center justify-center border-b border-slate-200">
                               {file.file_type === 'image' ? (
                                 <FileText className="h-10 w-10 text-slate-200 group-hover:scale-110 transition-transform" />
                               ) : (
                                 <Zap className="h-10 w-10 text-slate-200 group-hover:scale-110 transition-transform" />
                               )}
                               <div className="absolute inset-0 bg-blue-600/0 group-hover:bg-blue-600/10 transition-colors" />
                            </div>
                            <div className="p-4">
                               <p className="text-xs font-bold text-slate-900 truncate mb-1">{file.file_name}</p>
                               <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{file.mime_type}</p>
                               <div className="mt-4 flex items-center justify-between">
                                  <Badge variant="outline" className={cn("text-[9px] font-bold px-2", file.is_malware_scanned ? "bg-emerald-50 text-emerald-600 border-emerald-100" : "bg-slate-50 text-slate-400")}>
                                     {file.is_malware_scanned ? 'SCAN SECURE' : 'PENDING SCAN'}
                                  </Badge>
                                  <Button variant="ghost" size="icon" className="h-7 w-7 text-blue-600 hover:bg-blue-50">
                                     <Download className="h-4 w-4" />
                                  </Button>
                               </div>
                            </div>
                         </div>
                      ))
                   ) : (
                      <div className="col-span-full py-12 text-center border-2 border-dashed border-slate-200 rounded-3xl">
                         <AlertTriangle className="h-10 w-10 text-slate-200 mx-auto mb-4" />
                         <p className="text-sm font-bold text-slate-400 uppercase tracking-widest text-[10px]">No Physical Evidence Attached</p>
                      </div>
                   )}
                </div>
             </CardContent>
          </Card>
        </div>

        {/* Right Columns: Tactical Panels (Interactive) */}
        <div className="xl:col-span-4 space-y-8">
           
           {/* AI Analysis Panel */}
           <AIAnalysisPanel complaint={complaint} />

           {/* Decision Core */}
           <CaseDecisionPanel complaint={complaint} />

           {/* Communication Center */}
           <EmailDispatchPanel complaint={complaint} />

           {/* Activity Log / History */}
           <Card className="border-none shadow-sm ring-1 ring-slate-200/60 rounded-2xl overflow-hidden">
              <CardHeader className="bg-slate-50 border-b border-slate-100 flex items-center justify-between py-4">
                 <CardTitle className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                    <History className="h-3 w-3" /> System Audit Trail
                 </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                 <div className="divide-y divide-slate-100">
                    {complaint.status_history?.map((h: any, i: number) => (
                      <div key={h.id} className="p-4 flex gap-3 text-xs">
                         <div className="mt-0.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                         </div>
                         <div>
                            <p className="font-bold text-slate-900 leading-tight">
                               Status changed to <StatusBadge status={h.new_status} className="scale-75 origin-left" />
                            </p>
                            <p className="text-slate-500 mt-1 font-medium">By {h.changer?.full_name || 'System'}</p>
                            <p className="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-tighter">{formatDateTime(h.created_at)}</p>
                         </div>
                      </div>
                    ))}
                    <div className="p-4 flex gap-3 text-xs">
                       <div className="mt-0.5">
                          <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                       </div>
                       <div>
                          <p className="font-bold text-slate-900 leading-tight">Dossier Created & Assigned</p>
                          <p className="text-slate-500 mt-1 font-medium">Initial submission recorded</p>
                          <p className="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-tighter">{formatDateTime(complaint.created_at)}</p>
                       </div>
                    </div>
                 </div>
              </CardContent>
              <CardFooter className="bg-slate-50/50 justify-center py-3 border-t border-slate-100">
                 <Button variant="ghost" className="text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-blue-600 transition-colors">
                    View Comprehensive Audit Log
                 </Button>
              </CardFooter>
           </Card>
        </div>
      </div>
    </div>
  );
}
