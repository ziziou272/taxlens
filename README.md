# TaxLens 🔍

**AI-Powered Tax Intelligence for High-Income Tech Professionals**

> Year-round proactive tax planning, not just annual filing.

## 🌐 Live App

**https://taxlens.ziziou.com**

## What is TaxLens?

TaxLens is a **tax planning tool** (not a tax filing tool) designed for tech employees with equity compensation ($200K–$1M+). It helps you:

- **Avoid surprises** – Detect underwithholding before April hits
- **Optimize equity** – RSU/ISO/NSO/ESPP timing and strategies
- **Plan ahead** – What-if scenarios for major decisions
- **Stay alert** – 73+ automated tax red flags

## ✅ Current Status (v0.4.0)

| Component | Status | Details |
|-----------|--------|---------|
| **Tax Engine** | ✅ Live | Federal + CA/NY/WA, AMT, FICA, NIIT, LTCG, equity |
| **API** | ✅ Live | FastAPI on Docker, 11+ endpoints |
| **Flutter Web** | ✅ Live | Dashboard, calculator, scenarios, alerts |
| **Auth** | ✅ Live | Google, Apple, Email via Supabase |
| **Database** | ✅ Live | Supabase Postgres |
| **Tests** | ✅ | 520+ engine tests, 74 auth tests, 82%+ coverage |

## 🧪 How to Test

### 1. Tax Calculator

1. Open **https://taxlens.ziziou.com**
2. You should see the **Dashboard** with a tax calculator
3. Enter income details:
   - Gross income (e.g., `350000`)
   - Filing status (Single, MFJ, etc.)
   - State (CA, NY, WA)
4. Click **Calculate** — results show federal tax, state tax, FICA, effective rate
5. Try different income levels to see bracket changes

**Via API:**
```bash
curl -s https://taxlens.ziziou.com/api/tax/calculate \
  -H "Content-Type: application/json" \
  -d '{"gross_income": 350000, "filing_status": "single", "state": "CA"}' | python3 -m json.tool
```

### 2. Authentication

**Email sign-up:**
1. Click the **Sign In** / profile icon
2. Choose **Sign Up** tab
3. Enter email + password → submit
4. Check email for confirmation link (Supabase sends it)
5. After confirming, sign in with those credentials

**Google sign-in:**
1. Click **Sign in with Google**
2. Complete the Google OAuth flow
3. You should be redirected back to `taxlens.ziziou.com` and logged in

**Apple sign-in:**
1. Click **Sign in with Apple**
2. Complete the Apple ID flow
3. Redirected back and logged in

**After logging in:**
- Profile icon should show your account
- Protected features (save scenarios, alerts profile) become available

### 3. Alerts

1. Open the **Alerts** section from the navigation
2. Run an alert check — the engine scans for red flags:
   - Underwithholding warnings
   - Estimated payment deadlines
   - AMT triggers
   - Wash sale risks

**Via API:**
```bash
curl -s https://taxlens.ziziou.com/api/alerts/check \
  -H "Content-Type: application/json" \
  -d '{"gross_income": 500000, "withholding": 80000, "filing_status": "single", "state": "CA"}' | python3 -m json.tool
```

### 4. What-If Scenarios

1. Open the **Scenarios** section
2. Choose a scenario type (e.g., "RSU Timing", "State Move", "Bonus Timing")
3. Enter parameters (e.g., RSU value, current state, target state)
4. Click **Run** — see side-by-side tax comparison
5. The engine shows which option saves the most in taxes

**Via API:**
```bash
# List available scenario types
curl -s https://taxlens.ziziou.com/api/scenarios/types | python3 -m json.tool

# Run a scenario
curl -s https://taxlens.ziziou.com/api/scenarios/run \
  -H "Content-Type: application/json" \
  -d '{"type": "state_move", "params": {"income": 400000, "from_state": "CA", "to_state": "WA"}}' | python3 -m json.tool
```

### 5. API Direct Testing

