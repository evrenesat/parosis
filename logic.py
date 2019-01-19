"""

"""
import random
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any, DefaultDict, List, Optional, Type, cast

# Exceptions


class PlayerError(Exception):
    pass


class GameError(Exception):
    pass


class Result(Enum):
    DRAW = 0
    WIN = 1
    LOSE = -1


@dataclass
class Tool:
    cuttable: bool = False
    wrappable: bool = False
    crushable: bool = False
    can_wrap: bool = False
    can_crush: bool = False
    can_cut: bool = False

    def encounter(self, tool: "Tool") -> Result:
        result = self.lose(tool) or self.draw(tool) or Result.WIN
        assert result is not None
        return result

    def draw(self, tool: "Tool") -> Optional[Result]:
        return Result.DRAW if self == tool else None

    def lose(self, tool: "Tool") -> Optional[Result]:
        return Result.LOSE if (
            (self.cuttable and tool.can_cut) or
            (self.crushable and tool.can_crush) or
            (self.wrappable and tool.can_wrap)
        ) else None


class Selection(Enum):
    ROCK = Tool(wrappable=True, can_crush=True)
    PAPER = Tool(cuttable=True, can_wrap=True)
    SCISSORS = Tool(crushable=True, can_cut=True)


class GameMode(Enum):
    # player can press the button any time
    CHANCE = 1
    # player needs to press the button before time up!
    TIMEOUT = 2
    # player needs to press the button when countdown finishes
    TIMING = 3


@dataclass
class Options:
    countdown: int = 3
    rounds: int = 3

    def set(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            try:
                getattr(self, key)
                setattr(self, key, value)
            except AttributeError:
                raise AttributeError("Cannot set a non existing option")


@dataclass
class Player:
    selection: Optional[Selection] = field(init=False)
    name: str = 'Player'
    auto_play: bool = False

    def get_random_selection(self) -> Selection:
        if self.auto_play:
            self.selection = random.choice(list(Selection))
            return self.selection
        else:
            raise PlayerError("Player did not made any choice")

    def get_selected_tool(self) -> Tool:
        return cast(Tool, (self.selection or self.get_random_selection()).value)

    def set_selection(self, selection_selection: Selection) -> None:
        self.selection = selection_selection

    def reset_selection(self) -> None:
        self.selection = None


class Round:
    def __init__(self, player1: Player, player2: Player, options: Options):
        self.player1 = player1
        self.player2 = player2
        self.options = options
        self.winner: Optional[Player] = None
        self.draw: bool = False
        self.player1.reset_selection()
        self.player2.reset_selection()

    def play(self, player: Player, selection: Selection) -> None:
        player.set_selection(selection)

    def finalize(self) -> None:
        tool_of_p1 = self.player1.get_selected_tool()
        tool_of_p2 = self.player2.get_selected_tool()
        result = tool_of_p1.encounter(tool_of_p2)

        if result == Result.WIN:
            self.winner = self.player1
        elif result == Result.LOSE:
            self.winner = self.player2
        else:
            self.draw = True


class TimerRound(Round):
    start_time: float = .0
    timings: DefaultDict[Player, float] = defaultdict(float)

    def __init__(self, player1: Player, player2: Player, options: Options) -> None:
        self.start_time = time()
        return super().__init__(player1, player2, options)

    def play(self, player: Player, selection: Selection) -> None:
        self.timings[player] = time()
        super().play(player, selection)

    # def check_timings(self):
    #     self.timings

    def finalize(self) -> None:
        return super().finalize()


class Game:
    def __init__(self, round_type: Type[Round]):
        self.RoundType = round_type
        self.options = Options()
        self.player = Player()
        self.cpu = Player(name="CPU", auto_play=True)
        self.rounds: List[Round] = []
        self.current_round: Optional[Round]

    def set_options(self, **kwargs: Any) -> None:
        self.options.set(**kwargs)

    def is_running(self) -> bool:
        return len(self.rounds) < self.options.rounds

    def play(self, selection: Selection, player: Optional[Player] = None) -> None:
        assert self.current_round is not None
        self.current_round.play(player or self.player, selection)

    def start_round(self) -> Round:
        if self.is_running():
            self.current_round = self.RoundType(
                player1=self.player, player2=self.cpu, options=self.options)
            return self.current_round
        else:
            raise GameError("Game already finished")

    def finish_round(self) -> Round:
        assert self.current_round is not None
        finished_round = self.current_round
        finished_round.finalize()
        self.rounds.append(finished_round)
        self.current_round = None
        return finished_round

    def get_number_of_wins(self, player: Player) -> int:
        return sum([1 for round in self.rounds if round.winner == player])

    def get_result(self) -> Result:
        player_won = self.get_number_of_wins(self.player)
        cpu_won = self.get_number_of_wins(self.cpu)
        if player_won > cpu_won:
            return Result.WIN
        elif player_won == cpu_won:
            return Result.DRAW
        else:
            return Result.LOSE
