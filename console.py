import curses
import sys
import time
from curses import wrapper
from typing import Any, Dict, List, Optional

import art
from logic import Game, GameMode, Player, Result, Round, Selection

HANDS = {
    Selection.PAPER: art.PAPER,
    Selection.ROCK: art.ROCK,
    Selection.SCISSORS: art.SCISSORS
}


class CGame:
    WAIT_BEFORE_NEXT_ROUND_OR_QUIT = 2

    def __init__(self, game: Game) -> None:
        self.selection = ''
        self.game = game
        self.options = game.options
        self.use_timer = game.get_mode() is GameMode.TIMING
        self.result_visuals = self.prepare_result_visuals()
        self.previous_round = game.start_round()
        self.player_images = {game.cpu: art.ROBOT, game.player: art.PLAYER}
        self.last_play_time = .0

    def prepare_result_visuals(self) -> Dict[Player, Dict[Result, str]]:
        return {
            self.game.cpu: {
                Result.DRAW: art.ROBOT,
                Result.LOSE: art.ROBOT,
                Result.WIN: art.ROBOT_WON,
            },
            self.game.player: {
                Result.DRAW: art.PLAYER,
                Result.LOSE: art.PLAYER,
                Result.WIN: art.PLAYER_WON,
            }
        }

    def show_players(self) -> None:
        winner = self.game.winner or self.previous_round.winner
        robot = art.ROBOT_WON if winner is self.game.cpu else art.ROBOT
        player = art.PLAYER_WON if winner is self.game.player else art.PLAYER
        self.show_art("{}\n ==================\n{}".format(robot, player))

    def start_game(self) -> None:
        wrapper(self.main)

    def show_art(self, gesture: str, y: int = 0, x: int = 0) -> None:
        for yy, line in enumerate(gesture.splitlines(), 2):
            self.screen.addstr(y + yy, x + 2, line)

    def show_string(self, s: str, y: int, x: int) -> None:
        for col, c in enumerate(s):
            self.screen.addch(y, x+col, c)

    def show_timer(self) -> None:
        self.show_string(str(time.time()), 30, 50)

    def show_robot(self, selection: Selection) -> None:
        self.show_art(art.ROBOT)

    def handle_game(self) -> None:
        if (not self.game.is_running() or
                time.time() - self.last_play_time < self.WAIT_BEFORE_NEXT_ROUND_OR_QUIT):
            return
        if self.game.player_played():
            self.game.start_round()

    def finalize_round(self) -> None:
        if self.use_timer:
            pass  # TODO
        elif self.game.player_played() and self.game.current_round:
            self.previous_round = self.game.finish_round()

    def show_hands(self) -> None:
        self.show_art(HANDS.get(self.game.player.selection, ''), 17, 25)
        self.show_art(HANDS.get(self.game.cpu.selection, ''), 3, 25)

    def play(self, selection: Selection) -> None:
        if not self.game.current_round:
            self.game.start_round()
        self.game.play(selection)
        self.last_play_time = time.time()

    def handle_selection(self, c: int) -> None:
        if c in [ord('p'), curses.KEY_LEFT]:
            self.play(Selection.PAPER)
        elif c in [ord('r'), curses.KEY_UP]:
            self.play(Selection.ROCK)
        elif c in [ord('s'), curses.KEY_RIGHT]:
            self.play(Selection.SCISSORS)

    def main(self, screen: Any) -> None:
        self.screen = screen
        screen.nodelay(True)
        screen.clear()
        last_loop_is_required = True
        while self.game.is_running() or last_loop_is_required:
            last_loop_is_required = self.game.is_running()
            c = screen.getch()
            screen.clear()
            self.show_players()
            self.show_hands()
            self.handle_selection(c)
            self.finalize_round()
            self.handle_game()
            time.sleep(0.1)
        # this additional getch call required to
        # print the results of the last round
        screen.getch()
        time.sleep(2)


if __name__ == "__main__":
    game = Game(GameMode.CHANCE.value)
    CGame(game).start_game()
    print("Game result: {} ".format(game.get_player_result()))
