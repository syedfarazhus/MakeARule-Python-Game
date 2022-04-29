from game import *
from actor import *
import pytest
import pygame
import os

# USE PYGAME VARIABLES INSTEAD
keys_pressed = [0] * 323

# Setting key constants because of issue on devices
pygame.K_RIGHT = 1
pygame.K_DOWN = 2
pygame.K_LEFT = 3
pygame.K_UP = 4
pygame.K_LCTRIL = 5
pygame.K_z = 6
RIGHT = pygame.K_RIGHT
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
UP = pygame.K_UP
CTRL = pygame.K_LCTRL
Z = pygame.K_z


def setup_map(map: str) -> 'Game':
    """Returns a game with map1"""
    game = Game()
    game.new()
    game.load_map(os.path.abspath(os.getcwd()) + '/maps/' + map)
    game.new()
    game._update()
    game.keys_pressed = keys_pressed
    return game


def set_keys(up, down, left, right, CTRL=0, Z=0):
    keys_pressed[pygame.K_UP] = up
    keys_pressed[pygame.K_DOWN] = down
    keys_pressed[pygame.K_LEFT] = left
    keys_pressed[pygame.K_RIGHT] = right


def test1_move_player_up():
    """
    Check if player is moved up correctly
    """
    game = setup_map("student_map1.txt")
    set_keys(1, 0, 0, 0)
    result = game.player.player_move(game)
    assert result == True
    assert game.player.y == 1


def test2_push_block():
    """
    Check if player pushes block correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
    [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][0]
    result = game.player.player_move(game)
    assert result == True
    assert game.player.x == 3
    assert wall.x == 4


def test3_create_rule_wall_is_push():
    """
    Check if player creates wall is push rule correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
    [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][0]
    result = game.player.player_move(game)
    game._update()
    assert "Wall isPush" in game._rules
    assert game.player.x == 3
    assert wall.x == 4


def test_4_follow_rule_wall_is_push():
    """
    Check if player follows rules correctly
    """
    game = setup_map("student_map3.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 3


def test_5_no_push():
    """
    Check if player is not able to push because of rule not existing
    """
    game = setup_map("student_map4.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 2


def test_6_out_of_bounds():
    """
    Player shouldn't go out of bounds
    """
    game = setup_map("student_map6.txt")
    set_keys(0, 1, 0, 0)
    oldx = game.player.x
    oldy = game.player.y
    assert game.player.player_move(game) == False
    assert game.player.x == oldx
    assert game.player.y == oldy


def test_7_flag_is_win():
    """
    Meepo should win when moving into flag
    """
    game = setup_map("student_map8.txt")
    player = game.player
    set_keys(0, 1, 0, 0)
    result = game.player.player_move(game)

    assert game.get_running() == False


def test_8_flag_is_lose():
    """
    Meepo should lose when moving into flag
    """
    game = setup_map("student_map9.txt")

    player = game.player
    set_keys(0, 1, 0, 0)
    result = game.player.player_move(game)
    game._update()

    assert game.player == None


def test_10_rule_priority():
    """
    New rule should be prioritized over old rule
    """
    game = setup_map("student_map10.txt")
    player = game.player

    for a in game._actors:
        if isinstance(a, actor.Flag):
            flag = a
            y = a.y

    set_keys(0, 0, 1, 0)
    result = game.player.player_move(game)
    game._update()
    set_keys(0, 1, 0, 0)
    result = game.player.player_move(game)
    game._update()

    assert "Flag isPush" in game._rules
    assert flag.y == y + 1


if __name__ == "__main__":

    import pytest
    pytest.main(['student_tests.py'])

