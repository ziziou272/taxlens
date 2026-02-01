"""
Schwab Equity Award Center CSV parser.

Parses transaction history and tax lot exports from Charles Schwab,
commonly used for RSU, ISO, NSO, and ESPP management.

Typical Schwab CSV columns for transactions:
- Date
- Action
- Symbol
- Quantity
- Price
- Amount
- Description

Schwab also provides specialized reports:
- "Equity Award Summary" - vesting history
- "Gain/Loss Report" - sales with cost basis
"""

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from typing import Optional
from enum import Enum


class SchwabActionType(str, Enum):
    """Schwab transaction action types."""
    LAPSE = "lapse"  # RSU vesting (Schwab calls it "Lapse")
    RELEASE = "release"  # Shares released
    SALE = "sale"
    EXERCISE = "exercise"  # Option exercise
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TAX_WITHHOLD = "tax_withhold"
    DIVIDEND = "dividend"
    UNKNOWN = "unknown"


@dataclass
class SchwabTransaction:
    """
    Represents a single transaction from Schwab export.
    """
    date: date
    action: SchwabActionType
    symbol: str
    description: str
    quantity: Decimal
    price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
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
class SchwabParseResult:
    """Result of parsing a Schwab CSV file."""
    transactions: list[SchwabTransaction] = field(default_factory=list)
    vesting_events: list[dict] = field(default_factory=list)
    exercises: list[dict] = field(default_factory=list)
    sales: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_rows: int = 0
    
    @property
    def success(self) -> bool:
        return len(self.errors) == 0 or len(self.transactions) > 0


