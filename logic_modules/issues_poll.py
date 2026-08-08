"""
Voter Issues Priority Poll

In-memory live poll that tracks which issues voters care about most.
Provides vote, results, and reset endpoints for the web app.
"""

from threading import Lock

# Default issues voters can choose from
ISSUES = [
    "Housing",
    "Infrastructure",
    "Education",
    "Economy",
    "Halal Economy",
    "Senior Advocacy",
    "Healthcare",
    "Jobs & Wages"
]

# In-memory vote store: {issue_name: vote_count}
_votes = {issue: 0 for issue in ISSUES}
_lock = Lock()


def _initialize():
    """Ensure all issues exist in the vote store (handles resets/restarts)."""
    global _votes
    for issue in ISSUES:
        _votes.setdefault(issue, 0)


def vote(issue):
    """Increment the vote count for a given issue. Returns the issue name."""
    _initialize()
    if issue not in _votes:
        raise ValueError(f"Unknown issue: {issue}")
    with _lock:
        _votes[issue] += 1
    return issue


def results():
    """Return the current vote tally as a list of {issue, votes} dicts."""
    _initialize()
    with _lock:
        total = sum(_votes.values())
        data = [
            {
                "issue": issue,
                "votes": count,
                "percent": round((count / total * 100), 1) if total else 0.0
            }
            for issue, count in _votes.items()
        ]
    return {
        "issues": data,
        "total": total
    }


def reset():
    """Zero out all vote counts. Returns the fresh (empty) state."""
    global _votes
    with _lock:
        _votes = {issue: 0 for issue in ISSUES}
    return results()


def run(**kwargs):
    """Generic module bridge used by the web app's /api/<module> route."""
    action = kwargs.get('action', 'results')
    if action == 'vote':
        return vote(kwargs.get('issue', ''))
    if action == 'reset':
        return reset()
    return results()


# Ensure the store is initialized on import
_initialize()