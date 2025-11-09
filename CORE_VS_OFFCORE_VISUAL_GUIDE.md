# Salesforce Core vs Off-Core: Visual Learning Guide

## The Mental Model: Two Complementary Systems

Think of Salesforce as **two connected brains**:
- **Left Brain (Core)**: Fast, precise, transactional - handles day-to-day CRM operations
- **Right Brain (Off-Core/Data Cloud)**: Creative, analytical, pattern-seeking - handles insights and AI

---

## Visual 1: The Complete Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        SALESFORCE PLATFORM ECOSYSTEM                       │
└────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┐         ┌──────────────────────────────────┐
│      SALESFORCE CORE             │         │     DATA CLOUD (OFF-CORE)        │
│      (Left Brain)                │         │     (Right Brain)                │
├──────────────────────────────────┤         ├──────────────────────────────────┤
│                                  │         │                                  │
│  🏢 CRM Objects                  │         │  👤 Unified Customer Profiles    │
│  ┌────────────────────┐          │         │  ┌────────────────────┐          │
│  │ Account            │          │         │  │ Customer 360       │          │
│  │ Contact            │◄─────────┼─────────┼─►│ All touchpoints    │          │
│  │ Opportunity        │  Zero-   │         │  │ Behavioral data    │          │
│  │ Case               │   ETL    │         │  │ External data      │          │
│  │ Lead               │          │         │  └────────────────────┘          │
│  │ Custom Objects     │          │         │                                  │
│  └────────────────────┘          │         │  📊 Analytical Data              │
│                                  │         │  ┌────────────────────┐          │
│  ⚙️ Business Logic               │         │  │ Billions of events │          │
│  ┌────────────────────┐          │         │  │ Historical trends  │          │
│  │ Apex Code          │          │         │  │ Aggregations       │          │
│  │ Flows              │          │         │  │ ML Features        │          │
│  │ Validation Rules   │          │         │  └────────────────────┘          │
│  │ Triggers           │          │         │                                  │
│  └────────────────────┘          │         │  📄 Unstructured Data            │
│                                  │         │  ┌────────────────────┐          │
│  🖥️ User Interface               │         │  │ PDFs, Images       │          │
│  ┌────────────────────┐          │         │  │ Audio, Video       │          │
│  │ Lightning Web Comp │          │         │  │ Emails, Chats      │          │
│  │ Record Pages       │          │         │  │ Vector Embeddings  │          │
│  │ List Views         │          │         │  └────────────────────┘          │
│  └────────────────────┘          │         │                                  │
│                                  │         │  🤖 AI/ML                        │
│  🔐 Security                     │         │  ┌────────────────────┐          │
│  ┌────────────────────┐          │         │  │ Einstein Models    │          │
│  │ Profiles           │          │         │  │ Predictions        │          │
│  │ Permission Sets    │          │         │  │ Vector Search      │          │
│  │ Sharing Rules      │          │         │  │ RAG (AI Memory)    │          │
│  └────────────────────┘          │         │  └────────────────────┘          │
│                                  │         │                                  │
│  ⏱️ Performance: <100ms          │         │  ⏱️ Performance: Seconds         │
│  💾 Storage: GBs-TBs             │         │  💾 Storage: TBs-PBs             │
│  📈 Scale: Millions of records   │         │  📈 Scale: Billions of events    │
│  🎯 Optimized: Transactions      │         │  🎯 Optimized: Analytics         │
│                                  │         │                                  │
└──────────────────────────────────┘         └──────────────────────────────────┘
           │                                              ▲
           │                                              │
           └───────────── Zero-ETL Sync ─────────────────┘
                    (Automatic, near real-time)
```

---

## Visual 2: Data Flow - How They Work Together

```
USER INTERACTION FLOW
═══════════════════════════════════════════════════════════════

Step 1: Sales Rep Creates Opportunity (Core)
┌─────────────────┐
│  Sales Rep UI   │
│  (Lightning)    │
└────────┬────────┘
         │ Creates record
         ▼
┌─────────────────────────────────────────┐
│  Salesforce Core                        │
│  ┌───────────────────────────┐          │
│  │ Opportunity               │          │
│  │ - Name: "Acme Deal"       │          │
│  │ - Amount: $500k           │          │
│  │ - Stage: Prospecting      │          │
│  └───────────────────────────┘          │
└─────────────────────────────────────────┘
         │
         │ Zero-ETL sync (automatic)
         ▼
