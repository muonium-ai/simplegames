from abc import ABC, abstractmethod


class Player(ABC):
    @abstractmethod
    def make_move(self, board):
        raise NotImplementedError