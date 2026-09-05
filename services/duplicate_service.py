from difflib import SequenceMatcher


def text_similarity(a, b):
    if not a or not b:
        return 0

    return SequenceMatcher(
        None,
        a.lower().strip(),
        b.lower().strip()
    ).ratio()


def calculate_duplicate_score(new_claim, old_claim):
    score = 0

    # Amount similarity
    try:
        new_amount = float(new_claim["amount"])
        old_amount = float(old_claim["amount"])

        if new_amount == old_amount:
            score += 40
        elif abs(new_amount - old_amount) <= 10:
            score += 25
    except Exception:
        pass

    # Merchant similarity
    merchant_score = text_similarity(
        new_claim.get("merchant", ""),
        old_claim.get("merchant", "")
    )

    score += merchant_score * 30

    # Description similarity
    description_score = text_similarity(
        new_claim.get("description", ""),
        old_claim.get("description", "")
    )

    score += description_score * 20

    # Same date
    if new_claim.get("expense_date") == old_claim.get("expense_date"):
        score += 10

    return round(min(score, 100), 2)