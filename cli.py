#!/usr/bin/env python3

import argparse
import json
import requests
import time

from game import Game
import ui


TIMEOUT = 15


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


# Game playing section

class GameError(Exception):
    pass
class GameTimeout(Exception):
    pass
class GameCreationError(Exception):
    pass
class GameRequestError(Exception):
    pass


class Launcher:
    def __init__(self, args):
        self.args = args
        self.bot = None
        self.gui = None
        self.session = None  # http session to server
        self.state = None # game state object
        self.start_time = None

    def start_gui(self, **kargs):
        self.gui = ui.tui(**kargs)
        self.gui.draw_game_windows()

    def stop_gui(self):
        if self.gui is not None:
            self.gui.quit_ui()
            self.gui = None

    def pprint(self, *args, **kwargs):
        """Display args in the bot gui or
        print it if no gui is available
        For debugging purpose consider using self.gui.append_log()
        """
        printable = ""
        for arg in args:
            printable = printable + str(arg)+" "
        if kwargs and len(kwargs):
            a = 1
            coma = ""
            printable = printable + "["
            for k, v in kwargs.items():
                if 1 < a < len(kwargs):
                    coma = ", "
                else:
                    coma = "]"
                printable = printable + str(k) + ": " + str(v) + coma
                a = a + 1
        if self.gui and self.gui.running:
            # bot has a gui so we add this entries to its log panel
            if self.gui.log_win:
                self.gui.append_log(printable)
                self.gui.refresh()
        else:
            print(printable)

    def play(self):
        """Play all games"""
        import importlib

        import bot

        ai_builder = importlib.import_module('AIs.' + self.args.bot)

        try:
            self.start_gui(num_players=3)

            errors = 0
            timeouts = 0
            victories = 0
            for i in range(self.args.num_games):
                # start a new game

                ai = ai_builder.init()
                self.bot = bot.Curses_ui_bot(ai_logic=ai)

                try:
                    self.run_game()
                except GameTimeout():
                    timeouts += 1
                    continue
                except (GameCreationError, GameError, GameRequestError):
                    errors += 1
                    continue

                gold = 0
                winner = ("Noone", -1)
                for player in self.bot.game.heroes:
                    if int(player.gold) > gold:
                        winner = (player.name, player.bot_id)
                        gold = int(player.gold)
                if winner[1] == self.bot.game.hero.bot_id:
                    victories += 1
                self.pprint("* " + winner[0] + " wins. ******************")
                self.gui.display_summary(str(i+1) + "/" + str(args.num_games),
                                         str(victories) + "/" + str(i+1),
                                         str(timeouts) + "/" + str(i+1))
                self.pprint("Game finished: " + str(i+1) + "/" + str(args.num_games))

        finally:
            self.stop_gui()

    def run_game(self):
        """Starts a game with all the required parameters"""
        # Create a requests session that will be used throughout the game
        self.pprint('Connecting...')
        self.session = requests.session()
        try:
            if args.game_mode == 'arena':
                self.pprint('Waiting for other players to join...')
            # Get the initial state
            self.state = self.get_new_game_state()
            self.pprint("Playing at: " + self.state['viewUrl'])
            for i in range(self.args.number_of_turns + 1):
                # Choose a move
                self.start_time = time.time()
                try:
                    direction = self.bot.move(self.state)
                    self.display_game()
                except Exception as e:
                    self.pprint("Error at client.run_game:", str(e))
                    raise GameError()
                if not self.state['game']['finished']:
                    # Send the move and receive the updated game state
                    self.state = self.send_move(direction)
        finally:
            self.session.close()

    def get_new_game_state(self):
        """Get a JSON from the server containing the current state of the game"""
        if self.args.game_mode == 'training':
            # Don't pass the 'map' parameter if no map has been selected
            params = {'key': self.args.key, 'turns': self.args.number_of_turns}
            if 'map_name' in self.args:
                params['map'] =self.args.map_name
            api_endpoint = '/api/training'
        elif self.args.game_mode == 'arena':
            params = {'key': self.args.key}
            api_endpoint = '/api/arena'
        else:
            raise ValueError('Unknown game mode')
        # Wait for 10 minutes
        try:
            r = self.session.post(self.args.server_url + api_endpoint, params, timeout=10*60)
            if r.status_code == 200:
                return r.json()
            else:
                self.pprint("HttpError when creating the game:", str(r.status_code))
                raise GameCreationError()
        except requests.ConnectionError as e:
            self.pprint("Exception when creating the game:", e)
            raise GameCreationError()

    def send_move(self, direction):
        """Send a move to the server
        Moves can be one of: 'Stay', 'North', 'South', 'East', 'West'"""
        try:
            response = self.session.post(self.state['playUrl'], {'dir': direction}, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                self.pprint("Error HTTP ", str(response.status_code), ": ", response.text)
                raise GameTimeout()
        except requests.exceptions.RequestException as e:
            self.pprint("Error at client.move;", str(e))
            raise GameRequestError()

    def display_game(self):
        """Display game data on the U.I"""
        if self.gui is not None:
            # Draw the map
            self.gui.draw_map(self.bot.game.board_map, self.bot.path_to_goal, self.bot.game.heroes)
            # Use the following methods to display datas
            # within the interface
            self.gui.display_url(self.bot.game.url)
            self.gui.display_bot_name(self.bot.game.hero.name)
            self.gui.display_last_move(self.bot.hero_last_move)
            self.gui.display_pos(self.bot.game.hero.pos)
            self.gui.display_last_pos(self.bot.last_pos)
            self.gui.display_last_life(self.bot.last_life)
            self.gui.display_life(self.bot.game.hero.life)
            self.gui.display_last_action(self.bot.last_action)
            self.gui.display_turn((self.bot.game.turn // 4) - 1, self.bot.game.max_turns // 4)
            self.gui.display_elo(self.bot.game.hero.elo)
            self.gui.display_gold(self.bot.game.hero.gold)
            self.gui.display_last_gold(self.bot.last_gold)
            self.gui.display_mine_count(str(self.bot.game.hero.mine_count) + "/" + str(len(self.bot.game.mines)))
            self.gui.display_last_mine_count(str(self.bot.last_mine_count) + "/" + str(len(self.bot.game.mines)))
            # You can also use those methods to display more information
            # Function names are explicit, don't they ?
            self.gui.display_nearest_mine(self.bot.nearest_mine_pos)
            self.gui.display_nearest_hero(self.bot.nearest_enemy_pos)
            self.gui.display_nearest_tavern(self.bot.nearest_tavern_pos)
            self.gui.display_last_nearest_mine(self.bot.last_nearest_mine_pos)
            self.gui.display_last_nearest_hero(self.bot.last_nearest_enemy_pos)
            self.gui.display_last_nearest_tavern(self.bot.last_nearest_tavern_pos)
            # Print informations about other players
            self.gui.display_heroes(self.bot.game.heroes, self.bot.game.hero.bot_id)
            # Print a *list of tuples* representing what you think can be usefull
            # i.e an heuristic result
            self.gui.display_decision(self.bot.decision)
            # Print *list of tuples* representing
            # the estimated path to reach the goal if any.
            # If too long the path will be truncated to fit
            # in the display
            self.gui.display_path(self.bot.path_to_goal)
            # Move cursor along the time line (cost cpu time)
            cursor_pos = int(float(self.gui.TIME_W) / self.bot.game.max_turns * self.bot.game.turn)
            self.gui.move_time_cursor(cursor_pos)
            # Finally display selected move
            self.gui.display_move(self.bot.hero_move)
            self.gui.display_action(self.bot.action)
            # Add whathever you want to log using self.gui.append_log()
            # self.gui.append_log("Whatever")
            elapsed = round(time.time() - self.start_time, 3)
            self.gui.display_elapsed(elapsed)
            self.gui.refresh()

    # Help

    def help(args):
        parser.print_help()
        exit(1)



sub_cmds = parser.add_subparsers(description='operation to execute')

replay_parser = sub_cmds.add_parser('replay', help='replay a game')
replay_parser.add_argument('file', type=argparse.FileType('r'))
replay_parser.add_argument('--delay', type=float, default=1, help='delay between turns in seconds')
replay_parser.set_defaults(func=replay)

map_parser = sub_cmds.add_parser('show-map', help='show a single game frame')
map_parser.add_argument('file', type=argparse.FileType('r'))
map_parser.set_defaults(func=show_map)

play_parser = sub_cmds.add_parser('play', help='play a series of games')
play_parser.add_argument('--game-mode', default='training', choices=['arena', 'training'])
play_parser.add_argument('--bot', default='random')
play_parser.add_argument('--map')
play_parser.add_argument('--turns', dest='number_of_turns', type=int, default=1000, help='the number of turns')
play_parser.add_argument('--server-url', default='http://vindinium.org')
play_parser.add_argument('--num-games', type=int, default=1)
play_parser.add_argument('--key-file', type=argparse.FileType('r'), default=None, help='path to the keyfile (default is to use keys/<bot-name>)')

args = parser.parse_args()
if 'func' in args:
    args.func(args)
else:
    if args.key_file is None:
        with open('keys/%s.key' % args.bot, 'r') as f:
            args.key = f.readline().strip()
    else:
        args.key = args.key_file.readline().strip()
    del args.key_file

    launcher = Launcher(args)
    launcher.play()
