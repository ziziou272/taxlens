"""
Command-line interface for TaxLens Engine.

Provides a simple CLI for tax calculations.
"""

import sys
from decimal import Decimal, InvalidOperation
from typing import Optional

import click

from taxlens_engine.models import FilingStatus, IncomeBreakdown
from taxlens_engine.calculator import calculate_taxes, format_tax_summary


def parse_money(value: str) -> Decimal:
    """Parse a money string to Decimal, handling common formats."""
    # Remove common formatting
    cleaned = value.replace("$", "").replace(",", "").strip()
    return Decimal(cleaned)


@click.group()
@click.version_option(version="0.1.0", prog_name="taxlens")
def cli():
    """TaxLens - Accurate tax calculations for tech employees."""
    pass


@cli.command()
@click.option(
    "--income", "-i",
    type=str,
    default="0",
    help="W-2 wage income (e.g., 300000 or $300,000)",
)
@click.option(
    "--rsu", "-r",
    type=str,
    default="0",
    help="RSU income (vested value, e.g., 150000)",
)
@click.option(
    "--nso",
    type=str,
    default="0",
    help="NSO exercise income (spread)",
)
@click.option(
    "--ltcg",
    type=str,
    default="0",
    help="Long-term capital gains",
)
@click.option(
    "--stcg",
    type=str,
    default="0",
    help="Short-term capital gains",
)
@click.option(
    "--dividends",
    type=str,
    default="0",
    help="Qualified dividends",
)
@click.option(
    "--interest",
    type=str,
    default="0",
    help="Interest income",
)
@click.option(
    "--iso-bargain",
    type=str,
    default="0",
    help="ISO bargain element (for AMT calculation)",
)
@click.option(
    "--state", "-s",
    type=click.Choice(["CA", "ca", "none"], case_sensitive=False),
    default="CA",
    help="State for state tax (CA or none)",
)
@click.option(
    "--status",
    type=click.Choice([
        "single", "married_jointly", "married_separately", "head_of_household",
        "s", "mfj", "mfs", "hoh"
    ], case_sensitive=False),
    default="single",
    help="Filing status (single, married_jointly, married_separately, head_of_household)",
)
@click.option(
    "--year", "-y",
    type=int,
    default=2025,
    help="Tax year",
)
@click.option(
    "--itemized",
    type=str,
    default="0",
    help="Itemized deductions (if greater than standard)",
)
@click.option(
    "--withheld-federal",
    type=str,
    default="0",
    help="Federal tax already withheld",
)
@click.option(
    "--withheld-state",
    type=str,
    default="0",
    help="State tax already withheld",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON instead of formatted text",
)
def calculate(
    income: str,
    rsu: str,
    nso: str,
    ltcg: str,
    stcg: str,
    dividends: str,
    interest: str,
    iso_bargain: str,
    state: str,
    status: str,
    year: int,
    itemized: str,
    withheld_federal: str,
    withheld_state: str,
    output_json: bool,
):
    """
    Calculate taxes based on income and filing status.
    
    Examples:
    
    \b
      # Simple W-2 income
      taxlens calculate --income 200000 --state CA --status single
    
    \b
      # Tech employee with RSU
      taxlens calculate --income 300000 --rsu 150000 --state CA --status married_jointly
    
    \b
      # Full scenario with capital gains
      taxlens calculate --income 300000 --rsu 150000 --ltcg 50000 --state CA --status mfj
    """
    try:
        # Parse status
        status_map = {
            "single": FilingStatus.SINGLE,
            "s": FilingStatus.SINGLE,
            "married_jointly": FilingStatus.MARRIED_JOINTLY,
            "mfj": FilingStatus.MARRIED_JOINTLY,
            "married_separately": FilingStatus.MARRIED_SEPARATELY,
            "mfs": FilingStatus.MARRIED_SEPARATELY,
            "head_of_household": FilingStatus.HEAD_OF_HOUSEHOLD,
            "hoh": FilingStatus.HEAD_OF_HOUSEHOLD,
        }
        filing_status = status_map[status.lower()]
        
        # Parse state
        state_code: Optional[str] = None
        if state.lower() != "none":
            state_code = state.upper()
        
        # Parse income values
        income_breakdown = IncomeBreakdown(
            w2_wages=parse_money(income),
            rsu_income=parse_money(rsu),
            nso_income=parse_money(nso),
            long_term_gains=parse_money(ltcg),
            short_term_gains=parse_money(stcg),
            qualified_dividends=parse_money(dividends),
            interest_income=parse_money(interest),
            iso_bargain_element=parse_money(iso_bargain),
        )
        
        # Calculate taxes
        result = calculate_taxes(
            income=income_breakdown,
            filing_status=filing_status,
            state=state_code,
            year=year,
            itemized_deductions=parse_money(itemized),
            federal_withheld=parse_money(withheld_federal),
            state_withheld=parse_money(withheld_state),
        )
        
        # Output
        if output_json:
            import json
            # Convert to dict with string decimals for JSON serialization
            result_dict = result.model_dump()
            # Convert Decimal to float for JSON
            def decimal_to_float(obj):
                if isinstance(obj, dict):
                    return {k: decimal_to_float(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decimal_to_float(v) for v in obj]
                elif isinstance(obj, Decimal):
                    return float(obj)
                return obj
            click.echo(json.dumps(decimal_to_float(result_dict), indent=2))
        else:
            click.echo(format_tax_summary(result))
    
    except InvalidOperation as e:
        click.echo(f"Error: Invalid number format: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def brackets():
    """Show 2025 federal tax brackets."""
    from taxlens_engine.models import FEDERAL_BRACKETS_2025
    
    click.echo("2025 Federal Tax Brackets")
    click.echo("=" * 60)
    
    for status in FilingStatus:
        click.echo(f"\n{status.value.replace('_', ' ').title()}")
        click.echo("-" * 40)
        brackets = FEDERAL_BRACKETS_2025[status]
        prev = Decimal("0")
        for threshold, rate in brackets:
            if threshold == Decimal("Infinity"):
                click.echo(f"  ${prev:>10,.0f}+        : {rate * 100:.0f}%")
            else:
                click.echo(f"  ${prev:>10,.0f} - ${threshold:>10,.0f}: {rate * 100:.0f}%")
                prev = threshold


@cli.command()
@click.option("--status", type=str, default="single", help="Filing status")
def deductions(status: str):
    """Show standard deductions for 2025."""
    from taxlens_engine.models import TaxYear
    from taxlens_engine.california import CA_STANDARD_DEDUCTIONS
    
    tax_year = TaxYear()
    
    click.echo("2025 Standard Deductions")
    click.echo("=" * 60)
    
    click.echo("\nFederal:")
    click.echo("-" * 40)
    for fs in FilingStatus:
        fed = tax_year.get_standard_deduction(fs)
        click.echo(f"  {fs.value.replace('_', ' ').title():<25}: ${fed:>10,.0f}")
    
    click.echo("\nCalifornia:")
    click.echo("-" * 40)
    for fs in FilingStatus:
        ca = CA_STANDARD_DEDUCTIONS[fs]
        click.echo(f"  {fs.value.replace('_', ' ').title():<25}: ${ca:>10,.0f}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
