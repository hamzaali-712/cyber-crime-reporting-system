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

    const { complaintId } = await req.json();

    // 1. Fetch complaint data
    const { data: complaint, error: fetchError } = await supabase
      .from('complaints')
      .select('*')
      .eq('id', complaintId)
      .single();

    if (fetchError || !complaint) {
      return NextResponse.json({ error: 'Complaint not found' }, { status: 404 });
    }

    // 2. Call AI to analyze
    const prompt = `
      Analyze the following cyber crime complaint and provide a structured assessment.
      Complaint Category: ${complaint.category}
      Description: ${complaint.description}

      Provide response in JSON format:
      {
        "executive_summary": "Short 2-3 sentence summary of the incident.",
        "risk_assessment": "LOW | MEDIUM | HIGH | CRITICAL",
        "incident_classification": "Primary PECA 2016 Section (e.g. Section 14: Cyber Stalking)",
        "legal_recommendations": "Bullet points of suggested actions."
      }
    `;

    const chatCompletion = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: 'llama-3.3-70b-versatile',
      response_format: { type: 'json_object' },
    });

    const aiResponse = JSON.parse(chatCompletion.choices[0].message.content || '{}');

    // 3. Save report to DB
    const { data: report, error: saveError } = await supabase
      .from('ai_reports')
      .insert({
        complaint_id: complaintId,
        executive_summary: aiResponse.executive_summary,
        risk_assessment: aiResponse.risk_assessment,
        incident_classification: aiResponse.incident_classification,
        raw_analysis: aiResponse,
      })
      .select()
      .single();

    if (saveError) throw saveError;

    return NextResponse.json(report);
  } catch (error: any) {
    console.error('AI Analysis Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
