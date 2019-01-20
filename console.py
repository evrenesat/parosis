import curses
import time
from curses import wrapper
from typing import Any

import art
from logic import Game, TimerRound, Round, Selection

HANDS = {
    Selection.PAPER: art.PAPER,
    Selection.ROCK: art.ROCK,
    Selection.SCISSORS: art.SCISSORS
}


class ConsoleGame:
    WAIT_BEFORE_NEXT_ROUND = 2
    LOOP_SLEEP = 0.1

    def __init__(self, game: Game) -> None:
        self.selection = ''
        self.game = game
        self.options = game.options
        self.previous_round = game.start_round()
        self.player_images = {game.cpu: art.ROBOT, game.player: art.PLAYER}
        self.last_play_time = .0

    def show_players(self) -> None:
        winner = self.game.winner or self.previous_round.winner
        robot = art.ROBOT_WON if winner is self.game.cpu else art.ROBOT
        player = art.PLAYER_WON if winner is self.game.player else art.PLAYER
        self.show_art("\n\n{}\n ==================\n\n\n{}".format(robot, player))

    def start_game(self) -> None:
        wrapper(self.main)

    def show_art(self, gesture: str, y: int = 0, x: int = 0) -> None:
        for yy, line in enumerate(gesture.splitlines(), 2):
            self.screen.addstr(y + yy, x + 2, line)

    def show_string(self, s: str, y: int, x: int) -> None:
        for col, c in enumerate(s):
            self.screen.addch(y, x+col, c)

    def show_robot(self, selection: Selection) -> None:
        self.show_art(art.ROBOT)

    def start_next_round(self) -> None:
        if (not self.game.is_running() or
                time.time() - self.last_play_time < self.WAIT_BEFORE_NEXT_ROUND):
            return
        if self.game.player_played():
            self.game.start_round()

    def finalize_round(self) -> None:
        if self.game.player_played() and self.game.current_round:
            self.previous_round = self.game.finish_round()

    def show_hands(self) -> None:
        X_COORD = 25  # chr
        Y_COORD_PLAYER = 17
        Y_COORD_CPU = 3
        self.show_art(HANDS.get(self.game.player.selection, ''), Y_COORD_PLAYER, X_COORD)
        self.show_art(HANDS.get(self.game.cpu.selection, ''), Y_COORD_CPU, X_COORD)

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

    def show_stats(self) -> None:
        played_rounds = len(self.game.rounds) or 1
        self.show_string("Round: {} / {}".format(played_rounds, self.options.rounds), 1, 1)
        self.show_string("Wins: {}".format(self.game.get_number_of_wins(self.game.cpu)), 4, 1)
        self.show_string("Wins: {}".format(self.game.get_number_of_wins(self.game.player)), 20, 1)

    def main(self, screen: Any) -> None:
        self.screen = screen
        screen.nodelay(True)
        screen.clear()
        last_loop_is_required = True
        while self.game.is_running() or last_loop_is_required:
            last_loop_is_required = self.game.is_running()
            c = screen.getch()
            screen.clear()
            self.show_stats()
            self.show_players()
            self.show_hands()
            self.handle_selection(c)
            self.finalize_round()
            self.start_next_round()
            time.sleep(self.LOOP_SLEEP)
        # this additional getch call required to
        # print the results of the last round
        screen.getch()
        time.sleep(5)


class TimerGame(ConsoleGame):
    def __init__(self, game: Game) -> None:
        self.last_play_time = .0
        self.round_duration = game.options.countdown_duration
        super().__init__(game)

    def finalize_round(self) -> None:
        self.round_duration -= self.LOOP_SLEEP
        if self.round_duration >= 0:
            self.show_string(str(self.round_duration), 30, 50)
        if self.game.current_round and self.round_duration <= 0:
            self.previous_round = self.game.finish_round()
            self.last_play_time = time.time()

    def start_next_round(self) -> None:

        if (not self.game.is_running() or
                time.time() - self.last_play_time < self.WAIT_BEFORE_NEXT_ROUND):
            return
        self.game.start_round()
        self.round_duration = self.options.countdown_duration
        self.last_play_time = time.time()


if __name__ == "__main__":

    # ConsoleGame(game).start_game()
    # game = Game(Round)
    game = Game(TimerRound)
    game.set_options(countdown_duration=2, threshold=0.8)
    TimerGame(game).start_game()
    print("Game result for the player: {} ".format(game.get_player_result()))
