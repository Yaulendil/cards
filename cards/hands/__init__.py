from enum import IntEnum
from typing import Dict, FrozenSet, Iterable, Iterator, List, Set, Tuple

from ..deck import Card, Suit
from .base import Hand

__all__ = ("Combo", "evaluate", "evaluate_best", "Hand")


# Tuple representing total Hand Value. The first Int is the Target Class, and
#   all subsequent Ints are the values of the Cards in the Hand, by Value.
HandRank = Tuple[int, ...]


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
    "Two Pair",
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


def best(cards: Set[Card], n: int = 5) -> Set[Card]:
    return set(sorted(list(cards))[-n:])


class Combo(object):
    __slots__ = ("cards", "hand", "kicker", "main", "rank", "target", "term")

    def __init__(self, target: Target, cards: Iterable[Card], hand: Set[Card]):
        self.cards: FrozenSet[Card] = frozenset(cards)
        self.hand: FrozenSet[Card] = frozenset(hand)

        self.target: Target = target
        self.main: Tuple[Card, ...] = tuple(cards)
        self.kicker: Tuple[Card, ...] = tuple(
            sorted((c for c in self.hand - self.cards), reverse=True)[
                : 5 - len(self.main)
            ]
        )

        self.rank: HandRank = (self.target.value, *self.main, *self.kicker)
        self.term: str = TARGET_NAMES[self.target]
        high, low = max(self.cards), min(self.cards)

        if self.target == Target.HIGH:
            self.term = "{!s} High".format(high.rank)

        elif high == 14:
            if self.target == Target.STRAIGHT_FLUSH:
                self.term = "Royal Flush"
            elif self.target == Target.STRAIGHT:
                self.term = "Broadway Straight"

        elif high == 5:
            if self.target == Target.STRAIGHT_FLUSH:
                self.term = "Steel Wheel"
            elif self.target == Target.STRAIGHT:
                self.term = "Baby Straight"

    def __eq__(self, other: "Combo") -> bool:
        if isinstance(other, Combo):
            return self.rank == other.rank
        else:
            return NotImplemented

    def __gt__(self, other: "Combo") -> bool:
        if isinstance(other, Combo):
            return self.rank > other.rank
        else:
            return NotImplemented

    def __lt__(self, other: "Combo") -> bool:
        if isinstance(other, Combo):
            return self.rank < other.rank
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return "{}: {}".format(self.term, ", ".join(map(repr, self.main))) + (
            " (+{})".format(", ".join(map(repr, self.kicker))) if self.kicker else ""
        )

    def __str__(self) -> str:
        return "{}: {}".format(self.term, ", ".join(map(repr, self.main)))


def evaluate(hand: Set[Card]) -> Iterator[Combo]:
    if not hand:
        return

    # Always yield at least a High Card.
    yield Combo(Target.HIGH, [max(hand)], hand)

    # OAK: Of A Kind: Subsets of the Hand which all have the same Rank, keyed by
    #   Number of a Kind.
    oak: Dict[int, List[Set[Card]]] = {
        2: [],
        3: [],
        4: [],
        5: [],
    }

    straights: List[Set[Card]] = []
    ranks: Set[int] = {card.rank for card in hand}

    # Calculate NoaKs.
    for r in ranks:
        sub = {card for card in hand if card.rank == r}
        l = len(sub)

        if l in oak:
            oak[l].append(sub)

    # Add NoaKs to the Possibles.
    for number, cards in oak.items():
        targ = Target(OAKS[number])
        for seq in cards:
            yield Combo(targ, sorted(seq), hand)

    # Check for TwoPairs.
    if len(oak[2]) >= 2:
        a, b = map(set, sorted(map(tuple, oak[2]))[-2:])
        yield Combo(Target.PAIR_TWO, sorted(a | b, reverse=True), hand)

    # Check for each Straight.
    for seq in STRAIGHTS:
        if seq <= ranks:
            # This Straight is a subset of our Hand.
            straight = {card for card in hand if card.rank in seq}
            straights.append(straight)
            yield Combo(
                Target.STRAIGHT,
                sorted(
                    ([card for card in hand if card.rank == i][0] for i in seq),
                    reverse=True,
                ),
                hand,
            )

    # Find Full Houses.
    over: Set[int] = {list(s)[0].rank for s in oak[5] + oak[4] + oak[3]}
    under: Set[int] = over | {list(s)[0].rank for s in oak[2]}
    if over and len(under) >= 2:
        # We have at least three of at least one Rank, and at least two of at
        #   least two Ranks. Higher amounts must be considered, because a Hand
        #   of XXXYYYZ can yield FH XXXYY, but cannot yield 2oaK YY (it would
        #   instead yield 3oaK YYY).
        val_trip = max(over)
        val_pair = max(under - {val_trip})
        yield Combo(
            Target.FULL_HOUSE,
            [card for card in hand if card == val_trip][:3]
            + [card for card in hand if card == val_pair][:2],
            hand,
        )

    # Calculate Flushes.
    for suit in Suit:
        flush = {card for card in hand if card.suit == suit}

        if len(flush) >= 5:
            yield Combo(Target.FLUSH, sorted(best(flush, 5), reverse=True), hand)

            for straight in straights[::-1]:
                # If any Straight set is a subset of a Flush set, it is a
                #   Straight Flush.
                if straight <= flush:
                    yield Combo(
                        Target.STRAIGHT_FLUSH,
                        sorted(best(straight, 5), reverse=True),
                        hand,
                    )
                    break


def evaluate_best(hand: Set[Card]) -> Combo:
    return max(evaluate(hand))