┌─────────────────────────────────────────┐
│  Data Cloud (Off-Core)                  │
│  ┌───────────────────────────┐          │
│  │ Profile: Acme Corp        │          │
│  │ - Core: Opportunity       │◄─────┐   │
│  │ - Web: 50 visits          │      │   │
│  │ - Email: 80% open rate    │      │   │
│  │ - AI Score: 85/100 ────┐  │      │   │
│  └────────────────────────│──┘      │   │
└────────────────────────────│─────────│───┘
                             │         │
                             │         │
Step 2: AI Enrichment (Off-Core)        │
                             │         │
┌────────────────────────────▼─────────│───┐
│  Einstein AI                         │   │
│  - Analyzes: Web behavior, emails    │   │
│  - Predicts: 85% likely to close     │   │
│  - Recommends: "Engage this week"    │   │
└──────────────────────────────────────│───┘
                                       │
                             Writes back
                             (Activation)
                                       │
Step 3: AI Insights Surface in Core    │
                                       │
┌──────────────────────────────────────▼───┐
│  Salesforce Core                         │
│  ┌───────────────────────────┐           │
│  │ Opportunity               │           │
│  │ - Einstein Score: 85      │◄──────────┘
│  │ - Next Best Action: Call  │
│  └───────────────────────────┘           │
└──────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Sales Rep UI   │
│  Sees AI insight│
│  in record page │
└─────────────────┘
```

---

## Visual 3: Decision Matrix - When to Use Each

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHOULD I USE CORE OR OFF-CORE?                       │
└─────────────────────────────────────────────────────────────────────────┘

Question 1: What type of data?
├─ Structured (fields, objects) ────────────► USE CORE
└─ Unstructured (PDFs, images, vectors) ────► USE OFF-CORE (Data Cloud)

Question 2: What volume?
├─ Millions of records ─────────────────────► USE CORE
└─ Billions of events/rows ─────────────────► USE OFF-CORE (Data Cloud)

Question 3: What operation?
├─ Create/Update CRM records ───────────────► USE CORE
├─ Real-time UI (<100ms) ───────────────────► USE CORE
├─ Complex analytics (aggregations) ────────► USE OFF-CORE (Data Cloud)
├─ AI/ML (training models) ─────────────────► USE OFF-CORE (Data Cloud)
└─ Streaming events (IoT, clickstream) ─────► USE OFF-CORE (Data Cloud)

Question 4: What's the user experience?
├─ Sales rep clicking buttons ──────────────► USE CORE
├─ Data scientist running SQL ──────────────► USE OFF-CORE (Data Cloud)
└─ AI agent analyzing patterns ─────────────► USE OFF-CORE (Data Cloud)

Question 5: Where does data come from?
├─ Salesforce users (manual entry) ─────────► USE CORE
├─ External systems (API, batch) ───────────► USE OFF-CORE (Data Cloud)
└─ Third-party data (Snowflake, S3) ────────► USE OFF-CORE (Data Cloud)
```

---

## Visual 4: Real-World Example - E-Commerce Company

```
SCENARIO: E-Commerce company selling on Salesforce Commerce Cloud
         wants to build a Customer 360 view

┌─────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                               │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Salesforce  │  │   Website    │  │  Mobile App  │  │  Call Center │
│     Core     │  │ (Clickstream)│  │   (Events)   │  │   (Calls)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       │ Account         │ Page views      │ App opens       │ Call logs
       │ Contact         │ Add to cart     │ Push notifs     │ Transcripts
       │ Opportunity     │ Purchases       │ Location        │ Sentiment
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           WHERE DOES IT GO?                             │
└─────────────────────────────────────────────────────────────────────────┘

SALESFORCE CORE                      DATA CLOUD (OFF-CORE)
┌──────────────────────┐            ┌──────────────────────────────┐
│ Account, Contact     │            │ Unified Profile              │
│ Opportunity          │────────────►│ - Core data (Account, Opp)  │
│                      │ Zero-ETL   │ - Web events (clicks)        │
│ Structured, clean    │            │ - Mobile events (opens)      │
│ Manual entry         │            │ - Call transcripts (AI)      │
│                      │            │                              │
│ Used by:             │            │ Used by:                     │
│ - Sales reps         │            │ - Marketing (segments)       │
│ - Service agents     │            │ - Data scientists (analysis) │
│                      │            │ - AI (predictions)           │
└──────────────────────┘            └──────────────────────────────┘
         │                                      │
         │                                      │ Activation
         │                                      │ (AI insights)
         ▼                                      ▼
┌──────────────────────┐            ┌──────────────────────────────┐
│ Sales Rep sees:      │◄───────────│ Einstein generates:          │
│ - Contact info       │            │ - Propensity to buy: 78%     │
│ - Recent purchases   │            │ - Churn risk: Low            │
│ - Einstein score ✨  │            │ - Next best product: Shoes   │
└──────────────────────┘            └──────────────────────────────┘
```

