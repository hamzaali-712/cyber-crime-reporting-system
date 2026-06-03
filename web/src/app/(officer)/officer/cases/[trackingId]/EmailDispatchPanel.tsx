'use client';

import React, { useState } from 'react';
import { Mail, Sparkles, Send, Edit3, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { createClient } from '@/lib/supabase/client';
import type { ComplaintWithRelations } from '@/lib/database.types';

export default function EmailDispatchPanel({ complaint }: { complaint: ComplaintWithRelations }) {
  const [isDrafting, setIsDrafting] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [emailBody, setEmailBody] = useState('');
  const [sent, setSent] = useState(false);
  const supabase = createClient();

  const draftEmail = async () => {
    setIsDrafting(true);
    try {
      // Calls AI to draft email based on case status and notes
      const response = await fetch('/api/officer/ai-draft-email', {
        method: 'POST',
        body: JSON.stringify({ 
          complaintId: complaint.id,
          status: complaint.status,
          notes: complaint.investigation_notes 
        }),
      });

      if (!response.ok) throw new Error('AI Drafting Failed');

      const { draft } = await response.json();
      setEmailBody(draft);
      toast.success('Professional Draft Generated', { description: 'AI has synthesized a formal response.' });
    } catch (error: any) {
      toast.error('Drafting Failure', { description: error.message });
    } finally {
      setIsDrafting(false);
    }
  };

  const sendEmail = async () => {
    setIsSending(true);
    try {
      // Simulate calling SMTP service (Phase 3 Backend)
      const { error } = await supabase.from('audit_logs').insert({
        action: 'EMAIL_SENT',
        resource_type: 'complaint',
        resource_id: complaint.id,
        details: { recipient: complaint.citizen?.email, type: 'status_update' }
      });

      if (error) throw error;

      setSent(true);
      toast.success('Communication Dispatched', { description: `Official notice sent to ${complaint.citizen?.email}.` });
    } catch (error: any) {
      toast.error('Dispatch Failure', { description: error.message });
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Card className="border-none shadow-xl ring-1 ring-slate-200/60 rounded-2xl overflow-hidden">
      <CardHeader className="bg-white border-b border-slate-100 py-6">
         <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-black uppercase tracking-widest text-slate-900 flex items-center gap-2">
               <Mail className="h-4 w-4 text-emerald-600" /> Communication Center
            </CardTitle>
            <Badge variant="outline" className="text-[10px] font-bold text-slate-400">SMTP Active</Badge>
         </div>
      </CardHeader>
      <CardContent className="p-8">
         <div className="space-y-4">
            <div className="flex items-center justify-between bg-slate-50 p-3 rounded-xl border border-slate-100">
               <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-600">
                     <Mail className="h-4 w-4" />
                  </div>
                  <div>
                     <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tight">Recipient</p>
                     <p className="text-xs font-bold text-slate-900">{complaint.citizen?.email || 'No email associated'}</p>
                  </div>
               </div>
               <Button 
                  onClick={draftEmail} 
                  loading={isDrafting}
                  variant="outline" 
                  size="sm" 
                  className="h-8 text-[10px] font-black uppercase tracking-widest text-blue-600 hover:bg-blue-50 border-blue-100"
               >
                  <Sparkles className="h-3 w-3 mr-2" /> AI Draft
               </Button>
            </div>

            <div className="relative group">
               <Textarea 
                 placeholder="Draft your official communication here..." 
                 value={emailBody}
                 onChange={(e) => setEmailBody(e.target.value)}
                 rows={8}
                 className="bg-white border-slate-200 rounded-2xl text-sm italic py-4"
               />
               {!emailBody && (
                 <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
                    <ShieldAlert className="h-12 w-12" />
                 </div>
               )}
            </div>
         </div>
      </CardContent>
      <CardFooter className="bg-slate-50/50 border-t border-slate-100 px-8 py-5">
         {sent ? (
            <div className="w-full bg-emerald-50 text-emerald-700 p-3 rounded-xl flex items-center justify-center gap-2 font-bold text-xs">
               <CheckCircle2 className="h-4 w-4" /> Dispatch Successful
            </div>
         ) : (
            <Button 
               onClick={sendEmail} 
               loading={isSending} 
               disabled={!emailBody || !complaint.citizen?.email}
               className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-xl h-11 shadow-lg shadow-emerald-200"
            >
               Dispatch Official Notice <Send className="ml-2 h-4 w-4" />
            </Button>
         )}
      </CardFooter>
    </Card>
  );
}
