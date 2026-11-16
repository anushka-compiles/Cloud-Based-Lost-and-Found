from datetime import datetime


def calculate_match_score(item_a, item_b):
    """
    Calculate a rule-based match score between two items.

    Maximum score: 100
    """

    score = 0

    # Only compare LOST with FOUND
    if item_a.get("item_type") == item_b.get("item_type"):
        return 0

    # Same category
    if (
        item_a.get("category", "").strip().lower()
        == item_b.get("category", "").strip().lower()
    ):
        score += 35

    # Same location
    if (
        item_a.get("location", "").strip().lower()
        == item_b.get("location", "").strip().lower()
    ):
        score += 25

    # Matching words in item name
    name_a = set(
        item_a.get("name", "").lower().split()
    )

    name_b = set(
        item_b.get("name", "").lower().split()
    )

    common_words = name_a.intersection(name_b)

    if common_words:
        score += min(len(common_words) * 10, 30)

    # Compare dates
    date_a = item_a.get("date")
    date_b = item_b.get("date")

    if date_a and date_b:

        try:

            date_a = datetime.strptime(
                date_a,
                "%Y-%m-%d"
            ).date()

            date_b = datetime.strptime(
                date_b,
                "%Y-%m-%d"
            ).date()

            difference = abs(
                (date_a - date_b).days
            )

            if difference == 0:
                score += 10

            elif difference <= 2:
                score += 5

        except ValueError:
            pass

    return min(score, 100)


def find_matches(item, all_items, minimum_score=40):
    """
    Find possible matches for an item.

    Returns matches sorted by highest score.
    """

    matches = []

    for other_item in all_items:

        # Don't match an item with itself
        if (
            other_item.get("item_id")
            == item.get("item_id")
        ):
            continue

        score = calculate_match_score(
            item,
            other_item
        )

        if score >= minimum_score:

            matches.append({
                "item": other_item,
                "score": score
            })

    # Highest score first
    matches.sort(
        key=lambda match: match["score"],
        reverse=True
    )

    return matches