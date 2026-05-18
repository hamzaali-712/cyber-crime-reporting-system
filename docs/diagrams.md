# Cyber Crime Reporting System - Comprehensive System Diagrams & Workflows

This document contains 18 in-depth, government-grade architectural, operational, and procedural diagrams for the **Cyber Crime Reporting System (CCRS)**. The diagrams are structured using **Mermaid.js** with professional, customized HSL color styling.

---

## 1. System Architecture Diagram

This diagram maps the interactive client browsers, the Streamlit front-end layers, the core FastAPI gateway, independent services, and the unique **Supabase Cloud + Thread-Safe Local JSON Failover** database architecture.

```mermaid
flowchart TB
    %% Styling Class Definitions
    classDef client fill:#38bdf8,stroke:#0284c7,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef server fill:#a78bfa,stroke:#7c3aed,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef storage fill:#34d399,stroke:#059669,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef ai fill:#fb7185,stroke:#e11d48,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef secondary fill:#94a3b8,stroke:#475569,stroke-width:1px,color:#1e293b;

    subgraph Presentation_Layer ["Presentation Layer (Streamlit App)"]
        direction LR
        CitApp["Citizen Portal (citizen_app.py)"]:::client
        OffApp["Officer Portal (officer_app.py)"]:::client
    end

    subgraph Service_Layer ["Service Layer (FastAPI API Core)"]
        direction TB
        APIServer["FastAPI Gateway (backend/api/main.py)"]:::server
        DBService["Database Service (database_service.py)"]:::server
        AIService["AI Service (ai_service.py)"]:::server
        FileService["File Service (file_service.py)"]:::server
        SecurityUtils["Security Utils (security.py)"]:::server
    end

    subgraph AI_Layer ["AI & Analysis Layer"]
        GroqAPI["Groq AI Engine (LLaMA-3 API)"]:::ai
    end

    subgraph Cloud_Storage ["Cloud Storage Layer (Supabase - Primary)"]
        direction TB
        SupaDB[("PostgreSQL DB (Supabase)")]:::storage
        SupaStore[("Evidence Storage Bucket")]:::storage
    end

    subgraph Local_Storage ["Local Failover Storage (JSON Files - Backup)"]
        direction TB
        LocalJSON[("Local JSON Files (complaints, decisions, etc.)")]:::secondary
        LocalFiles[("Local Secure Evidence Store")]:::secondary
    end

    %% Mappings & Data Flow
    CitApp -->|Submit report, track, chat| APIServer
    OffApp -->|Login, review case, update status| APIServer

    APIServer --> DBService
    APIServer --> AIService
    APIServer --> FileService

    DBService --> SecurityUtils
    FileService --> SecurityUtils

    AIService -->|API Request| GroqAPI

    DBService -->|Write / Read (Primary)| SupaDB
    FileService -->|Upload / Download (Primary)| SupaStore

    DBService -.->|Automatic Failover / Thread Lock| LocalJSON
    FileService -.->|Local Backup Storage| LocalFiles

    DBService -->|Auto Cloud Sync on Start| SupaDB
```

---

## 2. Class Diagram

This UML class diagram represents the structure of the key backend service components, their respective methods, variables, and cross-class associations.

```mermaid
classDiagram
    class DatabaseService {
        +Lock lock
        +Path COMPLAINTS_FILE
        +Path OFFICERS_FILE
        +Path DECISIONS_FILE
        +Path AUDIT_LOG_FILE
        +create_complaint(complaint_data: Dict) str
        +get_complaint(tracking_id: str) Optional~Dict~
        +get_all_complaints() Dict
        +update_complaint_status(tracking_id: str, status: str, notes: str, officer_id: str) bool
        +get_decision(tracking_id: str) Optional~Dict~
        +get_all_decisions() Dict
        +get_officer(officer_id: str) Optional~Dict~
        +create_officer(officer_data: Dict) str
        +verify_officer(officer_id: str, password: str) bool
        +create_audit_log(user_id: str, action: str, resource_type: str, resource_id: str, details: Dict) bool
        +get_audit_logs() List~Dict~
        -_migrate_local_to_supabase()
        -_load_file(file_path: Path) Any
        -_save_file(file_path: Path, data: Any)
    }

    class SecurityUtils {
        +hash_password(password: str) str
        +verify_password(password: str, hashed: str) bool
        +generate_jwt_token(data: Dict, expires_in: int) str
        +verify_jwt_token(token: str) Optional~Dict~
        +encrypt_evidence_file(file_data: bytes, key: bytes) bytes
        +decrypt_evidence_file(encrypted_data: bytes, key: bytes) bytes
        +generate_file_sha256(file_path: Path) str
    }

    class AIService {
        +Groq client
        +analyze_complaint(description: str) Dict
        +summarize_incident(description: str) str
        +classify_peca_category(description: str) Dict
        +get_legal_assistance(query: str, category: str) str
    }

    class FileService {
        +Path UPLOAD_DIR
        +save_evidence(file_name: str, file_data: bytes) str
        +secure_evidence_metadata(complaint_id: str, file_name: str, file_size: int, file_path: str) Dict
        +scan_file_for_malware(file_path: Path) bool
    }

    DatabaseService --> SecurityUtils : Uses for hashing & audit logging
    FileService --> SecurityUtils : Uses for hashing & encryption
    DatabaseService ..> AIService : Populates AI classification
```

---

## 3. Component & Data Flow Diagram

This diagram displays how frontend pages, UI views, backend routers, services, database tables, and JSON cache files connect.

