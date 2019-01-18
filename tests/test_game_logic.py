import pytest

from ..logic import *

def test_options():
    option = Options()
    assert option.countdown == Options.countdown
    option.countdown = 1
    assert option.countdown == 1
    option.set(rounds=1, countdown=4)
    assert option.countdown == 4
    assert option.rounds == 1
    with pytest.raises(AttributeError):
        option.set(foo=1)
        

def test_game_play():
    game = Game()
    game.start_round()    
    game.player.set_tool(Selection.PAPER)
    game.cpu.set_tool(Selection.PAPER)
    finished_round = game.finish_round()
    assert finished_round.winner == None
    assert finished_round.draw == True
    game.start_round()    
    game.player.set_tool(Selection.PAPER)
    game.cpu.set_tool(Selection.ROCK)
    finished_round = game.finish_round()
    assert finished_round.winner == game.player
    game.start_round()    
    with pytest.raises(PlayerError):
        game.finish_round()
    game.player.set_tool(Selection.SCISSORS)
    game.cpu.set_tool(Selection.ROCK)
    finished_round = game.finish_round()
    assert finished_round.winner == game.cpu
    assert game.get_result() == Result.DRAW
    with pytest.raises(GameError):
        game.start_round()    
    


    

    
