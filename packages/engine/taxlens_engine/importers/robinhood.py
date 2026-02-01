"""
Robinhood CSV parser for brokerage transactions.

Parses transaction history exports from Robinhood,
typically used for retail investors with stocks and options.

Typical Robinhood CSV columns:
- Activity Date
- Process Date
- Settle Date
- Instrument
- Description
- Trans Code
- Quantity
- Price
- Amount
"""

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from typing import Optional
from enum import Enum


class RobinhoodActionType(str, Enum):
    """Robinhood transaction action types."""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    DIVIDEND_REINVEST = "dividend_reinvest"
    STOCK_SPLIT = "stock_split"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    INTEREST = "interest"
    OPTION_EXERCISE = "option_exercise"
    OPTION_ASSIGNMENT = "option_assignment"
    UNKNOWN = "unknown"


@dataclass
class RobinhoodTransaction:
    """
    Represents a single transaction from Robinhood export.
    """
    activity_date: date
    process_date: Optional[date] = None
    settle_date: Optional[date] = None
    action: RobinhoodActionType = RobinhoodActionType.UNKNOWN
    symbol: str = ""
    description: str = ""
    quantity: Decimal = Decimal("0")
    price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    trans_code: str = ""


@dataclass
class RobinhoodParseResult:
    """Result of parsing a Robinhood CSV file."""
    transactions: list[RobinhoodTransaction] = field(default_factory=list)
    buys: list[dict] = field(default_factory=list)
    sells: list[dict] = field(default_factory=list)
    dividends: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    raw_rows: int = 0
    
    @property
    def success(self) -> bool:
        return len(self.errors) == 0 or len(self.transactions) > 0


