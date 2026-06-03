'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { 
  ShieldAlert, 
  ChevronRight, 
  ChevronLeft, 
  Upload, 
  Info, 
  CheckCircle2, 
  FileText,
  AlertTriangle,
  X
} from 'lucide-react';
import { toast } from 'sonner';

import { 
  complaintStep1Schema, 
  complaintSubmitSchema,
  type ComplaintStep1Data,
  type ComplaintSubmitData 
} from '@/lib/validations';
import { PECA_CATEGORIES } from '@/lib/database.types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select } from '@/components/ui/select';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn, formatFileSize } from '@/lib/utils';
import { createClient } from '../../../../../lib/supabase/client';

export default function NewReportWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const supabase = createClient();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    trigger,
  } = useForm<ComplaintSubmitData>({
    resolver: zodResolver(complaintSubmitSchema),
    defaultValues: {
      is_anonymous: false,
      agree_terms: false as any,
    }
  });

  const formData = watch();

  const nextStep = async () => {
    const isStepValid = await trigger();
    if (isStepValid) {
      setStep(s => s + 1);
      window.scrollTo(0, 0);
    }
  };

  const prevStep = () => {
    setStep(s => s - 1);
    window.scrollTo(0, 0);
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      // Basic validation: max 5 files
      if (files.length + newFiles.length > 5) {
        toast.error('Limit Exceeded', { description: 'You can upload maximum 5 files.' });
        return;
      }
      setFiles([...files, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const onSubmit = async (data: ComplaintSubmitData) => {
    setIsSubmitting(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      // 1. Create complaint record
      const { data: complaint, error: complaintError } = await supabase
        .from('complaints')
        .insert({
          citizen_id: user?.id,
          category: data.category,
          incident_date: data.incident_date,
          incident_location: data.incident_location,
          description: data.description,
          is_anonymous: data.is_anonymous,
          status: 'PENDING',
        })
        .select()
        .single();

      if (complaintError) throw complaintError;

      // 2. Upload files if any
      if (files.length > 0) {
        for (const file of files) {
          const fileExt = file.name.split('.').pop();
          const filePath = `${complaint.id}/${Math.random().toString(36).substring(2)}.${fileExt}`;
          
          const { error: uploadError } = await supabase.storage
            .from('evidence')
            .upload(filePath, file);

          if (uploadError) {
            toast.warning(`File Upload Failed: ${file.name}`);
            continue;
          }

          // Store metadata in DB
          await supabase.from('evidence_files').insert({
            complaint_id: complaint.id,
            file_name: file.name,
            file_type: file.type.startsWith('image/') ? 'image' : file.type.startsWith('video/') ? 'video' : 'document',
            mime_type: file.type,
            file_size_bytes: file.size,
            storage_path: filePath,
          });
        }
      }

      toast.success('Complaint Submitted Successfully!', {
        description: `Tracking ID: ${complaint.tracking_id}`,
      });
      router.push(`/citizen/cases/${complaint.tracking_id}`);
    } catch (error: any) {
      toast.error('Submission Failed', { description: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const steps = [
    { title: 'Incident Details', desc: 'What happened?', icon: Info },
    { title: 'Evidence', desc: 'Upload proof', icon: Upload },
    { title: 'Review & Submit', desc: 'Final check', icon: CheckCircle2 },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-10">
      {/* Stepper Header */}
      <div className="flex items-center justify-between">
        {steps.map((s, i) => {
          const currentStep = i + 1;
          const isComplete = step > currentStep;
          const isActive = step === currentStep;
          return (
            <div key={i} className="flex flex-col items-center gap-2 flex-1 relative">
              {i !== 0 && (
                <div 
                  className={cn(
                    "absolute top-5 -left-1/2 w-full h-[2px] -z-10",
                    isComplete ? "bg-blue-600" : "bg-gray-200"
                  )} 
                />
              )}
              <div 
                className={cn(
                  "h-10 w-10 rounded-full flex items-center justify-center font-bold transition-all border-2",
                  isComplete ? "bg-blue-600 border-blue-600 text-white" : 
                  isActive ? "bg-white border-blue-600 text-blue-600 shadow-md scale-110" : 
                  "bg-white border-gray-200 text-gray-400"
                )}
              >
                {isComplete ? <CheckCircle2 className="h-5 w-5" /> : currentStep}
              </div>
              <div className="text-center">
                <p className={cn("text-xs font-bold uppercase tracking-wider", isActive ? "text-blue-900" : "text-gray-400")}>
                  {s.title}
                </p>
                <p className="text-[10px] text-gray-400 hidden sm:block">{s.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      <Card className="shadow-xl border-none ring-1 ring-gray-100">
        <CardHeader className="border-b border-gray-50 pb-8">
          <CardTitle className="text-2xl">{steps[step-1].title}</CardTitle>
          <CardDescription>{steps[step-1].desc}</CardDescription>
        </CardHeader>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="py-8">
            {step === 1 && (
              <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Select
                    label="Incident Category"
                    options={PECA_CATEGORIES.map(c => ({ value: c, label: c }))}
                    placeholder="Select crime type"
                    {...register('category')}
                    error={errors.category?.message}
                  />
                  <Input
                    label="Date of Incident"
                    type="date"
                    {...register('incident_date')}
                    error={errors.incident_date?.message}
                  />
                </div>

                <Input
                  label="Location (Optional)"
                  placeholder="e.g. Website URL, City, or Virtual Space"
                  {...register('incident_location')}
                  error={errors.incident_location?.message}
                />

                <Textarea
                  label="Detailed Description"
                  placeholder="Describe the incident in detail. Include what happened, how it started, and any impact."
                  rows={6}
                  {...register('description')}
                  error={errors.description?.message}
                />

                <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <input
                    type="checkbox"
                    id="is_anonymous"
                    {...register('is_anonymous')}
                    className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="is_anonymous" className="text-sm font-medium text-blue-900">
                    Submit this report anonymously
                    <span className="block text-xs font-normal text-blue-700 mt-0.5">
                      Your identity will be hidden from the public, but stored for legal verification.
                    </span>
                  </label>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6 animate-in slide-in-from-right-4 duration-300 text-center py-4">
                <div 
                  className={cn(
                    "border-2 border-dashed rounded-2xl p-12 transition-all",
                    "hover:bg-blue-50/50 hover:border-blue-300 group cursor-pointer"
                  )}
                  onClick={() => document.getElementById('file-upload')?.click()}
                >
                  <input
                    type="file"
                    id="file-upload"
                    multiple
                    className="hidden"
                    onChange={onFileChange}
                    accept="image/*,video/*,.pdf,.doc,.docx"
                  />
                  <div className="bg-blue-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                    <Upload className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">Click to upload evidence</h3>
                  <p className="text-sm text-gray-500 mt-2 max-w-sm mx-auto">
                    Allowed formats: Images (PNG/JPG), Video (MP4), Documents (PDF/DOCX). Max 5 files.
                  </p>
                </div>

                {files.length > 0 && (
                  <div className="text-left space-y-3">
                    <h4 className="font-bold text-gray-900 flex items-center gap-2">
                       Selected Files <Badge variant="secondary">{files.length}</Badge>
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {files.map((file, i) => (
                        <div key={i} className="bg-white border border-gray-200 rounded-xl p-3 flex items-center justify-between animate-in zoom-in-95 duration-200">
                          <div className="flex items-center gap-3 overflow-hidden">
                            <div className="h-10 w-10 rounded bg-gray-50 flex items-center justify-center text-gray-400 shrink-0">
                              <FileText className="h-5 w-5" />
                            </div>
                            <div className="overflow-hidden">
                              <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                              <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                            </div>
                          </div>
                          <button 
                            type="button" 
                            onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                            className="p-1 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-red-500"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 flex gap-3 text-left">
                  <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-bold text-amber-900">Important</p>
                    <p className="text-xs text-amber-700 leading-relaxed mt-1">
                      Do not modify evidence files. Tampered evidence may be inadmissible in court. 
                      Keep original files on your device until the investigation is complete.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                 <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 space-y-4">
                    <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                       <h3 className="font-bold text-gray-900">Summary Review</h3>
                       <Badge variant={formData.is_anonymous ? 'warning' : 'info'}>
                         {formData.is_anonymous ? 'Anonymous' : 'Full Reporting'}
                       </Badge>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                       <div>
                         <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Category</p>
                         <p className="text-sm font-semibold text-gray-900 mt-1">{formData.category}</p>
                       </div>
                       <div>
                         <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Incident Date</p>
                         <p className="text-sm font-semibold text-gray-900 mt-1">{formData.incident_date}</p>
                       </div>
                       <div>
                         <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Evidence</p>
                         <p className="text-sm font-semibold text-gray-900 mt-1">{files.length} file(s)</p>
                       </div>
                    </div>

                    <div>
                      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Description</p>
                      <p className="text-sm text-gray-700 mt-1 leading-relaxed whitespace-pre-wrap">{formData.description}</p>
                    </div>
                 </div>

                 <div className="space-y-4">
                    <div className="flex items-start gap-3">
                       <input 
                         type="checkbox" 
                         id="agree_terms"
                         {...register('agree_terms')}
                         className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 mt-1"
                       />
                       <label htmlFor="agree_terms" className="text-sm text-gray-600 cursor-pointer">
                         I solemnly swear that the information provided is accurate and true to the best of my knowledge. 
                         I understand that knowingly providing false information is an offense under PECA 2016.
                       </label>
                    </div>
                    {errors.agree_terms && <p className="text-xs text-red-500 ml-8">{errors.agree_terms.message}</p>}
                 </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex items-center justify-between border-t border-gray-50 pt-8 mt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={prevStep} 
              disabled={step === 1 || isSubmitting}
              className="px-8"
            >
              <ChevronLeft className="mr-2 h-4 w-4" /> Back
            </Button>

            {step < 3 ? (
              <Button type="button" onClick={nextStep} className="px-8">
                Next Step <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button type="submit" loading={isSubmitting} className="px-12 bg-blue-700">
                Submit Official Report <CheckCircle2 className="ml-2 h-4 w-4" />
              </Button>
            )}
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
