from collections import deque
from enum import IntEnum, Enum
from random import shuffle
from secrets import randbelow
from typing import Deque, Final, Hashable, Iterator, Tuple


def rfloat(scale: int = 1000000) -> float:
    return randbelow(scale) / scale


PRIMES = (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79)
RANKS: Tuple[str, ...] = (
    "Joker",
    "Ace",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "Jack",
    "Queen",
    "King",
    "Ace",
)
SUITS = {
    2: chr(0x2663),
    3: chr(0x2666),
    5: chr(0x2665),
    7: chr(0x2660),
}


class Rank(IntEnum):
    JOKER = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self) -> str:
        return RANKS[self]


class Suit(IntEnum):
    CLUBS = 2
    DIAMONDS = 3
    HEARTS = 5
    SPADES = 7

    def __str__(self) -> str:
        return SUITS[self]


class Values(Tuple[Rank, ...], Enum):
    STANDARD = tuple(map(Rank, range(2, 15)))
    LOWBALL = tuple(map(Rank, range(1, 14)))

    def __str__(self) -> str:
        return self.name.title()


class Card(Hashable):
    __slots__ = ("rank", "suit")

    def __init__(self, rank: Rank, suit: Suit):
        self.rank: Final[int] = rank
        self.suit: Final[Suit] = suit

    def __hash__(self) -> int:
        return self.suit * PRIMES[self.rank]

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return hash(self) == hash(other)
        elif isinstance(other, Suit):
            return self.suit == other
        elif isinstance(other, int):
            return self.rank == other
        else:
            return NotImplemented

    def __gt__(self, other: "Card") -> bool:
        if isinstance(other, Card):
            return self.rank > other.rank
        else:
            return NotImplemented

    def __lt__(self, other: "Card") -> bool:
        if isinstance(other, Card):
            return self.rank < other.rank
        else:
            return NotImplemented

    def __repr__(self) -> str:
        name: str = RANKS[self.rank]

        if not name.isdigit():
            name = name[0]

        return f"{name:>2}{self.suit!s}"

    def __str__(self) -> str:
        return f"{RANKS[self.rank]} of {self.suit.name.title()}"


class DeckExhausted(Exception):
    pass


class Deck(object):
    __slots__ = ("data", "faceup")

    def __init__(self, faceup: bool = False):
        self.data: Deque[Card] = deque()
        self.faceup: bool = faceup

    def add(self, *cards: Card, bottom: bool = False) -> None:
        if bottom:
            self.data.extendleft(cards)
        else:
            self.data.extend(cards)

    def draw(self, *, bottom: bool = False) -> Card:
        if self.data:
            if bottom:
                return self.data.popleft()
            else:
                return self.data.pop()
        else:
            raise DeckExhausted

    def populate(self, variant: Values = Values.STANDARD) -> None:
        self.data.extend(Card(rank, suit) for suit in Suit for rank in variant)

    def shuffle(self, n: int = 1) -> None:
        for _ in range(n):
            shuffle(self.data, rfloat)

    def __contains__(self, item) -> bool:
        return item in self.data

    def __iter__(self) -> Iterator[Card]:
        return iter(self.data)

    def __len__(self):
        return len(self.data)
