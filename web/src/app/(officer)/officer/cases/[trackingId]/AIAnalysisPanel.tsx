'use client';

import React, { useState } from 'react';
import { Sparkles, BrainCircuit, ShieldAlert, Scale, ChevronDown, CheckCircle2, Zap, FileText } from 'lucide-react';
import { toast } from 'sonner';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { createClient } from '@/lib/supabase/client';
import type { ComplaintWithRelations } from '@/lib/database.types';

export default function AIAnalysisPanel({ complaint }: { complaint: ComplaintWithRelations }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [report, setReport] = useState(complaint.ai_reports?.[0] || null);
  const supabase = createClient();

  const generateAIReport = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/officer/ai-analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ complaintId: complaint.id }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'AI Service Timeout');
      }

      const newReport = await response.json();
      setReport(newReport);
      toast.success('AI Report Synthesized', { description: 'Case dossier updated with intelligence.' });
    } catch (error: any) {
      toast.error('Synthesis Failed', { description: error.message });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card className="bg-gradient-to-br from-indigo-950 to-blue-900 text-white border-none shadow-2xl relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform duration-1000">
        <BrainCircuit className="h-48 w-48 text-white" />
      </div>
      
      <CardHeader className="relative z-10 border-b border-white/10">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xs font-black uppercase tracking-widest text-indigo-300 flex items-center gap-2">
             <Sparkles className="h-4 w-4" /> NCIA Digital Intel
          </CardTitle>
          {report && (
            <Badge className="bg-emerald-500/20 text-emerald-300 border-none text-[10px] uppercase font-black">
              Verified by Llama 3.3
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="relative z-10 p-6">
        {!report ? (
          <div className="py-8 text-center">
            <p className="text-sm text-indigo-200 mb-6 font-medium">Use Large Language Models to analyze the statement and map to PECA 2016 law sections.</p>
            <Button 
              onClick={generateAIReport} 
              loading={isGenerating}
              className="bg-white text-indigo-950 hover:bg-indigo-50 font-black shadow-xl shadow-indigo-900/40 rounded-xl px-8"
            >
              Synthesize Intelligence <Zap className="ml-2 h-4 w-4 fill-indigo-950" />
            </Button>
          </div>
        ) : (
          <div className="space-y-6 animate-in zoom-in-95 duration-500">
            <div className="grid grid-cols-2 gap-4">
               <div>
                  <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mb-1">Risk Assessment</p>
                  <Badge variant={report.risk_assessment === 'HIGH' || report.risk_assessment === 'CRITICAL' ? 'danger' : 'warning'} className="bg-white/10 text-white border-none py-1 group-hover:bg-white/20 transition-colors">
                     {report.risk_assessment}
                  </Badge>
               </div>
               <div>
                  <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest mb-1">Legal Mapping</p>
                  <p className="text-xs font-bold text-white leading-none mt-2 truncate underline decoration-indigo-400 decoration-2">
                    {report.incident_classification}
                  </p>
               </div>
            </div>

            <div className="space-y-2">
               <p className="text-[10px] font-black text-indigo-300 uppercase tracking-widest flex items-center gap-2">
                  <FileText className="h-3 w-3" /> Executive Summary
               </p>
               <p className="text-xs text-indigo-50/90 leading-relaxed font-medium bg-white/5 p-3 rounded-xl border border-white/5 italic">
                  "{report.executive_summary}"
               </p>
            </div>

            <div className="pt-4 border-t border-white/10 flex items-center justify-between">
               <div className="flex -space-x-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-6 w-6 rounded-full border border-indigo-900 bg-indigo-700 flex items-center justify-center text-[10px] font-bold">
                       {i}
                    </div>
                  ))}
                  <div className="px-3 py-1 text-[10px] font-bold text-indigo-300">Sections Identified</div>
               </div>
               <Button variant="ghost" size="sm" className="h-7 text-[10px] font-black uppercase text-indigo-300 hover:text-white hover:bg-white/10 rounded-lg">
                  Full Mapping <ChevronDown className="ml-2 h-3 w-3" />
               </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
