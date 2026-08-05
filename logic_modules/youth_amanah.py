import json

# ─── YOUTH ORGANIZATIONS ────────────────────────────────────
# To add a new organization, just add a new dictionary below.
# Fields: name, type, impact, urgency (Critical/High/Active)
# ─────────────────────────────────────────────────────────────

ORGANIZATIONS = [
    {"name": "Detroit Youth Collective", "type": "Mentorship Hub", "impact": "120 students mentored in 2025", "urgency": "Critical"},
    {"name": "Dearborn Youth Council", "type": "Civic Engagement", "impact": "Led 3 city council advocacy campaigns", "urgency": "High"},
    {"name": "Flint Youth Media Lab", "type": "Digital Arts", "impact": "Produced 8 student documentaries", "urgency": "Active"},
    {"name": "Hamtramck Youth Initiative", "type": "Community Garden", "impact": "Built 12 urban garden plots", "urgency": "Active"},
    {"name": "Grand Rapids Youth Radio", "type": "Media & Journalism", "impact": "Weekly broadcast on WYCE 88.1 FM", "urgency": "High"},
]


def load_data():
    try:
        with open('youth_data.json', 'r') as f:
            return json.load(f)
    except:
        return {}


def run(user_input=None, **kwargs):
    """
    Youth Amanah: Youth mentorship and education funding tracker.

    Usage: /api/youth_amanah
           /api/youth_amanah?user_input=help
    """
    if user_input and "help" in user_input.lower():
        return (
            "🔥 YOUTH HELP SYSTEM\n"
            "If you are a young person in crisis, contact:\n"
            "  Youth Crisis Line: 1-800-334-HELP\n"
            "  Campaign Youth Desk: (313) 555-YOUTH\n"
            "  Or text START to 22777"
        )

    lines = []
    lines.append("╔═══════════════════════════════════════════╗")
    lines.append("║     YOUTH MOMENTUM TRACKER               ║")
    lines.append("╚═══════════════════════════════════════════╝")
    lines.append("")

    for org in ORGANIZATIONS:
        if org['urgency'] == "Critical":
            badge = "🔥 CRITICAL"
        elif org['urgency'] == "High":
            badge = "⚡ HIGH"
        else:
            badge = "🌱 ACTIVE"

        lines.append(f"  {badge}")
        lines.append(f"  {org['name'].upper()} ({org['type']})")
        lines.append(f"     {org['impact']}")
        lines.append("")

    lines.append("─" * 50)
    lines.append(f"  Tracked Organizations: {len(ORGANIZATIONS)}")
    lines.append("  Total Youth Impacted: 840+")
    lines.append("  Status: Optimistic. Keep pushing!")

    return "\n".join(lines)