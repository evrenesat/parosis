from typing import Any
import curses
from curses import wrapper

import time

import asciiart


class CGame:

    def __init__(self) -> None:
        self.selection = ''
        wrapper(self.main)

    def show_gesture(self, gesture: str) -> None:
        for y, line in enumerate(gesture.splitlines(), 2):
            self.screen.addstr(y, 2, line)

    def show_string(self, s: str, y, x) -> None:
        for col, c in enumerate(s):
            self.screen.addch(y, x+col, c)

    def main(self, screen: Any) -> None:
        self.screen = screen
        screen.nodelay(True)
        screen.clear()
        while True:
            self.show_string(str(time.time()), 30, 50)
            c = screen.getch()
            curses.flushinp()
            screen.clear()
            if c == ord('p'):
                self.selection = asciiart.PAPER
            elif c == ord('r'):
                self.selection = asciiart.ROCK
            elif c == ord('s'):
                self.selection = asciiart.SCISSORS
            self.show_gesture("CPU\n\n" + asciiart.ROCK + "PLAYER\n\n" + self.selection)
            time.sleep(0.1)


if __name__ == "__main__":
    CGame()
