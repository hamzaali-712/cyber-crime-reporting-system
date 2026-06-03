'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, 
  Send, 
  Trash2, 
  History, 
  Sparkles, 
  Plus,
  ShieldCheck,
  MoreVertical,
  ArrowRight,
  Bot
} from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { chatMessageSchema, type ChatMessageFormData } from '@/lib/validations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { createClient } from '@/lib/supabase/client';
import { chatWithAssistant } from '@/lib/ai';
import { cn } from '@/lib/utils';
import type { ChatSession, ChatMessage } from '@/lib/database.types';

export default function CitizenChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const supabase = createClient();

  const { register, handleSubmit, reset, watch } = useForm<ChatMessageFormData>({
    resolver: zodResolver(chatMessageSchema),
  });

  const messageText = watch('message');

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (currentSessionId) {
      fetchMessages(currentSessionId);
    }
  }, [currentSessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false });

      if (data) {
        setSessions(data);
        if (data.length > 0 && !currentSessionId) {
          setCurrentSessionId(data[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch sessions');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const fetchMessages = async (sessionId: string) => {
    const { data } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true });

    if (data) setMessages(data as ChatMessage[]);
  };

  const createNewSession = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const { data } = await supabase
      .from('chat_sessions')
      .insert({ user_id: user.id, title: 'New Consultation' })
      .select()
      .single();

    if (data) {
      setSessions([data as ChatSession, ...sessions]);
      setCurrentSessionId(data.id);
      setMessages([]);
    }
  };

  const onSubmit = async (data: ChatMessageFormData) => {
    if (!currentSessionId) {
      // Logic would be to create session automatically if none exists
      return;
    }

    const userMessage = data.message;
    reset();
    
    // Optimistic UI update
    const tempUserMsg: any = { id: Math.random().toString(), role: 'user', content: userMessage };
    setMessages(prev => [...prev, tempUserMsg]);
    setIsTyping(true);

    try {
      // 1. Save user message to DB
      const { data: savedMsg } = await supabase
        .from('chat_messages')
        .insert({ session_id: currentSessionId, role: 'user', content: userMessage })
        .select()
        .single();
      
      // Update session's title if it's the first message
      if (messages.length === 0) {
        await supabase
          .from('chat_sessions')
          .update({ title: userMessage.slice(0, 30) + '...' })
          .eq('id', currentSessionId);
        fetchSessions();
      }

      // 2. Call AI API
      const aiResponse = await chatWithAssistant([
        ...messages.map(m => ({ role: m.role as any, content: m.content })),
        { role: 'user', content: userMessage }
      ]);

      // 3. Save assistant message to DB
      const { data: assistantMsg } = await supabase
        .from('chat_messages')
        .insert({ session_id: currentSessionId, role: 'assistant', content: aiResponse })
        .select()
        .single();

      if (assistantMsg) {
        setMessages(prev => [...prev.filter(m => m.id !== tempUserMsg.id), savedMsg as ChatMessage, assistantMsg as ChatMessage]);
      }
    } catch (error) {
      toast.error('AI Consultation Failed', { description: 'Please try again later.' });
    } finally {
      setIsTyping(false);
    }
  };

  const suggestedPrompts = [
    "What is cyberstalking?",
    "How do I report financial fraud?",
    "What evidence should I keep?",
    "My photos were leaked online."
  ];

  return (
    <div className="flex h-[calc(100vh-10rem)] gap-6 animate-in fade-in duration-500">
      {/* Sidebar - History */}
      <aside className="w-80 bg-white rounded-3xl border border-gray-100 shadow-sm flex flex-col overflow-hidden hidden lg:flex">
        <div className="p-6 border-b border-gray-50 flex items-center justify-between">
          <h2 className="font-bold text-gray-900 flex items-center gap-2">
            <History className="h-4 w-4 text-blue-600" /> Consultations
          </h2>
          <Button variant="ghost" size="icon" onClick={createNewSession} className="h-8 w-8 hover:bg-blue-50 hover:text-blue-600">
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar">
          {isLoadingHistory ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-12 bg-gray-50 rounded-xl animate-pulse m-2" />
            ))
          ) : sessions.length > 0 ? (
            sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => setCurrentSessionId(session.id)}
                className={cn(
                  "group p-3 rounded-2xl cursor-pointer transition-all flex items-center justify-between",
                  currentSessionId === session.id 
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-200" 
                    : "hover:bg-gray-50 text-gray-600"
                )}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                   <MessageSquare className={cn("h-4 w-4 shrink-0", currentSessionId === session.id ? "text-blue-100" : "text-gray-400")} />
                   <p className="text-sm font-medium truncate">{session.title}</p>
                </div>
                <MoreVertical className={cn("h-4 w-4 opacity-0 group-hover:opacity-100", currentSessionId === session.id ? "text-white" : "text-gray-400")} />
              </div>
            ))
          ) : (
            <div className="text-center py-10 px-6">
              <MessageSquare className="h-10 w-10 text-gray-100 mx-auto mb-4" />
              <p className="text-xs text-gray-400">No recent consultations found.</p>
            </div>
          )}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden relative">
        {/* Chat Header */}
        <header className="px-6 py-4 border-b border-gray-50 flex items-center justify-between bg-white/50 backdrop-blur-sm sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-lg shadow-blue-100">
               <Bot className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 flex items-center gap-2">
                NCIA Assistant <Badge className="text-[10px] bg-emerald-100 text-emerald-700 border-none">Online</Badge>
              </h3>
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">PECA 2016 Expert Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
             <Button variant="ghost" size="icon" className="h-9 w-9 text-gray-400">
               <ShieldCheck className="h-5 w-5" />
             </Button>
          </div>
        </header>

        {/* Message Log */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 flex flex-col custom-scrollbar">
          {messages.length === 0 && !isTyping ? (
             <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-700">
                <div className="relative group mb-6">
                   <div className="absolute -inset-4 bg-blue-100 rounded-full blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                   <div className="relative bg-white p-6 rounded-3xl shadow-2xl border border-blue-50">
                      <Sparkles className="h-10 w-10 text-blue-600" />
                   </div>
                </div>
                <h2 className="text-2xl font-bold text-gray-900">How can NCIA help you today?</h2>
                <p className="text-sm text-gray-500 mt-2 max-w-sm">
                  Get instant legal guidance, identify cyber crimes, and understand how to protect yourself under Pakistani law.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 w-full max-w-lg px-4">
                   {suggestedPrompts.map(p => (
                     <button 
                       key={p} 
                       onClick={() => reset({ message: p })}
                       className="p-3 bg-gray-50 border border-gray-200 rounded-2xl text-xs font-semibold text-gray-700 hover:border-blue-600 hover:bg-white hover:text-blue-600 transition-all text-left flex items-center justify-between group"
                     >
                       {p} <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                     </button>
                   ))}
                </div>
             </div>
          ) : (
            <>
              {messages.map((m) => (
                <div 
                  key={m.id} 
                  className={cn(
                    "flex w-full mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300",
                    m.role === 'user' ? "justify-end" : "justify-start"
                  )}
                >
                  <div className={cn(
                    "max-w-[80%] rounded-3xl p-4 shadow-sm",
                    m.role === 'user' 
                      ? "bg-blue-600 text-white rounded-tr-none px-6" 
                      : "bg-gray-100 text-gray-800 rounded-tl-none border border-gray-100 px-6 prose prose-sm prose-slate"
                  )}>
                    {m.content}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start animate-in fade-in duration-300">
                  <div className="bg-gray-100 rounded-3xl rounded-tl-none p-4 px-6 flex items-center gap-1">
                    <div className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="h-1.5 w-1.5 bg-gray-400 rounded-full animate-bounce" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Chat Input */}
        <footer className="p-6 pt-2 bg-gradient-to-t from-white via-white to-transparent">
           <form onSubmit={handleSubmit(onSubmit)} className="relative max-w-4xl mx-auto flex gap-3">
              <div className="relative flex-1 group">
                 <Input 
                   placeholder="Type your question here..." 
                   className="h-14 pl-6 pr-16 bg-gray-50/50 border-gray-200 rounded-2xl shadow-inner focus:ring-blue-500/20 text-base"
                   {...register('message')}
                   autoComplete="off"
                 />
                 <div className="absolute right-3 top-2.5">
                    <Button 
                      type="submit" 
                      disabled={!messageText || isTyping} 
                      className="bg-blue-600 hover:bg-blue-700 h-9 w-9 p-0 rounded-xl shadow-lg shadow-blue-200"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                 </div>
              </div>
           </form>
           <p className="text-[10px] text-center text-gray-400 mt-4 leading-relaxed font-bold uppercase tracking-widest">
             AI Chat can make mistakes. For official legal processing, file a formal complaint.
           </p>
        </footer>
      </main>
    </div>
  );
}