def _parse_date(date_str: str) -> Optional[date]:
    """Parse date from various Schwab formats."""
    if not date_str or date_str.strip() == "":
        return None
    
    date_str = date_str.strip()
    
    # Common Schwab date formats
    formats = [
        "%m/%d/%Y",  # 01/15/2025
        "%Y-%m-%d",  # 2025-01-15
        "%m/%d/%y",  # 01/15/25
        "%b %d, %Y",  # Jan 15, 2025
        "%d-%b-%Y",  # 15-Jan-2025
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


def _classify_action(action: str, description: str = "") -> SchwabActionType:
    """Classify Schwab action type from action string."""
    action_upper = action.upper().strip()
    desc_upper = description.upper()
    
    # RSU vesting - Schwab uses "Lapse" for RSU release
    if "LAPSE" in action_upper:
        return SchwabActionType.LAPSE
    
    # Share release
    if "RELEASE" in action_upper or "VEST" in action_upper:
        return SchwabActionType.RELEASE
    
    # Sales
    if any(kw in action_upper for kw in ["SALE", "SOLD", "SELL"]):
        return SchwabActionType.SALE
    
    # Option exercise
    if "EXERCISE" in action_upper or "EXER" in action_upper:
        return SchwabActionType.EXERCISE
    
    # Deposits
    if "DEPOSIT" in action_upper or "DEP" in action_upper:
        return SchwabActionType.DEPOSIT
    
    # Withdrawals
    if "WITHDRAW" in action_upper or "W/D" in action_upper:
        return SchwabActionType.WITHDRAWAL
    
    # Tax withholding
    if any(kw in action_upper for kw in ["TAX", "WITHHOLD", "W/H"]):
        return SchwabActionType.TAX_WITHHOLD
    
    # Dividends
    if "DIV" in action_upper:
        return SchwabActionType.DIVIDEND
    
    return SchwabActionType.UNKNOWN


def _detect_award_type(description: str, action: str = "") -> Optional[str]:
    """Detect equity award type from description."""
    text = f"{description} {action}".upper()
    
    if "RSU" in text or "RESTRICTED STOCK" in text:
        return "RSU"
    if "ISO" in text or "INCENTIVE STOCK" in text:
        return "ISO"
    if "NSO" in text or "NQSO" in text or "NON-QUAL" in text:
        return "NSO"
    if "ESPP" in text or "EMPLOYEE STOCK PURCHASE" in text:
        return "ESPP"
    
    return None


def parse_schwab_csv(
    csv_content: str,
    symbol_filter: Optional[str] = None,
) -> SchwabParseResult:
    """
    Parse Schwab Equity Award Center CSV export.
    
    Args:
        csv_content: Raw CSV file content as string
        symbol_filter: Optional stock symbol to filter (e.g., "AAPL")
        
    Returns:
        SchwabParseResult with parsed transactions
    """
    result = SchwabParseResult()
    
    try:
        # Use StringIO to handle CSV content
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(reader, start=2):
            result.raw_rows += 1
            
            try:
                # Normalize column names
                normalized = {k.lower().strip(): v for k, v in row.items() if k}
                
                # Extract date
                date_str = (
                    normalized.get("date") or
                    normalized.get("trade date") or
                    normalized.get("settlement date") or
                    ""
                )
                parsed_date = _parse_date(date_str)
                if not parsed_date:
                    result.errors.append(f"Row {row_num}: Could not parse date '{date_str}'")
                    continue
                
                # Extract action
                action_str = (
                    normalized.get("action") or
                    normalized.get("transaction type") or
                    normalized.get("type") or
                    ""
                )
                
                # Extract symbol
                symbol = (
                    normalized.get("symbol") or
                    normalized.get("ticker") or
                    ""
                ).strip().upper()
                
                # Apply symbol filter
                if symbol_filter and symbol != symbol_filter.upper():
                    continue
                
                # Extract description
                description = normalized.get("description", "") or ""
                
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
                    normalized.get("share price") or
                    normalized.get("fair market value") or
                    normalized.get("fmv") or
                    ""
                )
                
                # Extract amount
                amount = _parse_decimal(
                    normalized.get("amount") or
                    normalized.get("total") or
                    normalized.get("proceeds") or
                    normalized.get("value") or
                    ""
                )
                
                # Extract fees
                fees = _parse_decimal(
                    normalized.get("fees") or
                    normalized.get("commission") or
                    ""
                )
                
                # Extract cost basis (for sales)
                cost_basis = _parse_decimal(
                    normalized.get("cost basis") or
                    normalized.get("cost") or
                    normalized.get("adjusted cost basis") or
                    ""
                )
                
                # Extract gain/loss
                gain_loss = _parse_decimal(
                    normalized.get("gain/loss") or
                    normalized.get("gain") or
                    normalized.get("realized gain") or
                    ""
                )
                
                # Extract acquisition date
                acq_date_str = (
                    normalized.get("acquisition date") or
                    normalized.get("acquired") or
                    normalized.get("vest date") or
                    ""
                )
                acquisition_date = _parse_date(acq_date_str)
                
                # Extract grant date
                grant_date_str = (
                    normalized.get("grant date") or
                    ""
                )
                grant_date = _parse_date(grant_date_str)
                
                # Extract term
                term = normalized.get("term") or normalized.get("holding period") or None
                
                # Classify action
                action_type = _classify_action(action_str, description)
                
                # Detect award type
                award_type = _detect_award_type(description, action_str)
                
                # Create transaction
                txn = SchwabTransaction(
                    date=parsed_date,
                    action=action_type,
                    symbol=symbol,
                    description=description,
                    quantity=quantity,
                    price=price,
                    amount=amount,
                    fees=fees,
                    raw_action=action_str,
                    award_type=award_type,
                    grant_date=grant_date,
                    vest_date=acquisition_date,
                    vest_fmv=price if action_type == SchwabActionType.LAPSE else None,
                    acquisition_date=acquisition_date,
                    cost_basis=cost_basis,
                    gain_loss=gain_loss,
                    term=term,
                )
                
                result.transactions.append(txn)
                
                # Categorize for convenience
                if action_type in (SchwabActionType.LAPSE, SchwabActionType.RELEASE):
                    result.vesting_events.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "fmv": price,
                        "value": amount or (quantity * price if price else None),
                        "symbol": symbol,
                        "award_type": award_type,
                        "grant_date": grant_date,
                    })
                elif action_type == SchwabActionType.EXERCISE:
                    result.exercises.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "price": price,  # Exercise price
                        "symbol": symbol,
                        "award_type": award_type,
                        "grant_date": grant_date,
                    })
                elif action_type == SchwabActionType.SALE:
                    result.sales.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "price": price,
                        "proceeds": amount,
                        "cost_basis": cost_basis,
                        "gain_loss": gain_loss,
                        "symbol": symbol,
                        "acquisition_date": acquisition_date,
                        "term": term,
                        "award_type": award_type,
                    })
                    
            except Exception as e:
                result.errors.append(f"Row {row_num}: {str(e)}")
                
    except Exception as e:
        result.errors.append(f"CSV parsing error: {str(e)}")
    
    return result


