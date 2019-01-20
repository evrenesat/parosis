from time import time

import pytest

from ..logic import (Game, GameError, Options, PlayerError, Result, Round,
                     Selection, TimerRound)


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
    assert finished_round.winner is None
    assert finished_round.draw is True