```mermaid
flowchart TB
    classDef page fill:#fef08a,stroke:#eab308,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef comp fill:#93c5fd,stroke:#3b82f6,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef file fill:#f9a8d4,stroke:#ec4899,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef db fill:#6ee7b7,stroke:#10b981,stroke-width:2px,color:#0f172a,font-weight:bold;

    subgraph Frontend_Components ["Frontend Components (Views & Modals)"]
        c_app["citizen_app.py"]:::page
        o_app["officer_app.py"]:::page
        views["Views Module (views/)"]:::page
        chatbot["Chatbot Widget (components/chatbot.py)"]:::comp
        report_form["report_form.py"]:::page
        tracking["tracking.py"]:::page
        officer_panel["officer_panel.py"]:::page
    end

    subgraph Backend_Modules ["Backend Business Logic Units"]
        api_core["main.py API Gateway"]:::comp
        db_serv["database_service.py"]:::comp
        ai_serv["ai_service.py"]:::comp
        file_serv["file_service.py"]:::comp
    end

    subgraph Data_Files ["Data Persistence & Database Entities"]
        c_json["complaints.json"]:::file
        o_json["officers.json"]:::file
        d_json["officer_decisions.json"]:::file
        l_db[("laws table")]:::db
        a_db[("audit_logs table")]:::db
        c_db[("complaints table")]:::db
    end

    %% Connections
    c_app --> views
    o_app --> views
    views --> chatbot
    views --> report_form
    views --> tracking
    views --> officer_panel

    report_form -->|REST API POST| api_core
    tracking -->|REST API GET| api_core
    officer_panel -->|REST API PUT/GET| api_core
    chatbot -->|Invoke| ai_serv

    api_core --> db_serv
    api_core --> ai_serv
    api_core --> file_serv

    db_serv -->|Synchronize| c_json
    db_serv -->|Synchronize| o_json
    db_serv -->|Synchronize| d_json
    db_serv -->|RLS Writes| c_db
    db_serv -->|RLS Writes| a_db
    db_serv -->|Query| l_db
```

---

## 4. Implementation Plan (Development Roadmap) Diagram

This Gantt chart reflects the structured developmental steps, tasks, milestones, and timelines for building the system.

```mermaid
gantt
    title Cyber Crime Reporting System Development Roadmap
    dateFormat  YYYY-MM-DD
    axisFormat  %m-%d
    
    section Core Infrastructure
    Setup Env & Config Variables     :active, 2026-05-10, 2d
    Database Migrations Setup        :active, 2026-05-11, 3d
    Thread-Safe Local Database Failover : 2026-05-13, 3d

    section Backend & Core Services
    Secure Hashing & JWT Auth         : 2026-05-14, 2d
    Evidence File AES Encryption      : 2026-05-15, 3d
    Groq AI Categorization Engine     : 2026-05-16, 3d
    PDF Reporting & Watermarking      : 2026-05-18, 2d

    section Frontend Integration
    Streamlit Session Router Design  : 2026-05-19, 2d
    Citizen Complaint Forms          : 2026-05-20, 3d
    Chatbot Interface & AI Legal Tool : 2026-05-21, 2d
    Officer Dashboard Panel          : 2026-05-22, 4d

    section Cloud Setup & Auditing
    Supabase RLS Policies Setup       : 2026-05-24, 2d
    CI/CD Deployment Pipelines       : 2026-05-25, 2d
    Final Security Audit & Logging    : 2026-05-27, 2d
```

---

## 5. Sequence Diagram

This sequence diagram visualizes the interactive, step-by-step API transaction flow for a citizen submitting a crime report and a law enforcement officer reviewing the case.

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen User
    participant UI as Streamlit UI (citizen_app)
    participant API as FastAPI Core (main)
    participant FS as File Service (file_service)
    participant DB as DB Service (database_service)
    participant AI as AI Service (ai_service)
    participant Sec as Security Utils
    actor Officer as Law Enforcement Officer

    %% Complaint Submission
    Citizen->>UI: Input details, upload evidence, submit report
    rect rgb(240, 248, 255)
        Note over UI, API: Phase 1: Complaint Ingestion
        UI->>API: HTTP POST /complaints/ (Form details)
        API->>FS: Save and process evidence files
        FS->>Sec: Scan for malware & calculate SHA-256
        Sec-->>FS: Scan result: clean, hash generated
        FS->>Sec: Envelope encryption (AES-256)
        Sec-->>FS: Encrypted byte streams
        FS-->>API: File storage metadata & paths
    end

    rect rgb(245, 245, 220)
        Note over API, AI: Phase 2: Groq AI Processing
        API->>AI: Analyze incident description
        AI->>AI: Groq LLaMA-3 categorization & PECA match
        AI-->>API: returns ai_summary & ai_category
    end

    rect rgb(240, 255, 240)
        Note over API, DB: Phase 3: Secure Data Persistence
        API->>DB: create_complaint(data)
        DB->>DB: Attempt Supabase connection
        alt Supabase Online
            DB->>DB: Write to Postgres table 'complaints'
            DB->>DB: Write to Postgres table 'evidence'
        else Supabase Down / Not Initialized
            DB->>DB: Acquire thread-safe file lock
            DB->>DB: Write details to 'complaints.json'
            DB->>DB: Release file lock
        end
        DB->>DB: Write security audit log to audit_logs table/JSON
        DB-->>API: tracking_id generated (CCRS-PK-2026-XXXXXX)
    end
    API-->>UI: 201 Created (tracking_id, ai_category)
    UI-->>Citizen: Show unique Tracking ID & AI categorization

    %% Case Management
    Note over Officer, UI: Phase 4: Officer Decision Workflow
    Officer->>UI: Enter ID & Password (officer_app)
    UI->>API: HTTP POST /auth/login
    API->>DB: verify_officer(id, password)
    DB->>Sec: Verify PBKDF2 hash
    Sec-->>DB: Match true
    DB->>DB: Write audit log: OFFICER_LOGIN_SUCCESS
    DB-->>API: Authorized
    API-->>UI: JWT Bearer Token
    UI-->>Officer: Load Dashboard with Case Table
    Officer->>UI: Select Tracking ID, review description & AI category
    Officer->>UI: Update status to 'under_review' and input remarks
    UI->>API: HTTP PUT /complaints/{tracking_id}/status (token)
    API->>DB: update_complaint_status(tracking_id, 'under_review', remarks, officer_id)
    DB->>DB: Atomic write to 'complaints' & 'officer_decisions' (Postgres or JSON locks)
    DB->>DB: Write audit log: UPDATE_CASE_STATUS
    DB-->>API: Done
    API-->>UI: 200 OK
    UI-->>Officer: Show Dashboard updated
