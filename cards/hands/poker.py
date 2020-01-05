from enum import IntEnum
from typing import List, Set, Tuple

from ..deck import Card, Suit
from .base import Hand

__all__ = ("evaluate",)


_value = lambda card: card.value


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
    possible: List[Tuple[Target, Set[Card]]] = []

    oak2: List[Set[Card]] = []
    oak3: List[Set[Card]] = []
    oak4: List[Set[Card]] = []
    oak5: List[Set[Card]] = []

    return min(possible, key=lambda o: o[0].value)
