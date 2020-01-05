from collections import deque
from enum import IntEnum
from random import shuffle
from secrets import randbelow
from typing import Deque, Final, Hashable, Iterator, Set, Tuple


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
        return f"{self.value}{self.suit!s}"

    def __str__(self) -> str:
        return f"{VALUES[self.value]} of {self.suit.name.title()}"


class DeckExhausted(Exception):
    pass


class Deck(object):
    __slots__ = ("data",)

    def __init__(self):
        self.data: Deque[Card] = deque()

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


class CardNotInHand(Exception):
    def __init__(self, card: Card):
        super().__init__(f"{card} is not in this Hand.")


class Hand(Hashable):
    __slots__ = ("cards", "community", "pile_discard", "pile_draw")

    def __init__(
        self, community: "Hand" = None, *, discard: Deck = None, draw: Deck = None
    ):
        self.cards: Deque[Card] = deque()
        self.community: Hand = community

        self.pile_discard: Deck = discard
        self.pile_draw: Deck = draw

    def discard(self, *cards: Card, pile: Deck = None) -> None:
        dst = pile or self.pile_discard
        if not dst:
            raise ValueError("Nowhere to discard to.")

        for card in cards:
            if card in self.cards:
                self.cards.remove(card)
                dst.add(card)
            else:
                raise CardNotInHand(card)

    def draw(self, n: int, *, pile: Deck = None) -> None:
        src = pile or self.pile_draw
        if not src:
            raise ValueError("Nowhere to draw cards from.")

        for _ in range(n):
            self.cards.append(src.draw())

    @property
    def full(self) -> Set[Card]:
        if self.community:
            return set(self.cards) | self.community.full
        else:
            return set(self.cards)

    def __contains__(self, item) -> bool:
        return item in self.cards

    def __hash__(self) -> int:
        o = 1

        for i in self.cards:
            o *= hash(i)

        return o

    def __iter__(self) -> Iterator[Card]:
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __str__(self) -> str:
        return "Hand of " + ", ".join(map(repr, self)) if self.cards else "Empty Hand"