```

---

## 6. System Architecture Flow Diagram

This flow diagram illustrates the path of a complaint record as it is created, sanitized, categorized, stored, and managed through the system architecture.

```mermaid
flowchart TD
    classDef process fill:#fbcfe8,stroke:#db2777,stroke-width:2px,color:#0f172a;
    classDef check fill:#fef08a,stroke:#ca8a04,stroke-width:2px,color:#0f172a;
    classDef action fill:#c6f6d5,stroke:#22543d,stroke-width:2px,color:#0f172a;
    classDef terminal fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#0f172a;

    Start([Citizen Opens App]):::terminal --> Form[Fills Complaint Form]:::process
    Form --> Upload{Uploaded Evidence?}:::check
    
    Upload -->|Yes| Scan[Scan file size & extension]:::process
    Scan --> Malware{Malware Scanned Clean?}:::check
    Malware -->|No| Fail[Reject upload & Alert User]:::terminal
    Malware -->|Yes| Encrypt[Encrypt File with AES-256 & Generate Hash]:::process
    
    Encrypt --> Payload[Create Ingestion Payload]:::process
    Upload -->|No| Payload
    
    Payload --> AI[Query Groq LLaMA-3 classification & Summary]:::process
    AI --> RouteDB{Is Supabase Available?}:::check
    
    RouteDB -->|Yes| Supa[Insert into Postgres Complaints Table]:::action
    RouteDB -->|No| local[Lock file & append to complaints.json]:::action
    
    Supa --> Log[Append to Security Audit Trail]:::process
    local --> Log
    
    Log --> ID[Generate Tracking ID]:::process
    ID --> CitizenView[Display Status: Submitted to Citizen]:::terminal
    
    CitizenView --> Off[Officer Reviews Complaint on Panel]:::process
    Off --> Remarks[Officer Enters Case Remarks]:::process
    Remarks --> Decision[Selects Action: Approve or Reject]:::process
    
    Decision --> SyncDB{Is Supabase Available?}:::check
    SyncDB -->|Yes| SupaUpdate[Update complaints & officer_decisions tables]:::action
    SyncDB -->|No| localUpdate[Lock files & update JSON data stores]:::action
    
    SupaUpdate --> Audit[Log Action UPDATE_CASE_STATUS]:::process
    localUpdate --> Audit
    
    Audit --> End[Citizen views new status on tracker: Approved/Resolved]:::terminal
```

---

## 7. API Routing & Fallback Diagram

This schematic defines the routing configuration for core REST API routes and demonstrates the hybrid database failover model where local, thread-locked JSON databases act as active backups.

```mermaid
flowchart TB
    classDef entry fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff,font-weight:bold;
    classDef route fill:#a78bfa,stroke:#6d28d9,stroke-width:2px,color:#0f172a;
    classDef decision fill:#eab308,stroke:#a16207,stroke-width:2px,color:#0f172a;
    classDef success fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef fail fill:#ef4444,stroke:#b91c1c,stroke-width:2px,color:#fff;

    Gateway["FastAPI Gateway (main.py)"]:::entry

    subgraph API_Routers ["REST Endpoints"]
        AuthRouter["POST /auth/login<br>POST /auth/register"]:::route
        CompRouter["POST /complaints/<br>GET /complaints/{tracking_id}"]:::route
        EvidRouter["POST /evidence/upload"]:::route
        LawsRouter["GET /laws/?category={cat}"]:::route
        PdfRouter["GET /pdf/{tracking_id}"]:::route
    end

    Gateway --> AuthRouter
    Gateway --> CompRouter
    Gateway --> EvidRouter
    Gateway --> LawsRouter
    Gateway --> PdfRouter

    subgraph Core_Database_Driver ["Database Integration Handler"]
        DBQuery{"Supabase Client Active?"}:::decision
        SupaExec{"Execute DB Query?"}:::decision
    end

    AuthRouter --> DBQuery
    CompRouter --> DBQuery
    EvidRouter --> DBQuery
    LawsRouter --> DBQuery
    PdfRouter --> DBQuery

    DBQuery -->|Yes| SupaExec
    DBQuery -->|No| JSONFailover["Activate JSON Failover Route"]:::fail

    SupaExec -->|Success| SupaDone["Cloud Write/Read Done"]:::success
    SupaExec -->|Failed / Network Timeout| JSONFailover

    subgraph JSON_Local_Engine ["Thread-Safe JSON Driver"]
        JSONFailover --> Lock["Acquire threading.Lock()"]:::route
        Lock --> ReadWrite["Perform I/O operations (complaints.json, decisions.json)"]:::route
        ReadWrite --> Unlock["Release threading.Lock()"]:::route
    end

    subgraph Startup_Sync_Agent ["Startup Cloud Synchronization Service"]
        Startup["CCRS Service Starts"]:::entry
        Startup --> Connection{"Supabase Available?"}:::decision
        Connection -->|Yes| CheckEmpty{"Is Supabase empty but JSON has data?"}:::decision
        CheckEmpty -->|Yes| Migrate["Migrate local JSON keys to cloud tables"]:::success
        Migrate --> SyncDone["Migration Complete - Cloud Synced!"]:::success
        Connection -->|No| StayLocal["Run in Local-Only Mode"]:::fail
        CheckEmpty -->|No| SyncDone
    end
