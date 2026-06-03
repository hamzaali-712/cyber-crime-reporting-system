'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldCheck, MessageSquare, Lock, AlertCircle, Save, Gavel } from 'lucide-react';
import { toast } from 'sonner';
import { z } from 'zod';

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { createClient } from '@/lib/supabase/client';
import type { Complaint } from '@/lib/database.types';

const decisionSchema = z.object({
  status: z.string().min(1, 'Please select a case status'),
  investigation_notes: z.string().min(50, 'Investigation remarks must be at least 50 characters'),
  internal_notes: z.string().optional(),
});

type DecisionFormData = z.infer<typeof decisionSchema>;

export default function CaseDecisionPanel({ complaint }: { complaint: Complaint }) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    watch,
  } = useForm<DecisionFormData>({
    resolver: zodResolver(decisionSchema),
    defaultValues: {
      status: complaint.status,
      investigation_notes: complaint.investigation_notes || '',
      internal_notes: '',
    }
  });

  const onSubmit = async (data: DecisionFormData) => {
    setIsSubmitting(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // 1. Update complaint
      const { error: updateError } = await supabase
        .from('complaints')
        .update({
          status: data.status as any,
          investigation_notes: data.investigation_notes,
          updated_at: new Date().toISOString(),
        })
        .eq('id', complaint.id);

      if (updateError) throw updateError;

      // 2. Add to status history
      await supabase.from('complaint_status_history').insert({
        complaint_id: complaint.id,
        old_status: complaint.status as any,
        new_status: data.status as any,
        changer_id: user.id,
        remarks: data.internal_notes || 'Status updated during review.',
      });

      toast.success('Decision Recorded', { description: `Dossier status migrated to ${data.status.replace('_', ' ')}.` });
      router.refresh();
    } catch (error: any) {
      toast.error('Decision Failure', { description: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="border-none shadow-xl ring-1 ring-slate-200/60 rounded-2xl overflow-hidden">
      <CardHeader className="bg-slate-50 border-b border-slate-100 py-6">
         <CardTitle className="text-sm font-black uppercase tracking-widest text-slate-900 flex items-center gap-2">
            <Gavel className="h-4 w-4 text-blue-600" /> Judgment Core
         </CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
         <CardContent className="p-8 space-y-6">
            <Select 
               label="Current Resolution Status"
               options={[
                  { value: 'PENDING', label: 'Pending Review' },
                  { value: 'UNDER_REVIEW', label: 'Under Review' },
                  { value: 'UNDER_INVESTIGATION', label: 'Under Investigation' },
                  { value: 'APPROVED', label: 'Approved for Action' },
                  { value: 'REJECTED', label: 'Rejected / Invalid' },
                  { value: 'SOLVED', label: 'Case Resolved' },
                  { value: 'CLOSED', label: 'Closed' },
               ]}
               {...register('status')}
               error={errors.status?.message}
            />

            <div className="space-y-4">
               <div className="flex items-center justify-between">
                  <label className="block text-sm font-black text-slate-900 uppercase tracking-tight">Investigation Remarks</label>
                  <Badge variant="outline" className="bg-blue-50 text-[9px] text-blue-600 border-blue-100">Visible to Citizen</Badge>
               </div>
               <Textarea 
                 placeholder="Enter full technical and investigation details (Min 50 chars)..." 
                 rows={5}
                 className="bg-slate-50/50 border-slate-200 rounded-xl text-sm"
                 {...register('investigation_notes')}
                 error={errors.investigation_notes?.message}
               />
               <p className="text-[10px] text-slate-400 font-medium italic">
                  Note: These remarks will be shared via the citizen portal and official PDF report.
               </p>
            </div>

            <div className="space-y-4 pt-4 border-t border-slate-100">
               <div className="flex items-center gap-2 text-slate-400">
                  <Lock className="h-4 w-4" />
                  <label className="text-[10px] font-black uppercase tracking-widest">Internal Intelligence Notes</label>
               </div>
               <Textarea 
                 placeholder="Sensitive investigative notes (Restricted to officers)..." 
                 rows={3}
                 className="bg-slate-900 text-slate-300 border-none rounded-xl text-xs placeholder:text-slate-600"
                 {...register('internal_notes')}
               />
            </div>
         </CardContent>
         <CardFooter className="bg-slate-50/50 border-t border-slate-100 px-8 py-5">
            <Button 
               type="submit" 
               loading={isSubmitting} 
               disabled={!isDirty} 
               className="w-full bg-slate-900 hover:bg-black text-white font-black rounded-xl h-11 shadow-lg shadow-slate-200"
            >
               Record Official Decision <ShieldCheck className="ml-2 h-4 w-4" />
            </Button>
         </CardFooter>
      </form>
    </Card>
  );
}
