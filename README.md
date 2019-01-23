Parosis is a Paper-Rock-Scissors game
=====================================================

Motivation
----------

Primary goal of this project is getting more experienced on some Python related stuff:

- typing library and mypy.
- Dataclasses
- Enum
- curses library.
- Python suport of Visual Studio Code (conclusion: barely usable).
- Single-dispatch generic functions ([todo](https://www.python.org/dev/peps/pep-0443/))
- Literal String Interpolation ([todo](https://www.python.org/dev/peps/pep-0498/))
- Asyncio ([todo](https://github.com/timofurrer/awesome-asyncio#web-frameworks) )

Requirements
------------

- Python 3.7
- A terminal that properly supports curses interface.

Game play
-----------

Currently only curses based console interface is implemented which should work on Linux and MacOS.

![screencast](https://github.com/evrenesat/parosis/blob/master/screencast.gif?raw=true)


Run `python game.py --help` to get more info about possible options.

I plan to implement a browser based UI probably using aiohttp or Quart.


You can check `screencast.gif` file to get an idea about what it looks like.

- Number of rounds can be specified using `--rounds` parameter.

Can be played in two different modes:

- Just chance
  - Player can make a choice any time.
- Chance and timing:
  - Pass `--timer` parameter to enable countdown timer.
  - Player needs to make a choice just before the countdown finishes but within a certain threshold. 
  - Countdown time can be set using `--countdown` parameter. Check `--help` to see the default threshold.
  - Threshold can be set using `--threshold` parameter.
