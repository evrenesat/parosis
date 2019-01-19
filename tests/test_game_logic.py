import pytest

from ..logic import (Game, GameError, Options, PlayerError, Result, Round,
                     Selection)


def test_options() -> None:
    option = Options()
    assert option.countdown == Options.countdown
    option.countdown = 1
    assert option.countdown == 1
    option.set(rounds=1, countdown=4)
    assert option.countdown == 4
    assert option.rounds == 1
    with pytest.raises(AttributeError):
        option.set(foo=1)


def test_game_play() -> None:
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
    assert game.get_result() == Result.DRAW
    with pytest.raises(GameError):
        game.start_round()
