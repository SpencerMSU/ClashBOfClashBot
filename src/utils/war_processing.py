"""Shared helpers for transforming Clan War API payloads into DB models."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

EXPECTED_ATTACKS_PER_MEMBER = 2


def analyze_member_violations(attacks: List[Dict[str, Any]]) -> int:
    """Count missing attacks for a member to detect simple violation cases."""
    total_attacks = len(attacks or [])
    if total_attacks >= EXPECTED_ATTACKS_PER_MEMBER:
        return 0
    return EXPECTED_ATTACKS_PER_MEMBER - total_attacks


def analyze_attacks(clan_data: Dict[Any, Any]) -> Tuple[int, int, Dict[str, List[Dict[str, Any]]]]:
    """Aggregate attack stats from clan war data."""
    members = clan_data.get("members", []) if clan_data else []
    total_attacks_used = 0
    total_violations = 0
    attacks_by_member: Dict[str, List[Dict[str, Any]]] = {}

    for member in members:
        member_tag = member.get("tag", "")
        member_attacks = member.get("attacks", []) or []
        total_attacks_used += len(member_attacks)
        total_violations += analyze_member_violations(member_attacks)

        if not member_attacks:
            continue

        attacks_by_member[member_tag] = [
            {
                "attacker_name": member.get("name", ""),
                "defender_tag": attack.get("defenderTag", ""),
                "stars": attack.get("stars", 0),
                "destruction": attack.get("destructionPercentage", 0.0),
                "order": attack.get("order", 0),
                "timestamp": 0,  # API does not expose timestamps for historic war attacks.
                "is_violation": 0,
            }
            for attack in member_attacks
        ]

    return total_attacks_used, total_violations, attacks_by_member


__all__ = ["analyze_attacks", "analyze_member_violations"]
