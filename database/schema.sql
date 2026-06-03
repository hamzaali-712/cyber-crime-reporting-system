-- ============================================================
-- Pakistan National Cyber Crime Reporting System (CCRS)
-- Complete PostgreSQL Schema with Row Level Security
-- Supabase Compatible
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE complaint_status AS ENUM (
  'PENDING',
  'UNDER_REVIEW',
  'APPROVED',
  'REJECTED',
  'UNDER_INVESTIGATION',
  'ESCALATED',
  'SOLVED',
  'CLOSED'
);

CREATE TYPE user_role AS ENUM (
  'citizen',
  'officer',
  'admin'
);

CREATE TYPE evidence_type AS ENUM (
  'image',
  'video',
  'document',
  'other'
);

CREATE TYPE email_status AS ENUM (
  'queued',
  'sent',
  'delivered',
  'failed',
  'bounced'
);

CREATE TYPE risk_level AS ENUM (
  'LOW',
  'MEDIUM',
  'HIGH',
  'CRITICAL'
);

CREATE TYPE audit_action AS ENUM (
  'LOGIN',
  'LOGOUT',
  'COMPLAINT_CREATED',
  'COMPLAINT_UPDATED',
  'STATUS_CHANGED',
  'DECISION_MADE',
  'EMAIL_SENT',
  'OFFICER_CREATED',
  'OFFICER_UPDATED',
  'USER_SUSPENDED',
  'USER_ACTIVATED',
  'PASSWORD_RESET',
  'FILE_UPLOADED',
  'AI_REPORT_GENERATED',
  'LAW_CREATED',
  'LAW_UPDATED',
  'LAW_DELETED',
  'SETTINGS_UPDATED'
);

-- ============================================================
-- PROFILES TABLE (extends auth.users)
-- ============================================================

CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  cnic TEXT, -- National ID, nullable for anonymous
  phone TEXT,
  address TEXT,
  avatar_url TEXT,
  role user_role NOT NULL DEFAULT 'citizen',
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- OFFICERS TABLE (extends profiles for officer-specific data)
-- ============================================================

CREATE TABLE officers (
  id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
  officer_id TEXT UNIQUE NOT NULL, -- Format: CYBER{YEAR}{NAME}
  designation TEXT NOT NULL DEFAULT 'Cyber Crime Officer',
  badge_number TEXT,
  department TEXT DEFAULT 'National Cyber Investigation Agency',
  cases_assigned INTEGER NOT NULL DEFAULT 0,
  cases_resolved INTEGER NOT NULL DEFAULT 0,
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  force_password_change BOOLEAN NOT NULL DEFAULT true
);

-- ============================================================
-- COMPLAINTS TABLE
-- ============================================================

CREATE TABLE complaints (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tracking_id TEXT UNIQUE NOT NULL, -- Format: CCRS-YYYYMMDD-XXXXX
  citizen_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  is_anonymous BOOLEAN NOT NULL DEFAULT false,
  
  -- Incident details
  category TEXT NOT NULL,
  incident_date DATE NOT NULL,
  incident_location TEXT,
  description TEXT NOT NULL,
  
  -- Status tracking
  status complaint_status NOT NULL DEFAULT 'PENDING',
  assigned_officer_id UUID REFERENCES officers(id) ON DELETE SET NULL,
  
  -- AI generated
  ai_summary TEXT,
  risk_level risk_level,
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at TIMESTAMPTZ
);

-- Create index for fast lookups
CREATE INDEX idx_complaints_tracking_id ON complaints(tracking_id);
CREATE INDEX idx_complaints_citizen_id ON complaints(citizen_id);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_category ON complaints(category);
CREATE INDEX idx_complaints_created_at ON complaints(created_at DESC);
CREATE INDEX idx_complaints_assigned_officer ON complaints(assigned_officer_id);

-- ============================================================
-- EVIDENCE FILES TABLE
-- ============================================================

