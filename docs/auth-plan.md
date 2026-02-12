# TaxLens Authentication & User Accounts Plan

## 1. Do We Need Accounts?

**Yes, absolutely.** Here's why:

- **Data persistence** — Users input complex tax scenarios (salary, RSUs, ISOs, ESPP, multiple states). Without accounts, they re-enter everything each session. That's a dealbreaker for a tool handling $200K-$1M+ earners
- **Document storage** — OCR'd W-2s, 1099-Bs, brokerage statements need to persist
- **Plaid integration** — Already wired up with `get_current_user()` dependency. Account linking is meaningless without real user identity
- **Alert system** — Tax deadline alerts, AMT threshold warnings need a user to notify
- **Competitive necessity** — Every competitor requires accounts (see below)

**But: offer a "try without account" mode**
- Let users explore the tax calculator and what-if scenarios with sample data or manual input
- Show a "Save your work — create an account" prompt when they try to save, upload docs, or link Plaid
- This reduces friction and lets people see value before committing
- Technically: keep the `anonymous` user stub but gate persistence/Plaid/docs behind real auth

---

## 2. Competitor Analysis

**TurboTax (Intuit)**
- Email/password + phone/email as user ID
- Mandatory 2FA (SMS or authenticator app)
- Recently added passkey support
- Account required before any tax work begins

**H&R Block**
- Email/password with optional social login (Google)
- 2FA via SMS
- Account required upfront

**Wealthfront / Betterment**
- Email/password + mandatory 2FA
- Some support Google/Apple OAuth
- Heavy KYC (SSN, address verification) since they're financial institutions

**Harness Wealth / Carta Tax**
- Google OAuth + email/password
- Target the same tech equity audience as TaxLens
- Carta uses existing Carta account (SSO)

**Key takeaway:** Every tax/finance tool requires accounts. The standard is email/password + 2FA. OAuth (Google) is increasingly common. Nobody does "anonymous-only."

---

## 3. Auth Approach Comparison

**Email/Password**
- ✅ Universal, everyone understands it
- ✅ Works offline, no third-party dependency
- ❌ Password management burden
- ❌ You handle password hashing, reset flows, breach monitoring
- Verdict: Must-have as a baseline

**Magic Link (passwordless email)**
- ✅ No passwords to manage
- ✅ Great UX for infrequent-use tools
- ❌ Depends on email delivery speed
- ❌ Annoying for frequent users (check email every time)
- Verdict: Good secondary option, not primary

**OAuth (Google/Apple)**
- ✅ One-click signup, lowest friction
- ✅ Tech professionals overwhelmingly have Google accounts
- ✅ Apple Sign-In required for iOS App Store if you offer any social login
- ❌ Dependency on third-party providers
- Verdict: **Primary recommended approach** for this audience

**Passkeys**
- ✅ Most secure, phishing-resistant
- ✅ Growing support (Apple, Google, 1Password)
- ❌ Still confusing for many users
- ❌ Flutter support is maturing but not bulletproof
- Verdict: Add later as an enhancement, not launch requirement

**Recommended combo: Google OAuth + Apple Sign-In + email/password fallback**
- Covers 95%+ of the target audience
- Google OAuth will be the most-used option for tech workers
- Email/password as fallback for enterprise users with restricted OAuth
- Add MFA (TOTP) for email/password users handling sensitive financial data

---

## 4. Tech Stack Recommendation: **Supabase Auth**

### Why Supabase Auth wins for TaxLens

**vs Firebase Auth**
- Firebase: free up to 50K MAU, then $0.0055/MAU
- Supabase: free up to 50K MAU, included in $25/mo Pro plan beyond that
- Supabase has a proper Postgres DB (you already use SQLAlchemy — natural fit)
- Firebase locks you into Firestore/RTDB which conflicts with your existing SQLite/Postgres setup
- Supabase has better self-hosting story if you need it later

**vs Auth0**
- Auth0: free up to 25K MAU, then $240/mo minimum
- Overkill for a startup. Enterprise features you don't need yet
- Verdict: too expensive, too complex