```

---

## 8. Deployment Architecture

This diagram maps the production deployment environment (using Streamlit Cloud, Render/ECS containers, Supabase Cloud, and Groq AI APIs) alongside development-level local setups.

```mermaid
flowchart TB
    classDef cloud fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff;
    classDef edge fill:#7c3aed,stroke:#5b21b6,stroke-width:2px,color:#fff;
    classDef client fill:#eab308,stroke:#b45309,stroke-width:2px,color:#0f172a;
    classDef onprem fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff;

    subgraph User_Client_Space ["Client Interfaces"]
        direction LR
        CitUser["Citizen Browser"]:::client
        OffUser["Officer Workspace"]:::client
    end

    subgraph Edge_Infrastructure ["Network & Routing"]
        Cloudflare{"Cloudflare Edge (HTTPS, CORS, Rate Limiting)"}:::edge
    end

    CitUser -->|HTTPS| Cloudflare
    OffUser -->|HTTPS| Cloudflare

    subgraph Streamlit_Cloud_Platform ["Streamlit Cloud hosting Frontend"]
        frontend["Streamlit Web Services (front-end portal)"]:::cloud
    end

    subgraph API_Hosting_App ["API App Server (Render/AWS ECS/FastAPI)"]
        api_srv["Dockerized FastAPI Service"]:::cloud
        local_fs["Secure Ephemeral Volume (Local Failover Stores)"]:::onprem
        api_srv -->|Thread-locked local fallbacks| local_fs
    end

    Cloudflare -->|HTTPS Route| frontend
    frontend -->|REST API Calls| api_srv

    subgraph Supabase_Cloud_Platform ["Supabase Serverless Database Infrastructure"]
        SupaDB[("Supabase Cloud Database (PostgreSQL)")]:::cloud
        SupaStorage[("Supabase File Storage Bucket")]:::cloud
    end

    api_srv -->|SQL Transactions over SSL / RLS| SupaDB
    api_srv -->|Encrypted Multipart uploads| SupaStorage

    subgraph AI_Engine_Cloud ["AI Processing Engine"]
        GroqCloud["Groq Cloud API Endpoint (LLaMA-3)"]:::cloud
    end

    api_srv -->|Secure API Key POST requests| GroqCloud
```

---

## 9. Layer Architecture Overview

This logical model details the five fundamental code layers of the CCRS alongside standard cross-cutting security features.

```mermaid
flowchart TB
    classDef p_layer fill:#93c5fd,stroke:#2563eb,stroke-width:2px,color:#0f172a;
    classDef a_layer fill:#c084fc,stroke:#7e22ce,stroke-width:2px,color:#0f172a;
    classDef s_layer fill:#fed7aa,stroke:#ea580c,stroke-width:2px,color:#0f172a;
    classDef d_layer fill:#a7f3d0,stroke:#059669,stroke-width:2px,color:#0f172a;
    classDef security fill:#fecdd3,stroke:#e11d48,stroke-width:2px,color:#0f172a,stroke-dasharray: 5 5;

    subgraph UI_Presentation_Layer ["1. Presentation Layer (UI)"]
        direction LR
        views["Streamlit Views (report_form, tracking, law_guide, officer_panel)"]:::p_layer
        chatbot_ui["Chatbot Interface (components/chatbot)"]:::p_layer
    end

    subgraph API_Router_Layer ["2. Application API Layer"]
        direction LR
        api_main["FastAPI Core App Router (main.py)"]:::a_layer
        jwt_auth["JWT Bearer Token Guard"]:::a_layer
    end

    subgraph Core_Service_Layer ["3. Business Logic & Service Layer"]
        direction TB
        ai_serv["AI Service (ai_service.py)"]:::s_layer
        file_serv["File Service (file_service.py)"]:::s_layer
        sec_util["Security & Cryptography (SecurityUtils)"]:::s_layer
    end

    subgraph Data_Access_Layer ["4. Data Access Layer (DAL)"]
        db_serv["Central Database Manager (database_service.py)"]:::d_layer
    end

    subgraph Storage_Layer ["5. Storage Layer"]
        direction LR
        postgres[("Supabase PostgreSQL DB")]:::d_layer
        local_json[("Local Failover JSON Files")]:::d_layer
        cloud_storage[("Supabase Storage Buckets")]:::d_layer
        local_evidence[("Local Crypt-Evidence Files")]:::d_layer
    end

    subgraph Security_Infrastructure ["Cross-Cutting Security Mechanisms"]
        rate_limit["Rate Limiter"]:::security
        audit_trail["Exhaustive Audit Logging"]:::security
        input_san["Input Sanitizer (XSS Protection)"]:::security
    end

    %% Flow through layers
    UI_Presentation_Layer --> API_Router_Layer
    API_Router_Layer --> Core_Service_Layer
    Core_Service_Layer --> Data_Access_Layer
    Data_Access_Layer --> Storage_Layer

    %% Security bindings
    Security_Infrastructure -.-> UI_Presentation_Layer
    Security_Infrastructure -.-> API_Router_Layer
    Security_Infrastructure -.-> Core_Service_Layer
    Security_Infrastructure -.-> Data_Access_Layer
