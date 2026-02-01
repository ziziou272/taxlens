"""
E*TRADE CSV parser for equity compensation.

Parses transaction history exports from E*TRADE,
commonly used for RSU, ISO, NSO, and ESPP management.

Typical E*TRADE CSV columns:
- TransactionDate
- TransactionType
- SecurityType
- Symbol
- Quantity
- Price
- Amount
- CommissionAndFees
"""

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from typing import Optional
from enum import Enum


class ETradeActionType(str, Enum):
    """E*TRADE transaction action types."""
    VEST = "vest"  # RSU/Stock vesting
    RELEASE = "release"  # Shares released
    SALE = "sale"
    EXERCISE = "exercise"  # Option exercise
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TAX_WITHHOLD = "tax_withhold"
    DIVIDEND = "dividend"
    ESPP_PURCHASE = "espp_purchase"
    UNKNOWN = "unknown"


@dataclass
class ETradeTransaction:
    """
    Represents a single transaction from E*TRADE export.
    """
    date: date
    action: ETradeActionType
    symbol: str
    description: str
    quantity: Decimal
    price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    fees: Optional[Decimal] = None
    raw_action: str = ""
    
    # For equity awards
    award_type: Optional[str] = None  # RSU, ISO, NSO, ESPP
    grant_date: Optional[date] = None
    grant_id: Optional[str] = None
    vest_date: Optional[date] = None
    vest_fmv: Optional[Decimal] = None
    
    # For sales - tax lot info
    acquisition_date: Optional[date] = None
    cost_basis: Optional[Decimal] = None
    gain_loss: Optional[Decimal] = None
    term: Optional[str] = None  # "Short" or "Long"


@dataclass
class ETradeParseResult:
    """Result of parsing an E*TRADE CSV file."""
    transactions: list[ETradeTransaction] = field(default_factory=list)
    vesting_events: list[dict] = field(default_factory=list)
    exercises: list[dict] = field(default_factory=list)
    sales: list[dict] = field(default_factory=list)
    espp_purchases: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_rows: int = 0
    
    @property
    def success(self) -> bool:
        return len(self.errors) == 0 or len(self.transactions) > 0


