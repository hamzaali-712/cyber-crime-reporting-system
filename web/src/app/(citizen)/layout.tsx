'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  FileText, 
  Gavel, 
  MessageSquare, 
  User, 
  LogOut,
  ShieldAlert,
  Bell
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const navItems = [
  { name: 'Dashboard', href: '/citizen/dashboard', icon: LayoutDashboard },
  { name: 'My Cases', href: '/citizen/cases', icon: FileText },
  { name: 'Legal Guide', href: '/citizen/laws', icon: Gavel },
  { name: 'AI Assistant', href: '/citizen/chat', icon: MessageSquare },
  { name: 'Profile', href: '/citizen/profile', icon: User },
];

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // If it's an auth page, don't show the layout
  if (pathname?.includes('/auth/')) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen bg-gray-50/50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <ShieldAlert className="h-6 w-6 text-white" />
          </div>
          <span className="font-bold text-xl text-blue-900 tracking-tight text-nowrap">NCIA Portal</span>
        </div>

        <nav className="flex-1 px-4 py-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <item.icon className={cn('h-5 w-5', isActive ? 'text-blue-700' : 'text-gray-400')} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <Button variant="ghost" className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 gap-3">
            <LogOut className="h-5 w-5" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 md:pl-64 flex flex-col">
        {/* Top Header */}
        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200 h-16 flex items-center justify-between px-4 md:px-8">
          <div className="md:hidden flex items-center gap-3">
            <ShieldAlert className="h-7 w-7 text-blue-600" />
            <span className="font-bold text-lg text-blue-900">NCIA</span>
          </div>
          <div className="flex-1" />
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" className="relative text-gray-500">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 right-2 h-2 w-2 bg-red-500 rounded-full border-2 border-white" />
            </Button>
            <div className="h-8 w-px bg-gray-200" />
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold text-gray-900 leading-none">Citizen User</p>
                <p className="text-xs text-gray-500 mt-1">Verified Account</p>
              </div>
              <div className="h-10 w-10 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-700 font-bold">
                C
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>

        {/* Footer */}
        <footer className="py-6 px-8 border-t border-gray-200 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} National Cyber Investigation Agency. All rights reserved.
        </footer>
      </div>
    </div>
  );
}
