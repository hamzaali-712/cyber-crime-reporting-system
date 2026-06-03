import React from 'react';
import Link from 'next/link';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  FileText, 
  ChevronRight,
  MoreVertical,
  Download
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { StatusBadge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import type { Complaint } from '@/lib/database.types';

export default async function CitizenCasesPage({
  searchParams,
}: {
  searchParams: { status?: string; search?: string };
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;

  let query = supabase
    .from('complaints')
    .select('*')
    .eq('citizen_id', user.id)
    .order('created_at', { ascending: false });

  if (searchParams.status) {
    query = query.eq('status', searchParams.status);
  }

  if (searchParams.search) {
    query = query.ilike('category', `%${searchParams.search}%`);
  }

  const { data: cases, error } = await query;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Reports</h1>
          <p className="text-gray-500 mt-1">Manage and track your filed cyber crime complaints.</p>
        </div>
        <Link href="/citizen/report/new">
          <Button className="bg-blue-600 hover:bg-blue-700">
            File New Report
          </Button>
        </Link>
      </div>

      {/* Search and Filter Bar */}
      <Card className="border-none shadow-sm ring-1 ring-gray-100 p-2">
        <CardContent className="p-0 flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Input 
              placeholder="Search by category..." 
              className="pl-10 h-11"
              defaultValue={searchParams.search}
            />
            <Search className="absolute left-3 top-3.5 h-4 w-4 text-gray-400" />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="h-11 flex gap-2">
              <Filter className="h-4 w-4" /> Filter
            </Button>
            <Button variant="outline" className="h-11 flex gap-2">
              <ArrowUpDown className="h-4 w-4" /> Sort
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Cases Table (Responsive Cards) */}
      <div className="space-y-4">
        {cases && cases.length > 0 ? (
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead className="bg-gray-50/50">
                <tr className="border-b border-gray-200">
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-widest">Tracking ID</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-widest">Category</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-widest">Date Filed</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-widest">Status</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-widest">Last Updated</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-widest text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {cases.map((c: Complaint) => (
                  <tr key={c.id} className="hover:bg-gray-50/50 transition-colors group cursor-pointer">
                    <td className="px-6 py-4">
                      <Link href={`/citizen/cases/${c.tracking_id}`} className="font-mono text-sm text-blue-600 font-medium">
                        {c.tracking_id}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded bg-blue-50 flex items-center justify-center text-blue-600">
                          <FileText className="h-4 w-4" />
                        </div>
                        <span className="text-sm font-semibold text-gray-900">{c.category}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(c.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {formatDate(c.updated_at)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link href={`/citizen/cases/${c.tracking_id}`}>
                          <Button variant="ghost" size="sm" className="hidden sm:inline-flex">
                            View Details
                          </Button>
                        </Link>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Card className="border-dashed border-2 py-12 flex flex-col items-center justify-center text-gray-500">
            <div className="h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
              <FileText className="h-8 w-8 text-gray-300" />
            </div>
            <p className="text-lg font-bold text-gray-900">No reports found</p>
             <p className="text-sm text-gray-400 mt-1">Try adjusting your filters or file a new report.</p>
             <Link href="/citizen/report/new" className="mt-6">
                <Button variant="outline">File New Report</Button>
             </Link>
          </Card>
        )}
      </div>
    </div>
  );
}
