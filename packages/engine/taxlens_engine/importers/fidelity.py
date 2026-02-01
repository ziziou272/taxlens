"""
Fidelity NetBenefits CSV parser for equity compensation.

Parses transaction history exports from Fidelity NetBenefits,
commonly used for RSU, ESPP, and stock option management.

Typical Fidelity CSV columns:
- Date
- Action (e.g., "DEPOSIT STOCK", "SALE", "RELEASE")
- Symbol
- Description
- Quantity
- Price
- Amount
- Cost Basis
- Gain/Loss
"""

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from typing import Optional
from enum import Enum


class FidelityActionType(str, Enum):
    """Fidelity transaction action types."""
    DEPOSIT = "deposit"  # RSU vesting deposit
    RELEASE = "release"  # Shares released from restriction
    SALE = "sale"  # Share sale
    TAX_WITHHOLD = "tax_withhold"  # Shares withheld for taxes
    DIVIDEND = "dividend"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    UNKNOWN = "unknown"


@dataclass
class FidelityTransaction:
    """
    Represents a single transaction from Fidelity export.
    """
    date: date
    action: FidelityActionType
    symbol: str
    description: str
    quantity: Decimal
    price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    gain_loss: Optional[Decimal] = None
    raw_action: str = ""
    
    # For RSU/vesting context
    grant_id: Optional[str] = None
    vest_date: Optional[date] = None
    vest_fmv: Optional[Decimal] = None


@dataclass
class FidelityParseResult:
    """Result of parsing a Fidelity CSV file."""
    transactions: list[FidelityTransaction] = field(default_factory=list)
    vesting_events: list[dict] = field(default_factory=list)
    sales: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_rows: int = 0
    
    @property
    def success(self) -> bool:
        return len(self.errors) == 0 or len(self.transactions) > 0


def _parse_date(date_str: str) -> Optional[date]:
    """Parse date from various Fidelity formats."""
    if not date_str or date_str.strip() == "":
        return None
    
    date_str = date_str.strip()
    
    # Common Fidelity date formats
    formats = [
        "%m/%d/%Y",  # 01/15/2025
        "%Y-%m-%d",  # 2025-01-15
        "%b %d, %Y",  # Jan 15, 2025
        "%B %d, %Y",  # January 15, 2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def _parse_decimal(value: str) -> Optional[Decimal]:
    """Parse decimal from string, handling currency symbols."""
    if not value or value.strip() in ("", "-", "--", "N/A"):
        return None
    
    # Remove currency symbols and commas
    cleaned = value.strip().replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
    
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _classify_action(action: str, description: str = "") -> FidelityActionType:
    """Classify Fidelity action type from action string."""
    action_upper = action.upper().strip()
    desc_upper = description.upper()
    
    # RSU/Stock deposits (vesting)
    if any(kw in action_upper for kw in ["DEPOSIT", "VEST", "RELEASE"]):
        if "STOCK" in action_upper or "RSU" in desc_upper:
            return FidelityActionType.DEPOSIT
        return FidelityActionType.RELEASE
    
    # Sales
    if any(kw in action_upper for kw in ["SALE", "SOLD", "SELL"]):
        return FidelityActionType.SALE
    
    # Tax withholding
    if any(kw in action_upper for kw in ["TAX", "WITHHOLD", "W/H"]):
        return FidelityActionType.TAX_WITHHOLD
    
    # Dividends
    if "DIVIDEND" in action_upper or "DIV" in action_upper:
        return FidelityActionType.DIVIDEND
    
    # Transfers
    if "TRANSFER" in action_upper:
        if "IN" in action_upper:
            return FidelityActionType.TRANSFER_IN
        elif "OUT" in action_upper:
            return FidelityActionType.TRANSFER_OUT
    
    return FidelityActionType.UNKNOWN


def parse_fidelity_csv(
    csv_content: str,
    symbol_filter: Optional[str] = None,
) -> FidelityParseResult:
    """
    Parse Fidelity NetBenefits CSV export.
    
    Args:
        csv_content: Raw CSV file content as string
        symbol_filter: Optional stock symbol to filter (e.g., "AAPL")
        
    Returns:
        FidelityParseResult with parsed transactions
    """
    result = FidelityParseResult()
    
    try:
        # Use StringIO to handle CSV content
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(reader, start=2):
            result.raw_rows += 1
            
            try:
                # Normalize column names (handle variations)
                normalized = {k.lower().strip(): v for k, v in row.items()}
                
                # Extract date
                date_str = (
                    normalized.get("date") or
                    normalized.get("trade date") or
                    normalized.get("run date") or
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
                    normalized.get("security") or
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
                    normalized.get("units") or
                    "0"
                ) or Decimal("0")
                
                # Extract price
                price = _parse_decimal(
                    normalized.get("price") or
                    normalized.get("share price") or
                    ""
                )
                
                # Extract amount
                amount = _parse_decimal(
                    normalized.get("amount") or
                    normalized.get("total") or
                    normalized.get("proceeds") or
                    ""
                )
                
                # Extract cost basis
                cost_basis = _parse_decimal(
                    normalized.get("cost basis") or
                    normalized.get("cost") or
                    ""
                )
                
                # Extract gain/loss
                gain_loss = _parse_decimal(
                    normalized.get("gain/loss") or
                    normalized.get("gain") or
                    normalized.get("profit/loss") or
                    ""
                )
                
                # Classify action
                action_type = _classify_action(action_str, description)
                
                # Create transaction
                txn = FidelityTransaction(
                    date=parsed_date,
                    action=action_type,
                    symbol=symbol,
                    description=description,
                    quantity=quantity,
                    price=price,
                    amount=amount,
                    cost_basis=cost_basis,
                    gain_loss=gain_loss,
                    raw_action=action_str,
                )
                
                result.transactions.append(txn)
                
                # Categorize for convenience
                if action_type == FidelityActionType.DEPOSIT:
                    result.vesting_events.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "fmv": price,
                        "value": amount or (quantity * price if price else None),
                        "symbol": symbol,
                    })
                elif action_type == FidelityActionType.SALE:
                    result.sales.append({
                        "date": parsed_date,
                        "shares": quantity,
                        "price": price,
                        "proceeds": amount,
                        "cost_basis": cost_basis,
                        "gain_loss": gain_loss,
                        "symbol": symbol,
                    })
                    
            except Exception as e:
                result.errors.append(f"Row {row_num}: {str(e)}")
                
    except Exception as e:
        result.errors.append(f"CSV parsing error: {str(e)}")
    
    return result


def extract_vesting_summary(
    result: FidelityParseResult,
    year: Optional[int] = None,
) -> dict:
    """
    Extract vesting summary from parse result.
    
    Args:
        result: Parsed Fidelity data
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
    
    return {
        "year": year,
        "vesting_count": len(vestings),
        "total_shares": total_shares,
        "total_value": total_value,
        "events": vestings,
    }


def extract_sales_summary(
    result: FidelityParseResult,
    year: Optional[int] = None,
) -> dict:
    """
    Extract sales summary from parse result.
    
    Args:
        result: Parsed Fidelity data
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
    
    return {
        "year": year,
        "sale_count": len(sales),
        "total_shares": total_shares,
        "total_proceeds": total_proceeds,
        "total_cost_basis": total_cost_basis,
        "total_gain_loss": total_gain_loss,
        "sales": sales,
    }
