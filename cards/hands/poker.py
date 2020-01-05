from enum import IntEnum
from typing import Dict, List, Set, Tuple

from ..deck import Card, Suit, VALUES
from .base import Hand

__all__ = ("evaluate",)


class Target(IntEnum):
    FIVE_OF_KIND = 9
    STRAIGHT_FLUSH = 8
    FOUR_OF_KIND = 7
    FULL_HOUSE = 6
    FLUSH = 5
    STRAIGHT = 4
    THREE_OF_KIND = 3
    PAIR_TWO = 2
    PAIR_ONE = 1
    HIGH = 0


def best_card(card: Card) -> Tuple[int, int]:
    return card.value, card.suit.value


def best_hand(pair: Tuple[Target, Set[Card]]) -> Tuple[int, int, int]:
    """Sort Key: Sort pairs of Target and Hand by best Target. On ties between
        Targets, prefer highest Value. On ties between Values, prefer "best"
        Suit.
    """
    targ, cards = pair
    best = max(cards, key=best_card)
    return targ.value, best.value, best.suit.value


def evaluate(hand: Hand) -> Tuple[Target, Set[Card]]:
    full = hand.full
    possible: List[Tuple[Target, Set[Card]]] = [
        (Target.HIGH, {max(full, key=best_card)}),
    ]

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

    return max(possible, key=best_hand)
