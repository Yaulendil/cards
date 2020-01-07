from typing import List, Set, Dict

from ..deck import Deck
from ..hands import Combo, evaluate_best, Hand
from .base import Game, Player


class PlayerHoldem(Player):
    __slots__ = ("hand", "name")

    def __init__(self, name: str, hand: Hand):
        self.hand: Hand = hand
        self.name: str = name

    def send(self, *a, **kw):
        print(*a, **kw)

    def take_turn(self, game: Game, turn: int):
        input("{}: {}\n  {}".format(self, self.hand, evaluate_best(self.hand.full)))

    def __str__(self) -> str:
        return self.name


class Holdem(Game):
    __slots__ = ("community", "deck", "discard", "playing", "pot")

    def __init__(self, nplayers: int):
        self.deck: Deck = Deck()
        self.deck.populate()
        self.deck.shuffle()
        self.discard: Deck = Deck()

        self.community: Hand = Hand(discard=self.discard, draw=self.deck)
        self.pot: int = 0

        self.players: List[PlayerHoldem] = []

        super().__init__(
            [
                PlayerHoldem(
                    f"Player {i + 1}",
                    Hand(self.community, discard=self.discard, draw=self.deck),
                )
                for i in range(nplayers)
            ]
        )
        self.playing: Set[PlayerHoldem] = set(self.players)

    def deal(self, n: int = 1):
        for _ in range(n):
            for p in self.players:
                if p in self.playing:
                    p.hand.draw(1)

    def go(self):
        try:
            self.play_hand()
        except (EOFError, KeyboardInterrupt):
            pass

    def play_hand(self):
        self.community.scrap()
        for p in self.players:
            p.hand.scrap()

        while len(self.discard) > 0:
            self.deck.add(self.discard.draw())

        self.deck.shuffle(3)
        self.playing: Set[PlayerHoldem] = set(self.players)
        self.deal(2)
        self.take_bets()

        self.community.draw(3)
        self.take_bets()

        self.community.draw(1)
        self.take_bets()

        self.community.draw(1)
        self.take_bets()

        hands: Dict[PlayerHoldem, Combo] = {
            p: evaluate_best(p.hand.full) for p in self.playing
        }
        best_hand: Combo = max(hands.values())
        winners = [p for p, h in hands.items() if h == best_hand]

        self.send()

        if (l := len(winners)) > 1:
            # self.send
            input(
                "Tie: {}; ${} each.\nWinning Hand: {}".format(
                    ", ".join("{} ({})".format(p, p.hand) for p in winners),
                    self.pot // l,  # round(self.pot / l, 2)
                    best_hand,
                )
            )
        elif l == 1:
            # self.send
            input(
                f"Winner: {winners[0]} ({winners[0].hand}); ${self.pot}."
                f"\nWinning Hand: {best_hand}"
            )
        else:
            # self.send
            input(f"No Winner; ${self.pot} donated to Cat Charity.")

    def send(self, *a, **kw):
        print(*a, **kw)

    def take_bets(self):
        self.full_turn()

    def turn_begin(self):
        self.send()
        self.send("Community Cards: {}".format(self.community or "None"))

    def turn_end(self):
        pass

    def turn_post(self, player: Player):
        pass

    def turn_pre(self, player: Player):
        pass
