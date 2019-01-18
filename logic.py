"""

"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import random
from time import time

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

    def encounter(self, tool: "Tool"):
        return self.lose(tool) or self.draw(tool) or Result.WIN

    def draw(self, tool: "Tool"):
        if self == tool:
            return Result.DRAW

    def lose(self, tool: "Tool"):
        if ((self.cuttable and tool.can_cut) or
                (self.crushable and tool.can_crush) or
                (self.wrappable and tool.can_wrap)):
            return Result.LOSE


class Selection(Enum):
    NO_CHOICE = None
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

    def set(self, **kwargs):
        for key, value in kwargs.items():
            try:
                getattr(self, key)
                setattr(self, key, value)
            except AttributeError:
                raise AttributeError("Cannot set a non existing option")


@dataclass
class Player:
    name: str = 'Player'
    tool: Tool = None
    auto_play: bool = False


    def get_random_tool(self):
        if self.auto_play:
            self.tool = random.choice(list(Selection))
            return self.tool
        else:
            raise PlayerError("Player did not made any choice")

    def get_tool(self):
        return (self.tool or self.get_random_tool()).value

    def set_tool(self, tool: Tool):        
        self.tool = tool

    def reset_tool(self):
        self.tool = None

@dataclass
class Round:
    winner: Player = None
    draw: bool = False
    player1: Player = None
    player2: Player = None
    start_time: float = .0

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.player1.reset_tool()
        self.player2.reset_tool()
        self.start_time = time()
    
    def finalize(self):
        tool_of_p1 = self.player1.get_tool()
        tool_of_p2 = self.player2.get_tool()
        result = tool_of_p1.encounter(tool_of_p2)

        if result == Result.WIN:
            self.winner = self.player1
        elif result == Result.LOSE:
            self.winner = self.player2
        else:
            self.draw = True


class Game:
    def __init__(self):
        self.options = Options()
        self.player = Player()
        self.cpu = Player(name="CPU", auto_play=True)
        self.rounds = []
        self.current_round = None

    def set_options(self, **kwargs):
        self.options.set(**kwargs)

    def is_running(self):
        return len(self.rounds) < self.options.rounds

    def start_round(self):
        if self.is_running():
            self.current_round = Round(player1=self.player, player2=self.cpu)
        else:
            raise GameError("Game already finished")
        
    
    def finish_round(self):
        finished_round = self.current_round
        self.current_round.finalize()
        self.rounds.append(self.current_round)
        self.current_round = None
        return finished_round
        
