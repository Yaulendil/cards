from ..deck import Card, Deck
from ..hands import Combo, evaluate_best, Hand
from .base import Game, Player


class PlayerHoldem(Player):
    def __init__(self, hand: Hand):
        self.hand = hand

    def send(self, *a, **kw):
        print(*a, **kw)

    def take_turn(self, game: Game, turn: int):
        pass


class Holdem(Game):
    __slots__ = ("community", "deck", "discard")

    def __init__(self, nplayers: int):
        self.deck: Deck = Deck()
        self.deck.populate()
        self.deck.shuffle()

        self.discard: Deck = Deck()

        self.community: Hand = Hand(discard=self.discard, draw=self.deck)

        super().__init__(
            [
                PlayerHoldem(Hand(self.community, discard=self.discard, draw=self.deck))
                for _ in range(nplayers)
            ]
        )

    def turn_begin(self):
        pass

    def turn_end(self):
        pass

    def turn_post(self, player: Player):
        pass

    def turn_pre(self, player: Player):
        pass
