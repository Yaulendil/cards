from enum import IntEnum
from typing import Dict, List, Set, Tuple, Iterator, FrozenSet

from ..deck import Card, Suit, VALUES
from .base import Hand

__all__ = ("Combo", "evaluate", "evaluate_best", "Hand")


# Tuple representing total Hand Value. The first Int is the Target Class, and
#   all subsequent Ints are the values of the Cards in the Hand, by Value.
HandValue = Tuple[int, ...]


class Target(IntEnum):
    HIGH = 0
    PAIR_ONE = 1
    PAIR_TWO = 2
    THREE_OF_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_KIND = 7
    STRAIGHT_FLUSH = 8
    FIVE_OF_KIND = 9


TARGET_NAMES = (
    "High Card",
    "One Pair",
    "Two Pairs",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
    "Five of a Kind",
)


OAKS = {
    2: 1,
    3: 3,
    4: 7,
    5: 9,
}


STRAIGHTS: Tuple[Set[int], ...] = tuple(map(set, (range(i, i + 5) for i in range(9))))


def card_value(card: Card) -> int:
    return card.value


def best(cards: Set[Card], n: int = 5) -> Set[Card]:
    return set(sorted(list(cards))[-n:])


class Combo(object):
    __slots__ = ("cards", "hand", "target", "term", "value")

    def __init__(self, target: Target, cards: Set[Card], hand: Set[Card]):
        self.cards: FrozenSet[Card] = frozenset(cards)
        self.hand: FrozenSet[Card] = frozenset(hand)
        self.target: Target = target

        self.term: str = "Royal Flush" if (
            self.target is Target.STRAIGHT_FLUSH and max(self.cards) == len(VALUES)
        ) else TARGET_NAMES[self.target]
        self.value: HandValue = (
            self.target.value,
            *(c.value for c in sorted(self.cards, reverse=True)),
            *(c.value for c in sorted(self.hand, reverse=True)),
        )

    def __gt__(self, other: "Combo") -> bool:
        if isinstance(other, Combo):
            return self.value > other.value
        else:
            return NotImplemented

    def __lt__(self, other: "Combo") -> bool:
        if isinstance(other, Combo):
            return self.value < other.value
        else:
            return NotImplemented

    def __str__(self) -> str:
        return "{}: {}".format(
            self.term,
            ", ".join(map(repr, sorted(self.cards, reverse=True))),
            self.value,
        )


def evaluate(hand: Hand) -> Iterator[Combo]:
    full = hand.full
    yield Combo(Target.HIGH, {max(full)}, full)

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

    straights: List[Set[Card]] = []
    values: Set[int] = {card.value for card in full}

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
            yield Combo(targ, seq, full)

    # Check for TwoPairs.
    if len(oak[2]) >= 2:
        a, b = oak[2][-2:]
        yield Combo(Target.PAIR_TWO, a | b, full)

    # Check for each Straight.
    for seq in STRAIGHTS:
        if seq <= values:
            # This Straight is a subset of our Hand.
            straight = {card for card in full if card.value in seq}
            straights.append(straight)
            yield Combo(
                Target.STRAIGHT,
                {[card for card in full if card.value == i][0] for i in seq},
                full,
            )

    # Find Full Houses.
    over: Set[int] = {list(s)[0].value for s in oak[5] + oak[4] + oak[3]}
    under: Set[int] = over | {list(s)[0].value for s in oak[2]}
    if over and len(under) >= 2:
        # We have at least three of at least one Value, and at least two of at
        #   least two Values. Higher amounts must be considered, because a Hand
        #   of XXXYYYZ can yield FH XXXYY, but cannot yield 2oaK YY (it would
        #   instead yield 3oaK YYY).
        val_trip = max(over)
        val_pair = max(under - {val_trip})
        yield Combo(
            Target.FULL_HOUSE,
            {card for card in full if card == val_trip or card == val_pair},
            full,
        )

    # Calculate Flushes.
    for suit in Suit:
        sub = {card for card in full if card.suit == suit}

        if len(sub) >= 5:
            flushes[suit] = sub
            yield Combo(Target.FLUSH, best(sub, 5), full)
            strflush = None

            for straight in straights:
                isect = straight & sub
                if len(isect) >= 5:
                    strflush = isect

            if strflush:
                yield Combo(Target.STRAIGHT_FLUSH, best(strflush, 5), full)


def evaluate_best(hand: Hand) -> Combo:
    return max(evaluate(hand))
