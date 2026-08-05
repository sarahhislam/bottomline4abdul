import random

# ─── PARTNER BUSINESSES ─────────────────────────────────────
# To add a business, just add a new dictionary to this list.
# Fields: name, type, impact, loc
# ─────────────────────────────────────────────────────────────

PARTNERS = [
    {"name": "Kitab Cafe", "type": "Bookstore & Cafe", "impact": "3 Youth Literacy Events", "loc": "Detroit, MI"},
    {"name": "Cannelle Detroit", "type": "Patisserie & Cafe", "impact": "Senior Outreach Sponsor", "loc": "Detroit, MI"},
    {"name": "A Taste of Marrakech", "type": "Moroccan Culinary", "impact": "Volunteer Catering Partner", "loc": "Dearborn, MI"},
    {"name": "Uyu Coffee", "type": "Specialty Coffee Shop", "impact": "Student Organizer Hub", "loc": "Detroit, MI"},
    {"name": "Cafe Sous Terre", "type": "Neighborhood Cafe", "impact": "Hosted 2 Policy Roundtables", "loc": "Detroit, MI"},
    {"name": "Zamzam Grocers", "type": "Grocery & Halal Butcher", "impact": "Food Security Partner", "loc": "Hamtramck, MI"},
    {"name": "Noor Textiles", "type": "Clothing & Tailoring", "impact": "Job Training Sponsor", "loc": "Dearborn, MI"},
]


def view_partnered_businesses():
    """Formats the partner businesses directory."""
    output = "PARTNERED MUSLIM-OWNED BUSINESSES\n" + "=" * 60 + "\n"
    for i, biz in enumerate(PARTNERS, 1):
        output += f"[{i}] {biz['name']} ({biz['type']}) | Impact: {biz['impact']} | Loc: {biz['loc']}\n"
    output += "=" * 60 + "\nTotal Active Network: 35+ District Businesses."
    return output


def calculate_financing_demo():
    """Interest-free financing calculator."""
    asset_value = 50000
    months = 36
    monthly_payment = round(asset_value / months, 2)
    return (
        "HALAL ASSET FINANCING SIMULATOR\n"
        "================================\n"
        f"Asset Value: ${asset_value:,}\n"
        "Interest: 0.0% (Strictly Interest-Free)\n"
        f"Term: {months} Months\n"
        f"Monthly Equity Buy-in: ${monthly_payment:,}/month\n"
        "--------------------------------\n"
        "[STRUCTURE]: Co-ownership model protects equity."
    )


def run(option=None, investment=50000, **kwargs):
    """
    Halal Economy & Community Financing dashboard.

    Usage:
      /api/halal_economy              → Menu overview
      /api/halal_economy?option=1     → Financing simulator
      /api/halal_economy?option=2     → View partnered businesses
      /api/halal_economy?option=3     → Policy brief
      /api/halal_economy?option=1&investment=25000  → Custom investment
    """
    # Logic for Option 1: Financing Simulator
    def get_financing():
        inv = float(investment)
        return (f"--- FINANCING SIMULATOR ---\n"
                f"Target: ${inv:,.2f}\n"
                f"Equity Buy-in: ${round(inv/36, 2):,.2f}/mo (0% Interest)")

    # Logic for Option 2: Partner Network
    def get_partners():
        output = "PARTNERED MUSLIM-OWNED BUSINESSES\n" + "=" * 60 + "\n"
        for i, biz in enumerate(PARTNERS, 1):
            output += f"[{i}] {biz['name']} ({biz['type']}) | Impact: {biz['impact']} | Loc: {biz['loc']}\n"
        output += "=" * 60 + f"\nTotal Active Network: 35+ District Businesses."
        return output

    # Logic for Option 3: Policy Brief
    def get_brief():
        return ("POLICY BRIEF: The Halal economy creates sustainable local growth "
                "by circulating capital within the district. Interest-free financing "
                "empowers small businesses and builds community wealth.")

    # Routing logic
    if option == "1":
        return get_financing()
    if option == "2":
        return get_partners()
    if option == "3":
        return get_brief()

    # Default Menu
    return ("--- HALAL ECONOMY DASHBOARD ---\n"
            "Select an option:\n"
            "[1] Financing Simulator\n"
            "[2] View Partner Network\n"
            "[3] Read Policy Brief")