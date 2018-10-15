# creating a simple minesweeper game
from enum import Enum
from json import JSONEncoder, dumps
from random import shuffle

from pprint import pprint

class GameState(Enum):
    READY = 0
    INPROGRESS = 1
    WON = 2
    LOST = 3


class GameStateResponse:
    def __init__(self, state: GameState, board_layout):
        super().__init__()
        self.state = state.value
        self.board_layout = board_layout


class Game:
    def __init__(self, height, width, mines):
        self.height = height
        self.width = width
        self.mines = mines
        self.pieces_revealed = 0
        self.state = GameState.READY
        self.board_state = [[Piece(h, w, self, 0) for w in range(self.width)] for h in range(self.height)]

    def game_lost(self):
        self.state = GameState.LOST

    def restart(self):
        self.__init__(self.height, self.width, self.mines)

    def game_won(self):
        self.state = GameState.WON

    def print_board(self, reveal):
        return [[item.to_symbol(reveal=reveal) for item in row] for row in self.board_state]

    def dump_board(self):
        return dumps(self.__dict__, cls=MineSweeperJsonEncoder, sort_keys=True, indent=4)

    def reveal_empty_at(self, row, col):
        # do resursive reveal of pieces
        pieces = self.get_surrounding_pieces(row, col)
        for p in pieces:
            if p.is_empty() and not p.is_revealed():
                p.step_on()
                self.reveal_empty_at(*p.get_coordinate())
            elif p.is_regular() and not p.is_revealed():
                p.step_on()

    def step_on(self, row, col):
        if self.state == GameState.READY:
            self.state = GameState.INPROGRESS
            # ensures the first step is never on a mine
            self.setup(row, col)
        if self.state == GameState.LOST or self.state == GameState.WON:
            return
        self.board_state[row][col].step_on()
        if self.state != GameState.LOST and self.pieces_revealed == self.height * self.width - self.mines:
            self.game_won()

    def mark(self, row, col):
        self.board_state[row][col].toggle_mark()

    def setup(self, row, col):
        max_possible_mines = self.height * self.width
        if self.mines >= max_possible_mines:
            raise ValueError
        mine_placements = [n for n in range(max_possible_mines)]
        mine_placements = [*mine_placements[:row * self.width + col], *mine_placements[row * self.width + col + 1:]]
        shuffle(mine_placements)
        for i in range(self.mines):
            row, col = self.convert_placement_to_location(mine_placements[i])
            self.board_state[row][col].change_to_mine()
        for i in range(self.mines):
            row, col = self.convert_placement_to_location(mine_placements[i])
            pieces = self.get_surrounding_pieces(row, col)
            for p in pieces:
                p.increment_surrounding_mine_count()

    def get_surrounding_pieces(self, row, col):
        pieces = []
        for row_shift in range(-1, 2):
            for col_shift in range(-1, 2):
                if row_shift == col_shift == 0:
                    continue
                if row + row_shift >= self.height or row + row_shift < 0:
                    continue
                if col + col_shift >= self.width or col + col_shift < 0:
                    continue

                pieces.append(self.board_state[row + row_shift][col + col_shift])
        return pieces

    def convert_placement_to_location(self, placement):
        # just an integer between 0 to w/e the size of n * m array is, convert it to row,col
        row = placement // self.width
        col = placement % self.width
        return row, col


class PieceFlag(Enum):
    Empty = 0
    Regular = 1
    Mine = 2


class Piece:
    def __init__(self, row, col, game: Game, value):
        super().__init__()
        self._game = game
        self._row = row
        self._col = col
        self._marked = False
        self._revealed = False
        self._value = value
        self._state = PieceFlag.Empty
        self.set_piece_flag()

    def set_piece_flag(self):
        if self._value < 0:
            self._state = PieceFlag.Mine
        elif self._value > 0:
            self._state = PieceFlag.Regular

    def increment_surrounding_mine_count(self):
        if self._state != PieceFlag.Mine:
            self._value += 1
            self.set_piece_flag()

    def get_coordinate(self):
        return self._row, self._col

    def is_revealed(self):
        return self._revealed

    def is_regular(self):
        return self._state == PieceFlag.Regular

    def is_empty(self):
        return self._state == PieceFlag.Empty

    def change_to_mine(self):
        if self._state != PieceFlag.Empty and self._value != -1:
            raise ValueError
        self._state = PieceFlag.Mine
        self._value = -1
        return self

    def toggle_mark(self):
        if not self.is_revealed():
            self._marked = not self._marked

    def to_symbol(self, reveal):

        if self._marked:
            return "#"
        if not reveal and not self._revealed:
            return "?"
        if self._state == PieceFlag.Mine:
            return "*"
        else:
            return f"{ self._value }"

    def step_on(self):
        if self._revealed:
            return
        if self._marked:
            self.toggle_mark()
            return
        self._revealed = True
        self._game.pieces_revealed += 1
        if self._state == PieceFlag.Empty:
            self._game.reveal_empty_at(self._row, self._col)
        elif self._state == PieceFlag.Mine:
            self._game.game_lost()
        return

    def display(self):
        return {"row": self._row, "col": self._col, "revealed": self._revealed, "flag": self._state.name}


class MineSweeperJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Piece):
            return obj.display()
        if isinstance(obj, Enum):
            return obj.name
        else:
            return JSONEncoder.default(self, obj)


def main():
    game = Game(2, 1, 1)
    # print(game.show_board())

    pprint(game.print_board(False), indent=2, width=100)
    game.step_on(1, 0)
    # game.step_on(9, 0)

    pprint(game.print_board(False), indent=2, width=100)
    pprint(game.print_board(True), indent=2, width=100)
    print(game.dump_board())
    # pprint(game.print_board(True), indent=2, width=100)


if __name__ == "__main__":
    main()
