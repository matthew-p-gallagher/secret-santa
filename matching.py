import random
from typing import List, Set, Tuple


def generate_matches(
    participants: List[int], exclusions: List[Tuple[int, int]]
) -> dict:
    """
    Generate Secret Santa matches respecting exclusion pairs
    Args:
        participants: List of participant IDs
        exclusions: List of (giver_id, receiver_id) tuples that can't be matched
    Returns:
        Dictionary of {giver_id: receiver_id}
    """
    max_attempts = 100

    for _ in range(max_attempts):
        available_receivers = participants.copy()
        matches = {}
        success = True

        for giver in participants:
            valid_receivers = [
                r
                for r in available_receivers
                if r != giver
                and (giver, r) not in exclusions
                and (r, giver) not in exclusions
            ]

            if not valid_receivers:
                success = False
                break

            receiver = random.choice(valid_receivers)
            matches[giver] = receiver
            available_receivers.remove(receiver)

        if success and len(matches) == len(participants):
            return matches

    raise ValueError("Could not generate valid matches after maximum attempts")
