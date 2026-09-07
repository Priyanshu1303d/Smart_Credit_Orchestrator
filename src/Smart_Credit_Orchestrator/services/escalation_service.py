"""
Escalation Service – maps days_overdue to a tone stage (1-4) or escalation flag.

Escalation Matrix (from the assignment):
  Stage 1 →  1–7  days  (Warm & Friendly)
  Stage 2 →  8–14 days  (Polite but Firm)
  Stage 3 → 15–21 days  (Formal & Serious)
  Stage 4 → 22–30 days  (Stern & Urgent)
  Escalate → 30+  days  (Flag for Legal Review — no email sent)
"""

TONE_LABELS = {
    1: "Warm & Friendly",
    2: "Polite but Firm",
    3: "Formal & Serious",
    4: "Stern & Urgent",
}


def resolve_stage(days_overdue: int) -> tuple[int, bool]:
    """
    Returns (tone_stage, is_escalated).
    is_escalated=True means skip email generation and flag for legal review.
    """
    if days_overdue > 30:
        return 4, True
    if days_overdue >= 22:
        return 4, False
    if days_overdue >= 15:
        return 3, False
    if days_overdue >= 8:
        return 2, False
    return 1, False
