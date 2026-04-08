def calculate_pii_score(action, is_pii):
    """
    Logic for the pii_accuracy_grader.
    Returns scores STRICTLY between 0 and 1.
    """
    # Success cases
    if (action == "REDACT" and is_pii) or (action == "KEEP" and not is_pii):
        return 0.85
    # Failure cases
    return 0.15