def _parse_date(date_str: str) -> Optional[date]:
    """Parse date from various E*TRADE formats."""
    if not date_str or date_str.strip() == "":
        return None
    
    date_str = date_str.strip()
    
    # Common E*TRADE date formats
    formats = [
        "%m/%d/%Y",      # 01/15/2025
        "%Y-%m-%d",      # 2025-01-15
        "%m-%d-%Y",      # 01-15-2025
        "%b %d, %Y",     # Jan 15, 2025
        "%B %d, %Y",     # January 15, 2025
        "%m/%d/%y",      # 01/15/25
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def _parse_decimal(value: str) -> Optional[Decimal]:
    """Parse decimal from string, handling currency symbols."""
    if not value or value.strip() in ("", "-", "--", "N/A", "n/a"):
        return None
    
    # Remove currency symbols, commas, and handle negative in parens
    cleaned = (
        value.strip()
        .replace("$", "")
        .replace(",", "")
        .replace("(", "-")
        .replace(")", "")
    )
    
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _classify_action(action: str, description: str = "") -> ETradeActionType:
    """Classify E*TRADE action type from action string."""
    action_upper = action.upper().strip()
    desc_upper = description.upper()
    
    # RSU/Stock vesting
    if any(kw in action_upper for kw in ["VEST", "LAPSE", "RELEASE"]):
        if "RSU" in desc_upper or "RESTRICTED" in desc_upper:
            return ETradeActionType.VEST
        return ETradeActionType.RELEASE
    
    # Sales
    if any(kw in action_upper for kw in ["SALE", "SOLD", "SELL"]):
        return ETradeActionType.SALE
    
    # Option exercise
    if "EXERCISE" in action_upper or "EXER" in action_upper:
        return ETradeActionType.EXERCISE
    
    # ESPP Purchase
    if "ESPP" in action_upper or "PURCHASE" in action_upper:
        if "ESPP" in desc_upper or "EMPLOYEE STOCK" in desc_upper:
            return ETradeActionType.ESPP_PURCHASE
    
    # Deposits
    if "DEPOSIT" in action_upper or "DEP" in action_upper:
        return ETradeActionType.DEPOSIT
    
    # Withdrawals
    if "WITHDRAW" in action_upper:
        return ETradeActionType.WITHDRAWAL
    
    # Tax withholding
    if any(kw in action_upper for kw in ["TAX", "WITHHOLD"]):
        return ETradeActionType.TAX_WITHHOLD
    
    # Dividends
    if "DIV" in action_upper:
        return ETradeActionType.DIVIDEND
    
    return ETradeActionType.UNKNOWN


def _detect_award_type(description: str, action: str = "") -> Optional[str]:
    """Detect equity award type from description."""
    text = f"{description} {action}".upper()
    
    if "RSU" in text or "RESTRICTED STOCK UNIT" in text:
        return "RSU"
    if "ISO" in text or "INCENTIVE STOCK" in text:
        return "ISO"
    if "NSO" in text or "NQSO" in text or "NON-QUAL" in text or "NONQUALIFIED" in text:
        return "NSO"
    if "ESPP" in text or "EMPLOYEE STOCK PURCHASE" in text:
        return "ESPP"
    
    return None


def parse_etrade_csv(
    csv_content: str,
    symbol_filter: Optional[str] = None,
) -> ETradeParseResult:
    """
    Parse E*TRADE CSV export.
    
    Args:
        csv_content: Raw CSV file content as string
        symbol_filter: Optional stock symbol to filter (e.g., "AAPL")
        
    Returns:
        ETradeParseResult with parsed transactions
    """
    result = ETradeParseResult()
    
    try:
        # Use StringIO to handle CSV content
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(reader, start=2):
            result.raw_rows += 1
            
            try:
                # Normalize column names (E*TRADE uses various formats)
                normalized = {k.lower().strip().replace(" ", "_"): v for k, v in row.items() if k}
                
                # Extract date
                date_str = (
                    normalized.get("transaction_date") or
                    normalized.get("transactiondate") or
                    normalized.get("date") or
                    normalized.get("trade_date") or
                    ""
                )
                parsed_date = _parse_date(date_str)
                if not parsed_date:
                    result.errors.append(f"Row {row_num}: Could not parse date '{date_str}'")
                    continue
                
                # Extract action
                action_str = (
                    normalized.get("transaction_type") or
                    normalized.get("transactiontype") or
                    normalized.get("type") or
                    normalized.get("action") or
                    ""
                )
                
                # Extract symbol
                symbol = (
                    normalized.get("symbol") or
                    normalized.get("ticker") or
                    normalized.get("security_symbol") or
                    ""
                ).strip().upper()
                
                # Apply symbol filter
                if symbol_filter and symbol != symbol_filter.upper():
                    continue
                
                # Extract description
                description = (
                    normalized.get("description") or
                    normalized.get("security_type") or
                    ""
                )
                
                # Extract quantity
                quantity = _parse_decimal(
                    normalized.get("quantity") or
                    normalized.get("shares") or
                    normalized.get("qty") or
                    "0"
                ) or Decimal("0")
                
                # Extract price
                price = _parse_decimal(
                    normalized.get("price") or
                    normalized.get("share_price") or
                    normalized.get("market_price") or
                    ""
                )
                
                # Extract amount
                amount = _parse_decimal(
                    normalized.get("amount") or
                    normalized.get("total") or
                    normalized.get("proceeds") or
                    normalized.get("market_value") or
                    ""
                )
                
                # Extract commission and fees
                commission = _parse_decimal(
                    normalized.get("commission") or
                    normalized.get("commissionandfees") or
                    ""
                )
                fees = _parse_decimal(
                    normalized.get("fees") or
                    normalized.get("other_fees") or
                    ""
                )
                
                # Extract cost basis
                cost_basis = _parse_decimal(
                    normalized.get("cost_basis") or
                    normalized.get("costbasis") or
                    ""
                )
                
                # Extract gain/loss
                gain_loss = _parse_decimal(
                    normalized.get("gain_loss") or
                    normalized.get("gain/loss") or
                    normalized.get("realized_gain") or
                    ""
                )
                
                # Extract acquisition date
                acq_date_str = (
                    normalized.get("acquisition_date") or
                    normalized.get("acquired_date") or
                    normalized.get("vest_date") or
                    ""
                )
                acquisition_date = _parse_date(acq_date_str)
                
                # Extract grant date
                grant_date_str = (
                    normalized.get("grant_date") or
                    normalized.get("grantdate") or
                    ""
                )
                grant_date = _parse_date(grant_date_str)
                
                # Classify action
                action_type = _classify_action(action_str, description)
                
                # Detect award type
                award_type = _detect_award_type(description, action_str)
                
                # Create transaction
                txn = ETradeTransaction(
                    date=parsed_date,
                    action=action_type,
                    symbol=symbol,
                    description=description,
                    quantity=quantity,
                    price=price,
                    amount=amount,
                    commission=commission,
                    fees=fees,
                    raw_action=action_str,
                    award_type=award_type,
                    grant_date=grant_date,
                    vest_date=acquisition_date,
                    vest_fmv=price if action_type == ETradeActionType.VEST else None,
                    acquisition_date=acquisition_date,
                    cost_basis=cost_basis,
                    gain_loss=gain_loss,
                )
                
                result.transactions.append(txn)
                
                # Categorize for convenience
                if action_type in (ETradeActionType.VEST, ETradeActionType.RELEASE):
                    result.vesting_events.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "fmv": price,
                        "value": amount or (quantity * price if price else None),
                        "symbol": symbol,
                        "award_type": award_type,
                        "grant_date": grant_date,
                    })
                elif action_type == ETradeActionType.EXERCISE:
                    result.exercises.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "exercise_price": price,
                        "symbol": symbol,
                        "award_type": award_type,
                        "grant_date": grant_date,
                    })
                elif action_type == ETradeActionType.ESPP_PURCHASE:
                    result.espp_purchases.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "purchase_price": price,
                        "fmv": _parse_decimal(normalized.get("fmv") or ""),
                        "symbol": symbol,
                    })
                elif action_type == ETradeActionType.SALE:
                    result.sales.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "price": price,
                        "proceeds": amount,
                        "cost_basis": cost_basis,
                        "gain_loss": gain_loss,
                        "symbol": symbol,
                        "acquisition_date": acquisition_date,
                        "award_type": award_type,
                    })
                    
            except Exception as e:
                result.errors.append(f"Row {row_num}: {str(e)}")
                
    except Exception as e:
        result.errors.append(f"CSV parsing error: {str(e)}")
    
    return result


