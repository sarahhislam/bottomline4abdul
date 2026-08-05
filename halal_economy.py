import random
from logic_modules.simulation_history import log_event

# Example: Inside run_finance_demo()
log_event("Halal Asset Financing Simulation")
def view_partnered_businesses():
    """
    Displays a curated directory of Muslim-owned small businesses
    partnered with the campaign for community development.
    """
    print("\n" + "=" * 90)
    print(" PARTNERED MUSLIM-OWNED BUSINESSES ".center(90, "="))
    print("=" * 90)

    # Added location field to each dictionary
    partners = [
        {"name": "Kitab Cafe", "type": "Bookstore & Cafe", "impact": "3 Youth Literacy Events", "loc": "Detroit, MI"},
        {"name": "Cannelle Detroit", "type": "Patisserie & Cafe", "impact": "Senior Outreach Sponsor", "loc": "Detroit, MI"},
        {"name": "A Taste of Marrakech", "type": "Moroccan Culinary", "impact": "Volunteer Catering Partner", "loc": "Dearborn, MI"},
        {"name": "Uyu Coffee", "type": "Specialty Coffee Shop", "impact": "Student Organizer Hub", "loc": "Detroit, MI"},
        {"name": "Cafe Sous Terre", "type": "Neighborhood Cafe", "impact": "Hosted 2 Policy Roundtables", "loc": "Detroit, MI"},
        {"name": "Zamzam Grocers", "type": "Grocery & Halal Butcher", "impact": "Food Security Partner", "loc": "Hamtramck, MI"},
        {"name": "Noor Textiles", "type": "Clothing & Tailoring", "impact": "Job Training Sponsor", "loc": "Dearborn, MI"}
    ]

    # Updated header and formatting for the new column
    print(f" {'ID':<4} | {'Business Name':<20} | {'Type':<20} | {'Impact':<25} | {'Location'}")
    print("-" * 90)

    for i, biz in enumerate(partners, 1):
        print(f" [{i}]  | {biz['name']:<20} | {biz['type']:<20} | {biz['impact']:<25} | {biz['loc']}")

    print("-" * 90)
    print(" Total Active Network: 35+ District Businesses Onboarded")
    print("=" * 90)
    input("\nPress Enter to return to Halal Economy menu...")


def calculate_financing_demo():
    """
    Simulates a transparent, interest-free risk-sharing asset purchase template.
    """
    print("\n" + "=" * 60)
    print(" HALAL ASSET FINANCING SIMULATOR ".center(60, "="))
    print("=" * 60)

    # Concrete example scenario calculation
    asset_value = 50000
    months = 36
    monthly_payment = round(asset_value / months, 2)

    print(f" Simulating Capital Equipment Line for Small Business:")
    print(f"  * Asset Value          : ${asset_value:,}")
    print(f"  * Traditional Interest : 0.0% (Strictly Interest-Free)")
    print(f"  * Term Length          : {months} Months")
    print(f"  * Monthly Equity Buy-in: ${monthly_payment:,}/month")
    print("-" * 60)
    print(" [STRUCTURE]: Co-ownership model. The campaign framework protects")
    print(" equity balances and shares risk ratios transparently over time.")
    print("=" * 60)
    input("\nPress Enter to return to Halal Economy menu...")


def run_finance_demo():
    """
    Main interface entry point for Option [2] from app.py.
    """
    while True:
        print("\n" + "=" * 60)
        print(" HALAL ECONOMY & COMMUNITY FINANCING ".center(60, "="))
        print("=" * 60)
        print(" [1] Run Interest-Free Financing Calculation")
        print(" [2] View Partnered Muslim-Owned Businesses")
        print(" [3] Return to Main Campaign Dashboard")
        print("-" * 60)

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            calculate_financing_demo()
        elif choice == "2":
            view_partnered_businesses()
        elif choice == "3":
            print("\nReturning to main dashboard...")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")