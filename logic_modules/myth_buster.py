# ─── MYTH BUSTER ENGINE ──────────────────────────────────────
# To add a new myth, just add a new dictionary entry below.
# Each myth needs:
#   "title"  — The myth statement (displayed as Q: ...)
#   "fact"   — The truth (displayed as A: ...)
# That's it! The code handles the rest.
# ─────────────────────────────────────────────────────────────

MYTHS = [
    {
        "id": "1",
        "title": "Banning corporate money isolates a campaign.",
        "fact": "Dr. El-Sayed's campaigns successfully raise millions derived entirely from small-dollar grassroots contributions. People-powered > corporate-powered."
    },
    {
        "id": "2",
        "title": "Medicare for All expands bureaucratic cost.",
        "fact": "Over 30% of standard health expenditures are eaten by private insurance claims-processing walls. Single-payer eliminates that entirely — less bureaucracy, not more."
    },
    {
        "id": "3",
        "title": "A Green New Deal is too expensive.",
        "fact": "The cost of inaction on climate change far exceeds the investment. Lead pipe removal alone saves $188B in healthcare costs over 20 years."
    },
    {
        "id": "4",
        "title": "Small-dollar campaigns can't compete nationally.",
        "fact": "In 2024, grassroots-funded candidates outperformed PAC-funded opponents in 73% of tested districts. People, not billionaires, decide elections."
    },
]


def run(**kwargs):
    """
    Myth Buster Engine.
    Returns all myths in a clean Q&A format.

    To add a new myth: just add to the MYTHS list above.
    """
    lines = []
    lines.append("╔═══════════════════════════════════════════╗")
    lines.append("║            CAMPAIGN MYTH BUSTER           ║")
    lines.append("╚═══════════════════════════════════════════╝")
    lines.append("")

    for myth in MYTHS:
        lines.append(f"  ❓ Q: {myth['title']}")
        lines.append(f"  ✅ A: {myth['fact']}")
        lines.append("")

    lines.append("─" * 50)
    lines.append(f"  Total Myths Busted: {len(MYTHS)}")
    lines.append("  Status: Truth in progress.")

    return "\n".join(lines)