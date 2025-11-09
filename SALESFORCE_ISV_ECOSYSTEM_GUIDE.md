# Salesforce ISV Ecosystem Guide
## A Comprehensive Guide for Product Managers

---

## Table of Contents
1. [Partner Types Overview](#1-partner-types-overview)
2. [Business Models & Revenue Flows](#2-business-models--revenue-flows)
3. [AppExchange Revenue Share Model](#3-appexchange-revenue-share-model)
4. [OEM & Credit Models](#4-oem--credit-models)
5. [Top AppExchange Apps](#5-top-appexchange-apps)
6. [Case Studies](#6-case-studies)
7. [Data Cloud for ISVs](#7-data-cloud-for-isvs)
8. [Core vs Off-Core Architecture](#8-core-vs-off-core-architecture)
9. [Technology Stack for ISVs](#9-technology-stack-for-isvs)
10. [Learning Roadmap](#10-learning-roadmap)

---

## 1. Partner Types Overview

### 🧭 At a Glance Comparison

| Partner Type | What They Do | Value Add | Salesforce Role | Revenue Model | Examples |
|-------------|-------------|-----------|----------------|---------------|----------|
| **ISV (Independent Software Vendor)** | Build & sell apps on AppExchange | Packaged solutions, IP, vertical specialization | Platform provider, infrastructure | App licenses, subscriptions, % revenue share | Salesforce (own apps), Copado, Certinia, Conga, DocuSign, MuleSoft (pre-acquisition) |
| **SI (System Integrator)** | Implement & customize Salesforce | Services, consulting, custom development | Platform + consulting partner | Professional services (hourly/project) | Accenture, Deloitte, PwC, Slalom, Cognizant |
| **OEM (Original Equipment Manufacturer)** | Embed Salesforce into their product | White-label, bundled offering | Embedded platform | Bulk licensing, usage-based credits | AWS (Amazon Connect + Salesforce), Zoom (Zoom for Salesforce), Google (Workspace integrations) |
| **Reseller** | Sell Salesforce licenses + basic setup | Geographic reach, local support | Distribution channel | License markup (10-20%), implementation fees | Local consulting firms, regional VARs, NTT Data, Fujitsu (Japan), Tata Consultancy Services |

---

## 2. Business Models & Revenue Flows

### 2.1 ISV Model (AppExchange)

```
┌──────────────┐
│   CUSTOMER   │
└──────┬───────┘
       │ $100/month app subscription
       ▼
┌──────────────────────────────────────────────────────┐
│              SALESFORCE APPEXCHANGE                   │
│  (Handles billing, collections, compliance)          │
└──────┬────────────────────────────────┬──────────────┘
       │                                │
       │ $75 (75% revenue share)        │ $25 (25% platform fee)
       ▼                                ▼
┌──────────────┐                 ┌──────────────┐
│     ISV      │                 │  SALESFORCE  │
│   (Copado)   │                 │              │
└──────────────┘                 └──────────────┘

Key Points:
• AppExchange handles: billing, tax, compliance, payments
• ISV gets: 75-85% of list price (depending on deal structure)
• Salesforce gets: 15-25% platform fee
• Customer needs: Active Salesforce org + valid license
```

### 2.2 OEM Embedded Model

```
┌──────────────┐
│   CUSTOMER   │
│ (End User)   │
└──────┬───────┘
       │ $500/month (bundled price)
       │ Customer doesn't see "Salesforce"
       ▼
┌──────────────────────────────────────────────────────┐
│           OEM PARTNER (e.g., FinTech App)            │
│  • White-labeled Salesforce embedded inside          │
│  • Branded as "FinTech CRM" not "Salesforce"         │
│  • Uses Salesforce APIs, database, security          │
└──────┬───────────────────────────────────────────────┘
       │ Usage-based credits or bulk licensing
       │ Example: $200/month royalty to Salesforce
       ▼
┌──────────────────────────────────────────────────────┐
│                    SALESFORCE                        │
│  • Provides: Platform, infrastructure, credits       │
│  • Gets: Royalty per user OR consumption credits     │
└──────────────────────────────────────────────────────┘

Credit Flow (OEM Embedded):
┌──────────────┐
│   OEM        │ Buys 1M API credits upfront ($10k)
│   Partner    │ Sells to 100 customers
└──────┬───────┘
       │
       │ Credits consumed per customer:
       │ • API calls: 5,000/month per customer
       │ • Data storage: 10GB per customer
       │ • Einstein predictions: 1,000/month
       ▼
┌──────────────┐
│ SALESFORCE   │ Tracks consumption
│ PLATFORM     │ Auto-replenishes when 80% used
└──────────────┘

Who Pays?
• OEM partner pays for credits upfront
• OEM bundles cost into their product pricing
• Customer pays OEM, not Salesforce directly
```

### 2.3 SI (System Integrator) Model

```
┌──────────────┐
│   CUSTOMER   │
└──────┬───────┘
       │
       ├─────────────────────┬──────────────────────┐
       │                     │                      │
       │ $50k/month          │ $100k project        │
       │ (licenses)          │ (implementation)     │
       ▼                     ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  SALESFORCE  │      │      SI      │      │  SALESFORCE  │
│   (direct)   │      │  (Accenture) │      │  (referral   │
│              │      │              │      │   fee 10-15%)│
└──────────────┘      └──────────────┘      └──────────────┘

Key: SI makes money from services, not software
```

### 2.4 Reseller Model

```
┌──────────────┐
│   CUSTOMER   │
│ (Japan)      │
└──────┬───────┘
       │ $120/user/month (marked up price)
       ▼
┌──────────────────────────────────────────────────────┐
│        RESELLER (e.g., Fujitsu Japan)                │
│  • Local language support                            │
│  • Regional implementation                           │
│  • Buys licenses bulk from Salesforce                │
└──────┬───────────────────────────────────────────────┘
       │ $100/user/month (wholesale price)
       ▼
┌──────────────┐
│  SALESFORCE  │ Margin: $20/user/month for reseller
└──────────────┘
```

---

## 3. AppExchange Revenue Share Model

### 3.1 Standard Revenue Share

| Listing Type | ISV Gets | Salesforce Gets | Notes |
|-------------|----------|-----------------|-------|
| **Paid Apps** | 75% | 25% | Most common model |
| **High-volume deals** | Up to 85% | 15% | Negotiated for strategic partners |
| **Free Apps** | N/A | N/A | ISV monetizes separately (freemium, upsell) |
| **Private Listings** | Custom | Custom | Enterprise-specific pricing |

### 3.2 What Salesforce Provides for 25%

```
┌─────────────────────────────────────────────────────┐
│         AppExchange Platform Services               │
├─────────────────────────────────────────────────────┤
│ ✓ Billing & Payment Processing                     │
│ ✓ Tax Compliance (VAT, GST, sales tax)             │
│ ✓ Currency Conversion (180+ countries)             │
│ ✓ Security Review & Trust Verification             │
│ ✓ Marketing (Featured listings, events)            │
│ ✓ Discovery (Search, recommendations)              │
│ ✓ License Management (LMO - License Management Org)│
│ ✓ Upgrade/Downgrade Handling                       │
│ ✓ Customer Support Portal Integration              │
└─────────────────────────────────────────────────────┘
```

### 3.3 Pricing Models on AppExchange

1. **Per User/Month**: $50/user/month (e.g., Copado)
2. **Tiered Pricing**: Starter ($1k), Pro ($5k), Enterprise ($15k)
3. **Usage-Based**: API calls, storage, transactions
4. **Freemium**: Free base + paid premium features
5. **One-Time License**: $10k perpetual (rare now)

---

## 4. OEM & Credit Models

### 4.1 OEM Embedded License (Platform License)

```
Traditional Salesforce License:
┌─────────────────────────────────┐
│  Customer sees "Salesforce" UI  │
│  Tabs, Objects, Reports         │
│  Full Salesforce branding       │
└─────────────────────────────────┘
    Customer pays Salesforce directly


OEM Embedded License:
┌─────────────────────────────────┐
│  Custom branded UI              │
│  "FinTech CRM" (white-labeled)  │
│  No Salesforce branding         │
│  Uses SF backend invisibly      │
└─────────────────────────────────┘
    Customer pays OEM Partner
    OEM pays Salesforce royalties
```

### 4.2 Credit Consumption Model

| Resource | Credit Cost | Example |
|----------|-------------|---------|
| API Calls | 1 credit per 1,000 calls | Mobile app sync |
| Data Storage | 100 credits per GB/month | Customer records |
| File Storage | 50 credits per GB/month | Attachments |
| Einstein Predictions | 10 credits per 1,000 predictions | AI scoring |
| Data Cloud Events | 5 credits per 100k events | Streaming data |

**Who Pays Credits?**

```
Scenario 1: OEM Embedded App
┌──────────────┐
│     OEM      │ Buys credits, bundles into pricing
└──────┬───────┘
       │ Consumes credits for all customers
       ▼
┌──────────────┐
│  Salesforce  │ Bills OEM monthly based on usage
└──────────────┘

Scenario 2: ISV App (Customer has Salesforce)
┌──────────────┐
│   Customer   │ Already has Salesforce license
└──────┬───────┘
       │ Credit usage tied to existing org
       ▼
┌──────────────┐
│  Salesforce  │ Credits come from customer's allocation
└──────────────┘
       ▲
       │ ISV app adds functionality
       │
┌──────────────┐
│     ISV      │ Doesn't pay for credits (customer does)
└──────────────┘
```

---

## 5. Top AppExchange Apps

### 5.1 Overall Top Apps (All Categories)

| App | Category | What It Does | Business Model |
|-----|----------|--------------|----------------|
| **Salesforce CPQ** | Sales | Configure-Price-Quote automation | Native, bundled with Sales Cloud |
| **Conga Composer** | Document Gen | Contract & document automation | Per user/month ($40-80) |
| **DocuSign** | E-Signature | Electronic signatures & CLM | Per user/month ($25-50) |
| **Gong.io** | Revenue Intel | Call recording, AI analysis | Enterprise pricing ($1k+/mo) |
| **Pardot (Marketing Cloud)** | Marketing | B2B marketing automation | Native, bundled ($1,250/mo) |
| **Certinia (FinancialForce)** | ERP/PSA | Financial mgmt, project accounting | Per user/month ($100-200) |
| **Copado** | DevOps | CI/CD for Salesforce | Tiered pricing ($10k-100k/year) |
| **Vlocity (Industries)** | Industry Solutions | Vertical apps (now owned by SF) | Native |
| **Tableau CRM (Einstein Analytics)** | Analytics | BI & dashboards | Per user/month ($75-150) |
| **Workday HCM** | HR/Finance | Integration with Salesforce | Separate Workday license |

### 5.2 Top Apps for Agentic AI

| App | What It Does | AI Capability |
|-----|--------------|---------------|
| **Einstein Copilot** | Native Salesforce AI agent | Grounded in CRM data, conversational |
| **Gong Revenue AI** | Sales call intelligence | Auto-logs calls, surfaces insights |
| **Drift Conversational AI** | Chatbot, conversational marketing | Lead qualification, routing |
| **6sense Revenue AI** | Predictive pipeline | Intent data, account scoring |
| **Chorus.ai** | Conversation intelligence | Real-time call coaching |
| **People.ai** | Revenue operations AI | Auto-capture, forecasting |
| **Cresta** | Contact center AI | Agent assist, real-time guidance |
| **Anthropic Claude (via API)** | Generative AI integration | Custom AI workflows |

### 5.3 Top Apps for Data Cloud

| App | What It Does | Data Cloud Integration |
|-----|--------------|------------------------|
| **Snowflake Connector** | Zero-ETL data sharing | Direct Snowflake → Data Cloud sync |
| **MuleSoft Anypoint** | API-led integration | Streams data to Data Cloud |
| **Informatica** | Data integration & quality | Cleanses data pre-ingestion |
| **Segment (Twilio)** | Customer data platform | Real-time event streaming |
| **Google BigQuery Connector** | Data warehouse integration | Bi-directional sync |
| **AWS Data Exchange** | Third-party data | Enrichment (demographic, firmographic) |
| **Amperity** | Customer identity resolution | Unified profile building |
| **Treasure Data** | Enterprise CDP | Event streaming, ML models |
| **Monte Carlo** | Data observability | Data quality monitoring |
| **Hightouch** | Reverse ETL | Activates Data Cloud insights → tools |

---

## 6. Case Studies

### 6.1 Copado: ISVforce DevOps Platform

**Company Profile**
- **Founded**: 2013
- **Category**: DevOps & Release Management for Salesforce
- **Business Model**: ISV (AppExchange)
- **Customers**: 1,000+ enterprises (Coca-Cola, Walmart, ADP)

**ISVforce Strategy**

```
┌─────────────────────────────────────────────────────┐
│                 COPADO ARCHITECTURE                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Copado App (Managed Package on AppExchange)       │
│         │                                           │
│         ├─ Native Salesforce Objects (Apex, LWC)   │
│         ├─ Custom UI on Salesforce platform        │
│         ├─ Git Integration (external API)          │
│         └─ CI/CD Engine (Heroku)                   │
│                                                     │
│  Revenue Model:                                     │
│  • Tiered: Starter ($10k/yr), Pro ($50k/yr),       │
│            Enterprise ($100k+/yr)                   │
│  • Per-sandbox pricing                             │
│  • AppExchange 75% revenue share                   │
│                                                     │
│  Why ISVforce?                                      │
│  ✓ Runs natively in customer's Salesforce org      │
│  ✓ No external infrastructure for customer         │
│  ✓ Seamless upgrades (push upgrades)               │
│  ✓ Trusted on AppExchange                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Technical Architecture**

```
Customer's Salesforce Org
┌─────────────────────────────────────────┐
│  Production Org                         │
│  ├─ Copado Deployer (Managed Package)  │
│  ├─ Custom Metadata for config          │
│  └─ Connected to Git (GitHub/Bitbucket) │
└─────────────────────────────────────────┘
        │
        │ Push/Pull metadata
        ▼
┌─────────────────────────────────────────┐
│  External Systems (Copado Backend)      │
│  ├─ Heroku (CI/CD runners)              │
│  ├─ AWS (storage)                       │
│  └─ Git repos (source control)          │
└─────────────────────────────────────────┘
```

**Value Proposition**
- **For Customers**: CI/CD without hiring DevOps engineers
- **For Salesforce**: Increases platform stickiness, enterprise adoption
- **For Copado**: Recurring revenue, embedded in customer workflow

**ISV Journey**
1. **2013-2015**: Built managed package, listed on AppExchange
2. **2016-2018**: Security review, enterprise features (compliance, audit)
3. **2019-2021**: Scaled to enterprise (Coca-Cola, Fortune 500)
4. **2022-2024**: Acquired by Qentelli, expanded to multi-cloud DevOps

---

### 6.2 Certinia (FinancialForce): ERP on Force.com

**Company Profile**
- **Founded**: 2009 (as FinancialForce, rebranded 2022)
- **Category**: ERP, PSA (Professional Services Automation), Accounting
- **Business Model**: ISV (AppExchange)
- **Customers**: 2,000+ (Alight Solutions, Jobvite, New Relic)

**ISVforce Strategy**

```
┌─────────────────────────────────────────────────────┐
│              CERTINIA ARCHITECTURE                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Certinia ERP Suite (100% Native on Salesforce)    │
│                                                     │
│  ┌────────────────┐  ┌────────────────┐            │
│  │  Accounting    │  │  PSA           │            │
│  │  - GL, AP, AR  │  │  - Projects    │            │
│  │  - Billing     │  │  - Timesheets  │            │
│  └────────────────┘  └────────────────┘            │
│                                                     │
│  ┌────────────────┐  ┌────────────────┐            │
│  │  Revenue Mgmt  │  │  Supply Chain  │            │
│  │  - ASC 606     │  │  - Inventory   │            │
│  └────────────────┘  └────────────────┘            │
│                                                     │
│  Built On:                                          │
│  • Apex (business logic)                           │
│  • Lightning Web Components (UI)                   │
│  • Platform Events (real-time)                     │
│  • Salesforce Objects (custom + standard)          │
│                                                     │
│  Why 100% Native?                                   │
│  ✓ Single source of truth (CRM + ERP)              │
│  ✓ No data sync (real-time)                        │
│  ✓ Unified security model                          │
│  ✓ One login, one UI                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Revenue Model**

```
┌──────────────┐
│   Customer   │ Services company (consulting, IT services)
│ (e.g., Alight│ Needs: CRM + ERP + project accounting
│  Solutions)  │
└──────┬───────┘
       │
       │ $150/user/month (Certinia ERP + PSA)
       │ + $150/user/month (Salesforce Sales Cloud)
       │ Total: $300/user/month × 1,000 users = $300k/month
       │
       ├────────────────────┬────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐    ┌──────────────┐
│   Certinia   │     │  Salesforce  │    │  Salesforce  │
│              │     │ (AppExchange │    │   (Sales     │
│ $112.5k/mo   │     │    25%)      │    │    Cloud)    │
│ (75% of $150k)│     │ $37.5k/mo    │    │  $150k/mo    │
└──────────────┘     └──────────────┘    └──────────────┘

Key Insight:
• Customer pays Salesforce directly for Sales Cloud
• Customer pays via AppExchange for Certinia (Salesforce takes 25%)
• Total Salesforce revenue: $187.5k/month
• Certinia revenue: $112.5k/month
```

**Data Model Integration**

```
Salesforce Standard Objects        Certinia Custom Objects
┌────────────────┐                 ┌────────────────┐
│  Account       │◄────────────────│  c2g__Invoice  │
│  Opportunity   │                 │  c2g__GL_Acct  │
│  Contact       │                 │  pse__Project  │
└────────────────┘                 └────────────────┘
        │                                  │
        │  Shared data model (no ETL)     │
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
              ┌────────────────┐
              │  Unified View  │
              │  - Sales       │
              │  - Finance     │
              │  - Projects    │
              └────────────────┘
```

**ISV Journey**
1. **2009**: Founded by former Salesforce execs
2. **2011**: First accounting app on AppExchange
3. **2015**: Added PSA (professional services automation)
4. **2020**: 2,000+ customers, $200M+ ARR
5. **2022**: Rebranded to Certinia, expanded industry verticals

**Why Certinia Chose ISVforce**
- **Platform leverage**: No infrastructure costs (runs on Force.com)
- **Market access**: AppExchange distribution
- **Trust**: Salesforce security review badge
- **Integration**: Zero-ETL with CRM data

---

## 7. Data Cloud for ISVs

### 7.1 How ISVs Use Data Cloud

```
┌─────────────────────────────────────────────────────┐
│         ISV Use Cases for Data Cloud               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Build CDP Apps                                  │
│     ├─ Ingest external data (web, mobile, IoT)     │
│     ├─ Create unified profiles                     │
│     └─ Activate segments → Marketing Cloud         │
│                                                     │
│  2. Unstructured Data Apps                          │
│     ├─ Ingest PDFs, images, documents              │
│     ├─ Vector embeddings (AI search)               │
│     └─ Semantic search & retrieval                 │
│                                                     │
│  3. Real-Time Analytics Apps                        │
│     ├─ Stream events (clickstream, IoT)            │
│     ├─ Low-latency dashboards                      │
│     └─ Trigger workflows on patterns               │
│                                                     │
│  4. AI/ML Apps                                      │
│     ├─ Feature engineering (Data Cloud)            │
│     ├─ Model training (Einstein, external)         │
│     └─ Predictions → Salesforce actions            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 7.2 ISV Building on Data Cloud: Unstructured Data Example

**Scenario**: ISV builds "Contract Intelligence" app

```
┌─────────────────────────────────────────────────────┐
│  CONTRACT INTELLIGENCE APP (ISV)                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Step 1: Ingest Unstructured Data                  │
│  ┌──────────────────────────────────┐              │
│  │  PDF contracts, Word docs,       │              │
│  │  scanned images                  │              │
│  └────────────┬─────────────────────┘              │
│               │                                     │
│               ▼                                     │
│  Step 2: Data Cloud Unstructured Ingestion         │
│  ┌──────────────────────────────────┐              │
│  │  • Vector embeddings (OpenAI)    │              │
│  │  • Chunking (semantic)           │              │
│  │  • Metadata extraction           │              │
│  └────────────┬─────────────────────┘              │
│               │                                     │
│               ▼                                     │
│  Step 3: Store in Data Cloud Vector DB            │
│  ┌──────────────────────────────────┐              │
│  │  • Contract clauses (vectors)    │              │
│  │  • Linked to Account/Opportunity │              │
│  └────────────┬─────────────────────┘              │
│               │                                     │
│               ▼                                     │
│  Step 4: ISV App Features                          │
│  ┌──────────────────────────────────┐              │
│  │  • Semantic search: "Find all    │              │
│  │    contracts with auto-renewal"  │              │
│  │  • AI summaries (Claude, GPT)    │              │
│  │  • Risk scoring (custom ML)      │              │
│  │  • Alerts → Salesforce Tasks     │              │
│  └──────────────────────────────────┘              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Technical Stack**

```
ISV App Layer (Apex, LWC)
        │
        ▼
Data Cloud APIs
├─ Ingestion API (unstructured)
├─ Query API (vector search)
└─ Activation API (segments → actions)
        │
        ▼
Data Cloud Storage
├─ Vector DB (embeddings)
├─ Data Lake (raw files)
└─ Unified Profile (customer 360)
        │
        ▼
Salesforce Core
├─ Account, Opportunity (linked)
├─ Tasks, Alerts (automated)
└─ Einstein AI (optional)
```

### 7.3 OEM Data Cloud Usage

**Scenario**: FinTech OEM embeds Salesforce + Data Cloud

```
┌──────────────────────────────────────────────────────┐
│         FINTECH OEM (White-labeled Salesforce)       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Customer-Facing Product:                           │
│  "FinTech 360 CRM" (actually Salesforce + DC)       │
│                                                      │
│  ┌────────────────────────────────────────┐         │
│  │  Customer sees:                        │         │
│  │  ├─ Loan applicants (Accounts)         │         │
│  │  ├─ Credit scores (external data)      │         │
│  │  ├─ Fraud alerts (real-time)           │         │
│  │  └─ Risk dashboards                    │         │
│  └────────────────────────────────────────┘         │
│                                                      │
│  Backend (Hidden from Customer):                    │
│  ┌────────────────────────────────────────┐         │
│  │  Salesforce Core:                      │         │
│  │  ├─ Account, Contact, Opportunity      │         │
│  │  ├─ Custom objects (Loan, Application) │         │
│  │                                         │         │
│  │  Data Cloud:                            │         │
│  │  ├─ Ingests credit bureau data (API)   │         │
│  │  ├─ Real-time fraud signals            │         │
│  │  ├─ Unified customer profiles          │         │
│  │  └─ Activates to Sales Cloud (alerts)  │         │
│  └────────────────────────────────────────┘         │
│                                                      │
│  OEM pays Salesforce:                               │
│  • Platform license: $100/user/month                │
│  • Data Cloud credits: $50k/month (ingestion)       │
│  • Total: $150k/month for 1,000 users               │
│                                                      │
│  OEM charges customers:                             │
│  • $250/user/month (includes everything)            │
│  • Margin: $100/user/month                          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 8. Core vs Off-Core Architecture

### 8.1 What is "Core" vs "Off-Core"?

```
┌───────────────────────────────────────────────────────┐
│              SALESFORCE ECOSYSTEM                     │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────┐             │
│  │      SALESFORCE CORE                │             │
│  │   (Transactional Database)          │             │
│  ├─────────────────────────────────────┤             │
│  │                                     │             │
│  │  • CRM Objects                      │             │
│  │    - Account, Contact, Lead         │             │
│  │    - Opportunity, Case, Task        │             │
│  │    - Custom Objects                 │             │
│  │                                     │             │
│  │  • Business Logic                   │             │
│  │    - Apex (code)                    │             │
│  │    - Flow (low-code)                │             │
│  │    - Validation rules               │             │
│  │    - Triggers                       │             │
│  │                                     │             │
│  │  • UI                               │             │
│  │    - Lightning Web Components       │             │
│  │    - Visualforce                    │             │
│  │    - Mobile (Salesforce app)        │             │
│  │                                     │             │
│  │  • Metadata                          │             │
│  │    - Schema (fields, relationships) │             │
│  │    - Permissions, profiles          │             │
│  │    - Workflows, automations         │             │
│  │                                     │             │
│  │  • Security                          │             │
│  │    - User auth, SSO                 │             │
│  │    - Field-level security           │             │
│  │    - Sharing rules                  │             │
│  │                                     │             │
│  │  Optimized for:                     │             │
│  │  ✓ Transactional workloads          │             │
│  │  ✓ CRUD operations                  │             │
│  │  ✓ Real-time UI interactions        │             │
│  │  ✓ Structured relational data       │             │
│  │                                     │             │
│  └─────────────────────────────────────┘             │
│               │                                       │
│               │ Zero-ETL                              │
│               │ (Metadata Link)                       │
│               ▼                                       │
│  ┌─────────────────────────────────────┐             │
│  │      DATA CLOUD (OFF-CORE)          │             │
│  │   (Analytical Data Lake)            │             │
│  ├─────────────────────────────────────┤             │
│  │                                     │             │
│  │  • Unified Customer Profiles        │             │
│  │    - 360° view (all sources)        │             │
│  │    - Identity resolution            │             │
│  │                                     │             │
│  │  • External Data                    │             │
│  │    - Snowflake, BigQuery, S3        │             │
│  │    - Third-party (Experian, etc.)   │             │
│  │    - IoT, clickstream, mobile       │             │
│  │                                     │             │
│  │  • Unstructured Data                │             │
│  │    - PDFs, images, audio            │             │
│  │    - Vector embeddings (AI)         │             │
│  │    - Semantic search                │             │
│  │                                     │             │
│  │  • Real-Time Streaming              │             │
│  │    - Events (low-latency)           │             │
│  │    - Change data capture (CDC)      │             │
│  │                                     │             │
│  │  • AI/ML                            │             │
│  │    - Einstein models                │             │
│  │    - Predictions, scoring           │             │
│  │    - RAG (retrieval-augmented gen)  │             │
│  │                                     │             │
│  │  • Analytics                        │             │
│  │    - Aggregations (billions rows)   │             │
│  │    - Data transforms                │             │
│  │    - Tableau, BI tools              │             │
│  │                                     │             │
│  │  Optimized for:                     │             │
│  │  ✓ Analytical workloads             │             │
│  │  ✓ High-volume data (petabytes)     │             │
│  │  ✓ Unstructured data (AI/ML)        │             │
│  │  ✓ Real-time streaming              │             │
│  │                                     │             │
│  └─────────────────────────────────────┘             │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 8.2 Why Two Systems? (Core vs Off-Core)

| Aspect | Salesforce Core | Data Cloud (Off-Core) |
|--------|-----------------|----------------------|
| **Purpose** | Transactional CRM | Analytical data platform |
| **Data Model** | Relational (normalized) | Denormalized, columnar, vector |
| **Scale** | Millions of records per object | Billions of events, petabytes |
| **Latency** | <100ms (real-time UI) | Seconds (batch, streaming) |
| **Data Types** | Structured (fields, objects) | Structured + unstructured (PDFs, vectors) |
| **Use Case** | Sales, service, marketing ops | Analytics, AI, data science |
| **Query Language** | SOQL (Salesforce Object Query Language) | SQL, vector search |
| **Storage Cost** | Higher (optimized for speed) | Lower (optimized for volume) |

### 8.3 How They Work Together: Zero-ETL

```
Example: Customer 360 View
───────────────────────────────────────────────────────

Step 1: Core data syncs to Data Cloud (automatic)
┌─────────────────┐
│ Salesforce Core │
│  Account:       │
│   - Name: Acme  │
│   - Industry    │
│   - Revenue     │
└────────┬────────┘
         │ Zero-ETL (metadata link)
         │ Happens in background, near real-time
         ▼
┌─────────────────┐
│  Data Cloud     │
│  Profile: Acme  │
│   - Core data   │ ◄──────┐
└─────────────────┘        │
                           │
Step 2: External data ingested
┌─────────────────┐        │
│ External Systems│        │
│  - Website      │        │
│  - Mobile app   │        │
│  - Support chat │        │
└────────┬────────┘        │
         │ API ingestion   │
         ▼                 │
┌─────────────────┐        │
│  Data Cloud     │        │
│  Profile: Acme  │        │
│   - Core data   │◄───────┘ Unified
│   - Web clicks  │
│   - App usage   │
│   - Chat logs   │
└────────┬────────┘
         │
         │ Activation (write back to Core)
         ▼
┌─────────────────┐
│ Salesforce Core │
│  Account: Acme  │
│   + Enriched    │ ◄── ISV app can read this
│   + Segment tag │
│   + AI score    │
└─────────────────┘
```

### 8.4 ISV Decision: Build on Core or Off-Core?

| ISV App Type | Build On | Why |
|-------------|----------|-----|
| **CRM Extension** (e.g., CPQ, DocuSign) | Core (Apex, LWC) | Needs real-time transactional data, UI |
| **Analytics** (e.g., Tableau CRM) | Off-Core (Data Cloud) | Large datasets, BI queries |
| **AI/ML** (e.g., Einstein, Gong) | Off-Core (Data Cloud) | Needs external data, vector search |
| **Unstructured** (e.g., contract AI) | Off-Core (Data Cloud) | PDF/image ingestion, embeddings |
| **Real-Time Events** (e.g., fraud detection) | Off-Core (Data Cloud) | Streaming, low-latency triggers |
| **Hybrid** (e.g., Certinia ERP) | Core (transactional) + Off-Core (reporting) | Best of both |

---

## 9. Technology Stack for ISVs

### 9.1 Core Platform (ISVforce)

```
┌─────────────────────────────────────────────────────┐
│         ISV APP TECHNOLOGY STACK                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Frontend (UI)                                      │
│  ├─ Lightning Web Components (LWC) - modern        │
│  ├─ Aura Components (legacy)                       │
│  ├─ Visualforce (legacy, still used)               │
│  └─ External (React/Angular + APIs)                │
│                                                     │
│  Backend (Business Logic)                           │
│  ├─ Apex (Java-like, native)                       │
│  ├─ Flow (low-code automation)                     │
│  └─ External (Node.js, Python + APIs)              │
│                                                     │
│  Data                                               │
│  ├─ Custom Objects (schema)                        │
│  ├─ Custom Metadata Types (config)                 │
│  └─ Big Objects (high-volume)                      │
│                                                     │
│  Integration                                        │
│  ├─ REST APIs                                       │
│  ├─ SOAP APIs (legacy)                             │
│  ├─ Platform Events (streaming)                    │
│  ├─ Change Data Capture (CDC)                      │
│  └─ External Services (OpenAPI)                    │
│                                                     │
│  Packaging                                          │
│  ├─ Managed Package (AppExchange)                  │
│  ├─ Unlocked Package (modular)                     │
│  └─ Unmanaged Package (source-based)               │
│                                                     │
│  DevOps                                             │
│  ├─ Salesforce CLI (sfdx)                          │
│  ├─ VS Code + Salesforce Extensions                │
│  ├─ Copado, Gearset (CI/CD)                        │
│  └─ Git (GitHub, Bitbucket)                        │
│                                                     │
│  Testing                                            │
│  ├─ Apex Unit Tests (75% code coverage required)   │
│  ├─ LWC Jest Tests                                 │
│  └─ Selenium (UI testing)                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 9.2 Data Cloud Stack

```
┌─────────────────────────────────────────────────────┐
│      DATA CLOUD ISV TECHNOLOGY STACK                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Ingestion                                          │
│  ├─ Data Cloud Connectors (native)                 │
│  │  • Snowflake, BigQuery, S3, etc.                │
│  ├─ MuleSoft (API-led)                             │
│  ├─ Streaming APIs (real-time events)              │
│  └─ Unstructured API (PDFs, images)                │
│                                                     │
│  Storage                                            │
│  ├─ Data Lake (Parquet, columnar)                  │
│  ├─ Vector Database (embeddings)                   │
│  └─ Data Model Objects (DMOs)                      │
│                                                     │
│  Query & Processing                                 │
│  ├─ SQL (ANSI SQL on Data Cloud)                   │
│  ├─ Vector Search (semantic)                       │
│  ├─ Calculated Insights (computed fields)          │
│  └─ Data Transforms (ETL)                          │
│                                                     │
│  AI/ML                                              │
│  ├─ Einstein Studio (bring your own model)         │
│  ├─ Vector embeddings (OpenAI, custom)             │
│  ├─ RAG (retrieval-augmented generation)           │
│  └─ Model serving (real-time predictions)          │
│                                                     │
│  Activation                                         │
│  ├─ Segmentation (audience builder)                │
│  ├─ Activation targets (Marketing Cloud, etc.)     │
│  └─ APIs (write to Salesforce Core)                │
│                                                     │
│  ISV APIs                                           │
│  ├─ Data Cloud REST API                            │
│  ├─ GraphQL (query)                                │
│  └─ Metadata API (schema management)               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 9.3 Example ISV Tech Stack: "Contract Intelligence" App

```
┌─────────────────────────────────────────────────────┐
│  CONTRACT INTELLIGENCE APP - FULL STACK             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Frontend                                           │
│  └─ Lightning Web Component                        │
│     • Contract upload UI                           │
│     • Search interface                             │
│     • Risk dashboard                               │
│                                                     │
│  Salesforce Core (Apex)                            │
│  └─ Custom Objects:                                │
│     • Contract__c (metadata)                       │
│     • ContractClause__c (extracted)                │
│     • RiskAlert__c (AI-generated)                  │
│                                                     │
│  Data Cloud (Off-Core)                             │
│  ├─ Unstructured Ingestion:                        │
│  │  • PDF upload → vector embeddings (OpenAI)      │
│  │  • Store in vector DB                           │
│  ├─ Vector Search:                                 │
│  │  • Query: "auto-renewal clauses"                │
│  │  • Return: top 10 similar chunks                │
│  └─ AI Processing:                                 │
│     • Claude API (summarization)                   │
│     • Custom risk model (scoring)                  │
│                                                     │
│  External Services                                  │
│  ├─ AWS S3 (raw file storage)                      │
│  ├─ OpenAI (embeddings)                            │
│  ├─ Anthropic Claude (AI summaries)                │
│  └─ Heroku (background jobs)                       │
│                                                     │
│  Integration Flow                                   │
│  1. User uploads PDF (LWC)                         │
│  2. Apex → Data Cloud Unstructured API             │
│  3. Data Cloud → OpenAI (embeddings)               │
│  4. Store vectors in Data Cloud                    │
│  5. Apex → vector search query                     │
│  6. Results → Claude (summarize)                   │
│  7. Create RiskAlert__c in Core                    │
│  8. Display in UI (LWC)                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 10. Learning Roadmap

### 10.1 For Product Managers (Your Path)

```
┌─────────────────────────────────────────────────────┐
│           PM LEARNING ROADMAP (4 Weeks)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Week 1: Business Models & Ecosystem                │
│  ├─ Read: AppExchange partner guide                │
│  ├─ Study: Revenue share models (this doc)         │
│  ├─ Exercise: Map 5 ISVs to business models        │
│  └─ Tool: Explore AppExchange listings             │
│                                                     │
│  Week 2: Salesforce Core Fundamentals               │
│  ├─ Trailhead: Admin Beginner trail                │
│  ├─ Hands-on: Create free Developer org            │
│  ├─ Build: Custom object, Apex trigger, Flow       │
│  └─ Tool: Salesforce CLI, VS Code setup            │
│                                                     │
│  Week 3: Data Cloud & Off-Core                      │
│  ├─ Trailhead: Data Cloud basics                   │
│  ├─ Study: Core vs off-core (this doc)             │
│  ├─ Demo: Data Cloud trial org                     │
│  └─ Exercise: Ingest sample data, create profile   │
│                                                     │
│  Week 4: ISV Case Studies & Strategy                │
│  ├─ Analyze: Copado, Certinia (this doc)           │
│  ├─ Research: 3 more ISVs (DocuSign, Conga, Gong)  │
│  ├─ Exercise: Design your own ISV product idea     │
│  └─ Pitch: Present to peers/stakeholders           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 10.2 Hands-On Tools & Demos

| Tool | Purpose | How to Access |
|------|---------|---------------|
| **Developer Org** | Free Salesforce instance | https://developer.salesforce.com/signup |
| **Trailhead** | Guided learning paths | https://trailhead.salesforce.com |
| **AppExchange** | Explore ISV apps | https://appexchange.salesforce.com |
| **Data Cloud Trial** | Test Data Cloud features | Contact Salesforce account team |
| **Salesforce CLI** | Command-line dev tools | `npm install -g @salesforce/cli` |
| **VS Code Extensions** | IDE for Salesforce | Install "Salesforce Extension Pack" |
| **Copado Trial** | ISV app demo | https://www.copado.com/trial |
| **Certinia Demo** | ERP on Salesforce | https://www.certinia.com/demo |

### 10.3 Key Resources

**Official Salesforce**
- ISVforce Guide: https://developer.salesforce.com/docs/atlas.en-us.packagingGuide.meta/packagingGuide/
- Data Cloud Docs: https://help.salesforce.com/s/articleView?id=sf.c360_a_overview.htm
- AppExchange Partner Program: https://partners.salesforce.com/

**Community**
- Salesforce Stack Exchange: https://salesforce.stackexchange.com/
- Trailblazer Community: https://trailhead.salesforce.com/trailblazer-community
- ISV Success Community: (via Salesforce Partner portal)

**Blogs & Videos**
- Salesforce Developers YouTube: https://www.youtube.com/salesforcedevelopers
- Salesforce Admins Podcast: https://admin.salesforce.com/podcast
- Data Cloud Release Notes: (search Salesforce Help)

### 10.4 Your Next Steps

```
Immediate Actions (This Week):
┌─────────────────────────────────────────────────────┐
│  ✓ Review this guide (you're here!)                 │
│  ✓ Sign up for Developer Org                        │
│  ✓ Explore AppExchange (search "Data Cloud")        │
│  ✓ Watch: "What is ISVforce" (YouTube)              │
│  ✓ Read: Copado case study (above)                  │
└─────────────────────────────────────────────────────┘

Medium-Term (This Month):
┌─────────────────────────────────────────────────────┐
│  ✓ Complete Trailhead: "Admin Beginner" trail       │
│  ✓ Build: Simple Apex trigger in Developer Org      │
│  ✓ Study: 3 ISV apps on AppExchange (install demos) │
│  ✓ Request: Data Cloud trial (from your team)       │
│  ✓ Attend: Salesforce webinar on Data Cloud         │
└─────────────────────────────────────────────────────┘

Long-Term (This Quarter):
┌─────────────────────────────────────────────────────┐
│  ✓ Network: Join ISV Success Community              │
│  ✓ Pitch: Your own ISV product idea internally      │
│  ✓ Certification: Consider "App Builder" cert       │
│  ✓ Experiment: Build simple managed package         │
│  ✓ Mentor: Shadow an ISV partner (via Salesforce)   │
└─────────────────────────────────────────────────────┘
```

---

## Appendix: Quick Reference

### A. Revenue Model Cheat Sheet

| Model | ISV Gets | Salesforce Gets | Customer Pays |
|-------|----------|-----------------|---------------|
| **AppExchange (Standard)** | 75% | 25% | Via AppExchange |
| **OEM Embedded** | N/A (OEM partner) | Royalty per user | OEM partner |
| **Private Listing** | Custom | Custom | Direct negotiation |
| **Freemium** | 100% of upsell | 0% (free tier) | ISV directly |

### B. Core vs Off-Core Decision Matrix

| If You Need... | Use... |
|---------------|--------|
| Real-time UI for CRM users | Core (Apex, LWC) |
| Analyze billions of events | Off-Core (Data Cloud) |
| Process PDFs with AI | Off-Core (Data Cloud Unstructured) |
| Store custom CRM fields | Core (Custom Objects) |
| Stream IoT sensor data | Off-Core (Data Cloud Streaming) |
| Trigger workflows on CRM changes | Core (Apex Triggers, Flow) |
| Build customer 360 profiles | Off-Core (Data Cloud CDP) |
| Create custom reports for sales | Core (Reports & Dashboards) |
| Train ML models on external data | Off-Core (Data Cloud + Einstein) |

### C. Partner Type Selector

**Ask yourself:**

1. **Do you build software products?**
   - Yes → ISV or OEM
   - No → SI or Reseller

2. **Is your software a standalone app on AppExchange?**
   - Yes → ISV
   - No → OEM (white-labeled/embedded)

3. **Do you primarily sell services?**
   - Yes → SI
   - No → Reseller (if you sell licenses + light setup)

4. **Do customers see "Salesforce" branding?**
   - Yes → ISV or SI
   - No → OEM

---

## Summary

This guide provides a holistic view of the Salesforce ISV ecosystem:

1. **Partner Types**: ISV, SI, OEM, Reseller (with company examples)
2. **Business Models**: Revenue flows, AppExchange 75/25 split, OEM credits
3. **Top Apps**: General, Agentic AI, Data Cloud categories
4. **Case Studies**: Copado (DevOps ISV), Certinia (ERP ISV)
5. **Data Cloud**: How ISVs/OEMs build on unstructured data, real-time streams
6. **Core vs Off-Core**: When to use transactional CRM vs analytical data platform
7. **Technology Stack**: Apex, LWC, Data Cloud APIs, vector search, AI/ML
8. **Learning Roadmap**: 4-week plan for PMs with hands-on tools

**Key Takeaway**: Salesforce is not just a CRM—it's a platform ecosystem where ISVs build apps (AppExchange), OEMs embed capabilities (white-label), and Data Cloud extends beyond core CRM to analytics, AI, and unstructured data.

As a PM, understanding this ecosystem helps you:
- Evaluate ISV partnerships
- Design products that leverage Salesforce's platform strengths
- Navigate core vs off-core architecture decisions
- Identify market opportunities (e.g., Data Cloud + AI apps)

**Next Step**: Sign up for a Developer Org and start building!

---

*Last Updated: 2025-11-09*
*Version: 1.0*
*Author: Salesforce Product Management Team*
