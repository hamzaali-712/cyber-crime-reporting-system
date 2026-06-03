import React from 'react';
import Link from 'next/link';
import { 
  Gavel, 
  Search, 
  Scale, 
  AlertCircle, 
  ArrowRight,
  Info,
  ChevronDown,
  WifiOff
} from 'lucide-react';

import { createClient } from '@/lib/supabase/server';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { Law } from '@/lib/database.types';

// Static fallback data for when Supabase is unreachable
const FALLBACK_LAWS: Partial<Law>[] = [
  {
    id: '1', section_number: 'Section 3', title: 'Unauthorized Access to Information System',
    category: 'Unauthorized Access', short_description: 'Accessing any information system without authorization or exceeding authorized access.',
    punishment: 'Imprisonment up to 3 months, or fine up to Rs. 50,000, or both.', is_published: true, sort_order: 1,
  },
  {
    id: '2', section_number: 'Section 4', title: 'Unauthorized Copying of Data',
    category: 'Data Theft', short_description: 'Copying or transmitting data from any information system without authorization.',
    punishment: 'Imprisonment up to 6 months, or fine up to Rs. 100,000, or both.', is_published: true, sort_order: 2,
  },
  {
    id: '3', section_number: 'Section 5', title: 'Interference with Information System',
    category: 'System Interference', short_description: 'Intentionally interfering with the functioning of any information system.',
    punishment: 'Imprisonment up to 2 years, or fine up to Rs. 500,000, or both.', is_published: true, sort_order: 3,
  },
  {
    id: '4', section_number: 'Section 8', title: 'Electronic Fraud',
    category: 'Forgery & Fraud', short_description: 'Committing fraud through electronic means or causing damage through interference with information systems.',
    punishment: 'Imprisonment up to 3 years, or fine up to Rs. 250,000, or both.', is_published: true, sort_order: 6,
  },
  {
    id: '5', section_number: 'Section 10', title: 'Cyber Terrorism',
    category: 'Terrorism', short_description: 'Using information systems with intent to create terror, fear, or insecurity in society.',
    punishment: 'Imprisonment up to 14 years, or fine up to Rs. 50,000,000, or both.', is_published: true, sort_order: 8,
  },
  {
    id: '6', section_number: 'Section 11', title: 'Hate Speech',
    category: 'Content Offenses', short_description: 'Preparing or disseminating information through information systems to advance religious, ethnic, or sectarian hatred.',
    punishment: 'Imprisonment up to 7 years, or fine up to Rs. 10,000,000, or both.', is_published: true, sort_order: 9,
  },
  {
    id: '7', section_number: 'Section 14', title: 'Malicious Code',
    category: 'Malware', short_description: 'Creating, distributing, or deploying viruses, worms, trojans, or other malicious software.',
    punishment: 'Imprisonment up to 2 years, or fine up to Rs. 1,000,000, or both.', is_published: true, sort_order: 12,
  },
  {
    id: '8', section_number: 'Section 15', title: 'Cyber Stalking',
    category: 'Harassment', short_description: 'Repeatedly contacting, monitoring, or threatening someone through electronic means.',
    punishment: 'Imprisonment up to 3 years, or fine up to Rs. 1,000,000, or both.', is_published: true, sort_order: 13,
  },
];