CREATE TABLE evidence_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_type evidence_type NOT NULL,
  mime_type TEXT NOT NULL,
  file_size_bytes BIGINT NOT NULL,
  storage_path TEXT NOT NULL, -- Supabase Storage path
  sha256_hash TEXT,
  is_malware_scanned BOOLEAN NOT NULL DEFAULT false,
  is_clean BOOLEAN,
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_evidence_complaint ON evidence_files(complaint_id);

-- ============================================================
-- OFFICER DECISIONS TABLE
-- ============================================================

CREATE TABLE officer_decisions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
  officer_id UUID NOT NULL REFERENCES officers(id) ON DELETE RESTRICT,
  decision complaint_status NOT NULL,
  investigation_notes TEXT NOT NULL, -- Min 50 chars enforced at app level
  internal_notes TEXT, -- Not visible to citizen
  is_final BOOLEAN NOT NULL DEFAULT false, -- Immutable once true
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_decisions_complaint ON officer_decisions(complaint_id);
CREATE INDEX idx_decisions_officer ON officer_decisions(officer_id);

-- ============================================================
-- CASE EMAILS TABLE
-- ============================================================

CREATE TABLE case_emails (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
  sent_by UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
  recipient_email TEXT NOT NULL,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  status email_status NOT NULL DEFAULT 'queued',
  error_message TEXT,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_emails_complaint ON case_emails(complaint_id);

-- ============================================================
-- AI REPORTS TABLE
-- ============================================================

CREATE TABLE ai_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
  generated_by UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
  executive_summary TEXT NOT NULL,
  incident_classification TEXT NOT NULL,
  key_evidence_points TEXT NOT NULL,
  recommended_actions TEXT NOT NULL,
  risk_assessment risk_level NOT NULL,
  suggested_timeline TEXT,
  raw_ai_response TEXT,
  model_used TEXT NOT NULL DEFAULT 'llama-3.3-70b-versatile',
  is_edited BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ai_reports_complaint ON ai_reports(complaint_id);

-- ============================================================
-- CHAT SESSIONS TABLE
-- ============================================================

CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL DEFAULT 'New Chat',
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);

-- ============================================================
-- CHAT MESSAGES TABLE
-- ============================================================

CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);

-- ============================================================
-- PECA LAWS TABLE
-- ============================================================

CREATE TABLE laws (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  section_number TEXT NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  short_description TEXT NOT NULL,
  full_description TEXT NOT NULL,
  punishment TEXT NOT NULL,
  is_published BOOLEAN NOT NULL DEFAULT true,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- AUDIT LOGS TABLE
-- ============================================================

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  action audit_action NOT NULL,
  resource_type TEXT NOT NULL, -- e.g., 'complaint', 'officer', 'user'
  resource_id TEXT, -- ID of the affected resource
  details JSONB, -- Additional context
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'info', -- info, success, warning, error
  is_read BOOLEAN NOT NULL DEFAULT false,
  link TEXT, -- Optional deep link
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = false;

-- ============================================================
-- COMPLAINT STATUS HISTORY TABLE
-- ============================================================

CREATE TABLE complaint_status_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
  old_status complaint_status,
  new_status complaint_status NOT NULL,
  changed_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_status_history_complaint ON complaint_status_history(complaint_id);

-- ============================================================
-- UPDATED_AT TRIGGER FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to relevant tables
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_complaints_updated_at BEFORE UPDATE ON complaints
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_reports_updated_at BEFORE UPDATE ON ai_reports
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_laws_updated_at BEFORE UPDATE ON laws
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- TRACKING ID GENERATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION generate_tracking_id()
RETURNS TRIGGER AS $$
DECLARE
  date_part TEXT;
  random_part TEXT;
BEGIN
  date_part := to_char(now(), 'YYYYMMDD');
  random_part := upper(substr(md5(random()::text), 1, 5));
  NEW.tracking_id := 'CCRS-' || date_part || '-' || random_part;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_tracking_id BEFORE INSERT ON complaints
  FOR EACH ROW WHEN (NEW.tracking_id IS NULL)
  EXECUTE FUNCTION generate_tracking_id();

-- ============================================================
-- STATUS CHANGE HISTORY TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION log_status_change()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.status IS DISTINCT FROM NEW.status THEN
    INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_by)
    VALUES (NEW.id, OLD.status, NEW.status, auth.uid());
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER complaint_status_change AFTER UPDATE ON complaints
  FOR EACH ROW EXECUTE FUNCTION log_status_change();

