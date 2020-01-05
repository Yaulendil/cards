from enum import IntEnum
from typing import Dict, List, Set, Tuple

from ..deck import Card, Suit, VALUES
from .base import Hand

__all__ = ("evaluate",)


_value = lambda card: card.value
_vsp = lambda card: (card.value, card.suit.value)


class Target(IntEnum):
    FIVE_OF_KIND = 0
    STRAIGHT_FLUSH = 1
    FOUR_OF_KIND = 2
    FULL_HOUSE = 3
    FLUSH = 4
    STRAIGHT = 5
    THREE_OF_KIND = 6
    PAIR_TWO = 7
    PAIR_ONE = 8
    HIGH = 9


def evaluate(hand: Hand) -> Tuple[Target, Set[Card]]:
    full = hand.full
    possible: List[Tuple[Target, Set[Card]]] = []

    # Flushes: Subsets of the Hand which all have the same Suit, keyed by Suit.
    flushes: Dict[Suit, Set[Card]] = {}

    # OAK: Of A Kind: Subsets of the Hand which all have the same Value, keyed
    #   by Number of a Kind.
    oak: Dict[int, List[Set[Card]]] = {
        2: [],
        3: [],
        4: [],
        5: [],
    }

    for v in range(len(VALUES)):
        sub = {card for card in full if card.value == v}
        l = len(sub)

        if l in oak:
            oak[l].append(sub)

    for suit in Suit:
        sub = {card for card in full if card.suit == suit}

        if len(sub) >= 5:
            flushes[suit] = sub

    if possible:
        return min(possible, key=lambda p: p[0].value)
    else:
        return Target.HIGH, {max(full, key=_vsp)}