```bash
# Health check
curl -s https://taxlens.ziziou.com/api/health | python3 -m json.tool

# Swagger docs (open in browser)
open https://taxlens.ziziou.com/api/docs

# Tax calculation
curl -s https://taxlens.ziziou.com/api/tax/calculate \
  -H "Content-Type: application/json" \
  -d '{"gross_income": 250000, "filing_status": "married_filing_jointly", "state": "NY"}' | python3 -m json.tool

# Alert check
curl -s https://taxlens.ziziou.com/api/alerts/check \
  -H "Content-Type: application/json" \
  -d '{"gross_income": 300000, "withholding": 50000, "filing_status": "single", "state": "CA"}' | python3 -m json.tool
```

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    taxlens.ziziou.com                      │
│              (Cloudflare Tunnel → port 8102)               │
├──────────────────────────────────────────────────────────┤
│  Caddy Reverse Proxy (port 8102)                          │
│   /api/* → FastAPI backend (Docker, port 8100)            │
│   /*     → Flutter web (Python HTTP, port 8101)           │
├──────────────────────────────────────────────────────────┤
│  FastAPI Backend          │  Flutter Web Frontend          │
│  • Tax engine             │  • Dashboard + Calculator      │
│  • Alerts engine          │  • Auth screens (login/signup) │
│  • What-if scenarios      │  • Scenarios UI                │
│  • User management        │  • Alerts UI                   │
│  • Supabase JWT auth      │  • Supabase Auth SDK           │
├──────────────────────────────────────────────────────────┤
│  Supabase (kccgncphhzodneomimzt)                          │
│  • Postgres database                                       │
│  • Auth (Google, Apple, Email)                             │
│  • Row Level Security                                      │
└──────────────────────────────────────────────────────────┘
```

## Quick Start (Local Development)

### Engine CLI
```bash
cd packages/engine
pip install -e ".[dev]"
taxlens calculate --income 300000 --filing-status single --state CA
```

### API Server
```bash
cd packages/api
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8100
# Docs at http://localhost:8100/docs
```

### Flutter Web
```bash
cd packages/flutter_app
flutter pub get
flutter run -d chrome \
  --dart-define=SUPABASE_URL=https://kccgncphhzodneomimzt.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=<your-anon-key>
```

## Project Structure

```
taxlens/
├── packages/
│   ├── engine/          # Python tax calculation engine (520+ tests)
│   ├── api/             # FastAPI backend (Docker deployed)
│   └── flutter_app/     # Flutter web frontend
│       └── lib/
│           ├── core/providers/  # auth_provider.dart, etc.
│           └── features/
│               ├── auth/        # login, signup, MFA, profile, settings
│               ├── dashboard/   # tax calculator
│               ├── scenarios/   # what-if engine UI
│               └── alerts/      # red flag alerts UI
├── CHANGELOG.md
├── DECISIONS.md
└── ROADMAP.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Engine | Python 3.11+, Decimal arithmetic |
| API | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Flutter 3.x (Web) |
| Database | Supabase Postgres |
| Auth | Supabase Auth (Google, Apple, Email) |
| Hosting | Docker + systemd + Cloudflare Tunnel |

## 🚀 Deployment

The app is deployed on a VPS behind Cloudflare Tunnel:

- **Backend**: `docker run --network host -p 8100:8100 taxlens-api`
- **Frontend**: Flutter web build served by `python3 -m http.server 8101` (systemd: `taxlens-web.service`)
- **Reverse Proxy**: Caddy on port 8102
- **Tunnel**: Cloudflare routes `taxlens.ziziou.com` → `localhost:8102`

### Rebuild & Deploy Frontend
```bash
cd packages/flutter_app
flutter build web --release \
  --dart-define=SUPABASE_URL=https://kccgncphhzodneomimzt.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=<your-anon-key>
sudo systemctl restart taxlens-web
```

## License

MIT

---

**Disclaimer:** TaxLens is a planning tool, not tax advice. Always consult a CPA for filing.
