import random
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any, DefaultDict, List, Optional, Type, Union, cast


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


@dataclass
class Options:
    countdown_duration: float = 3.0
    rounds: int = 3
    threshold: float = 0.5

    def set(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            try:
                getattr(self, key)
                setattr(self, key, value)
            except AttributeError:
                raise AttributeError(
                    "Cannot set non existing option: {}".format(key))


@dataclass(eq=False)
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
        if not player.selection:
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
    timings: DefaultDict[Player, float] = defaultdict(float)

    def play(self, player: Player, selection: Selection) -> None:
        self.timings[player] = time()
        super().play(player, selection)

    def played_on_time(self, player: Player, end_time: float) -> bool:
        NO_TIME = 0
        return player.auto_play or (end_time - self.options.threshold
                                    < self.timings.get(player, NO_TIME) <
                                    end_time + self.options.threshold)

    def find_winner_by_timing(self) -> bool:
        end_time = time()
        p1_on_time = self.played_on_time(self.player1, end_time)
        p2_on_time = self.played_on_time(self.player2, end_time)
        if p1_on_time and p2_on_time:
            return False
        if p1_on_time:
            self.winner = self.player1
        elif p2_on_time:
            self.winner = self.player2
        else:
            self.draw = True
        return bool(self.winner or self.draw)

    def finalize(self) -> None:
        if not self.find_winner_by_timing():
            super().finalize()


class Game:
    def __init__(self, round_type: Union[Type[Round], Type[TimerRound]]):
        self.RoundType = round_type
        self.options = Options()
        self.player = Player()
        self.winner: Optional[Player] = None
        self.cpu = Player(name="CPU", auto_play=True)
        self.rounds: List[Round] = []
        self.current_round: Union[Round, TimerRound, None]

    def set_options(self, **kwargs: Any) -> None:
        self.options.set(**kwargs)

    def is_running(self) -> bool:
        return len(self.rounds) < self.options.rounds

    def player_played(self) -> bool:
        return bool(self.player.selection)

    def play(self, selection: Selection, player: Optional[Player] = None) -> None:
        if self.current_round:
            self.current_round.play(player or self.player, selection)

    def start_round(self) -> Union[Round, TimerRound]:
        if self.is_running():
            self.current_round = self.RoundType(
                player1=self.player, player2=self.cpu, options=self.options)
            return self.current_round
        else:
            raise GameError("Game already finished")

    def check_for_winner(self) -> None:
        if self.is_running():
            return
        player_won = self.get_number_of_wins(self.player)
        cpu_won = self.get_number_of_wins(self.cpu)
        if player_won == cpu_won:
            return
        if player_won > cpu_won:
            self.winner = self.player
        else:
            self.winner = self.cpu

    def finish_round(self) -> Round:
        assert self.current_round is not None
        finished_round = self.current_round
        finished_round.finalize()
        self.rounds.append(finished_round)
        self.current_round = None
        self.check_for_winner()
        return finished_round

    def get_number_of_wins(self, player: Player) -> int:
        return sum([1 for round in self.rounds if round.winner == player])

    def get_player_result(self) -> Result:
        player_won = self.get_number_of_wins(self.player)
        cpu_won = self.get_number_of_wins(self.cpu)
        if player_won > cpu_won:
            return Result.WIN
        elif player_won == cpu_won:
            return Result.DRAW
        else:
            return Result.LOSE
