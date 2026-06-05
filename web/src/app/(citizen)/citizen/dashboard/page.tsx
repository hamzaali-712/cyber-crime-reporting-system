import React from 'react';

export const dynamic = 'force-dynamic';
import Link from 'next/link';
import { 
  PlusCircle, 
  Search, 
  Gavel, 
  MessageSquare,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  ArrowRight,
  FileText,
  ShieldAlert
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/ui/badge';
import { formatDateTime, cn } from '@/lib/utils';
import type { Complaint } from '@/lib/database.types';

export default async function CitizenDashboardPage() {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) return null;

  // Fetch user profile
  const { data: profile } = await supabase
    .from('profiles')
    .select('full_name')
    .eq('id', user.id)
    .single();

  // Fetch stats
  const { data: complaints } = await supabase
    .from('complaints')
    .select('status')
    .eq('citizen_id', user.id);

  const stats = {
    total: complaints?.length || 0,
    underReview: complaints?.filter(c => c.status === 'UNDER_REVIEW' || c.status === 'PENDING').length || 0,
    resolved: complaints?.filter(c => c.status === 'SOLVED' || c.status === 'CLOSED').length || 0,
    rejected: complaints?.filter(c => c.status === 'REJECTED').length || 0,
  };

  // Fetch recent cases
  const { data: recentCases } = await supabase
    .from('complaints')
    .select('*')
    .eq('citizen_id', user.id)
    .order('created_at', { ascending: false })
    .limit(5);

  const quickActions = [
    { name: 'File New Report', href: '/citizen/report/new', icon: PlusCircle, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'View All Cases', href: '/citizen/cases', icon: Search, color: 'text-purple-600', bg: 'bg-purple-50' },
    { name: 'Legal Guide', href: '/citizen/laws', icon: Gavel, color: 'text-amber-600', bg: 'bg-amber-50' },
    { name: 'AI Assistant', href: '/citizen/chat', icon: MessageSquare, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {profile?.full_name || 'Citizen'}</h1>
        <p className="text-gray-500 mt-1">Here's an overview of your cyber crime reports and activity.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Reports', value: stats.total, icon: Clock, color: 'bg-blue-50 text-blue-600' },
          { label: 'Under Review', value: stats.underReview, icon: AlertCircle, color: 'bg-amber-50 text-amber-600' },
          { label: 'Resolved', value: stats.resolved, icon: CheckCircle2, color: 'bg-emerald-50 text-emerald-600' },
          { label: 'Rejected', value: stats.rejected, icon: XCircle, color: 'bg-red-50 text-red-600' },
        ].map((stat, i) => (
          <Card key={i} className="border-none shadow-sm bg-white overflow-hidden ring-1 ring-gray-100">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={cn('p-3 rounded-xl', stat.color)}>
                  <stat.icon className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900">Recent Cases</h2>
            <Link href="/citizen/cases">
              <Button variant="ghost" size="sm" className="text-blue-600">
                View All <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
          
          <div className="space-y-3">
            {recentCases && recentCases.length > 0 ? (
              recentCases.map((caseItem: Complaint) => (
                <Link key={caseItem.id} href={`/citizen/cases/${caseItem.tracking_id}`}>
                  <Card className="hover:ring-2 hover:ring-blue-100 transition-all cursor-pointer group">
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 rounded-lg bg-gray-50 flex items-center justify-center text-gray-400 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                          <FileText className="h-6 w-6" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">{caseItem.category}</p>
                          <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                             <span className="font-mono text-gray-400">{caseItem.tracking_id}</span>
                             <span>•</span>
                             <span>{formatDateTime(caseItem.created_at)}</span>
                          </div>
                        </div>
                      </div>
                      <StatusBadge status={caseItem.status} />
                    </CardContent>
                  </Card>
                </Link>
              ))
            ) : (
              <Card className="border-dashed border-2 bg-gray-50/50">
                <CardContent className="h-32 flex flex-col items-center justify-center text-gray-500">
                  <p>No reports filed yet.</p>
                  <Link href="/citizen/report/new" className="mt-2 text-blue-600 font-medium">
                    Report your first incident
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-3">
            {quickActions.map((action, i) => (
              <Link key={i} href={action.href}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4 flex items-center gap-4">
                    <div className={cn('p-3 rounded-lg', action.bg, action.color)}>
                      <action.icon className="h-5 w-5" />
                    </div>
                    <span className="font-semibold text-gray-700">{action.name}</span>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Tips Card */}
          <Card className="bg-blue-900 text-white border-none shadow-lg mt-6 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <ShieldAlert className="h-24 w-24" />
            </div>
            <CardHeader>
              <CardTitle className="text-lg">Security Tip</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-blue-100">
                Never share your CCSR login credentials or tracking IDs with anyone. NCIA will never ask for your password via email.
              </p>
              <Button variant="outline" size="sm" className="mt-4 border-blue-400 text-white hover:bg-blue-800">
                Learn Security Basics
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
