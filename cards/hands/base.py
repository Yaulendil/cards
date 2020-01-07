from collections import deque
from typing import Deque, Hashable, Iterator, Set

from ..deck import Card, Deck


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

    def discard(self, *cards: Card, pile: Deck = None, bottom: bool = False) -> None:
        dst: Deck = pile or self.pile_discard
        if not dst:
            raise ValueError("Nowhere to discard to.")

        for card in cards:
            if card in self.cards:
                self.cards.remove(card)
                dst.add(card, bottom=bottom)
            else:
                raise CardNotInHand(card)

    def draw(self, n: int, *, pile: Deck = None, bottom: bool = False) -> None:
        src: Deck = pile or self.pile_draw
        if not src:
            raise ValueError("Nowhere to draw cards from.")

        for _ in range(n):
            self.cards.append(src.draw(bottom=bottom))

    def dump(self, pile: Deck = None, *, bottom: bool = False) -> None:
        dst: Deck = pile or self.pile_discard
        if not dst:
            raise ValueError("Nowhere to discard to.")

        self.discard(*self.cards, pile=pile, bottom=bottom)

    def sort(self, reverse: bool = False) -> None:
        self.cards = sorted(self.cards, reverse=reverse)

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
        return ", ".join(map(repr, self)) if self.cards else "Empty Hand"
