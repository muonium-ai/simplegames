class Player(ABC):
    @abstractmethod
    def make_move(self, board):
        pass