```

---

## 10. User Roles & Permissions

This permission map defines the operational actions permitted for Citizens (Registered/Anonymous), Law Enforcement Officers, and Administrators.

```mermaid
flowchart TB
    classDef citizen fill:#38bdf8,stroke:#0284c7,stroke-dasharray: 5 5,color:#0f172a;
    classDef officer fill:#a78bfa,stroke:#7c3aed,stroke-dasharray: 5 5,color:#0f172a;
    classDef admin fill:#f43f5e,stroke:#be123c,stroke-dasharray: 5 5,color:#0f172a;
    classDef feature fill:#10b981,stroke:#047857,color:#fff;
    classDef boundary fill:#f8fafc,stroke:#cbd5e1,color:#1e293b;

    CitRole["Citizen / Reporter Role<br>(Anonymous / Registered)"]:::citizen
    OffRole["Law Enforcement Officer Role<br>(CYBER2026xxxx ID)"]:::officer
    AdmRole["System Administrator Role<br>(Admin Token Auth)"]:::admin

    subgraph Guest_Permissions ["Anonymous & Guest Permissions"]
        F1["Submit Incident Reports"]:::feature
        F2["Upload Incident Evidence"]:::feature
        F3["Track Complaints by Tracking ID"]:::feature
        F4["Browse Pakistan Cyber Laws (PECA)"]:::feature
        F5["Use Legal Guidance AI Chatbot"]:::feature
    end

    subgraph Officer_Permissions ["Officer Case Management Permissions"]
        F6["Officer Portal Secure Login"]:::feature
        F7["View Interactive Officer Dashboard"]:::feature
        F8["Review all Registered Complaints"]:::feature
        F9["Update Case Status<br>(Submitted, Under Review, Resolved)"]:::feature
        F10["Record Case Decisions & Remarks"]:::feature
        F11["Download Case PDF Reports"]:::feature
    end

    subgraph Admin_Permissions ["System Administrative Permissions"]
        F12["Register New Law Enforcement Officers"]:::feature
        F13["View Comprehensive Security Audit Logs"]:::feature
        F14["Backend System Configuration Access"]:::feature
        F15["Database Row Level Security (RLS) Override"]:::feature
    end

    %% Mappings
    CitRole --> F1
    CitRole --> F2
    CitRole --> F3
    CitRole --> F4
    CitRole --> F5

    OffRole --> F6
    OffRole --> F7
    OffRole --> F8
    OffRole --> F9
    OffRole --> F10
    OffRole --> F11

    AdmRole --> F12
    AdmRole --> F13
    AdmRole --> F14
    AdmRole --> F15
```

---

## 11. Citizen & Complaint Workflow

This state transition diagram charts the operational and decision workflow for citizens submitting a crime report.

```mermaid
stateDiagram-v2
    [*] --> GuestPortal : Visit Website
    
    state GuestPortal {
        [*] --> BrowseLaws : Need legal reference?
        BrowseLaws --> [*]
        
        [*] --> ConsultChatbot : Need legal guidance?
        ConsultChatbot --> ConsultChatbot : Chat with Legal AI
        ConsultChatbot --> [*]
        
        [*] --> StartComplaint : File a crime report
    }

    state StartComplaint {
        [*] --> InputDetails : Enter Name, CNIC, Phone, Address
        InputDetails --> SetPrivacy : Choose Anonymous or Public
        SetPrivacy --> IncidentForm : Fills Date, Location, Incident Text
        IncidentForm --> EvidenceChoice : Has Evidence?
        
        state EvidenceChoice {
            [*] --> UploadFiles : Yes
            UploadFiles --> ScanCheck : Verify size & format
            ScanCheck --> EncryptSave : Clean & AES-256 Encrypted
            EncryptSave --> [*]
            [*] --> NoEvidence : No
            NoEvidence --> [*]
        }
        
        EvidenceChoice --> SubmitAction : Submit Report
        SubmitAction --> AISummarization : Backend processing
        AISummarization --> DBWrite : Save Case details (Postgres/JSON)
        DBWrite --> GenerateID : Compute CCRS Tracking ID
    }

    GenerateID --> DisplayTrackingID : Present ID to citizen
    DisplayTrackingID --> TrackCase : Check status later
    
    state TrackCase {
        [*] --> InputID : Enter Tracking ID
        InputID --> QueryDB : Query complaints database
        QueryDB --> ShowResult : Display Status & Officer Remarks
        ShowResult --> [*]
    }
