'use server';

import { createClient } from './supabase/server';
import type { AuditAction } from './database.types';

export async function createAuditLog(
  action: AuditAction,
  resourceType: string,
  resourceId?: string,
  details?: Record<string, unknown>,
) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    await supabase.from('audit_logs').insert({
      user_id: user?.id || null,
      action,
      resource_type: resourceType,
      resource_id: resourceId || null,
      details: details || null,
    });
  } catch {
    // Audit logging should never break the main flow
  }
}

export async function sendNotification(
  userId: string,
  title: string,
  message: string,
  type: 'info' | 'success' | 'warning' | 'error' = 'info',
  link?: string,
) {
  try {
    const supabase = await createClient();
    await supabase.from('notifications').insert({
      user_id: userId,
      title,
      message,
      type,
      link: link || null,
    });
  } catch {
    // Non-critical
  }
}