---

## Visual 5: ISV Use Cases - Build on Core or Off-Core?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ISV APP EXAMPLES                               │
└─────────────────────────────────────────────────────────────────────────┘

BUILD ON CORE (ISVforce)
┌──────────────────────────────────────────────────────────────────┐
│  App Type: CRM Extensions                                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │ DocuSign       │  │ Salesforce CPQ │  │ Copado DevOps  │     │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤     │
│  │ E-signatures   │  │ Quote builder  │  │ CI/CD pipeline │     │
│  │ on records     │  │ Price rules    │  │ Deployments    │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│                                                                  │
│  Why Core?                                                       │
│  ✓ Needs CRM objects (Opportunity, Account)                     │
│  ✓ Real-time UI for users                                       │
│  ✓ Transactional workflows                                      │
│  ✓ Runs inside Salesforce org (Lightning page)                  │
│                                                                  │
│  Tech Stack:                                                     │
│  • Apex (business logic)                                        │
│  • Lightning Web Components (UI)                                │
│  • Custom Objects (data model)                                  │
│  • Managed Package (distribution)                               │
└──────────────────────────────────────────────────────────────────┘


BUILD ON OFF-CORE (Data Cloud)
┌──────────────────────────────────────────────────────────────────┐
│  App Type: Analytics, AI, Unstructured Data                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │ Gong.io        │  │ Segment CDP    │  │ Contract AI    │     │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤     │
│  │ Call recording │  │ Event streams  │  │ PDF extraction │     │
│  │ AI insights    │  │ Real-time data │  │ Vector search  │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
│                                                                  │
│  Why Off-Core?                                                   │
│  ✓ Unstructured data (audio, PDFs, images)                      │
│  ✓ High-volume events (millions per day)                        │
│  ✓ AI/ML workloads (training, inference)                        │
│  ✓ External data sources (not just Salesforce)                  │
│                                                                  │
│  Tech Stack:                                                     │
│  • Data Cloud Ingestion API (unstructured)                      │
│  • Vector Database (embeddings)                                 │
│  • Einstein Studio (bring your own model)                       │
│  • Activation API (write insights back to Core)                 │
└──────────────────────────────────────────────────────────────────┘


HYBRID (Both Core + Off-Core)
┌──────────────────────────────────────────────────────────────────┐
│  App Type: Enterprise Solutions                                  │
│  ┌────────────────┐  ┌────────────────┐                          │
│  │ Certinia ERP   │  │ Tableau CRM    │                          │
│  ├────────────────┤  ├────────────────┤                          │
│  │ Core: GL, AP,  │  │ Core: Record   │                          │
│  │   AR, Billing  │  │   page embed   │                          │
│  │                │  │                │                          │
│  │ Off-Core:      │  │ Off-Core:      │                          │
│  │   Financial    │  │   Big data     │                          │
│  │   reporting    │  │   analytics    │                          │
│  └────────────────┘  └────────────────┘                          │
│                                                                  │
│  Why Hybrid?                                                     │
│  ✓ Best of both worlds                                          │
│  ✓ Transactional + analytical                                   │
│  ✓ Real-time updates + historical analysis                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Visual 6: Learning Journey - Connecting the Dots