**vs Clerk**
- Clerk: free up to 10K MAU, then $0.02/MAU ($25 for 10K, $250 for 100K)
- Beautiful pre-built UI components — but mostly for React/Next.js
- Flutter SDK is community-maintained, not official
- Verdict: wrong ecosystem

**vs Custom JWT**
- Full control, no vendor lock-in
- But: you build password hashing, token refresh, OAuth flows, email verification, MFA yourself
- Verdict: unnecessary complexity when Supabase gives you all this free

### Supabase Auth specifics
- **Flutter SDK**: `supabase_flutter` — official, well-maintained, 1000+ GitHub stars
- **FastAPI integration**: Validate Supabase JWTs with `python-jose` — ~20 lines of code
- **Built-in support for**: Google OAuth, Apple Sign-In, email/password, magic link, phone OTP
- **Row Level Security (RLS)**: Can enforce data isolation at the DB level
- **Free tier**: 50K MAU, unlimited API requests, 1GB storage
- **Pro tier**: $25/mo, 100K MAU, 8GB storage

### Integration architecture
```
Flutter App
  ↓ (Supabase Flutter SDK handles auth UI + token management)
Supabase Auth (hosted)
  ↓ (issues JWT)
Flutter App sends JWT in Authorization header
  ↓
FastAPI backend validates JWT, extracts user_id
  ↓
Your existing SQLAlchemy models (keyed by user_id from Supabase)
```

- Supabase handles: signup, login, OAuth, token refresh, email verification, password reset
- Your backend handles: business logic, tax calculations, data storage
- User records in your DB link to Supabase user IDs

---

## 5. Data Model — What Gets Stored Per User

**User table** (already exists, needs expansion)
- `id` — Supabase auth user UUID (primary key)
- `email` — from Supabase
- `name` — from Supabase/OAuth profile
- `created_at` — timestamp
- `last_login` — timestamp
- `subscription_tier` — free/pro/premium (future)
- `onboarding_complete` — boolean

**Tax Profile** (already exists)
- Filing status, state, dependents
- W-2 income, RSU/ISO/ESPP details
- Linked to user_id

**Documents** (already exists)
- Uploaded W-2s, 1099s, brokerage statements
- OCR results, extracted data
- File stored in Supabase Storage (encrypted at rest)
- Metadata in your DB

**Scenarios** (already exists)
- What-if scenario configs and results
- Linked to user_id

**Equity Grants** (already exists)
- RSU vesting schedules, ISO exercise plans, ESPP lots
- Linked to user_id

**Alert Preferences** (new)
- `user_id`, `alert_type`, `enabled`, `threshold`, `notify_method`
- Types: AMT warning, estimated tax due dates, RSU vesting reminders, tax bracket alerts

**Sessions/Audit Log** (new, for security)
- `user_id`, `action`, `ip_address`, `timestamp`
- Track: login, data export, document upload, Plaid link

---

## 6. Privacy & Compliance

### What's required for tax data

**This is sensitive financial PII.** Minimum security bar:

- **Encryption at rest** — All stored tax data, documents, and PII must be encrypted. Supabase Storage and managed Postgres both provide this by default
- **Encryption in transit** — HTTPS everywhere (already done via your deployment)
- **Access control** — Users can only see their own data. Enforce at API level AND database level (RLS)
- **Data deletion** — Users must be able to delete their account and all associated data (CCPA requirement for CA residents, which is most of your target audience)
- **No SSN storage** — Do NOT store Social Security Numbers. If OCR extracts them, redact immediately. You don't need them for tax calculations
- **Document retention policy** — Auto-delete uploaded documents after 7 years (IRS audit window) or on user request
- **Audit logging** — Log who accessed what and when

### Regulatory considerations

- **CCPA/CPRA** — California privacy law. Required if you have CA users (you will). Need: privacy policy, data deletion rights, disclosure of data collected
- **SOC 2** — Not legally required but expected by high-income users trusting you with financial data. Consider pursuing later (Year 2+)
- **GLBA** — Gramm-Leach-Bliley Act applies if you're a "financial institution." Tax prep software is borderline. Consult a lawyer before launch
- **No HIPAA** — Not applicable (no health data)
- **PCI DSS** — Only if you process payments. Use Stripe and it's handled