```

---

## 12. Officer Case Management Workflow

This state diagram visualizes the interactive step-by-step workflow for law enforcement officers logging in and managing citizen reports.

```mermaid
stateDiagram-v2
    [*] --> LoggedOut : Access Officer Portal
    
    state LoggedOut {
        [*] --> InputCredentials : Enter Officer ID & Password
        InputCredentials --> PBKDF2Verification : Secure Authentication
        PBKDF2Verification --> WriteAuditLog : Log Result
    }

    PBKDF2Verification --> LoggedIn : Success
    PBKDF2Verification --> LoggedOut : Failed (Inc. login failure count)

    state LoggedIn {
        [*] --> ShowDashboard : Load Officer Dashboard Panel
        
        state ShowDashboard {
            [*] --> CaseStats : View Statistics
            [*] --> CaseTable : View Complaint List
        }
        
        CaseTable --> CaseSelected : Select Tracking ID
        
        state CaseSelected {
            [*] --> ReviewCaseText : Read Description & Location
            ReviewCaseText --> ReadAISummary : Read Groq-generated AI Summary
            ReadAISummary --> AccessEvidence : Access Evidence Files
            AccessEvidence --> DecryptEvidence : Decrypt with Secure Keys
            DecryptEvidence --> ReviewPECA : Consult matched PECA laws
        }
        
        CaseSelected --> ModifyCase : Update Case State
        
        state ModifyCase {
            [*] --> SelectStatus : Change Status (Under Review / Resolved)
            SelectStatus --> EnterRemarks : Input Officer remarks/decisions
            EnterRemarks --> SubmitRemarks : Save updates
            SubmitRemarks --> WriteDBAtomic : Update complaints & decisions
            WriteDBAtomic --> LogAudit : Record action UPDATE_CASE_STATUS
        }
        
        ModifyCase --> ExportReport : Case completed?
        ExportReport --> GeneratePDF : Generate official PDF report
        GeneratePDF --> ApplyWatermark : Apply CCRS Secure Watermark
        ApplyWatermark --> DownloadReport : Download Report file
    }

    LoggedIn --> LoggedOut : Click Logout / Session Expired