def _parse_date(date_str: str) -> Optional[date]:
    """Parse date from various Robinhood formats."""
    if not date_str or date_str.strip() == "":
        return None
    
    date_str = date_str.strip()
    
    # Robinhood date formats
    formats = [
        "%m/%d/%Y",      # 01/15/2025
        "%Y-%m-%d",      # 2025-01-15
        "%m-%d-%Y",      # 01-15-2025
        "%b %d, %Y",     # Jan 15, 2025
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


def _classify_action(trans_code: str, description: str = "") -> RobinhoodActionType:
    """Classify Robinhood action type from trans code and description."""
    code_upper = trans_code.upper().strip()
    desc_upper = description.upper()
    
    # Buys
    if code_upper in ("BUY", "ACH", "DRIP"):
        if "DRIP" in desc_upper or "REINVEST" in desc_upper:
            return RobinhoodActionType.DIVIDEND_REINVEST
        return RobinhoodActionType.BUY
    
    # Sells
    if code_upper in ("SELL", "SLD"):
        return RobinhoodActionType.SELL
    
    # Dividends
    if code_upper in ("DIV", "CDIV") or "DIVIDEND" in desc_upper:
        return RobinhoodActionType.DIVIDEND
    
    # Stock splits
    if "SPLIT" in desc_upper or code_upper == "SPLIT":
        return RobinhoodActionType.STOCK_SPLIT
    
    # Transfers
    if "ACATS" in code_upper or "TRANSFER" in desc_upper:
        if "OUT" in desc_upper:
            return RobinhoodActionType.TRANSFER_OUT
        return RobinhoodActionType.TRANSFER_IN
    
    # Interest
    if code_upper == "INT" or "INTEREST" in desc_upper:
        return RobinhoodActionType.INTEREST
    
    # Options
    if "EXERCISE" in desc_upper:
        return RobinhoodActionType.OPTION_EXERCISE
    if "ASSIGNMENT" in desc_upper:
        return RobinhoodActionType.OPTION_ASSIGNMENT
    
    return RobinhoodActionType.UNKNOWN


def _extract_symbol(instrument: str, description: str = "") -> str:
    """Extract stock symbol from instrument or description."""
    # Instrument field usually has symbol directly
    if instrument and len(instrument) <= 6:
        return instrument.strip().upper()
    
    # Try to extract from description
    # Common formats: "AAPL - Apple Inc", "Buy AAPL"
    parts = description.split()
    for part in parts:
        cleaned = part.strip().upper().replace(",", "").replace("-", "")
        if len(cleaned) <= 5 and cleaned.isalpha():
            return cleaned
    
    return instrument.strip().upper() if instrument else ""


def parse_robinhood_csv(
    csv_content: str,
    symbol_filter: Optional[str] = None,
) -> RobinhoodParseResult:
    """
    Parse Robinhood CSV export.
    
    Args:
        csv_content: Raw CSV file content as string
        symbol_filter: Optional stock symbol to filter
        
    Returns:
        RobinhoodParseResult with parsed transactions
    """
    result = RobinhoodParseResult()
    
    try:
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(reader, start=2):
            result.raw_rows += 1
            
            try:
                # Normalize column names
                normalized = {k.lower().strip().replace(" ", "_"): v for k, v in row.items() if k}
                
                # Extract activity date
                date_str = (
                    normalized.get("activity_date") or
                    normalized.get("date") or
                    normalized.get("trade_date") or
                    ""
                )
                activity_date = _parse_date(date_str)
                if not activity_date:
                    result.errors.append(f"Row {row_num}: Could not parse date '{date_str}'")
                    continue
                
                # Extract other dates
                process_date = _parse_date(normalized.get("process_date", ""))
                settle_date = _parse_date(normalized.get("settle_date", ""))
                
                # Extract symbol
                instrument = normalized.get("instrument", "") or ""
                description = normalized.get("description", "") or ""
                symbol = _extract_symbol(instrument, description)
                
                # Apply symbol filter
                if symbol_filter and symbol != symbol_filter.upper():
                    continue
                
                # Extract trans code
                trans_code = normalized.get("trans_code", "") or ""
                
                # Extract quantity
                quantity = _parse_decimal(
                    normalized.get("quantity") or
                    normalized.get("shares") or
                    "0"
                ) or Decimal("0")
                
                # Extract price
                price = _parse_decimal(
                    normalized.get("price") or
                    normalized.get("share_price") or
                    ""
                )
                
                # Extract amount
                amount = _parse_decimal(
                    normalized.get("amount") or
                    normalized.get("total") or
                    ""
                )
                
                # Classify action
                action_type = _classify_action(trans_code, description)
                
                # Create transaction
                txn = RobinhoodTransaction(
                    activity_date=activity_date,
                    process_date=process_date,
                    settle_date=settle_date,
                    action=action_type,
                    symbol=symbol,
                    description=description,
                    quantity=quantity,
                    price=price,
                    amount=amount,
                    trans_code=trans_code,
                )
                
                result.transactions.append(txn)
                
                # Categorize
                if action_type == RobinhoodActionType.BUY:
                    result.buys.append({
                        "date": activity_date,
                        "symbol": symbol,
                        "shares": quantity,
                        "price": price,
                        "total": amount or (quantity * price if price else None),
                    })
                elif action_type == RobinhoodActionType.SELL:
                    result.sells.append({
                        "date": activity_date,
                        "symbol": symbol,
                        "shares": quantity,
                        "price": price,
                        "proceeds": amount,
                    })
                elif action_type in (RobinhoodActionType.DIVIDEND, RobinhoodActionType.DIVIDEND_REINVEST):
                    result.dividends.append({
                        "date": activity_date,
                        "symbol": symbol,
                        "amount": amount,
                        "reinvested": action_type == RobinhoodActionType.DIVIDEND_REINVEST,
                    })
                    
            except Exception as e:
                result.errors.append(f"Row {row_num}: {str(e)}")
                
    except Exception as e:
        result.errors.append(f"CSV parsing error: {str(e)}")
    
    return result


def calculate_cost_basis(
    buys: list[dict],
    method: str = "fifo"
) -> list[dict]:
    """
    Calculate cost basis for shares using specified method.
    
    Args:
        buys: List of buy transactions
        method: Cost basis method (fifo, lifo, avg)
        
    Returns:
        List of tax lots with cost basis
    """
    tax_lots = []
    
    for buy in buys:
        if buy.get("shares") and buy.get("price"):
            tax_lots.append({
                "date": buy["date"],
                "symbol": buy["symbol"],
                "shares": buy["shares"],
                "price": buy["price"],
                "cost_basis": buy["shares"] * buy["price"],
            })
    
    # Sort based on method
    if method.lower() == "fifo":
        tax_lots.sort(key=lambda x: x["date"])
    elif method.lower() == "lifo":
        tax_lots.sort(key=lambda x: x["date"], reverse=True)
    
    return tax_lots


def calculate_gain_loss(
    sells: list[dict],
    tax_lots: list[dict],
) -> list[dict]:
    """
    Calculate gain/loss for sales against tax lots.
    
    Args:
        sells: List of sell transactions
        tax_lots: List of available tax lots (FIFO order)
        
    Returns:
        List of sales with calculated gain/loss
    """
    sales_with_basis = []
    remaining_lots = [dict(lot) for lot in tax_lots]  # Copy
    
    for sell in sells:
        symbol = sell["symbol"]
        shares_to_match = sell["shares"]
        sale_price = sell["price"]
        sale_date = sell["date"]
        
        matched_lots = []
        total_cost = Decimal("0")
        
        for lot in remaining_lots:
            if lot["symbol"] != symbol or lot["shares"] <= 0:
                continue
            
            if shares_to_match <= 0:
                break
            
            shares_from_lot = min(lot["shares"], shares_to_match)
            cost_per_share = lot["price"]
            lot_cost = shares_from_lot * cost_per_share
            
            matched_lots.append({
                "acquisition_date": lot["date"],
                "shares": shares_from_lot,
                "cost_per_share": cost_per_share,
            })
            
            total_cost += lot_cost
            lot["shares"] -= shares_from_lot
            shares_to_match -= shares_from_lot
        
        proceeds = sell["shares"] * sale_price if sale_price else sell.get("proceeds", Decimal("0"))
        gain_loss = proceeds - total_cost if proceeds else None
        
        # Determine holding period
        term = "Unknown"
        if matched_lots:
            first_acq = matched_lots[0]["acquisition_date"]
            days_held = (sale_date - first_acq).days
            term = "Long" if days_held > 365 else "Short"
        
        sales_with_basis.append({
            **sell,
            "cost_basis": total_cost,
            "gain_loss": gain_loss,
            "term": term,
            "matched_lots": matched_lots,
        })
    
    return sales_with_basis


def extract_trading_summary(
    result: RobinhoodParseResult,
    year: Optional[int] = None,
) -> dict:
    """
    Extract trading summary from parse result.
    
    Args:
        result: Parsed Robinhood data
        year: Optional year to filter
        
    Returns:
        Summary dict
    """
    buys = result.buys
    sells = result.sells
    dividends = result.dividends
    
    if year:
        buys = [b for b in buys if b["date"].year == year]
        sells = [s for s in sells if s["date"].year == year]
        dividends = [d for d in dividends if d["date"].year == year]
    
    total_bought = sum(
        b["total"] for b in buys 
        if b.get("total") is not None
    )
    total_sold = sum(
        s["proceeds"] for s in sells 
        if s.get("proceeds") is not None
    )
    total_dividends = sum(
        d["amount"] for d in dividends 
        if d.get("amount") is not None
    )
    
    # Unique symbols traded
    all_symbols = set()
    for txn in result.transactions:
        if txn.symbol:
            all_symbols.add(txn.symbol)
    
    return {
        "year": year,
        "total_buys": len(buys),
        "total_sells": len(sells),
        "total_bought_value": total_bought,
        "total_sold_value": total_sold,
        "total_dividends": total_dividends,
        "unique_symbols": sorted(all_symbols),
    }
