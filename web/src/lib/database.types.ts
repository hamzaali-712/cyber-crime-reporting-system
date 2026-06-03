// ============================================================
// Database types matching the Supabase PostgreSQL schema
// ============================================================

export type ComplaintStatus =
  | 'PENDING'
  | 'UNDER_REVIEW'
  | 'APPROVED'
  | 'REJECTED'
  | 'UNDER_INVESTIGATION'
  | 'ESCALATED'
  | 'SOLVED'
  | 'CLOSED';

export type UserRole = 'citizen' | 'officer' | 'admin';
export type EvidenceType = 'image' | 'video' | 'document' | 'other';
export type EmailStatus = 'queued' | 'sent' | 'delivered' | 'failed' | 'bounced';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AuditAction =
  | 'LOGIN' | 'LOGOUT'
  | 'COMPLAINT_CREATED' | 'COMPLAINT_UPDATED' | 'STATUS_CHANGED'
  | 'DECISION_MADE' | 'EMAIL_SENT'
  | 'OFFICER_CREATED' | 'OFFICER_UPDATED'
  | 'USER_SUSPENDED' | 'USER_ACTIVATED' | 'PASSWORD_RESET'
  | 'FILE_UPLOADED' | 'AI_REPORT_GENERATED'
  | 'LAW_CREATED' | 'LAW_UPDATED' | 'LAW_DELETED'
  | 'SETTINGS_UPDATED';

// ---- Row types ----

export interface Profile {
  id: string;
  full_name: string;
  cnic: string | null;
  phone: string | null;
  address: string | null;
  avatar_url: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  email?: string;
}

export interface Officer {
  id: string;
  officer_id: string;
  designation: string;
  badge_number: string | null;
  department: string;
  cases_assigned: number;
  cases_resolved: number;
  joined_at: string;
  force_password_change: boolean;
}

export interface OfficerWithProfile extends Officer {
  profile: Profile;
}

export interface Complaint {
  id: string;
  tracking_id: string;
  citizen_id: string | null;
  is_anonymous: boolean;
  category: string;
  incident_date: string;
  incident_location: string | null;
  description: string;
  status: ComplaintStatus;
  assigned_officer_id: string | null;
  investigation_notes: string | null;
  internal_notes: string | null;
  ai_summary: string | null;
  risk_level: RiskLevel | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface ComplaintWithRelations extends Complaint {
  citizen?: Profile | null;
  assigned_officer?: OfficerWithProfile | null;
  evidence_files?: EvidenceFile[];
  decisions?: OfficerDecision[];
  status_history?: ComplaintStatusHistory[];
  ai_reports?: AIReport[];
}

export interface EvidenceFile {
  id: string;
  complaint_id: string;
  file_name: string;
  file_type: EvidenceType;
  mime_type: string;
  file_size_bytes: number;
  storage_path: string;
  sha256_hash: string | null;
  is_malware_scanned: boolean;
  is_clean: boolean | null;
  uploaded_at: string;
}

export interface OfficerDecision {
  id: string;
  complaint_id: string;
  officer_id: string;
  decision: ComplaintStatus;
  investigation_notes: string;
  internal_notes: string | null;
  is_final: boolean;
  created_at: string;
  officer?: OfficerWithProfile;
}

export interface CaseEmail {
  id: string;
  complaint_id: string;
  sent_by: string;
  recipient_email: string;
  subject: string;
  body: string;
  status: EmailStatus;
  error_message: string | null;
  sent_at: string | null;
  created_at: string;
}

export interface AIReport {
  id: string;
  complaint_id: string;
  generated_by: string;
  executive_summary: string;
  incident_classification: string;
  key_evidence_points: string;
  recommended_actions: string;
  risk_assessment: RiskLevel;
  suggested_timeline: string | null;
  raw_ai_response: string | null;
  model_used: string;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface Law {
  id: string;
  section_number: string;
  title: string;
  category: string;
  short_description: string;
  full_description: string;
  punishment: string;
  is_published: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: AuditAction;
  resource_type: string;
  resource_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
  user?: Profile | null;
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  link: string | null;
  created_at: string;
}

export interface ComplaintStatusHistory {
  id: string;
  complaint_id: string;
  old_status: ComplaintStatus | null;
  new_status: ComplaintStatus;
  changed_by: string | null;
  notes: string | null;
  created_at: string;
  changer?: Profile | null;
}

// ---- Stats Types ----

export interface CitizenStats {
  total: number;
  pending: number;
  under_review: number;
  approved: number;
  rejected: number;
  solved: number;
}

export interface OfficerStats {
  total_assigned: number;
  pending_review: number;
  approved_today: number;
  rejected_today: number;
  avg_resolution_days: number;
}

export interface AdminStats {
  total_complaints: number;
  total_complaints_this_month: number;
  total_citizens: number;
  total_officers: number;
  resolution_rate: number;
  avg_resolution_days: number;
  sla_breach_count: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface MonthlyTrend {
  month: string;
  count: number;
}

export interface OfficerPerformance {
  officer_id: string;
  officer_name: string;
  cases_resolved: number;
  cases_assigned: number;
  approval_rate: number;
}

// ---- Constants ----

export const PECA_CATEGORIES = [
  'Unauthorized Access',
  'Data Theft',
  'System Interference',
  'Data Interference',
  'Forgery & Fraud',
  'Cyber Weapons',
  'Terrorism',
  'Content Offenses',
  'Sexual Offenses',
  'Malware',
  'Harassment',
  'Nuisance',
  'Identity Theft',
  'Privacy Violations',
  'Telecom Fraud',
  'Financial Cyber Crime',
  'Other',
] as const;

export type PecaCategory = (typeof PECA_CATEGORIES)[number];

export const STATUS_CONFIG: Record<ComplaintStatus, {
  label: string;
  color: string;
  bgClass: string;
  textClass: string;
}> = {
  PENDING: { label: 'Pending', color: '#f59e0b', bgClass: 'bg-amber-500/10', textClass: 'text-amber-500' },
  UNDER_REVIEW: { label: 'Under Review', color: '#3b82f6', bgClass: 'bg-blue-500/10', textClass: 'text-blue-500' },
  APPROVED: { label: 'Approved', color: '#22c55e', bgClass: 'bg-green-500/10', textClass: 'text-green-500' },
  REJECTED: { label: 'Rejected', color: '#ef4444', bgClass: 'bg-red-500/10', textClass: 'text-red-500' },
  UNDER_INVESTIGATION: { label: 'Investigating', color: '#8b5cf6', bgClass: 'bg-purple-500/10', textClass: 'text-purple-500' },
  ESCALATED: { label: 'Escalated', color: '#f97316', bgClass: 'bg-orange-500/10', textClass: 'text-orange-500' },
  SOLVED: { label: 'Solved', color: '#10b981', bgClass: 'bg-emerald-500/10', textClass: 'text-emerald-500' },
  CLOSED: { label: 'Closed', color: '#6b7280', bgClass: 'bg-gray-500/10', textClass: 'text-gray-500' },
};
