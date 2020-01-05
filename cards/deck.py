from collections import deque
from enum import IntEnum
from random import shuffle
from secrets import randbelow
from typing import Deque, Final, Hashable, Iterator, Tuple


ICONS_SUIT = {
    2: chr(0x2663),
    3: chr(0x2666),
    5: chr(0x2665),
    7: chr(0x2660),
}
PRIMES = (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59)
VALUES: Tuple[str, ...] = (
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

COURT = {9, 10, 11}


def rfloat(scale: int = 1000000) -> float:
    return randbelow(scale) / scale


class Suit(IntEnum):
    CLUBS = 2
    DIAMONDS = 3
    HEARTS = 5
    SPADES = 7

    def __str__(self) -> str:
        return ICONS_SUIT[self]


class Card(Hashable):
    __slots__ = ("suit", "value")

    def __init__(self, suit: Suit, value: int):
        self.suit: Final[Suit] = suit
        self.value: Final[int] = value

    def __hash__(self) -> int:
        return self.suit * PRIMES[self.value]

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return hash(self) == hash(other)
        elif isinstance(other, Suit):
            return self.suit == other
        elif isinstance(other, int):
            return self.value == other
        else:
            return NotImplemented

    def __repr__(self) -> str:
        return f"{VALUES[self.value][:2]}{self.suit!s}"

    def __str__(self) -> str:
        return f"{VALUES[self.value]} of {self.suit.name.title()}"


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

    def populate(self) -> None:
        self.data.extend(
            Card(suit, value) for suit in Suit for value in range(len(VALUES))
        )

    def shuffle(self, n: int = 1) -> None:
        for _ in range(n):
            shuffle(self.data, rfloat)

    def __contains__(self, item) -> bool:
        return item in self.data

    def __iter__(self) -> Iterator[Card]:
        return iter(self.data)

    def __len__(self):
        return len(self.data)
