"""
Assignment 1: Meepo is You

=== CSC148 Winter 2021 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains the Game class and the main game application.
"""

from typing import Any, Type, Tuple, List, Sequence, Optional
import pygame
from settings import *
from stack import Stack
import actor


class Game:
    """
    Class representing the game.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None
        #
        self._actors = []
        self._is = []
        self._running = True
        self._rules = []
        self._history = Stack()
        self.player = None
        self.map_data = []
        self.keys_pressed = None

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:   # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        if self.player.player_move(self):
                            self._history.push(save)
                            self.win_or_lose()
        return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()

    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def remove_rules(self):
        """
        Remove settings for all previous rules in self._rules
        """
        for rule in self._rules:
            x = rule.split(' ')
            subject = x[0]
            attribute = x[1]
            for actor in self._actors:
                if isinstance(actor, self.get_character(subject)):
                    if attribute == 'isYou':
                        actor.unset_player()
                        self.player = None
                    elif attribute == 'isStop':
                        actor.unset_stop()
                    elif attribute == 'isVictory':
                        actor.unset_win()
                    elif attribute == 'isLose':
                        actor.unset_lose()
                    elif attribute == 'isPush':
                        actor.unset_push()

    def update_rules(self):
        """
        update settings for all rules in self._rules
        """
        for rule in self._rules:
            x = rule.split(' ')
            subject = x[0]
            attribute = x[1]
            for actor in self._actors:
                if isinstance(actor, self.get_character(subject)):
                    if attribute == 'isYou':
                        actor.set_player()
                        self.player = actor
                    elif attribute == 'isStop':
                        actor.set_stop()
                    elif attribute == 'isVictory':
                        actor.set_win()
                    elif attribute == 'isLose':
                        actor.set_lose()
                    elif attribute == 'isPush':
                        actor.set_push()

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """

        # TODO Task 3: Add code here to complete this method
        # What you need to do in this method:
        # - Get the lists of rules that need to be added to and remove from the
        #   current list of rules. Hint: use the update() method of the Is
        #   class.
        # - Apply the additional and removal of the rules. When applying the
        #   rules of a type of character, make sure all characters of that type
        #   have their flags correctly updated. Hint: take a look at the
        #   get_character() method -- it can be useful.
        # - The player may change if the "isYou" rule is updated. Make sure set
        #   self.player correctly after you update the rules. Note that
        #   self.player could be None in some cases.
        # - Update self._rules to the new list of rules.

        self.remove_rules()

        new_rules = []
        updated = []
        previous = []

        for block in self._is:
            up = self.get_tile(block.x, block.y - 1)
            down = self.get_tile(block.x, block.y + 1)
            left = self.get_tile(block.x - 1, block.y)
            right = self.get_tile(block.x + 1, block.y)
            rules = block.update(up, down, left, right)
            for rule in rules:
                if rule != '':
                    new_rules.append(rule)

        for rule in new_rules:
            if rule not in self._rules:
                updated.append(rule)
        for rule in self._rules:
            if rule in new_rules:
                previous.append(rule)

        self._rules = previous + updated
        self.update_rules()

    def get_tile(self, x, y):
        """
        Takes 2 ints x and y, returns actor at that location
        """
        for actor in self._actors:
            if actor.x == x and actor.y == y:
                return actor
        return None

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        if not self._history.is_empty():
            older = self._history.pop()
            self._actors = older._actors
            self._is = older._is
            self._rules = older._rules
            self._history = older._history
            self.player = older.player
        return

    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()

        for a in self._actors:
            if not isinstance(a, actor.Is):
                game_copy._actors.append(a.copy())
        for a in self._is:
            x = a.copy()
            game_copy._is.append(x)
            game_copy._actors.append(x)
        game_copy._rules = self._rules[:]
        game_copy.screen = self.screen
        game_copy.background = self.background
        game_copy._history = self._history
        game_copy.player = self.player.copy()

        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")


if __name__ == "__main__":

    game = Game()
    # load_map public function
    game.load_map(MAP_PATH)
    game.new()
    game.player = actor.Meepo(2, 2)
    game.run()

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    # })