def parse_schwab_gain_loss_report(
    csv_content: str,
    symbol_filter: Optional[str] = None,
) -> list[dict]:
    """
    Parse Schwab Gain/Loss Report (specialized format).
    
    This report includes detailed cost basis and holding period info.
    
    Args:
        csv_content: Raw CSV content
        symbol_filter: Optional symbol filter
        
    Returns:
        List of gain/loss entries
    """
    sales = []
    
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in reader:
            normalized = {k.lower().strip(): v for k, v in row.items() if k}
            
            symbol = (
                normalized.get("symbol") or
                normalized.get("security") or
                ""
            ).strip().upper()
            
            if symbol_filter and symbol != symbol_filter.upper():
                continue
            
            sale_date = _parse_date(
                normalized.get("sale date") or
                normalized.get("date sold") or
                ""
            )
            
            acquisition_date = _parse_date(
                normalized.get("acquisition date") or
                normalized.get("date acquired") or
                ""
            )
            
            shares = _parse_decimal(
                normalized.get("shares sold") or
                normalized.get("quantity") or
                "0"
            ) or Decimal("0")
            
            proceeds = _parse_decimal(
                normalized.get("proceeds") or
                normalized.get("sale proceeds") or
                ""
            )
            
            cost_basis = _parse_decimal(
                normalized.get("cost basis") or
                normalized.get("adjusted cost basis") or
                ""
            )
            
            gain_loss = _parse_decimal(
                normalized.get("gain/loss") or
                normalized.get("realized gain") or
                ""
            )
            
            # Determine if short or long term
            term = normalized.get("term") or ""
            if not term and sale_date and acquisition_date:
                days_held = (sale_date - acquisition_date).days
                term = "Long" if days_held > 365 else "Short"
            
            sales.append({
                "symbol": symbol,
                "sale_date": sale_date,
                "acquisition_date": acquisition_date,
                "shares": shares,
                "proceeds": proceeds,
                "cost_basis": cost_basis,
                "gain_loss": gain_loss,
                "term": term,
            })
            
    except Exception:
        pass
    
    return sales


def extract_tax_lots(
    result: SchwabParseResult,
    year: Optional[int] = None,
) -> dict:
    """
    Extract tax lot information for Form 8949.
    
    Organizes sales by short-term vs long-term for tax reporting.
    
    Args:
        result: Parsed Schwab data
        year: Optional year to filter
        
    Returns:
        Dict with short_term and long_term sales
    """
    sales = result.sales
    
    if year:
        sales = [s for s in sales if s["date"].year == year]
    
    short_term = []
    long_term = []
    
    for sale in sales:
        term = (sale.get("term") or "").upper()
        
        if "SHORT" in term:
            short_term.append(sale)
        elif "LONG" in term:
            long_term.append(sale)
        elif sale.get("acquisition_date") and sale.get("date"):
            # Calculate based on dates
            days = (sale["date"] - sale["acquisition_date"]).days
            if days > 365:
                long_term.append(sale)
            else:
                short_term.append(sale)
        else:
            # Default to short-term if unknown
            short_term.append(sale)
    
    def sum_field(lst, field):
        return sum(s[field] for s in lst if s.get(field) is not None)
    
    return {
        "year": year,
        "short_term": {
            "count": len(short_term),
            "proceeds": sum_field(short_term, "proceeds"),
            "cost_basis": sum_field(short_term, "cost_basis"),
            "gain_loss": sum_field(short_term, "gain_loss"),
            "sales": short_term,
        },
        "long_term": {
            "count": len(long_term),
            "proceeds": sum_field(long_term, "proceeds"),
            "cost_basis": sum_field(long_term, "cost_basis"),
            "gain_loss": sum_field(long_term, "gain_loss"),
            "sales": long_term,
        },
    }
