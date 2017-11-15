#!/usr/bin/env python3

import argparse
import json
import time

from game import Game
import ui

parser = argparse.ArgumentParser()


def replay(args):
    gui = None
    try:
        gui = ui.tui(num_players=4)
        #gui.draw_data_win()
        gui.draw_log_win()
        gui.draw_players_win()

        for line in args.file:
            if len(line) <= 1:
                continue

            assert line.startswith("data:")
            line = line[6:]
            state = json.loads(line)
            g = Game({'game': state})

            gui.draw_map(g.board_map, path=None, heroes=g.heroes)
            gui.display_heroes(g.heroes, bot_id=None)

            gui.refresh()
            time.sleep(args.delay)


    finally:
        if gui is not None:
            gui.quit_ui()


def help(args):
    parser.print_help()
    exit(1)


sub_cmds = parser.add_subparsers(description='operation to execute')
parser.set_defaults(func=help)

replay_parser = sub_cmds.add_parser('replay', help='replay a game')
replay_parser.add_argument('file', type=argparse.FileType('r'))
replay_parser.add_argument('--delay', type=float, default=1, help='delay between turns in seconds')
replay_parser.set_defaults(func=replay)


args = parser.parse_args()

args.func(args)