def extract_vesting_summary(
    result: ETradeParseResult,
    year: Optional[int] = None,
) -> dict:
    """
    Extract vesting summary from parse result.
    
    Args:
        result: Parsed E*TRADE data
        year: Optional year to filter
        
    Returns:
        Summary dict with totals
    """
    vestings = result.vesting_events
    
    if year:
        vestings = [v for v in vestings if v["date"].year == year]
    
    total_shares = sum(v["shares"] for v in vestings)
    total_value = sum(
        v["value"] for v in vestings 
        if v["value"] is not None
    )
    
    # Group by award type
    by_type = {}
    for v in vestings:
        award_type = v.get("award_type") or "unknown"
        if award_type not in by_type:
            by_type[award_type] = {"shares": Decimal("0"), "value": Decimal("0")}
        by_type[award_type]["shares"] += v["shares"]
        if v["value"]:
            by_type[award_type]["value"] += v["value"]
    
    return {
        "year": year,
        "vesting_count": len(vestings),
        "total_shares": total_shares,
        "total_value": total_value,
        "by_award_type": by_type,
        "events": vestings,
    }


def extract_sales_summary(
    result: ETradeParseResult,
    year: Optional[int] = None,
) -> dict:
    """
    Extract sales summary from parse result.
    
    Args:
        result: Parsed E*TRADE data
        year: Optional year to filter
        
    Returns:
        Summary dict with totals
    """
    sales = result.sales
    
    if year:
        sales = [s for s in sales if s["date"].year == year]
    
    total_shares = sum(s["shares"] for s in sales)
    total_proceeds = sum(
        s["proceeds"] for s in sales 
        if s["proceeds"] is not None
    )
    total_cost_basis = sum(
        s["cost_basis"] for s in sales 
        if s["cost_basis"] is not None
    )
    total_gain_loss = sum(
        s["gain_loss"] for s in sales 
        if s["gain_loss"] is not None
    )
    
    # Separate short vs long term
    short_term_gains = Decimal("0")
    long_term_gains = Decimal("0")
    
    for s in sales:
        if s.get("acquisition_date") and s.get("date"):
            days_held = (s["date"] - s["acquisition_date"]).days
            if s["gain_loss"]:
                if days_held > 365:
                    long_term_gains += s["gain_loss"]
                else:
                    short_term_gains += s["gain_loss"]
    
    return {
        "year": year,
        "sale_count": len(sales),
        "total_shares": total_shares,
        "total_proceeds": total_proceeds,
        "total_cost_basis": total_cost_basis,
        "total_gain_loss": total_gain_loss,
        "short_term_gains": short_term_gains,
        "long_term_gains": long_term_gains,
        "sales": sales,
    }
