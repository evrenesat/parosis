import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

import pytest
import art
from game import ConsoleGame, TimerGame
from logic import (Game, GameError, Options, PlayerError, Result, Round,
                   Selection, TimerRound)
import pytest
from time import time


def test_options() -> None:
    option = Options()
    assert option.countdown_duration == Options.countdown_duration
    option.countdown_duration = 1
    assert option.countdown_duration == 1
    option.set(rounds=1, countdown_duration=4)
    assert option.countdown_duration == 4
    assert option.rounds == 1
    with pytest.raises(AttributeError):
        option.set(foo=1)


def test_normal_game_play() -> None:
    game = Game(Round)
    game.start_round()
    game.play(Selection.PAPER)
    game.play(Selection.PAPER, game.cpu)
    finished_round = game.finish_round()
    assert finished_round.winner is None
    assert finished_round.draw is True
    game.start_round()
    game.play(Selection.PAPER)
    game.play(Selection.ROCK, game.cpu)
    finished_round = game.finish_round()
    assert finished_round.winner == game.player
    game.start_round()
    with pytest.raises(PlayerError):
        game.finish_round()
    game.play(Selection.SCISSORS)
    game.play(Selection.ROCK, game.cpu)
    finished_round = game.finish_round()
    assert finished_round.winner == game.cpu
    assert game.get_player_result() == Result.DRAW
    with pytest.raises(GameError):
        game.start_round()


def test_timer_game_play() -> None:
    game = Game(TimerRound)
    game.set_options(rounds=4)
    game.start_round()
    game.play(Selection.PAPER)
    game.play(Selection.ROCK, game.cpu)
    finished_round = game.finish_round()
    assert finished_round.winner is game.player
    game.start_round()
    game.play(Selection.PAPER)
    # to satisfy mypy
    assert isinstance(game.current_round, TimerRound)
    game.current_round.timings[game.player] = time() + 999999
    game.play(Selection.ROCK, game.cpu)
    finished_round = game.finish_round()
    assert finished_round.winner is game.cpu
    assert game.is_running()
    game.start_round()
    game.current_round.timings[game.player] = time() + 999999
    game.current_round.timings[game.cpu] = time() + 999999  # normally impossible
    finished_round = game.finish_round()
    assert finished_round.winner is game.cpu
    assert finished_round.draw is False


class FakeConsoleGame(ConsoleGame):

    def flush_output(self) -> None:
        self._output = []

    def show_string(self, s: str, y: int, x: int) -> None:
        self._output.append(s)

    def show_art(self, s: str, y: int, x: int) -> None:
        self._output.append(s)

    def get_output(self) -> str:
        return "|".join(self._output)


def test_normal_game() -> None:
    game = Game(Round)
    c = FakeConsoleGame(game)
    c.flush_output()
    c.show_stats()
    assert c.get_output() == 'Round: 1 / 3|Wins: 0|Wins: 0'
    c.handle_selection(ord('p'))
    game.play(Selection.PAPER, game.cpu)
    assert game.player.selection == Selection.PAPER
    c.flush_output()
    c.show_hands()
    assert c.get_output() == "{}|{}".format(art.PAPER, art.PAPER)
    c.finalize_round()
    c.start_next_round()
    c.handle_selection(ord('s'))
    game.play(Selection.PAPER, game.cpu)
    c.last_action_time = .0
    c.finalize_round()
    c.flush_output()
    c.show_stats()
    assert c.get_output() == 'Round: 2 / 3|Wins: 0|Wins: 1'