-- ============================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE officers ENABLE ROW LEVEL SECURITY;
ALTER TABLE complaints ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE officer_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE laws ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE complaint_status_history ENABLE ROW LEVEL SECURITY;

-- ---- PROFILES ----
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Officers can view all profiles" ON profiles
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

CREATE POLICY "Admins can manage all profiles" ON profiles
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

CREATE POLICY "New users can insert their profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- ---- COMPLAINTS ----
CREATE POLICY "Citizens can view own complaints" ON complaints
  FOR SELECT USING (citizen_id = auth.uid());

CREATE POLICY "Citizens can create complaints" ON complaints
  FOR INSERT WITH CHECK (citizen_id = auth.uid() OR is_anonymous = true);

CREATE POLICY "Officers can view all complaints" ON complaints
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

CREATE POLICY "Officers can update complaints" ON complaints
  FOR UPDATE USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

CREATE POLICY "Admins can delete complaints" ON complaints
  FOR DELETE USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- ---- EVIDENCE FILES ----
CREATE POLICY "Citizens can view own evidence" ON evidence_files
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM complaints WHERE complaints.id = evidence_files.complaint_id AND complaints.citizen_id = auth.uid())
  );

CREATE POLICY "Citizens can upload evidence" ON evidence_files
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM complaints WHERE complaints.id = evidence_files.complaint_id AND complaints.citizen_id = auth.uid())
  );

CREATE POLICY "Officers can view all evidence" ON evidence_files
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

-- ---- OFFICER DECISIONS ----
CREATE POLICY "Citizens can view decisions on own complaints" ON officer_decisions
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM complaints WHERE complaints.id = officer_decisions.complaint_id AND complaints.citizen_id = auth.uid())
  );

CREATE POLICY "Officers can create decisions" ON officer_decisions
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

CREATE POLICY "Officers can view all decisions" ON officer_decisions
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

-- ---- CASE EMAILS ----
CREATE POLICY "Officers can manage case emails" ON case_emails
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

-- ---- AI REPORTS ----
CREATE POLICY "Citizens can view AI reports on own complaints" ON ai_reports
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM complaints WHERE complaints.id = ai_reports.complaint_id AND complaints.citizen_id = auth.uid())
  );

CREATE POLICY "Officers can manage AI reports" ON ai_reports
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

-- ---- CHAT ----
CREATE POLICY "Users can manage own chat sessions" ON chat_sessions
  FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can manage own chat messages" ON chat_messages
  FOR ALL USING (
    EXISTS (SELECT 1 FROM chat_sessions WHERE chat_sessions.id = chat_messages.session_id AND chat_sessions.user_id = auth.uid())
  );

-- ---- LAWS ----
CREATE POLICY "Anyone can view published laws" ON laws
  FOR SELECT USING (is_published = true);

CREATE POLICY "Admins can manage laws" ON laws
  FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

-- ---- AUDIT LOGS ----
CREATE POLICY "Admins can view audit logs" ON audit_logs
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'admin')
  );

CREATE POLICY "System can insert audit logs" ON audit_logs
  FOR INSERT WITH CHECK (true); -- Allows server-side inserts

-- ---- NOTIFICATIONS ----
CREATE POLICY "Users can view own notifications" ON notifications
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update own notifications" ON notifications
  FOR UPDATE USING (user_id = auth.uid());

-- ---- STATUS HISTORY ----
CREATE POLICY "Citizens can view own complaint history" ON complaint_status_history
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM complaints WHERE complaints.id = complaint_status_history.complaint_id AND complaints.citizen_id = auth.uid())
  );

CREATE POLICY "Officers can view all status history" ON complaint_status_history
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role IN ('officer', 'admin'))
  );

-- ============================================================
-- PROFILE CREATION TRIGGER (on auth.users insert)
-- ============================================================

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, full_name, role)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', 'User'),
    COALESCE((NEW.raw_user_meta_data->>'role')::user_role, 'citizen')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
