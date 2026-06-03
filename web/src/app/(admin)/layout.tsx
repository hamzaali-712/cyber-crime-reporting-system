'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  BarChart, 
  Users, 
  ShieldCheck, 
  Settings, 
  History, 
  Lock,
  LogOut,
  Bell,
  Cpu,
  Globe
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const navItems = [
  { name: 'Control Center', href: '/admin/dashboard', icon: BarChart },
  { name: 'User Management', href: '/admin/users', icon: Users },
  { name: 'Law Management', href: '/admin/laws', icon: ShieldCheck },
  { name: 'System Logs', href: '/admin/logs', icon: History },
  { name: 'Global Settings', href: '/admin/settings', icon: Settings },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname?.includes('/auth/')) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen bg-[#020617] text-slate-400">
      {/* Admin Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-[#020617] border-r border-slate-800/50 hidden lg:flex flex-col">
        <div className="p-8 border-b border-slate-800/50 flex items-center gap-3">
          <div className="bg-red-500/10 p-2 rounded-xl border border-red-500/20">
            <Lock className="h-6 w-6 text-red-500" />
          </div>
          <div>
             <span className="block font-black text-lg text-white leading-none tracking-tight">NCIA Root</span>
             <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">Super Admin</span>
          </div>
        </div>

        <nav className="flex-1 px-4 py-8 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/admin/dashboard' && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-4 py-3.5 text-sm font-bold rounded-2xl transition-all duration-300 group relative overflow-hidden',
                  isActive 
                    ? 'bg-blue-600 text-white shadow-2xl shadow-blue-900/50 scale-[1.02]' 
                    : 'hover:bg-slate-900 hover:text-white'
                )}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 -z-10" />
                )}
                <item.icon className={cn('h-5 w-5', isActive ? 'text-white' : 'text-slate-500 group-hover:text-blue-400')} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800/50 bg-slate-950/30">
           <div className="flex items-center gap-3 p-3 mb-4 rounded-2xl bg-slate-900/50 border border-slate-800/50">
              <div className="h-10 w-10 rounded-xl bg-red-950 border border-red-900/50 flex items-center justify-center font-bold text-red-500 shadow-inner">
                SA
              </div>
              <div className="overflow-hidden">
                 <p className="text-sm font-black text-white truncate">System Admin</p>
                 <p className="text-[10px] text-emerald-500 font-black uppercase truncate tracking-widest flex items-center gap-1">
                   <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Root Access
                 </p>
              </div>
           </div>
          <Button variant="ghost" className="w-full justify-start text-slate-400 hover:text-white hover:bg-slate-900 gap-3 rounded-2xl h-12">
            <LogOut className="h-5 w-5" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Admin Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col">
        {/* Admin Header */}
        <header className="sticky top-0 z-40 bg-[#020617]/80 backdrop-blur-xl border-b border-slate-800/50 h-16 flex items-center justify-between px-8">
          <div className="flex items-center gap-8 flex-1">
              <div className="flex items-center gap-2 group cursor-pointer text-xs font-bold text-slate-500 hover:text-white transition-colors">
                 <Globe className="h-4 w-4" /> 
                 <span>V1.0.4-RELEASE</span>
              </div>
              <div className="h-4 w-px bg-slate-800" />
              <div className="flex items-center gap-2 text-xs font-bold text-slate-500">
                 <Cpu className="h-4 w-4 text-emerald-500" />
                 <span>CPU: 12%</span>
                 <span className="ml-4 text-blue-500">MEM: 1.4GB / 4GB</span>
              </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative text-slate-500 hover:bg-slate-900 rounded-xl">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2.5 right-2.5 h-2 w-2 bg-red-500 rounded-full border-2 border-[#020617]" />
            </Button>
            <div className="h-8 w-px bg-slate-800 mx-2" />
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 rounded-xl border border-slate-800">
               <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
               <span className="text-[10px] font-black text-white uppercase tracking-widest">PostgreSQL Cloud Connect</span>
            </div>
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
