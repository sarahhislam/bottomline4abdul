def run():
    # To add a new policy, just add a new line to this dictionary.
    policies = {
        "1": {
            "title": "Medicare for All Framework",
            "data": "Comprehensive single-payer architecture. Fully guarantees dental, vision, and mental healthcare with zero cost-sharing at delivery."
        },
        "2": {
            "title": "Green New Deal Blueprint",
            "data": "Infrastructure grid targeting lead pipe replacement networks and zero-emission municipal logistics across Michigan."
        },
        "3": {
            "title": "Corporate Super PAC Bans",
            "data": "Absolute ban on individual executive shell entities and campaign asset packaging via corporate lobbyists."
        },
        "4": {
            "title": "NEW POLICY TITLE",
            "data": "Details about the new policy go here."
        }
    }

    output = "=" * 60 + "\n"
    output += " POLICY DEEP DIVE ANALYSIS BACKEND ".center(60, "=") + "\n"
    output += "=" * 60 + "\n\n"
    output += "Select platform structure matrix to unpack:\n\n"

    # This loop handles everything automatically, no matter how many policies you add.
    for key, info in policies.items():
        output += f" [{key}] {info['title']}\n"
    
    output += "\n" + "-" * 60 + "\n"
    output += "Status: Ready for input."
    
    return output