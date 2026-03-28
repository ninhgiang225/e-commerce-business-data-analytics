"""Shared formatting utilities and design tokens."""

PALETTE: list[str] = [
    "#0EA5E9", "#38BDF8", "#0369A1", "#F59E0B", "#10B981", "#8B5CF6", "#F43F5E",
]
CHART_TEMPLATE: str = "plotly_white"


def fmt_currency(value: float, symbol: str = "$") -> str:
    """Format float as currency with K/M suffix."""
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000:
        return f"{sign}{symbol}{abs_val / 1_000_000:.1f}M"
    if abs_val >= 1_000:
        return f"{sign}{symbol}{abs_val / 1_000:.1f}K"
    return f"{sign}{symbol}{abs_val:,.2f}"


def fmt_number(value: float) -> str:
    """Format float with K/M suffix."""
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.1f}M"
    if abs_val >= 1_000:
        return f"{sign}{abs_val / 1_000:.1f}K"
    return f"{sign}{abs_val:,.0f}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format float as percentage string."""
    return f"{value:.{decimals}%}"