```
┌─────────────────────────────────────────────────────────────────────────┐
│              YOUR LEARNING JOURNEY (4 Levels)                           │
└─────────────────────────────────────────────────────────────────────────┘

LEVEL 1: Understand the "Why"
┌──────────────────────────────────────────────────────────────────┐
│  Question: Why two systems?                                      │
│                                                                  │
│  Answer:                                                         │
│  • Core = Built for CRM (decades of optimization)               │
│  • Off-Core = Built for data science (modern analytics)         │
│  • Together = Compete with standalone CDPs, data lakes          │
│                                                                  │
│  Analogy: Like having both Excel (Core) and Python (Off-Core)   │
│           - Excel: Quick, visual, user-friendly                 │
│           - Python: Powerful, scalable, AI-ready                │
│                                                                  │
│  Activity: Read Section 8 of this guide                         │
└──────────────────────────────────────────────────────────────────┘

LEVEL 2: See the "How"
┌──────────────────────────────────────────────────────────────────┐
│  Question: How do they connect?                                  │
│                                                                  │
│  Answer: Zero-ETL                                                │
│  ┌────────────┐                    ┌────────────┐               │
│  │    Core    │────────────────────►│ Data Cloud │               │
│  │  Account   │  Automatic sync     │  Profile   │               │
│  └────────────┘                    └────────────┘               │
│                                           │                      │
│                                           │ AI enrichment        │
│                                           ▼                      │
│  ┌────────────┐                    ┌────────────┐               │
│  │    Core    │◄────────────────────│ Data Cloud │               │
│  │ +AI Score  │  Activation         │ Einstein   │               │
│  └────────────┘                    └────────────┘               │
│                                                                  │
│  Activity: Sign up for Data Cloud trial, create a profile       │
└──────────────────────────────────────────────────────────────────┘

LEVEL 3: Build the "What"
┌──────────────────────────────────────────────────────────────────┐
│  Question: What can I build as an ISV?                           │
│                                                                  │
│  Exercise: Design your own app                                   │
│                                                                  │
│  Idea 1: "Customer Health Score" (Hybrid)                       │
│  ├─ Core: Display score on Account page (LWC)                   │
│  └─ Off-Core: Calculate score from 10+ data sources (DC)        │
│                                                                  │
│  Idea 2: "Contract Risk Analyzer" (Off-Core)                    │
│  ├─ Off-Core: Ingest PDFs, extract clauses (vector search)      │
│  └─ Core: Create alerts on Account (Apex)                       │
│                                                                  │
│  Idea 3: "Sales Playbook" (Core)                                │
│  └─ Core: Guided flows, templates, automation (Flow, Apex)      │
│                                                                  │
│  Activity: Sketch your ISV product idea (1 page)                │
└──────────────────────────────────────────────────────────────────┘

LEVEL 4: Master the "Business"
┌──────────────────────────────────────────────────────────────────┐
│  Question: How do I monetize this?                               │
│                                                                  │
│  Decision Matrix:                                                │
│                                                                  │
│  If Core-based app:                                              │
│  ├─ List on AppExchange                                         │
│  ├─ Revenue share: 75% to you, 25% to Salesforce                │
│  └─ Customer needs: Active Salesforce org                       │
│                                                                  │
│  If Off-Core-based app (Data Cloud):                            │
│  ├─ List on AppExchange (DC category)                           │
│  ├─ Revenue share: 75% to you, 25% to Salesforce                │
│  ├─ Customer needs: Salesforce + Data Cloud license             │
│  └─ Opportunity: Fewer competitors (newer platform)             │
│                                                                  │
│  If OEM (white-labeled):                                         │
│  ├─ Buy Salesforce credits/licenses in bulk                     │
│  ├─ Embed invisibly in your product                             │
│  └─ Charge customers your own price                             │
│                                                                  │
│  Activity: Review Section 2 (Business Models) of this guide     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Visual 7: Mental Model Summary (The "Aha!" Moment)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE SIMPLE MENTAL MODEL                              │
└─────────────────────────────────────────────────────────────────────────┘

Think of a Restaurant:

┌──────────────────────────────────┐
│      FRONT OF HOUSE (Core)       │
│                                  │
│  🧑‍💼 Customers (users)            │
│  📋 Orders (CRM records)         │
│  💳 Payments (transactions)      │
│  ⏱️ Fast service (<100ms)        │
│                                  │
│  Purpose: Serve customers NOW    │
└──────────────────────────────────┘
           │
           │ Orders flow to kitchen
           │ (Zero-ETL sync)
           ▼
┌──────────────────────────────────┐
│   BACK OF HOUSE (Off-Core / DC)  │
│                                  │
│  👨‍🍳 Chefs (data scientists)       │
│  📊 Inventory analytics          │
│  🤖 Recipe optimization (AI)     │
│  📈 Predict demand (ML)          │
│                                  │
│  Purpose: Optimize & innovate    │
└──────────────────────────────────┘
           │
           │ Insights flow back
           │ (Activation)
           ▼
┌──────────────────────────────────┐
│      FRONT OF HOUSE (Core)       │
│                                  │
│  "Tonight's special: Sea bass"   │
│  (AI recommendation on menu)     │
└──────────────────────────────────┘


KEY INSIGHT:
• Core = Customer-facing, fast, transactional
• Off-Core = Behind-the-scenes, analytical, AI-powered
• Together = Complete system (serve customers + learn from data)


FOR ISVs:
• Build on Core if your app is part of the "dining experience"
  (menus, payment, reservations)
• Build on Off-Core if your app is part of the "kitchen intelligence"
  (inventory prediction, recipe optimization, food safety AI)
• Build on Both if you need the full system
  (restaurant management suite: orders + analytics)
```

