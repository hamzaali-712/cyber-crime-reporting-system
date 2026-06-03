---
title: CCRS Backend
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🛡️ National Cyber Crime Reporting System (CCRS)

An enterprise-grade, multi-portal SaaS platform designed for the reporting, tracking, and management of cyber crimes in compliance with **PECA 2016 (Prevention of Electronic Crimes Act)**.

## 🚀 Key Features
- **Multi-Portal Architecture**: Dedicated interfaces for Citizens, Officers, and System Admins.
- **AI-Powered Intelligence**: Automated report summarization and risk assessment.
- **Role-Based Access Control (RBAC)**: Secure authentication and authorization powered by Supabase SSR.
- **Modern Tech Stack**: Built with Next.js 16 (Turbopack), FastAPI, and PostgreSQL.
- **Enterprise Performance**: Optimized middleware for <1s page loads.

---

## 🛠️ Technology Stack
### Frontend (Portal)
- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS / Shadcn/UI
- **Auth**: Supabase SSR (@supabase/ssr)
- **State Management**: React Hook Form + Zod

### Backend (AI Microservice)
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI Engine**: Groq SDK / AI Summarization
- **Database**: Supabase PostgreSQL

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/hamzaali-712/cyber-crime-reporting-system.git
cd cyber-crime-reporting-system
```

### 2. Environment Configuration
Create a `.env.local` in the `web/` directory and a `.env` in the root:

**web/.env.local**
```bash
NEXT_PUBLIC_SUPABASE_URL=your_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_public_key
GROQ_API_KEY=your_key
```

### 3. Start the Frontend
```bash
cd web
npm install
npm run dev
```

### 4. Start the AI Backend
```bash
# From root
python -m venv .venv
.\.venv\Scripts\activate
pip install -r python-api/requirements.txt
python python-api/main.py
```

---

## 🗄️ Database Setup (Supabase)
This project requires a Supabase instance for PostgreSQL and Auth.

1.  **Run Schema**: Copy contents of `database/schema.sql` into Supabase SQL Editor and run.
2.  **Seed Data**: Copy contents of `database/seed.sql` into Supabase SQL Editor and run.
3.  **Authentication**: Ensure Email Auth is enabled in Supabase Settings.

---

## 🔑 Default Test Credentials
| Role | Identity | Password |
| :--- | :--- | :--- |
| **Citizen** | `citizen@example.com` | `password123` |
| **Officer** | `CYBER2024-OFF-001` | `password123` |
| **Admin** | `admin@ncia.gov.pk` | `password123` |

---

## ⚖️ Legal Compliance
This system is strictly aligned with the **Pakistan Prevention of Electronic Crimes Act (PECA) 2016**. It handles sensitive sections including:
- Section 3: Unauthorized access
- Section 10: Cyber Terrorism
- Section 15: Cyber Stalking
- Section 17: Identity Theft

---
Developed for the National Cyber Investigation Agency.
