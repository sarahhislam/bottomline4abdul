import random
import os

ARCHIVE_FILE = "classified_archives.txt"

# ─── VAULT DATA ──────────────────────────────────────────────
# To add new lore, secrets, or system statuses, just add a new
# string to the appropriate list below. Easy as pie.

VAULT = {
    "LORE": [
        "The campaign logo was inspired by a 1970s Detroit transit map.",
        "Abdul once debated a squirrel on economic policy for 20 minutes.",
        "The 'Youth Amanah' module code is hidden behind a poem about the riverfront.",
        "There is a hidden command to turn the entire site into 'Dark Mode'.",
        "A time capsule is buried under the campaign headquarters parking lot.",
        "The policy database runs on a repurposed PlayStation 3.",
    ],
    "SYSTEM_STATUS": [
        "Servers running at 110% capacity. Cooling fans are screaming.",
        "Detected unauthorized access to the Treasury model. Good luck.",
        "The simulated 'Halal Economy' is currently outperforming reality.",
        "Neural network has started writing its own campaign speeches.",
        "Quantum encryption layer: ACTIVE. NSA decryption estimate: 42 years.",
        "Backup battery: powered by a hamster wheel. Hamster is unionizing.",
    ],
    "STAFF_SECRETS": [
        "Campaign Manager is secretly a competitive bird-watcher.",
        "Design lead has a secret stash of emergency snacks in the server room.",
        "Every policy document has at least one typo that acts as a watermarked 'trap'.",
        "The interns are technically running the world.",
        "Chief Strategist writes policy drafts as rap lyrics first, then translates.",
        "Outdated: Coffee machine has been promoted to Junior Policy Advisor.",
    ],
    "HIDDEN_POLICY": [
        "Proposing free coffee for every citizen within 5 miles of a library.",
        "Declaring the last Friday of every month 'Pizza Diplomacy Day'.",
        "Mandatory 15-minute nap time for all district officials.",
        "Establishing a formal alliance with the local neighborhood cats.",
        "Requiring all committee meetings to include a Lego-building exercise.",
        "Proposal to replace congressional ties with bow ties. Mandatory.",
    ],
}


def glitch_text(text):
    """Adds 'corrupted' noise to the logs for aesthetic effect."""
    glitch_chars = "¡™£¢∞§¶•ªº–≠µøœ€´®†¥¨ˆøπåß∂ƒ©˙∆˚¬…æ¥≈√∫Ω"
    return "".join(
        random.choice(glitch_chars) if random.random() < 0.04 else c
        for c in text
    )


def run(unlock=None, **kwargs):
    """
    The Vault: View classified campaign logs, lore, and secrets.

    Usage:
      /api/simulation_history                → Shows sealed archive
      /api/simulation_history?unlock=abdulwillbenchtovictory26  → Unlocks classified intel
    """
    # ─── MASTER KEY UNLOCK ────────────────────────────────
    if unlock == "abdulwillbenchtovictory26":
        category = random.choice(list(VAULT.keys()))
        entry = random.choice(VAULT[category])
        return (
            f"╔═══════════════════════════════════════════╗\n"
            f"║  🔓 CLASSIFIED ARCHIVE UNLOCKED          ║\n"
            f"║  CATEGORY: {category:<31} ║\n"
            f"╚═══════════════════════════════════════════╝\n\n"
            f"  {entry}\n\n"
            f"  ─── Decryption: Complete ───"
        )

    if unlock:
        return (
            f"╔═══════════════════════════════════════════╗\n"
            f"║  🚫 ACCESS DENIED                        ║\n"
            f"╚═══════════════════════════════════════════╝\n\n"
            f"  Key '{unlock}' is invalid.\n"
            f"  Hint: Try the campaign's launch year key."
        )

    # ─── DEFAULT: SEALED ARCHIVE ─────────────────────────
    if not os.path.exists(ARCHIVE_FILE):
        return (
            "╔═══════════════════════════════════════════╗\n"
            "║  📦 ARCHIVE STATUS: SEALED               ║\n"
            "╚═══════════════════════════════════════════╝\n\n"
            "  The classified simulation archive is\n"
            "  encrypted and locked.\n\n"
            "  To access, provide an unlock code:\n"
            "  ?unlock=XXXXXXXXXX\n\n"
            "  Categories locked inside:\n"
            f"    📜 Lore ({len(VAULT['LORE'])} entries)\n"
            f"    ⚙️  System Statuses ({len(VAULT['SYSTEM_STATUS'])} entries)\n"
            f"    🤫 Staff Secrets ({len(VAULT['STAFF_SECRETS'])} entries)\n"
            f"    📋 Hidden Policies ({len(VAULT['HIDDEN_POLICY'])} entries)\n"
        )

    # ─── FILE LOGS (if archive file exists) ──────────────
    with open(ARCHIVE_FILE, "r") as f:
        data = f.read()
    return glitch_text(
        f"--- SIMULATION LOGS [CORRUPTED] ---\n\n"
        f"{data if data else 'No simulations recorded.'}"
    )


def log_event(event_name, details):
    """Appends to the secret log file on disk."""
    try:
        with open(ARCHIVE_FILE, "a") as f:
            f.write(f"[{event_name}] - {details} | ID: {random.randint(1000, 9999)}\n")
    except Exception:
        pass