---

## Quick Reference: Core vs Off-Core Cheat Sheet

| Feature | Salesforce Core | Data Cloud (Off-Core) |
|---------|----------------|----------------------|
| **What is it?** | CRM database | Data lake + CDP + AI platform |
| **Primary users** | Sales, service, marketing ops | Data scientists, AI engineers, analysts |
| **Data types** | Structured (fields, objects) | Structured + unstructured (PDFs, vectors) |
| **Storage** | Gigabytes to terabytes | Terabytes to petabytes |
| **Speed** | <100ms (real-time) | Seconds (batch/streaming) |
| **Use cases** | Create leads, log calls, update opportunities | Analyze trends, train ML models, search docs |
| **Query language** | SOQL | SQL, vector search |
| **UI** | Lightning (web/mobile) | Tableau, SQL clients, APIs |
| **When to use** | Building CRM features | Building analytics/AI features |
| **ISV examples** | DocuSign, CPQ, Copado | Gong, Segment, Tableau CRM |

---

## Next Steps: Hands-On Practice

### Exercise 1: Developer Org Exploration (30 min)
1. Sign up: https://developer.salesforce.com/signup
2. Create an Account, add fields
3. Build a simple Flow (automation)
4. Notice: You're in "Core" - everything is transactional, real-time

### Exercise 2: Data Cloud Trial (1 hour)
1. Request Data Cloud trial from your Salesforce team
2. Ingest sample CSV data (external source)
3. Create a unified profile
4. Activate insights back to Core
5. Notice: You're in "Off-Core" - analytical, batch-oriented

### Exercise 3: Case Study Analysis (30 min)
Pick an ISV app from AppExchange:
- Is it Core, Off-Core, or Hybrid?
- What data does it use?
- Why did they choose that architecture?

Examples:
- **DocuSign** → Core (needs Opportunity object, real-time signatures)
- **Gong.io** → Off-Core (call recordings, AI analysis)
- **Certinia** → Hybrid (ERP transactions in Core, reporting in Off-Core)

---

## Conclusion: The Power of the Platform

Salesforce is unique because **Core + Off-Core together** create an end-to-end platform:

1. **Capture** (Core): Users enter data in CRM
2. **Enrich** (Off-Core): AI analyzes external + unstructured data
3. **Activate** (Core): Insights surface to users in real-time
4. **Act** (Core): Users take action (send email, close deal)

This cycle is **why ISVs choose Salesforce**:
- Not just a database (like PostgreSQL)
- Not just a data lake (like Snowflake)
- **Both** - in one platform, zero-ETL

Your role as a PM: **Understand where your product fits in this cycle**.

---

*Created: 2025-11-09*
*For: Salesforce Product Managers*
*Next: Read SALESFORCE_ISV_ECOSYSTEM_GUIDE.md for business models*
