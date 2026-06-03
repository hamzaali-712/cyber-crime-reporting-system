import { z } from 'zod';
import { PECA_CATEGORIES } from './database.types';

// ---- Auth Schemas ----

export const signUpSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[a-z]/, 'Must contain a lowercase letter')
    .regex(/[0-9]/, 'Must contain a number')
    .regex(/[^A-Za-z0-9]/, 'Must contain a special character'),
  confirm_password: z.string(),
  cnic: z.string().regex(/^\d{5}-\d{7}-\d{1}$/, 'Format: XXXXX-XXXXXXX-X').optional().or(z.literal('')),
  phone: z.string().regex(/^(\+92|0)\d{10}$/, 'Valid Pakistani number required').optional().or(z.literal('')),
}).refine((d) => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});
export type SignUpFormData = z.infer<typeof signUpSchema>;

export const signInSchema = z.object({
  email: z.string().email('Valid email required'),
  password: z.string().min(1, 'Password is required'),
});
export type SignInFormData = z.infer<typeof signInSchema>;

export const forgotPasswordSchema = z.object({
  email: z.string().email('Valid email required'),
});
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export const resetPasswordSchema = z.object({
  password: z.string().min(8).regex(/[A-Z]/).regex(/[a-z]/).regex(/[0-9]/).regex(/[^A-Za-z0-9]/),
  confirm_password: z.string(),
}).refine((d) => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

// ---- Profile ----

export const profileUpdateSchema = z.object({
  full_name: z.string().min(2).max(100),
  cnic: z.string().regex(/^\d{5}-\d{7}-\d{1}$/).optional().or(z.literal('')),
  phone: z.string().regex(/^(\+92|0)\d{10}$/).optional().or(z.literal('')),
  address: z.string().max(500).optional().or(z.literal('')),
});
export type ProfileUpdateFormData = z.infer<typeof profileUpdateSchema>;

// ---- Complaint ----

export const complaintStep1Schema = z.object({
  category: z.enum(PECA_CATEGORIES as unknown as [string, ...string[]], {
    description: 'Select a crime category'
  } as any),
  incident_date: z.string().min(1, 'Date is required'),
  incident_location: z.string().max(500).optional().or(z.literal('')),
  description: z.string().min(50, 'At least 50 characters').max(10000),
  is_anonymous: z.boolean(),
});
export type ComplaintStep1Data = z.infer<typeof complaintStep1Schema>;

export const complaintSubmitSchema = complaintStep1Schema.extend({
  agree_terms: z.literal(true, {
    invalid_type_error: 'You must agree to the terms',
  } as any),
});
export type ComplaintSubmitData = z.infer<typeof complaintSubmitSchema>;

// ---- Officer Decision ----

export const officerDecisionSchema = z.object({
  decision: z.enum(['APPROVED', 'REJECTED', 'UNDER_INVESTIGATION', 'ESCALATED', 'SOLVED'] as const),
  investigation_notes: z.string().min(50, 'At least 50 characters required').max(5000),
  internal_notes: z.string().max(2000).optional().or(z.literal('')),
});
export type OfficerDecisionFormData = z.infer<typeof officerDecisionSchema>;

// ---- Email ----

export const emailDispatchSchema = z.object({
  recipient_email: z.string().email(),
  subject: z.string().min(1).max(200),
  body: z.string().min(10).max(10000),
});
export type EmailDispatchFormData = z.infer<typeof emailDispatchSchema>;

// ---- Officer Creation ----

export const createOfficerSchema = z.object({
  full_name: z.string().min(2).max(100),
  email: z.string().email(),
  designation: z.string().min(2).max(100),
  phone: z.string().regex(/^(\+92|0)\d{10}$/).optional().or(z.literal('')),
  temp_password: z.string().min(8),
});
export type CreateOfficerFormData = z.infer<typeof createOfficerSchema>;

// ---- Law ----

export const lawSchema = z.object({
  section_number: z.string().min(1),
  title: z.string().min(1).max(200),
  category: z.string().min(1),
  short_description: z.string().min(10).max(500),
  full_description: z.string().min(50).max(5000),
  punishment: z.string().min(10).max(1000),
  is_published: z.boolean().default(true),
});
export type LawFormData = z.infer<typeof lawSchema>;

// ---- Chat ----

export const chatMessageSchema = z.object({
  message: z.string().min(1).max(5000),
});
export type ChatMessageFormData = z.infer<typeof chatMessageSchema>;
