'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  BarChart3, 
  ShieldAlert, 
  Inbox, 
  Zap, 
  Activity, 
  LogOut,
  Bell,
  Search,
  Settings
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const navItems = [
  { name: 'Dashboard', href: '/officer/dashboard', icon: BarChart3 },
  { name: 'Case Queue', href: '/officer/cases', icon: Inbox },
  { name: 'AI Workspace', href: '/officer/ai', icon: Zap },
  { name: 'My Activity', href: '/officer/activity', icon: Activity },
];

export default function OfficerLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname?.includes('/auth/')) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      {/* Officer Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-[#0f172a] text-slate-300 hidden md:flex flex-col shadow-2xl">
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="bg-blue-500/10 p-2 rounded-lg border border-blue-500/20">
            <ShieldAlert className="h-6 w-6 text-blue-400" />
          </div>
          <div>
             <span className="block font-bold text-lg text-white leading-none">NCIA Officer</span>
             <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Law Enforcement</span>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/officer/dashboard' && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 group',
                  isActive 
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20 translate-x-1' 
                    : 'hover:bg-slate-800 hover:text-white'
                )}
              >
                <item.icon className={cn('h-5 w-5', isActive ? 'text-white' : 'text-slate-500 group-hover:text-blue-400')} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800 bg-[#0c111d]/50">
           <div className="flex items-center gap-3 p-3 mb-4">
              <div className="h-10 w-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-blue-400">
                O1
              </div>
              <div className="overflow-hidden">
                 <p className="text-sm font-bold text-white truncate">Officer Ahmed</p>
                 <p className="text-[10px] text-slate-500 font-bold uppercase truncate">Badge: #7721</p>
              </div>
           </div>
          <Button variant="ghost" className="w-full justify-start text-slate-400 hover:text-white hover:bg-slate-800 gap-3 rounded-xl">
            <LogOut className="h-5 w-5" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Officer Content Area */}
      <div className="flex-1 md:pl-64 flex flex-col">
        {/* Officer Header */}
        <header className="sticky top-0 z-40 bg-white border-b border-slate-200 h-16 flex items-center justify-between px-8">
          <div className="flex items-center gap-4 flex-1">
             <div className="relative max-w-md w-full hidden sm:block">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input 
                  type="text" 
                  placeholder="Universal Case Search (ID, Petitioner, Crime...)" 
                  className="w-full bg-slate-50 border-none rounded-xl py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-500/20 transition-all font-medium"
                />
             </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative text-slate-500 hover:bg-slate-50 rounded-xl">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2.5 right-2.5 h-2 w-2 bg-blue-500 rounded-full border-2 border-white ring-2 ring-blue-500/20" />
            </Button>
            <div className="h-8 w-px bg-slate-200 mx-2" />
            <Button variant="ghost" size="icon" className="text-slate-500 hover:bg-slate-50 rounded-xl">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
