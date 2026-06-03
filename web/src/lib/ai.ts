'use server';

import Groq from 'groq-sdk';
import type { Complaint, RiskLevel } from './database.types';

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

const PRIMARY_MODEL = 'llama-3.3-70b-versatile';
const FALLBACK_MODEL = 'llama-3.1-8b-instant';

interface AIReportResult {
  executive_summary: string;
  incident_classification: string;
  key_evidence_points: string;
  recommended_actions: string;
  risk_assessment: RiskLevel;
  suggested_timeline: string;
  raw_response: string;
}

export async function generateCaseReport(complaint: Complaint, evidenceCount: number): Promise<AIReportResult> {
  const prompt = `You are an AI analyst for Pakistan's National Cyber Investigation Agency (NCIA).
Analyze this cybercrime complaint and generate a structured report.

COMPLAINT DATA:
- Tracking ID: ${complaint.tracking_id}
- Category: ${complaint.category}
- Date of Incident: ${complaint.incident_date}
- Location: ${complaint.incident_location || 'Not specified'}
- Description: ${complaint.description}
- Evidence Files: ${evidenceCount} file(s) attached
- Anonymous: ${complaint.is_anonymous ? 'Yes' : 'No'}

Generate a JSON response with these exact fields:
{
  "executive_summary": "2-3 sentence overview of the case",
  "incident_classification": "Relevant PECA 2016 sections (e.g., Section 15 - Cyber Stalking)",
  "key_evidence_points": "Bullet-pointed list of key evidence observations",
  "recommended_actions": "Specific investigation steps recommended",
  "risk_assessment": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "suggested_timeline": "Recommended resolution timeline"
}

Respond with ONLY valid JSON, no markdown.`;

  try {
    const response = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: PRIMARY_MODEL,
      temperature: 0.3,
      max_tokens: 2000,
    });

    const content = response.choices[0]?.message?.content || '{}';
    const parsed = JSON.parse(content) as AIReportResult;
    return { ...parsed, raw_response: content };
  } catch {
    // Fallback to smaller model
    const response = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: FALLBACK_MODEL,
      temperature: 0.3,
      max_tokens: 2000,
    });

    const content = response.choices[0]?.message?.content || '{}';
    const parsed = JSON.parse(content) as AIReportResult;
    return { ...parsed, raw_response: content };
  }
}

export async function chatWithAssistant(
  messages: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>,
): Promise<string> {
  const systemPrompt = {
    role: 'system' as const,
    content: `You are a legal assistant for Pakistan's National Cyber Investigation Agency (NCIA).
You specialize in the Prevention of Electronic Crimes Act (PECA) 2016.
Help citizens understand cybercrime laws, guide them on reporting procedures, and provide legal information.
Be empathetic, professional, and informative. Always recommend filing a formal complaint for serious matters.
Format responses with clear structure using markdown when helpful.
Never provide specific legal advice — always recommend consulting a lawyer for specific cases.`,
  };

  try {
    const response = await groq.chat.completions.create({
      messages: [systemPrompt, ...messages],
      model: PRIMARY_MODEL,
      temperature: 0.7,
      max_tokens: 1500,
    });
    return response.choices[0]?.message?.content || 'I apologize, I could not generate a response. Please try again.';
  } catch {
    const response = await groq.chat.completions.create({
      messages: [systemPrompt, ...messages],
      model: FALLBACK_MODEL,
      temperature: 0.7,
      max_tokens: 1500,
    });
    return response.choices[0]?.message?.content || 'I apologize, I could not generate a response. Please try again.';
  }
}

export async function generateEmailDraft(
  complaint: Complaint,
  decision: string,
  officerNotes: string,
): Promise<{ subject: string; body: string }> {
  const prompt = `Draft a professional email from NCIA Pakistan to a citizen regarding their cybercrime complaint.

Complaint: ${complaint.tracking_id}
Category: ${complaint.category}
Decision: ${decision}
Officer Notes: ${officerNotes}

Generate JSON: { "subject": "...", "body": "..." }
The email should be formal, reference PECA 2016, and include next steps.
Respond with ONLY valid JSON.`;

  try {
    const response = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: PRIMARY_MODEL,
      temperature: 0.4,
      max_tokens: 1000,
    });
    const content = response.choices[0]?.message?.content || '{}';
    return JSON.parse(content);
  } catch {
    return {
      subject: `NCIA Case Update: ${complaint.tracking_id}`,
      body: `Dear Citizen,\n\nRegarding your complaint ${complaint.tracking_id} (${complaint.category}), the assigned officer has made the following decision: ${decision}.\n\nOfficer Notes: ${officerNotes}\n\nFor further inquiries, please contact NCIA.\n\nRegards,\nNCIA Pakistan`,
    };
  }
}

export async function identifyPecaSections(description: string): Promise<string> {
  const prompt = `As a PECA 2016 legal expert, analyze this situation and identify applicable sections:

"${description}"

List the applicable PECA 2016 sections with brief explanations. Format as markdown.`;

  try {
    const response = await groq.chat.completions.create({
      messages: [{ role: 'user', content: prompt }],
      model: PRIMARY_MODEL,
      temperature: 0.3,
      max_tokens: 1000,
    });
    return response.choices[0]?.message?.content || 'Unable to analyze. Please try again.';
  } catch {
    return 'AI service temporarily unavailable. Please try again later.';
  }
}