```

---

## 13. Database Schema & Structure (ERD)

This entity-relationship diagram (ERD) describes the structural organization of your PostgreSQL database tables (from [main_schema.sql](file:///c:/Users/shahz/cyber-crime-reporting-system/database/schemas/main_schema.sql)), columns, primary/foreign keys, and specific security Row Level Security (RLS) policies.

```mermaid
erDiagram
    %% Entities
    USERS {
        uuid id PK "gen_random_uuid()"
        varchar email UK "unique email"
        varchar hashed_password "PBKDF2 secure hash"
        varchar full_name "user full name"
        varchar phone "phone number"
        varchar cnic UK "13-digit unique cnic"
        text address "mailing address"
        boolean is_active "DEFAULT true"
        timestamp_tz created_at "DEFAULT NOW()"
        timestamp_tz updated_at "DEFAULT NOW()"
    }

    COMPLAINTS {
        uuid id PK "gen_random_uuid()"
        varchar tracking_id UK "CCRS-PK-YYYY-XXXXXX"
        uuid user_id FK "REFERENCES users(id)"
        varchar full_name "NULL for anonymous"
        varchar phone "NULL for anonymous"
        varchar cnic "NULL for anonymous"
        text address "NULL for anonymous"
        date incident_date "incident date"
        varchar location "incident location"
        varchar complaint_reason "PECA Category"
        text description "Incident description"
        varchar status "submitted, under_review, resolved"
        text ai_summary "AI-generated incident summary"
        varchar ai_category "AI-matched PECA category"
        timestamp_tz created_at "DEFAULT NOW()"
        timestamp_tz updated_at "DEFAULT NOW()"
    }

    EVIDENCE {
        uuid id PK "gen_random_uuid()"
        uuid complaint_id FK "REFERENCES complaints(id) ON DELETE CASCADE"
        varchar file_name "Supabase storage name"
        varchar original_name "Upload name"
        varchar file_path "Supabase Storage Path"
        varchar file_type "video, image, pdf"
        varchar mime_type "file MIME type"
        bigint file_size "file size in bytes"
        varchar sha256_hash "For file integrity verification"
        boolean is_encrypted "DEFAULT true"
        varchar malware_scan_status "pending, clean, infected"
        jsonb metadata "EXIF, IPTC and file details"
        timestamp_tz uploaded_at "DEFAULT NOW()"
    }

    LAWS {
        uuid id PK "gen_random_uuid()"
        varchar category "e.g. Hacking, Cyberstalking"
        varchar section "PECA Section number"
        varchar title "Section law title"
        text description "Legal text of section"
        text punishment "Legal fine/imprisonment terms"
        text relevant_pepa_sections "Related acts and laws"
        timestamp_tz created_at "DEFAULT NOW()"
        timestamp_tz updated_at "DEFAULT NOW()"
    }

    AUDIT_LOGS {
        uuid id PK "AUDIT-YYYYMMDD-XXXX"
        uuid user_id FK "REFERENCES users(id) ON DELETE SET NULL"
        varchar action "SUBMIT_COMPLAINT, OFFICER_LOGIN_SUCCESS, etc."
        varchar resource_type "complaint, evidence, officer, etc."
        uuid resource_id "resource identification uuid"
        jsonb details "Context information payload"
        inet ip_address "Caller IP address"
        text user_agent "Caller User Agent"
        timestamp_tz created_at "DEFAULT NOW()"
    }

    OFFICER_DECISIONS {
        varchar tracking_id PK "REFERENCES complaints(tracking_id)"
        varchar officer_id "Officer ID (CYBER2026xxxx)"
        varchar decision "Status (approve/reject/pending)"
        text notes "Officer case management remarks"
        timestamp_tz decided_at "DEFAULT NOW()"
    }

    %% Relationships
    USERS ||--o{ COMPLAINTS : "submits"
    USERS ||--o{ AUDIT_LOGS : "triggers"
    COMPLAINTS ||--o{ EVIDENCE : "holds"
    COMPLAINTS ||--o| OFFICER_DECISIONS : "resolves"
```

### Table Security Boundaries (Row Level Security - RLS Policies)

*   **`users`**: Enforces strict separation. Only authenticated profiles can read/write their own matching UUID records (`auth.uid() = id`).
*   **`complaints`**: Citizens can select and insert complaints matching their UUID (`auth.uid() = user_id`) or view anonymous entries that match `user_id IS NULL`. 
*   **`evidence`**: Restricts access based on sub-queries. A user can read/write evidence only if they own the related complaint record.
*   **`laws`**: Fully public read access for PECA section browsing (`USING (true)`).
*   **`audit_logs`**: Strictly locked to administrative roles (`auth.users.raw_user_meta_data->>'role' = 'admin'`).

---

## 14. System Components & Modules Map

This component map describes the package, module, directory, and file configuration for both frontend and backend modules.

```mermaid
flowchart TB
    classDef folder fill:#cbd5e1,stroke:#475569,stroke-width:2px,color:#0f172a,font-weight:bold;
    classDef file fill:#f8fafc,stroke:#94a3b8,stroke-width:1px,color:#1e293b;
    classDef core fill:#38bdf8,stroke:#0284c7,stroke-width:2px,color:#0f172a,font-weight:bold;

    root["Root WorkSpace (cyber-crime-reporting-system/)"]:::folder
    
    subgraph Frontend_Module ["Frontend Module (frontend/)"]
        fe_dir["frontend/"]:::folder
        citizen_app["citizen_app.py Entry"]:::core
        officer_app_fe["officer_app.py Entry"]:::core
        fe_views["views/ (report_form.py, tracking.py, officer_panel.py, help.py, law_guide.py)"]:::file
        fe_comps["components/ (chatbot.py, init.py)"]:::file
        fe_dir --> citizen_app
        fe_dir --> officer_app_fe
        fe_dir --> fe_views
        fe_dir --> fe_comps
    end

    subgraph Backend_Module ["Backend Module (backend/)"]
        be_dir["backend/"]:::folder
        be_api["api/main.py Core Gateway"]:::core
        be_services["services/ (database_service.py, ai_service.py, file_service.py)"]:::file
        be_models["models/ (pydantic schemas)"]:::file
        be_utils["utils/ (security.py, integrity.py)"]:::file
        be_dir --> be_api
        be_dir --> be_services
        be_dir --> be_models
        be_dir --> be_utils
    end

    subgraph Database_Module ["Database Schema & SQL (database/)"]
        db_dir["database/"]:::folder
        db_schemas["schemas/main_schema.sql (PostgreSQL/Supabase)"]:::file
        db_migrations["migrations/ (version files)"]:::file
        db_seeders["seeders/ (initial law seeds)"]:::file
        db_dir --> db_schemas
        db_dir --> db_migrations
        db_dir --> db_seeders
    end

    subgraph Local_Data ["Data Cache (backend/data/)"]
        data_dir["backend/data/"]:::folder
        c_json["complaints.json"]:::file
        o_json["officers.json"]:::file
        d_json["officer_decisions.json"]:::file
        a_json["audit_logs.json"]:::file
        data_dir --> c_json
        data_dir --> o_json
        data_dir --> d_json
        data_dir --> a_json
    end

    root --> Frontend_Module
    root --> Backend_Module
    root --> Database_Module
    be_dir --> Local_Data
```

---

## 15. Security Architecture

This layout outlines the defense-in-depth model implemented in the system, ranging from edge rate-limiting to database Row Level Security.

```mermaid
flowchart TB
    classDef secure fill:#fee2e2,stroke:#ef4444,stroke-width:2px,color:#991b1b,font-weight:bold;
    classDef boundary fill:#f8fafc,stroke:#cbd5e1,color:#1e293b;

    subgraph Network_Boundary ["Network Level Security"]
        HTTPS["Enforced HTTPS/TLS 1.3"]:::secure
        CORS["Strict CORS Policies"]:::secure
        RateLimit["Rate Limiter (100 req / 15 min)"]:::secure
    end

    subgraph App_Boundary ["Application Level Security"]
        JWT["JWT Bearer Tokens (HMAC-SHA256)"]:::secure
        InputValidation["Input Sanitization & Bleach (XSS Shield)"]:::secure
        MalwareScan["Evidence Malware Scanning (ClamAV)"]:::secure
        AES["Envelope Encryption (AES-256) for Evidence"]:::secure
        PBKDF2["PBKDF2 Secure Hashing for Passwords"]:::secure
    end

    subgraph Database_Boundary ["Database Level Security"]
        RLS["PostgreSQL Row Level Security (RLS)"]:::secure
        Audit["Exhaustive Cryptographic Security Audit Log"]:::secure
        KeyMgmt["Secure Env Key Management (Dotenv)"]:::secure
    end

    %% Flow of defense
    Network_Boundary --> App_Boundary
    App_Boundary --> Database_Boundary
```

---

## 16. Deployment Pipeline

This schematic traces the automated integration and continuous deployment pipeline (CI/CD) for server and backend builds.

```mermaid
flowchart LR
    classDef stage fill:#f1f5f9,stroke:#64748b,stroke-width:2px,color:#0f172a;
    classDef active fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1,font-weight:bold;
    classDef final fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#166534,font-weight:bold;

    Commit["1. git commit & push"]:::stage
    --> Lint["2. Linting & Formatting<br>(Black, Flake8, Ruff)"]:::stage
    --> Test["3. Run Automated Tests<br>(pytest / coverage)"]:::stage
    --> Build["4. Docker Build Image<br>(Multi-stage builds)"]:::active
    --> DeployFE["5. Deploy Streamlit Frontend<br>(Streamlit Cloud)"]:::active
    --> DeployBE["6. Deploy FastAPI Backend<br>(Render / ECS)"]:::active
    --> Migrate["7. Apply DB Migrations<br>(Supabase Postgres)"]:::active
    --> Complete["8. Monitoring & Incident Alerting<br>(Sentry / Logs)"]:::final
```

---

## 17. User Interaction Diagram

This visualizes user navigation paths, pages, actions, and reactions when interacting with interactive form controls.

```mermaid
flowchart TB
    classDef action fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef page fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef system fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d;

    Home["Open CCRS Portal Homepage"]:::page
    --> Nav{"Navigation Choice"}:::action

    Nav -->|"1. File Complaint"| FormPage["Load Complaint Form Page"]:::page
    Nav -->|"2. Track Complaint"| TrackerPage["Load Case Tracking Page"]:::page
    Nav -->|"3. Ask AI Guide"| ChatBot["Open Legal Chatbot Modal"]:::page
    Nav -->|"4. Officer Panel"| LogPage["Load Officer Login View"]:::page

    FormPage -->|"Fill fields & upload files"| SubmitReport["Click Submit Report"]:::action
    SubmitReport -->|"Run sanitization & malware scans"| SysAccept["API Ingests Report"]:::system
    SysAccept -->|"Returns Tracking ID"| ShowID["Display Case Confirmed"]:::page

    TrackerPage -->|"Enter Tracking ID"| TrackSubmit["Click Search"]:::action
    TrackSubmit -->|"Query RLS / local JSON databases"| TrackResult["Display status & officer remarks"]:::page

    ChatBot -->|"Input cyber law question"| ChatSubmit["Click Send"]:::action
    ChatSubmit -->|"Groq LLaMA-3 context query"| ChatResponse["AI displays legal guidance response"]:::page

    LogPage -->|"Enter Officer ID & Password"| LogSubmit["Click Login"]:::action
    LogSubmit -->|"Check PBKDF2 hashes"| Dashboard["Open Officer Case Dashboard"]:::page
    Dashboard -->|"Select case"| CaseView["Open Case Review Panel"]:::page
    CaseView -->|"Update status & remarks"| UpdateSubmit["Save Remarks"]:::action
    UpdateSubmit -->|"Atomic DB write & security log"| DashRefresh["Dashboard Refreshed"]:::system
```

---

## 18. Feature & Capability Matrix

This matrix describes the functional capabilities, authorization, data endpoints, and security mechanisms of each user class in the Cyber Crime Reporting System.

| Functional Feature | Allowed Roles | Service Layer / Module | Data Target (Database / File) | Security Check & Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Submit Incident Report** | Citizen / Anonymous | `FastAPI Core`, `DatabaseService` | `complaints` table / `complaints.json` | Cross-Origin Policy, Input bleach sanitization, API rate-limiting |
| **Browse Pakistan Cyber Laws** | Public Guest | `FastAPI Core`, `main_schema.sql` | `laws` table | Read-Only database connection, Public GET endpoint |
| **Consult Legal AI Chatbot** | Public Guest | `AIService` (Groq API) | LLM context prompts | Dynamic prompt sanitization, rate-limiter |
| **Upload Evidence Files** | Citizen / Anonymous | `FileService`, `SecurityUtils` | `Supabase Storage` / Local FS | File-extension validation, ClamAV antivirus scan, AES-256 Envelope Encryption, SHA-256 integrity hash |
| **Track Complaint Status** | Citizen / Anonymous | `DatabaseService` | `complaints` & `officer_decisions` | Strict 18-character tracking ID format check, Read-Only GET |
| **Officer Portal Login** | Enforcement Officer | `DatabaseService`, `SecurityUtils` | `officers` table / `officers.json` | Officer ID verification, PBKDF2 cryptography hash matching, JWT Auth Token generation |
| **Interactive Dashboard & Statistics** | Enforcement Officer | `FastAPI Core`, `DatabaseService` | `complaints` table counts | Strict JWT token verification, HTTPS endpoint |
| **Review Complaints & Remarks** | Enforcement Officer | `DatabaseService`, `AIService` | `complaints` table + AI Summary | JWT verification, active database query over secure channel |
| **Update Case Status & Decisions** | Enforcement Officer | `DatabaseService` | `complaints` & `officer_decisions` | JWT role matching, thread-safe transactional updates with cross-thread files locks |
| **Generate Case PDF Report** | Enforcement Officer | `FastAPI Core`, `pdf_service` | Dynamic memory generation | JWT authentication, official watermarking logic |
| **Register Officers & Configuration** | System Admin | `DatabaseService` | `officers` table | Admin UUID session validation, Row Level Security bypass |
| **Inspect System Security Audit Log** | System Admin | `DatabaseService` | `audit_logs` table / `audit_logs.json` | RLS check (`role = 'admin'` metadata match in JWT payload) |
