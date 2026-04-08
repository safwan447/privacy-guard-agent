def calculate_pii_score(action, is_pii):
    """
    Returns scores STRICTLY between 0 and 1.
    """
    if (action == "REDACT" and is_pii) or (action == "KEEP" and not is_pii):
        return 0.85
    return 0.15