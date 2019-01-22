import sys
import curses
import argparse
import time
from curses import wrapper
from typing import Any, Type

import art
from logic import Game, TimerRound, Round, Selection, Options

HANDS = {
    Selection.PAPER: art.PAPER,
    Selection.ROCK: art.ROCK,
    Selection.SCISSORS: art.SCISSORS
}


class ConsoleGame:
    WAIT_BEFORE_CONTINUE = 2 #  sec
    LOOP_SLEEP = 0.1

    def __init__(self, game: Game) -> None:
        self.selection = ''
        self.game = game
        self.options = game.options
        self.previous_round = game.start_round()
        self.player_images = {game.cpu: art.ROBOT, game.player: art.PLAYER}
        self.last_action_time = .0

    def show_players(self) -> None:
        winner = self.game.winner or self.previous_round.winner
        robot = art.ROBOT_WON if winner is self.game.cpu else art.ROBOT
        player = art.PLAYER_WON if winner is self.game.player else art.PLAYER
        self.show_art("\n\n{}\n ==================\n\n\n{}".format(robot, player))

    def start_game(self) -> None:
        wrapper(self.main)

    def show_art(self, s: str, y: int = 0, x: int = 0) -> None:
        for yy, line in enumerate(s.splitlines(), 2):
            self.screen.addstr(y + yy, x + 2, line)

    def show_string(self, s: str, y: int, x: int) -> None:
        for col, c in enumerate(s):
            self.screen.addch(y, x+col, c)

    def start_next_round(self) -> None:
        if (not self.game.is_running() or
                time.time() - self.last_action_time < self.WAIT_BEFORE_CONTINUE):
            return
        if self.game.player_played():
            self.game.start_round()

    def finalize_round(self) -> None:
        if self.game.player_played() and self.game.current_round:
            self.previous_round = self.game.finish_round()

    def show_hands(self) -> None:
        X_COORD = 25  # chr
        Y_COORD_PLAYER = 19
        Y_COORD_CPU = 3
        self.show_art(HANDS.get(self.game.player.selection, ''), Y_COORD_PLAYER, X_COORD)
        self.show_art(HANDS.get(self.game.cpu.selection, ''), Y_COORD_CPU, X_COORD)

    def play(self, selection: Selection) -> None:
        if not self.game.is_running():
            return
        if not self.game.current_round:
            self.game.start_round()
        self.game.play(selection)
        self.last_action_time = time.time()

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
        self.show_string("Can be played with [P] [R] [S] or Arrow keys. [Q] to quit", 2, 0)
        c = screen.getch()
        time.sleep(self.WAIT_BEFORE_CONTINUE)
        while self.game.is_running() or last_loop_is_required:
            last_loop_is_required = self.game.is_running()
            c = screen.getch()
            if c == ord('q'):
                sys.exit()
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
        time.sleep(self.WAIT_BEFORE_CONTINUE)


class TimerGame(ConsoleGame):
    def __init__(self, game: Game) -> None:
        self.round_duration = game.options.countdown_duration
        super().__init__(game)

    def finalize_round(self) -> None:
        self.round_duration -= self.LOOP_SLEEP
        if self.round_duration >= 0:
            self.show_string(str("{:10.1f}".format(self.round_duration)), 30, 50)
        if self.game.current_round and self.round_duration <= 0:
            self.previous_round = self.game.finish_round()
            self.last_action_time = time.time()

    def start_next_round(self) -> None:
        if (not self.game.is_running() or
                self.game.current_round or
                time.time() - self.last_action_time < self.WAIT_BEFORE_CONTINUE):
            return
        self.game.start_round()
        self.round_duration = self.options.countdown_duration

    def play(self, selection: Selection) -> None:
        self.game.play(selection)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timer", action="store_true",
                        help="Play against both time and chance. You must make a choice before "
                        "the countdown is over. Threshold can be set with --threshold parameter.")

    parser.add_argument("--rounds",
                        help="Set number of rounds. Default is {}.".format(Options.rounds))

    parser.add_argument("--threshold", help="Selection acceptance threshold for timer mode. "
                        "Default is {} sec.".format(Options.threshold))

    parser.add_argument("--countdown", help="Countdown duration for timer mode. "
                        "Default is {} sec.".format(Options.countdown_duration))
    args = parser.parse_args()

    ui: Type[ConsoleGame] = ConsoleGame
    round: Type[Round] = Round
    if args.timer:
        round = TimerRound
        ui = TimerGame
    game = Game(round)
    if args.rounds:
        game.set_options(rounds=float(args.rounds))
    if args.threshold:
        game.set_options(threshold=float(args.threshold))
    if args.countdown:
        game.set_options(countdown_duration=int(args.countdown))
    ui(game).start_game()
    print("\nGame result for the player: {} \n".format(game.get_player_result().name))
