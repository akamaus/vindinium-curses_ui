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

            gui.draw_map(g.board_map, path=None, heroes=g.heroes, mines=g.mines)
            gui.display_heroes(g.heroes, bot_id=None)

            gui.refresh()
            time.sleep(args.delay)


    finally:
        if gui is not None:
            gui.quit_ui()


def show_map(args):
    """ Shows single json map """
    gui = None
    try:
        gui = ui.tui(num_players=3)
        gui.draw_data_win()
        gui.draw_log_win()
        gui.draw_players_win()

        state = json.load(args.file)
        game = Game(state)

        gui.draw_map(game.board_map, path=None, heroes=game.heroes, mines=game.mines, main_hero=game.hero)
        gui.display_url(game.url)
        gui.display_bot_name(game.hero.name)
        gui.display_pos(game.hero.pos)
        gui.display_life(game.hero.life)
        gui.display_turn((game.turn // 4) - 1, game.max_turns // 4)
        gui.display_elo(game.hero.elo)
        gui.display_gold(game.hero.gold)
        gui.display_mine_count(str(game.hero.mine_count) + "/" + str(len(game.mines)))
        gui.display_heroes(game.heroes, game.hero.bot_id)
        cursor_pos = int(float(gui.TIME_W) / game.max_turns * game.turn)
        gui.move_time_cursor(cursor_pos)
        # Finally display selected move

        gui.refresh()
        time.sleep(60)

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

map_parser = sub_cmds.add_parser('show-map', help='show a single game frame')
map_parser.add_argument('file', type=argparse.FileType('r'))
map_parser.set_defaults(func=show_map)

args = parser.parse_args()

args.func(args)
