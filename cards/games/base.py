from abc import ABC, abstractmethod
from typing import Callable, List, Optional


class Game(ABC):
    __slots__ = ("players", "turn")

    def __init__(self, players: List["Player"]):
        self.players: List["Player"] = players
        self.turn: int = 0

    def send(self, *a, **kw):
        for player in self.players:
            player.send(*a, **kw)

    def full_turn(self):
        self.turn_begin()

        for player in self.players:
            self.turn_pre(player)
            player.take_turn(self, self.turn)
            self.turn_post(player)

        self.turn_end()
        self.turn += 1

    def loop_basic(
        self, win_condition: Callable[["Game"], Optional["Player"]]
    ) -> "Player":
        """A simplistic "example" Game Loop. Given a "Win Condition" Function
            which takes a Game as its only argument, run Turns of the Game until
            the Function returns a Winner.
        """
        while (winner := win_condition(self)) is None:
            self.full_turn()

        return winner

    @abstractmethod
    def turn_begin(self):
        ...

    @abstractmethod
    def turn_end(self):
        ...

    @abstractmethod
    def turn_post(self, player: "Player"):
        ...

    @abstractmethod
    def turn_pre(self, player: "Player"):
        ...


class Player(ABC):
    __slots__ = ()

    @abstractmethod
    def send(self, *a, **kw):
        ...

    @abstractmethod
    def take_turn(self, game: Game, turn: int):
        ...
