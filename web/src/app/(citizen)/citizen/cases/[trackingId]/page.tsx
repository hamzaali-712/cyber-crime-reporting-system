import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { 
  ArrowLeft, 
  Download, 
  Clock, 
  MapPin, 
  Calendar, 
  Shield, 
  FileText,
  MessageSquare,
  Sparkles,
  ExternalLink,
  History,
  CheckCircle2,
  Star
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge, Badge } from '@/components/ui/badge';
import { formatDate, formatDateTime, formatFileSize, cn } from '@/lib/utils';
import type { ComplaintWithRelations, EvidenceFile } from '@/lib/database.types';

export default async function CaseDetailPage({
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
      evidence_files (*),
      ai_reports (*),
      status_history:complaint_status_history (*)
    `)
    .eq('tracking_id', trackingId)
    .single();

  if (!caseData || error) {
    return notFound();
  }

  const complaint = caseData as ComplaintWithRelations;

  const timelineSteps = [
    { label: 'Submitted', date: complaint.created_at, status: 'PENDING', icon: CheckCircle2 },
    { label: 'Under Review', date: complaint.status_history?.find(h => h.new_status === 'UNDER_REVIEW')?.created_at, status: 'UNDER_REVIEW', icon: Clock },
    { label: 'Decision', date: complaint.status_history?.find(h => ['APPROVED', 'REJECTED', 'SOLVED'].includes(h.new_status))?.created_at, status: 'APPROVED', icon: Shield },
    { label: 'Resolved', date: complaint.resolved_at, status: 'SOLVED', icon: Star },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-6xl mx-auto">
      {/* breadcrumbs-like back button */}
      <Link href="/citizen/cases" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to My Reports
      </Link>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{complaint.category}</h1>
            <StatusBadge status={complaint.status} />
          </div>
          <p className="text-gray-500 flex items-center gap-2">
            Tracking ID: <span className="font-mono font-bold text-gray-900">{complaint.tracking_id}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" /> Download PDF
          </Button>
          <Button className="bg-blue-600 hover:bg-blue-700">
            Submit Follow-up
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Case Details */}
        <div className="lg:col-span-2 space-y-8">
          <Card className="border-none shadow-sm ring-1 ring-gray-100">
            <CardHeader className="border-b border-gray-50 bg-gray-50/30">
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-600" /> Incident Description
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8 bg-gray-50 p-4 rounded-xl border border-gray-100">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-white border border-gray-100">
                    <Calendar className="h-4 w-4 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Incident Date</p>
                    <p className="text-sm font-semibold text-gray-900 mt-0.5">{formatDate(complaint.incident_date)}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-white border border-gray-100">
                    <MapPin className="h-4 w-4 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Location</p>
                    <p className="text-sm font-semibold text-gray-900 mt-0.5">{complaint.incident_location || 'Not Specified'}</p>
                  </div>
                </div>
              </div>
              <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                {complaint.description}
              </div>
            </CardContent>
          </Card>

          {/* Evidence Files */}
          <Card className="border-none shadow-sm ring-1 ring-gray-100">
            <CardHeader className="border-b border-gray-50">
              <CardTitle className="text-lg flex items-center gap-2">
                 Supporting Evidence 
                 <Badge variant="secondary" className="ml-2">{complaint.evidence_files?.length || 0}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {complaint.evidence_files && complaint.evidence_files.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {complaint.evidence_files.map((file: EvidenceFile) => (
                    <div key={file.id} className="group relative border border-gray-200 rounded-xl overflow-hidden hover:border-blue-300 transition-all shadow-sm hover:shadow-md">
                      {file.file_type === 'image' ? (
                        <div className="aspect-video bg-gray-50 flex items-center justify-center overflow-hidden">
                           <div className="flex flex-col items-center">
                              <Shield className="h-8 w-8 text-blue-200" />
                              <p className="text-[10px] text-gray-300 mt-2">SECURED IMAGE PREVIEW</p>
                           </div>
                        </div>
                      ) : (
                        <div className="aspect-video bg-gray-100 flex items-center justify-center">
                           <FileText className="h-12 w-12 text-gray-300" />
                        </div>
                      )}
                      <div className="p-3 border-t border-gray-200 bg-white">
                        <div className="flex items-center justify-between">
                           <div className="overflow-hidden">
                             <p className="text-sm font-bold text-gray-900 truncate">{file.file_name}</p>
                             <p className="text-xs text-gray-500 uppercase tracking-tighter">{file.mime_type} • {formatFileSize(file.file_size_bytes)}</p>
                           </div>
                           <Button variant="ghost" size="icon" className="h-8 w-8 text-blue-600">
                             <Download className="h-4 w-4" />
                           </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                   <p className="text-gray-400 text-sm">No evidence files provided.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Status & Sidebar Info */}
        <div className="space-y-8">
          <Card className="border-none shadow-sm ring-1 ring-gray-100 overflow-hidden">
             <CardHeader className="bg-gray-50 border-b border-gray-100">
                <CardTitle className="text-base flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-600" /> Track Status
                </CardTitle>
             </CardHeader>
             <CardContent className="p-6">
                <div className="space-y-6">
                   {timelineSteps.map((step, i) => {
                     const isDone = !!step.date;
                     const isLast = i === timelineSteps.length - 1;
                     return (
                       <div key={i} className="flex gap-4 relative">
                         {!isLast && (
                           <div className={cn(
                             "absolute top-8 left-4 w-0.5 h-10 -z-10",
                             isDone && timelineSteps[i+1]?.date ? "bg-blue-600" : "bg-gray-100"
                           )} />
                         )}
                         <div className={cn(
                            "h-8 w-8 rounded-full border-2 flex items-center justify-center shrink-0 transition-all",
                            isDone ? "bg-blue-600 border-blue-600 text-white" : "bg-white border-gray-200 text-gray-300"
                         )}>
                            <step.icon className="h-4 w-4" />
                         </div>
                         <div>
                            <p className={cn("text-sm font-bold", isDone ? "text-gray-900" : "text-gray-400")}>{step.label}</p>
                            {isDone && step.date ? (
                              <p className="text-xs text-gray-500 mt-0.5">{formatDate(step.date)}</p>
                            ) : (
                              <p className="text-[10px] text-gray-300 mt-1 italic uppercase tracking-widest">Pending</p>
                            )}
                         </div>
                       </div>
                     );
                   })}
                </div>
             </CardContent>
          </Card>

          {complaint.ai_reports && complaint.ai_reports.length > 0 && (
            <Card className="bg-gradient-to-br from-indigo-900 to-blue-800 text-white border-none shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <Sparkles className="h-24 w-24" />
              </div>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2 text-blue-100">
                  <Sparkles className="h-4 w-4 text-indigo-300" /> AI Preliminary Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                   <div>
                     <p className="text-[10px] font-bold text-blue-300 uppercase tracking-widest">Executive Summary</p>
                     <p className="text-xs text-white/90 leading-relaxed mt-1 line-clamp-4">
                       {complaint.ai_reports[0].executive_summary}
                     </p>
                   </div>
                   <div className="flex gap-4">
                      <div>
                        <p className="text-[10px] font-bold text-blue-300 uppercase tracking-widest">Risk Level</p>
                        <Badge variant={complaint.ai_reports[0].risk_assessment === 'HIGH' || complaint.ai_reports[0].risk_assessment === 'CRITICAL' ? 'danger' : 'warning'} className="mt-1 bg-white/10 text-white border-none">
                          {complaint.ai_reports[0].risk_assessment}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-blue-300 uppercase tracking-widest">Applicable Laws</p>
                        <p className="text-xs text-white font-bold mt-1 line-clamp-1">{complaint.ai_reports[0].incident_classification}</p>
                      </div>
                   </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
