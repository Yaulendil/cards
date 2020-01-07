from abc import ABC
from typing import List, Set, Dict

from ..deck import Deck
from ..hands import Combo, evaluate_best, Hand
from .base import Game, Player


class PlayerHoldem(Player, ABC):
    __slots__ = ("hand", "name")

    def __init__(self, name: str, hand: Hand):
        self.hand: Hand = hand
        self.name: str = name

    def __str__(self) -> str:
        return self.name


class PlayerHuman(PlayerHoldem):
    def send(self, *a, **kw):
        print(*a, **kw)

    def take_turn(self, game: Game, turn: int):
        input(
            "Round {}: {}\n  {}\n  {} Action: ".format(
                turn, self.hand, evaluate_best(self.hand.full), self.name
            )
        )


class PlayerBot(PlayerHoldem):
    def send(self, *a, **kw):
        pass

    def take_turn(self, game: Game, turn: int):
        ...


class Holdem(Game):
    __slots__ = ("community", "deck", "discard", "playing", "pot")

    def __init__(self, humans: int = 1, bots: int = 4):
        self.deck: Deck = Deck()
        self.deck.populate()
        self.deck.shuffle()
        self.discard: Deck = Deck()

        self.community: Hand = Hand(discard=self.discard, draw=self.deck)
        self.pot: int = 0

        self.players: List[PlayerHoldem] = []

        hand = lambda: Hand(self.community, discard=self.discard, draw=self.deck)

        super().__init__(
            [
                *(PlayerHuman(f"Player {i + 1}", hand(),) for i in range(humans)),
                *(PlayerBot(f"Bot {i + 1}", hand(),) for i in range(bots)),
            ]
        )
        self.playing: Set[PlayerHoldem] = set(self.players)

    def deal(self, n: int = 1):
        for _ in range(n):
            for p in self.players:
                if p in self.playing:
                    p.hand.draw(1)
                    p.hand.sort(True)

    def go(self):
        try:
            self.play_hand()
        except (EOFError, KeyboardInterrupt):
            pass

    def play_hand(self):
        # Reset Turn counter.
        self.turn = 0

        # Discard all.
        self.community.scrap()
        for p in self.players:
            p.hand.scrap()

        # Return Discard to Deck.
        while len(self.discard) > 0:
            self.deck.add(self.discard.draw())

        # Shuffle, deal, and begin.
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
            p: evaluate_best(p.hand.full) for p in self.players if p in self.playing
        }
        best_hand: Combo = max(hands.values())
        winners = [p for p, h in hands.items() if h == best_hand]

        self.send(
            "".join(
                "\n{:>8} :: {} :: {!r}".format(p.name, p.hand, h)
                for p, h in hands.items()
            ),
        )

        if (l := len(winners)) > 1:
            self.send(
                "\nTie: {}; ${} each.\nWinning Hand: {!r}".format(
                    ", ".join("{} ({})".format(p, p.hand) for p in winners),
                    self.pot // l,  # round(self.pot / l, 2)
                    best_hand,
                )
            )
        elif l == 1:
            self.send(
                f"\nWinner: {winners[0]} ({winners[0].hand}); ${self.pot}."
                f"\nWinning Hand: {best_hand!r}"
            )
        else:
            self.send(f"\nNo Winner; ${self.pot} donated to Cat Charity.")

    def send(self, *a, **kw):
        for p in self.players:
            p.send(*a, **kw)

    def take_bets(self):
        self.full_turn()

    def turn_begin(self):
        self.send()
        if self.community:
            self.send("Community Cards: {}".format(self.community))

    def turn_end(self):
        pass

    def turn_post(self, player: Player):
        pass

    def turn_pre(self, player: Player):
        pass
