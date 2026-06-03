import { NextResponse } from 'next/server';
import Groq from 'groq-sdk';
import { createClient } from '@/lib/supabase/server';

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

export async function POST(req: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { complaintId, status, notes } = await req.json();

    const { data: complaint } = await supabase
      .from('complaints')
      .select('tracking_id, citizen:profiles(full_name)')
      .eq('id', complaintId)
      .single();

    const citizenName = Array.isArray(complaint?.citizen) 
      ? complaint?.citizen[0]?.full_name 
      : (complaint?.citizen as any)?.full_name;

    const prompt = `
      Draft a formal professional email from the National Cyber Investigation Agency (NCIA) to a citizen.
      Citizen Name: ${citizenName || 'Citizen'}
      Tracking ID: ${complaint?.tracking_id}
      Current Status: ${status}
      Officer Investigation Notes: ${notes}

      Theme: Formal, authoritative but reassuring.
      Provide the email body only.
    `;

    const chatCompletion = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: 'llama-3.3-70b-versatile',
    });

    const draft = chatCompletion.choices[0].message.content;

    return NextResponse.json({ draft });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
