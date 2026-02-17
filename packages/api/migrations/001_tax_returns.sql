-- Migration: Create tax_returns table for previous-year 1040 import
-- Feature: Review Previous Year's Tax Return + Tax Tips
-- Run against: Supabase project kccgncphhzodneomimzt

-- ============================================================
-- 1. Create table
-- ============================================================
CREATE TABLE IF NOT EXISTS tax_returns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  tax_year INT NOT NULL,
  source TEXT NOT NULL DEFAULT 'pdf_upload',  -- 'pdf_upload' | 'manual' | 'irs_transcript'

  -- 1040 Key Fields
  filing_status TEXT,                    -- Single/MFJ/MFS/HOH/QW
  total_income NUMERIC,                  -- Line 9
  adjusted_gross_income NUMERIC,         -- Line 11
  deduction_type TEXT,                   -- 'standard' | 'itemized'
  deduction_amount NUMERIC,              -- Line 12
  taxable_income NUMERIC,                -- Line 15
  total_tax NUMERIC,                     -- Line 24
  total_credits NUMERIC,                 -- Lines 19-21 sum
  federal_withheld NUMERIC,              -- Line 25a
  refund_or_owed NUMERIC,                -- Line 34 (positive=refund) or 37 (negative=owed)

  -- Rich structured data
  schedule_data JSONB,                   -- Schedule C/D/E data
  raw_extracted_data JSONB,              -- Full Gemini extraction output

  -- Upload metadata
  pdf_storage_path TEXT,                 -- Supabase Storage path (if PDF uploaded)
  extraction_confidence FLOAT,           -- 0.0 – 1.0 from AI extraction
  user_confirmed BOOLEAN DEFAULT FALSE,  -- User reviewed and confirmed the data

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- One return per user per year
  UNIQUE(user_id, tax_year)
);

-- ============================================================
-- 2. Row-Level Security
-- ============================================================
ALTER TABLE tax_returns ENABLE ROW LEVEL SECURITY;

-- Users can only read/write their own returns
CREATE POLICY "Users manage own tax returns"
  ON tax_returns
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- 3. Auto-update updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_tax_returns_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tax_returns_updated_at ON tax_returns;
CREATE TRIGGER tax_returns_updated_at
  BEFORE UPDATE ON tax_returns
  FOR EACH ROW
  EXECUTE FUNCTION update_tax_returns_updated_at();

-- ============================================================
-- 4. Useful indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_tax_returns_user_year
  ON tax_returns(user_id, tax_year DESC);

-- ============================================================
-- 5. Comments
-- ============================================================
COMMENT ON TABLE tax_returns IS 'Previous-year 1040 data imported via PDF upload or manual entry';
COMMENT ON COLUMN tax_returns.source IS 'Import method: pdf_upload, manual, irs_transcript';
COMMENT ON COLUMN tax_returns.extraction_confidence IS 'AI extraction confidence 0-1; <0.7 should be reviewed';
COMMENT ON COLUMN tax_returns.refund_or_owed IS 'Positive = refund (line 34), negative = amount owed (line 37)';
