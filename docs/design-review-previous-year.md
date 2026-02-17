# Feature Design: Review Previous Year's Tax Return + Tax Tips

**Status:** Planning  
**Created:** 2026-02-17  
**Feature Branch:** `feature/pdf-tax-return-import`

---

## Overview

Allow users to import their previous year's 1040 tax return into TaxLens so we can:
1. Show year-over-year comparisons on the Dashboard
2. Provide AI-powered tax tips based on actual filed data
3. Detect patterns (under-withholding, missed deductions, bracket creep)

---

## Import Methods

### PRIMARY: PDF Upload + Gemini Vision AI Extraction
- User uploads their 1040 PDF (or image scan)
- Backend sends PDF pages to Gemini Vision API for structured extraction
- AI extracts all key fields and returns with confidence scores
- User reviews extracted data on a confirmation screen before saving

### FALLBACK: Manual Key Number Entry
- 10 fields with labels like "What was your AGI?" (line 11)
- Friendlier than asking users to find obscure line numbers
- Used when PDF upload isn't available or extraction fails

### FUTURE: IRS Transcript Import
- Direct IRS API integration (OAuth with IRS e-Services)
- Most accurate — bypasses OCR entirely
- Planned for Phase D

---

## Key 1040 Fields to Extract

| Field | Line | Description |
|-------|------|-------------|
| `filing_status` | Top section | Single / MFJ / MFS / HOH / QW |
| `total_income` | Line 9 | Total income |
| `adjusted_gross_income` | Line 11 | AGI |
| `deduction_type` | Line 12 | Standard or Itemized |
| `deduction_amount` | Line 12 | Deduction amount |
| `taxable_income` | Line 15 | Taxable income |
| `total_tax` | Line 24 | Total tax |
| `total_credits` | Lines 19-21 | Child tax credit, education, etc. |
| `federal_withheld` | Line 25a | Federal income tax withheld (W-2) |
| `refund_or_owed` | Lines 34 / 37 | Refund amount (34) or amount owed (37) |
| `schedule_data` | Schedules | C (self-employment), D (capital gains), E (rental) |

---

## Year Switcher UI

- Dropdown at the **top of the Dashboard** showing available tax years
- Options: `2024`, `2023`, `2022`, etc. based on what's been imported
- Last item: **"+ Import Year..."** — opens the PDF upload / manual entry flow
- Switching years updates all dashboard numbers + AI tips context

---

## Year-over-Year Comparison

- Side-by-side cards for current year estimate vs. previous year actuals
- % change indicators with color coding (red = higher tax, green = lower)
- Key comparisons:
  - AGI growth
  - Effective tax rate change
  - Withholding adequacy
  - Deduction type change (did they cross the standard deduction threshold?)

---

## AI Tax Tips (Powered by Gemini)

Based on previous year's actual filed data, surface:

1. **Missed deductions** — Were they close to the itemized threshold?
2. **Bracket changes** — Did income growth push into a higher bracket?
3. **Withholding optimization** — Over/under by how much? W-4 adjustment advice
4. **Credit opportunities** — Child tax credit phase-out, education credits, saver's credit
5. **Equity timing** — RSU vesting in relation to bracket
6. **State tax surprises** — CA SDI, NY surcharges, etc.

---

## Data Model

```sql
CREATE TABLE tax_returns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  tax_year INT NOT NULL,
  source TEXT NOT NULL,  -- 'pdf_upload', 'manual', 'irs_transcript'
  filing_status TEXT,
  total_income NUMERIC,
  adjusted_gross_income NUMERIC,
  deduction_type TEXT,
  deduction_amount NUMERIC,
  taxable_income NUMERIC,
  total_tax NUMERIC,
  total_credits NUMERIC,
  federal_withheld NUMERIC,
  refund_or_owed NUMERIC,
  schedule_data JSONB,
  raw_extracted_data JSONB,
  pdf_storage_path TEXT,
  extraction_confidence FLOAT,
  user_confirmed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, tax_year)
);

ALTER TABLE tax_returns ENABLE ROW LEVEL SECURITY;

-- Users can only see/edit their own returns
CREATE POLICY "Users can manage own tax returns"
  ON tax_returns FOR ALL
  USING (auth.uid() = user_id);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tax_returns_updated_at
  BEFORE UPDATE ON tax_returns
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tax-returns/upload-pdf` | Upload 1040 PDF, AI extracts fields |
| `POST` | `/api/tax-returns/confirm` | User confirms extracted data, saves to DB |
| `GET` | `/api/tax-returns` | List all years with data |
| `GET` | `/api/tax-returns/{tax_year}` | Get data for a specific year |
| `DELETE` | `/api/tax-returns/{tax_year}` | Delete a year's data |

---

## Implementation Phases

### Phase A — Manual Entry + Year Picker (MVP)
- Year switcher dropdown on Dashboard
- Manual 10-field entry form for previous year
- Basic year-over-year comparison cards

### Phase B — PDF AI Extraction (Current Sprint)
- `POST /api/tax-returns/upload-pdf` endpoint
- Gemini Vision API integration
- PDF-to-image conversion (PyMuPDF)
- Confidence scores + user confirmation screen
- Flutter upload UI

### Phase C — AI Tax Tips
- Prompt engineering for Gemini tax tips
- Tips carousel on Dashboard
- Tips tied to actual previous-year data

### Phase D — Multi-Year Trends
- 3+ year charts (AGI trend, effective rate trend)
- IRS transcript import
- Export to PDF report

---

## Technical Decisions

### Why Gemini Vision over Claude?
- Gemini API key already configured in the deployment environment
- Gemini's long-context window handles multi-page 1040s natively
- Native PDF support in Gemini 1.5+ (no image conversion needed for some formats)
- Cost: Gemini Flash is ~10x cheaper than Claude for document processing

### Why PyMuPDF for PDF conversion?
- Pure Python, lightweight, fast
- Better than pdf2image (no poppler system dependency)
- Handles scanned PDFs and native PDFs
- License: AGPL (acceptable for server-side use)

### Why store in Supabase directly?
- Consistent with existing auth pattern
- Row-level security out of the box
- Supabase Storage for the PDF files themselves
- Avoids duplicate storage in SQLite dev / Postgres prod split

### Confidence Scoring
- Per-field confidence based on Gemini's response quality
- Fields below 70% confidence flagged for user review
- Overall document confidence = average of key field confidences

---

## Security Considerations

- PDF files stored in Supabase Storage (private bucket, signed URLs)
- No PDF content stored in the database (only extracted structured data)
- JWT required for all endpoints
- RLS enforced at Supabase level
- File size limit: 10MB (typical 1040 is <2MB)
- File type validation: PDF only (MIME + magic bytes)

---

## Open Questions

1. Should we support scanned/photographed returns (JPEG/PNG) in addition to PDF?
2. Do we need to handle amended returns (1040-X)?
3. Should extraction run synchronously or as a background job?
   - Current plan: synchronous (Gemini Flash is fast enough, <5s for 2-3 pages)
4. How do we handle multi-state filers? (Store schedule_data as JSONB for flexibility)
