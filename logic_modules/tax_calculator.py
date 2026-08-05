def run(base=None, income=None, **kwargs):
    # If no input is provided, show the user how to use the calculator
    if base is None or income is None:
        return (
            "--- INTERACTIVE FINANCIAL CALCULATOR ---\n"
            "Status: Awaiting input parameters.\n\n"
            "USAGE: Append '?base=1000&income=75000' to the URL.\n"
            "Example: /tax?base=500&income=50000"
        )
    
    # Force conversion to numbers so the math works
    try:
        b, i = float(base), float(income)
    except ValueError:
        return "ERROR: Please provide numeric values for 'base' and 'income'."

    # Logic Engine
    corporate_model = b * 1.25
    abdul_model = b * 0.60
    savings = corporate_model - abdul_model
    
    # Progressive tax rate logic
    rate = 0.02 if i <= 50000 else 0.085
    contribution = i * rate
    
    return (
        f"--- FINANCIAL IMPACT DASHBOARD ---\n"
        f"Base Cost: ${b:,.2f} | Annual Income: ${i:,.2f}\n\n"
        f"INFLATION SAVINGS (Comparison):\n"
        f" • Corporate Model : ${corporate_model:,.2f}\n"
        f" • Abdul's Model   : ${abdul_model:,.2f}\n"
        f" • TOTAL SAVINGS   : ${savings:,.2f}\n\n"
        f"TAX CALCULATION (Progressive):\n"
        f" • Effective Rate  : {rate*100:.1f}%\n"
        f" • Contribution    : ${contribution:,.2f}\n\n"
        "STATUS: Calibration complete. Calculations are live."
    )