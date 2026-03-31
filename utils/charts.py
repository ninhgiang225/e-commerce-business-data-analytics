import plotly.graph_objects as go

# ── Palette ───────────────────────────────────────────────────────────────────
TEAL   = "#2BBFB3"
AMBER  = "#F5A623"
PURPLE = "#7B5EA7"
BLUE   = "#4A90D9"
GREEN  = "#5DB87A"
ROSE   = "#E8607A"
NAVY   = "#2C4A7C"

PALETTE = [TEAL, AMBER, PURPLE, BLUE, GREEN, ROSE, NAVY]

# Typography — clear, no blur
TITLE_COLOR = "#1A202C"
LABEL_COLOR = "#2D3748"    # darker than before — no more blur
GRID_COLOR  = "#EDF2F7"
FONT_FAMILY = "IBM Plex Sans, sans-serif"


def base_layout(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=64, r=32, t=72, b=60),   # t=72 so title never sits on legend
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=FONT_FAMILY, color=LABEL_COLOR, size=13),
        title_font=dict(size=15, color=TITLE_COLOR, family=FONT_FAMILY),
        title_pad=dict(t=4, b=16),              # space below title before chart
        legend=dict(
            orientation="v",
            yanchor="top",  y=1.0,
            xanchor="right", x=1.0,
            font=dict(size=12, color=LABEL_COLOR),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#CBD5E0",
            borderwidth=1,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#CBD5E0",
            font=dict(size=13, color=TITLE_COLOR),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#CBD5E0",
        linewidth=1,
        tickfont=dict(size=12, color=LABEL_COLOR),
        title_font=dict(size=13, color=LABEL_COLOR),
        title_standoff=16,
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        gridwidth=1,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(size=12, color=LABEL_COLOR),
        title_font=dict(size=13, color=LABEL_COLOR),
        title_standoff=16,
    )
    return fig


def fmt_currency(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:,.2f}"


def fmt_number(v: float) -> str:
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v:,.0f}"