### Minimum launch requirements
- Privacy policy on the website
- Terms of service
- Data deletion endpoint (`DELETE /api/users/me`)
- HTTPS (already done)
- No SSN storage
- Encrypted storage (Supabase default)
- Per-user data isolation (enforce in `get_current_user` dependency)

---

## 7. Implementation Plan

### Phase 1: Core Auth (1-2 weeks)

**Backend changes:**
- Add `supabase` Python client and JWT validation
- Update `get_current_user()` in `dependencies.py` to validate Supabase JWT
- Add user auto-creation on first API call (upsert from JWT claims)
- Add `DELETE /api/users/me` endpoint
- Add auth middleware that rejects unauthenticated requests (except health check + public calculator endpoints)

**Frontend changes:**
- Add `supabase_flutter` package
- Build login screen: Google OAuth button + email/password form
- Add Apple Sign-In button (required for iOS)
- Token management: store JWT, auto-refresh, attach to API calls
- Add "try without account" mode for calculator

**Infrastructure:**
- Create Supabase project
- Configure Google OAuth (GCP Console → OAuth consent screen)
- Configure Apple Sign-In (Apple Developer account)
- Set up email templates for verification/reset

### Phase 2: Data Migration & Persistence (1 week)

- Migrate from `anonymous` user to real user IDs
- Ensure all existing endpoints properly scope data to authenticated user
- Add onboarding flow: filing status, state, income range
- Save/restore tax profile on login

### Phase 3: Security Hardening (1 week)

- Add MFA (TOTP) option for email/password users
- Add audit logging
- Add rate limiting on auth endpoints
- Add session management (view/revoke active sessions)
- Security headers (CSP, HSTS — if not already present)

### Phase 4: Polish (ongoing)

- Password-less magic link option
- Account settings page (change email, delete account, export data)
- Re-authentication for sensitive actions (linking Plaid, deleting data)
- Passkey support (when Flutter ecosystem matures)

---

## 8. Cost Analysis

### Supabase Auth pricing

**Free tier (0-50K MAU)**
- Auth: unlimited
- Database: 500MB
- Storage: 1GB
- Edge Functions: 500K invocations
- Cost: **$0/mo**

**Pro tier ($25/mo)**
- Auth: 100K MAU
- Database: 8GB
- Storage: 100GB
- Cost: **$25/mo**

### Projected costs by scale

**100 users (launch)**
- Supabase: $0/mo (free tier)
- Total auth cost: **$0/mo**

**1,000 users (early traction)**
- Supabase: $0/mo (free tier)
- Total auth cost: **$0/mo**

**10,000 users (growing)**
- Supabase: $0/mo (still under 50K MAU free limit)
- Total auth cost: **$0/mo**

**50,000+ users (scale)**
- Supabase Pro: $25/mo
- Total auth cost: **$25/mo**

**100,000+ users**
- Supabase Pro: $25/mo (up to 100K MAU included)
- Additional MAU: contact Supabase for Team/Enterprise pricing
- Estimated: **$25-$300/mo**

### Comparison if we chose alternatives

- **Auth0**: Free to 25K MAU → $240/mo at scale
- **Clerk**: Free to 10K MAU → $200/mo at 20K MAU
- **Firebase Auth**: Free to 50K MAU → $275/mo at 100K MAU
- **Supabase**: Free to 50K MAU → **$25/mo** at 100K MAU ← winner

---

## 9. Summary & Recommendation

**Use Supabase Auth** with this login flow:
1. **Primary**: Google Sign-In (one tap, covers ~80% of tech users)
2. **Secondary**: Apple Sign-In (required for iOS, preferred by ~15%)
3. **Fallback**: Email/password with optional MFA
4. **Future**: Magic link, passkeys

**"Try without account" flow:**
- Calculator and what-if scenarios work anonymously
- Prompt to create account when user tries to save, upload, or link accounts
- Frictionless upgrade: data entered anonymously transfers to new account

**Total implementation effort**: ~3-4 weeks for a solid v1
**Monthly cost at launch**: $0
**Monthly cost at scale**: $25

**Next step**: Create a Supabase project, configure OAuth providers, and update `dependencies.py` to validate real JWTs instead of returning `anonymous`.
