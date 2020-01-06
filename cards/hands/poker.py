from enum import IntEnum
from typing import Dict, List, Set, Tuple

from ..deck import Card, Suit, VALUES
from .base import Hand

__all__ = ("evaluate",)


# Tuple representing total Hand Value. The first Int is the Target Class, and
#   all subsequent Ints are the values of the Cards in the Hand, by Value.
HandValue = Tuple[int, ...]


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


OAKS = {
    2: 1,
    3: 3,
    4: 7,
    5: 9,
}


def best_card(card: Card) -> int:  #Tuple[int, int]:
    return card.value  #, card.suit.value


class Combo(object):
    __slots__ = ("cards", "hand", "target")

    def __init__(self, target: Target, cards: Set[Card], hand: Set[Card]):
        self.cards: Set[Card] = cards
        self.hand: Set[Card] = hand
        self.target: Target = target

    def value(self) -> HandValue:
        return (
            self.target.value,
            *(c.value for c in sorted(self.cards, key=best_card, reverse=True)),
            *(c.value for c in sorted(self.hand, key=best_card, reverse=True)),
        )

    def __str__(self) -> str:
        return "{}: {}\nValue: {!r}".format(
            self.target.name, ", ".join(map(str, list(self.cards))), self.value()
        )


def evaluate(hand: Hand) -> Combo:
    full = hand.full
    possible: List[Combo] = [
        Combo(Target.HIGH, {max(full, key=best_card)}, full),
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

    # Calculate NoaKs.
    for v in range(len(VALUES)):
        sub = {card for card in full if card.value == v}
        l = len(sub)

        if l in oak:
            oak[l].append(sub)

    # Add NoaKs to the Possibles.
    for number, cards in oak.items():
        targ = Target(OAKS[number])
        for seq in cards:
            possible.append(Combo(targ, seq, full))

    # Check for TwoPairs.
    if len(oak[2]) >= 2:
        a, b = oak[2][-2:]
        possible.append(Combo(Target.PAIR_TWO, a | b, full))

    # Calculate Flushes.
    for suit in Suit:
        sub = {card for card in full if card.suit == suit}

        if len(sub) >= 5:
            flushes[suit] = sub
            possible.append(Combo(Target.FLUSH, sub, full))

    return max(possible, key=Combo.value)
