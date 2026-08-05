def run(budget=None, income=None, growth=None, years=None, **kwargs):
    """
    Policy-Impact Financial Simulator.
    Compares Abdul's proposed economic model against corporate benchmarks.

    Usage:
      /api/financial_simulator?budget=500&income=75000
      /api/financial_simulator?budget=1000&income=50000&growth=1.05&years=3
    """
    if budget is None or income is None:
        return (
            "--- FINANCIAL SIMULATOR ---\n"
            "Welcome to the Policy-Impact Calculator.\n\n"
            "This tool compares Abdul's proposed economic model against\n"
            "corporate benchmarks in real time.\n\n"
            "Enter your financial variables:\n"
            "  ?budget=500   (base cost in $)\n"
            "  ?income=75000 (annual income in $)\n"
            "  ?growth=1.05  (optional growth multiplier)\n"
            "  ?years=3      (optional projection years)\n\n"
            "Example: /financial?budget=500&income=75000"
        )

    try:
        b = float(budget)
        i = float(income)
    except (ValueError, TypeError):
        return "ERROR: 'budget' and 'income' must be numeric values."

    # Inflation models
    corporate_model = b * 1.25
    abdul_model = b * 0.60
    savings = corporate_model - abdul_model

    # Progressive tax rate logic
    rate = 0.02 if i <= 50000 else 0.085
    contribution = i * rate

    # Optional growth projection
    if growth:
        try:
            g = float(growth)
            y = int(years) if years else 1
            projected_savings = savings * ((1 + g) ** y)
        except (ValueError, TypeError):
            projected_savings = None
    else:
        projected_savings = None

    lines = []
    lines.append("╔══════════════════════════════════════════╗")
    lines.append("║        FINANCIAL IMPACT DASHBOARD        ║")
    lines.append("╚══════════════════════════════════════════╝")
    lines.append("")
    lines.append(f"  Base Cost : ${b:,.2f}")
    lines.append(f"  Income    : ${i:,.2f}")
    lines.append("")
    lines.append("  ── Inflation Model Comparison ──")
    lines.append(f"  Corporate Model : ${corporate_model:,.2f}")
    lines.append(f"  Abdul's Model   : ${abdul_model:,.2f}")
    lines.append(f"  YOU SAVE        : ${savings:,.2f}")
    lines.append("")
    lines.append("  ── Tax Contribution ──")
    lines.append(f"  Rate            : {rate*100:.1f}%")
    lines.append(f"  Contribution    : ${contribution:,.2f}")
    if projected_savings is not None:
        lines.append("")
        lines.append("  ── Growth Projection ──")
        lines.append(f"  Multiplier      : {g*100:.1f}%")
        lines.append(f"  Span            : {y} year(s)")
        lines.append(f"  Projected Value : ${projected_savings:,.2f}")
    lines.append("")
    lines.append("  ⚡ Status: Policy impact calculated live.")

    return "\n".join(lines)