export default async function LegalGuidePage({
  searchParams,
}: {
  searchParams: { q?: string; category?: string };
}) {
  let laws: any[] = [];
  let usingFallback = false;

  try {
    const supabase = await createClient();
    
    let query = supabase
      .from('laws')
      .select('*')
      .eq('is_published', true)
      .order('sort_order', { ascending: true });

    const q = (await searchParams).q;

    if (q) {
      query = query.or(`title.ilike.%${q}%,short_description.ilike.%${q}%,section_number.ilike.%${q}%`);
    }

    const { data, error } = await query;
    
    if (error || !data || data.length === 0) {
      laws = FALLBACK_LAWS as any[];
      usingFallback = true;
    } else {
      laws = data;
    }
  } catch (error) {
    // If Supabase is unreachable, use fallback static data
    laws = FALLBACK_LAWS as any[];
    usingFallback = true;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
            <Gavel className="h-8 w-8 text-blue-600" /> PECA 2016 Legal Guide
          </h1>
          <p className="text-gray-500 mt-1">Explore cyber laws in Pakistan and understand your rights and protections.</p>
        </div>
        <Link href="/citizen/chat">
          <Button className="bg-blue-600 hover:bg-blue-700 font-bold px-6 shadow-lg shadow-blue-200">
            Ask AI Assistant
          </Button>
        </Link>
      </div>

      {/* Connection Warning */}
      {usingFallback && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3">
          <WifiOff className="h-5 w-5 text-amber-600 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-bold text-amber-800">Showing Offline Data</p>
            <p className="text-xs text-amber-600 mt-1">
              Could not connect to the database. Displaying cached PECA 2016 laws. 
              Check your Supabase configuration for live data.
            </p>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-700 to-indigo-800 rounded-3xl p-8 md:p-12 text-white relative overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-2xl">
          <Badge className="bg-blue-500/30 text-blue-100 border-none mb-4 px-3 py-1 text-xs uppercase tracking-widest">
            Compliance & Awareness
          </Badge>
          <h2 className="text-2xl md:text-4xl font-bold leading-tight">
            Prevention of Electronic Crimes Act (PECA) 2016
          </h2>
          <p className="mt-4 text-blue-100 leading-relaxed text-sm md:text-base">
            Enacted by the Parliament of Pakistan, PECA provides a legal framework for addressing various types of cyber crimes, 
            including unauthorized access, forgery, fraud, and harassment. Knowing these laws is the first step in protecting yourself online.
          </p>
        </div>
        <div className="absolute right-0 bottom-0 p-8 opacity-10 hidden lg:block">
           <Scale className="h-64 w-64" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Filters */}
        <div className="space-y-6">
          <div className="sticky top-24">
            <h3 className="font-bold text-gray-900 mb-4 pb-2 border-b border-gray-100 italic">Finding a Law?</h3>
            <div className="space-y-4">
              <div className="relative">
                <Input 
                  placeholder="Search sections..." 
                  className="pl-10 focus:ring-blue-500/20"
                />
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              </div>
              <div className="bg-gray-50 border border-gray-100 rounded-2xl p-5 shadow-inner">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Common Categories</p>
                <div className="flex flex-wrap gap-2">
                   {['Fraud', 'Harassment', 'Access', 'Privacy', 'Terrorism'].map(cat => (
                     <Badge key={cat} variant="secondary" className="cursor-pointer hover:bg-blue-100 hover:text-blue-700 transition-colors">
                       {cat}
                     </Badge>
                   ))}
                </div>
              </div>
              
              {/* Help Widget */}
              <div className="bg-blue-50/50 p-6 rounded-2xl border border-blue-100 mt-8">
                <Info className="h-6 w-6 text-blue-600 mb-3" />
                <h4 className="font-bold text-blue-900 text-sm">Need Help Identifying?</h4>
                <p className="text-xs text-blue-700 mt-2 leading-relaxed">
                  Our AI Assistant can help you map your situation to specific legal sections.
                </p>
                <Link href="/citizen/chat" className="mt-4 inline-flex items-center text-xs font-bold text-blue-600 hover:underline">
                  Start Consultation <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Laws Grid */}
        <div className="lg:col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {laws && laws.length > 0 ? (
              laws.map((law: any) => (
                <Card key={law.id} className="group hover:shadow-xl hover:ring-2 hover:ring-blue-100 transition-all duration-300 border-none ring-1 ring-gray-100 overflow-hidden flex flex-col">
                  <CardHeader className="bg-gray-50/50 border-b border-gray-50 pb-4">
                    <div className="flex items-center justify-between gap-4">
                      <Badge variant="default" className="bg-blue-600 text-white font-mono">
                        {law.section_number}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] uppercase font-bold text-gray-400 tracking-tighter">
                        {law.category}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg mt-4 group-hover:text-blue-900 transition-colors">
                      {law.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-6 flex-1">
                    <p className="text-sm text-gray-600 leading-relaxed italic">
                      {law.short_description}
                    </p>
                    
                    <div className="mt-6 p-4 bg-red-50/50 rounded-xl border border-red-100">
                       <div className="flex items-center gap-2 text-red-700 font-bold text-xs uppercase tracking-widest px-1">
                         <AlertCircle className="h-3.5 w-3.5" /> Punishment
                       </div>
                       <p className="text-sm text-red-900 mt-2 font-medium">
                         {law.punishment}
                       </p>
                    </div>
                  </CardContent>
                  <CardFooter className="bg-gray-50/30 border-t border-gray-50 pt-4">
                    <Button variant="ghost" size="sm" className="w-full text-blue-600 hover:text-blue-700 hover:bg-blue-50 font-bold group/btn">
                      Read Full Section <ChevronDown className="ml-2 h-4 w-4 transition-transform group-hover/btn:translate-y-0.5" />
                    </Button>
                  </CardFooter>
                </Card>
              ))
            ) : (
              <div className="col-span-full py-20 text-center text-gray-400">
                <Search className="h-12 w-12 mx-auto mb-4 text-gray-200" />
                <p>No laws found matching your search.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
