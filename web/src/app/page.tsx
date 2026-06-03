import React from 'react';
import Link from 'next/link';
import { 
  ShieldAlert, 
  ChevronRight, 
  Gavel, 
  Search, 
  FileCheck, 
  Users,
  ShieldCheck,
  Lock,
  ExternalLink,
  MessageSquare,
  Settings
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white selection:bg-blue-100 selection:text-blue-900">
      {/* Navigation Header */}
      <header className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-gray-100 h-20 flex items-center px-6 lg:px-12 justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-200">
            <ShieldAlert className="h-7 w-7 text-white" />
          </div>
          <div>
             <span className="block font-black text-xl text-blue-900 tracking-tight leading-none uppercase">NCIA</span>
             <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">Cyber Investigation</span>
          </div>
        </div>
        <nav className="hidden md:flex items-center gap-8">
           <Link href="#features" className="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Features</Link>
           <Link href="#laws" className="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">PECA 2016</Link>
           <Link href="#stats" className="text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors">Incident Hub</Link>
        </nav>
        <div className="flex items-center gap-4">
           <Link href="/citizen/auth/sign-in">
              <Button variant="ghost" className="font-bold text-gray-600">Portal Login</Button>
           </Link>
           <Link href="/citizen/auth/sign-up">
              <Button className="bg-blue-600 hover:bg-blue-700 shadow-xl shadow-blue-200 font-bold px-6">Get Started</Button>
           </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-40 pb-20 px-6 lg:px-12 max-w-7xl mx-auto w-full">
         <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8 animate-in fade-in slide-in-from-left-8 duration-1000">
               <Badge className="bg-blue-50 text-blue-700 border-blue-100 px-4 py-1.5 text-xs font-black uppercase tracking-widest">
                  Official Government Portal
               </Badge>
               <h1 className="text-5xl lg:text-7xl font-black text-blue-950 leading-[1.1] tracking-tight">
                  Defending <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Pakistan's</span> Digital Frontier.
               </h1>
               <p className="text-xl text-gray-500 leading-relaxed max-w-xl">
                  Report cyber crimes, identify digital threats, and access legal justice under PECA 2016. Powered by AI investigation tools.
               </p>
               <div className="flex flex-col sm:flex-row gap-4 pt-4">
                  <Link href="/citizen/auth/sign-up">
                     <Button size="lg" className="bg-blue-600 hover:bg-blue-700 h-16 px-10 rounded-2xl text-lg font-black shadow-2xl shadow-blue-200 group">
                        File Official Report <ChevronRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                     </Button>
                  </Link>
                  <Link href="/citizen/laws">
                     <Button size="lg" variant="outline" className="h-16 px-10 rounded-2xl text-lg font-bold border-gray-200 text-gray-600 hover:bg-gray-50">
                        Legal Awareness Guide
                     </Button>
                  </Link>
               </div>
               
               <div className="flex items-center gap-6 pt-8">
                  <div className="flex -space-x-3">
                     {[1, 2, 3, 4].map(i => (
                        <div key={i} className="h-12 w-12 rounded-full border-4 border-white bg-gray-100 overflow-hidden ring-1 ring-gray-100">
                           <Users className="h-full w-full p-2 text-gray-400" />
                        </div>
                     ))}
                  </div>
                  <p className="text-sm font-bold text-gray-500">
                     Trusted by <span className="text-blue-600 font-black">10,000+</span> verified citizens
                  </p>
               </div>
            </div>

            {/* Visual Element: Tactical Dashboard Preview */}
            <div className="relative animate-in fade-in slide-in-from-right-8 duration-1000 delay-200">
               <div className="absolute -inset-4 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-[3rem] blur-[80px] opacity-10" />
               <Card className="bg-white/80 backdrop-blur-2xl border-white shadow-[0_32px_64px_-16px_rgba(30,58,138,0.15)] rounded-[2.5rem] p-4 relative z-10 ring-1 ring-white/50">
                  <div className="bg-gray-100/50 rounded-[2rem] p-8 aspect-square flex flex-col items-center justify-center text-center">
                     <div className="bg-white p-6 rounded-3xl shadow-xl mb-6">
                        <Lock className="h-12 w-12 text-blue-600" />
                     </div>
                     <h3 className="font-black text-2xl text-blue-950">Secure Submission</h3>
                     <p className="text-gray-400 mt-2 text-sm max-w-[240px]">End-to-end encrypted evidence repository compliant with judicial standards.</p>
                     
                     {/* Pulse indicators */}
                     <div className="mt-12 w-full space-y-4">
                        {[40, 70, 55].map((w, i) => (
                           <div key={i} className="h-2 bg-white rounded-full overflow-hidden w-full max-w-[200px] mx-auto">
                              <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: `${w}%`, animationDelay: `${i*200}ms` }} />
                           </div>
                        ))}
                     </div>
                  </div>
               </Card>
               
               {/* Floaties */}
               <div className="absolute -top-12 -left-12 bg-white p-4 rounded-2xl shadow-2xl border border-gray-100 animate-bounce duration-[4000ms]">
                  <Badge className="bg-emerald-50 text-emerald-600 border-none">SYSTEM ACTIVE</Badge>
               </div>
            </div>
         </div>
      </section>

      {/* Gateway Grid */}
      <section id="features" className="py-20 bg-gray-50/50">
         <div className="max-w-7xl mx-auto px-6 lg:px-12">
            <div className="text-center mb-16 space-y-4">
               <h2 className="text-3xl font-black text-blue-950 uppercase tracking-tighter">Portal Access Gateway</h2>
               <p className="text-gray-500 font-medium">Select the appropriate portal to proceed with your objectives.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
               {/* Citizen Portal */}
               <Link href="/citizen/auth/sign-in" className="group">
                  <Card className="h-full hover:shadow-2xl transition-all duration-500 rounded-[2rem] border-none ring-1 ring-gray-100 overflow-hidden group-hover:-translate-y-2">
                     <CardHeader className="p-8">
                        <div className="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 mb-6 group-hover:bg-blue-600 group-hover:text-white transition-all transform group-hover:rotate-6">
                           <Users className="h-7 w-7" />
                        </div>
                        <CardTitle className="text-2xl font-black text-blue-950">Citizen Portal</CardTitle>
                        <CardDescription className="text-gray-500 font-medium leading-relaxed">
                           Report incidents, track cases, and consult with the AI on legal matters.
                        </CardDescription>
                     </CardHeader>
                     <CardContent className="px-8 pb-8 flex items-center text-blue-600 font-black text-xs uppercase tracking-widest">
                        Enter Workspace <ChevronRight className="ml-2 h-4 w-4" />
                     </CardContent>
                  </Card>
               </Link>

               {/* Officer Portal */}
               <Link href="/officer/auth/sign-in" className="group">
                  <Card className="h-full hover:shadow-2xl transition-all duration-500 rounded-[2rem] border-none ring-1 ring-gray-100 overflow-hidden group-hover:-translate-y-2">
                     <CardHeader className="p-8">
                        <div className="h-14 w-14 rounded-2xl bg-slate-900 flex items-center justify-center text-white mb-6 group-hover:bg-blue-600 transition-all transform group-hover:-rotate-6">
                           <ShieldCheck className="h-7 w-7" />
                        </div>
                        <CardTitle className="text-2xl font-black text-blue-950">Officer Portal</CardTitle>
                        <CardDescription className="text-gray-500 font-medium leading-relaxed">
                           Authorized law enforcement access for case investigation and triage.
                        </CardDescription>
                     </CardHeader>
                     <CardContent className="px-8 pb-8 flex items-center text-slate-900 font-black text-xs uppercase tracking-widest">
                        Access Ops Center <ChevronRight className="ml-2 h-4 w-4" />
                     </CardContent>
                  </Card>
               </Link>

               {/* Admin Portal */}
               <Link href="/admin/auth/sign-in" className="group">
                  <Card className="h-full hover:shadow-2xl transition-all duration-500 rounded-[2rem] border-none ring-1 ring-gray-100 overflow-hidden group-hover:-translate-y-2">
                     <CardHeader className="p-8">
                        <div className="h-14 w-14 rounded-2xl bg-red-50 flex items-center justify-center text-red-600 mb-6 group-hover:bg-red-600 group-hover:text-white transition-all transform group-hover:scale-110">
                           <Settings className="h-7 w-7" />
                        </div>
                        <CardTitle className="text-2xl font-black text-blue-950">Admin Root</CardTitle>
                        <CardDescription className="text-gray-500 font-medium leading-relaxed">
                           System maintenance, user management, and global audit oversight.
                        </CardDescription>
                     </CardHeader>
                     <CardContent className="px-8 pb-8 flex items-center text-red-600 font-black text-xs uppercase tracking-widest">
                        System Control <ChevronRight className="ml-2 h-4 w-4" />
                     </CardContent>
                  </Card>
               </Link>
            </div>
         </div>
      </section>

      {/* Footer */}
      <footer className="bg-blue-950 pt-20 pb-12 text-white overflow-hidden relative">
         <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-600" />
         <div className="max-w-7xl mx-auto px-6 lg:px-12 grid grid-cols-1 md:grid-cols-4 gap-12 border-b border-white/5 pb-20">
            <div className="col-span-2 space-y-6">
               <div className="flex items-center gap-3">
                 <ShieldAlert className="h-8 w-8 text-blue-400" />
                 <span className="font-black text-2xl tracking-tight uppercase">NCIA CCSR</span>
               </div>
               <p className="text-blue-100/60 max-w-sm text-sm leading-relaxed font-medium">
                  The National Cyber Investigation Agency's Cyber Crime Reporting System is the primary platform for digital justice in the Islamic Republic of Pakistan.
               </p>
               <div className="flex gap-4">
                  {[1, 2, 3].map(i => <div key={i} className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 cursor-pointer transition-colors" />)}
               </div>
            </div>
            <div>
               <h4 className="font-black text-xs uppercase tracking-widest mb-6 text-blue-400">Legal Resources</h4>
               <ul className="space-y-4 text-sm font-bold text-blue-100/40">
                  <li className="hover:text-blue-100 transition-colors cursor-pointer">PECA 2016 Act</li>
                  <li className="hover:text-blue-100 transition-colors cursor-pointer">Privacy Policy</li>
                  <li className="hover:text-blue-100 transition-colors cursor-pointer">Terms of Service</li>
                  <li className="hover:text-blue-100 transition-colors cursor-pointer">Judicial Guidelines</li>
               </ul>
            </div>
            <div>
               <h4 className="font-black text-xs uppercase tracking-widest mb-6 text-blue-400">Security Node</h4>
               <ul className="space-y-4 text-sm font-bold text-blue-100/40">
                  <li className="flex items-center gap-2"><div className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Cloud Server: PK-SOUTH-1</li>
                  <li className="flex items-center gap-2"><div className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> AES-256 Encrypted</li>
                  <li>Uptime: <span className="text-white">99.998%</span></li>
                  <li>Build: <span className="text-white font-mono">1.0.4-BETA</span></li>
               </ul>
            </div>
         </div>
         <div className="max-w-7xl mx-auto px-6 lg:px-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-6 pointer-events-none">
            <p className="text-[10px] font-black text-blue-100/20 uppercase tracking-widest">
               © {new Date().getFullYear()} Government of Pakistan — NCIA Division.
            </p>
            <div className="flex gap-8 text-[10px] font-black text-blue-100/20 uppercase tracking-widest">
               <span>Compliance ISO 27001</span>
               <span>Harden Protocol V4</span>
            </div>
         </div>
      </footer>
    </div>
  );
}
