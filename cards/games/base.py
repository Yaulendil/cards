from abc import ABC, abstractmethod
from typing import List


class Game(ABC):
    __slots__ = ("components", "players", "turn")

    def __init__(self, components, players: List["Player"]):
        self.components: dict = components
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

    @abstractmethod
    def turn_begin(self):
        ...

    @abstractmethod
    def turn_end(self):
        ...

    @abstractmethod
    def turn_post(self, player):
        ...

    @abstractmethod
    def turn_pre(self, player):
        ...


class Player(ABC):
    @abstractmethod
    def send(self, *a, **kw):
        ...

    @abstractmethod
    def take_turn(self, game: Game, turn: int):
        ...
