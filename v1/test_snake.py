"""Testes para snake.py — cobra do jogador e cobra IA."""
import pytest
from unittest.mock import patch

from snake import Snake, SnakeAI, collision, on_grid_random, UP, DOWN, LEFT, RIGHT


# ---------------------------------------------------------------------------
# on_grid_random
# ---------------------------------------------------------------------------

def test_on_grid_random_returns_tuple():
    pos = on_grid_random()
    assert isinstance(pos, tuple)
    assert len(pos) == 2


def test_on_grid_random_multiples_of_10():
    for _ in range(50):
        x, y = on_grid_random()
        assert x % 10 == 0
        assert y % 10 == 0


def test_on_grid_random_within_bounds():
    for _ in range(50):
        x, y = on_grid_random()
        assert 0 <= x <= 590
        assert 0 <= y <= 590


# ---------------------------------------------------------------------------
# collision
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("c1,c2,expected", [
    ((100, 100), (100, 100), True),
    ((100, 100), (110, 100), False),
    ((0, 0), (0, 0), True),
    ((590, 590), (590, 590), True),
    ((10, 20), (20, 10), False),
])
def test_collision(c1, c2, expected):
    assert collision(c1, c2) == expected


# ---------------------------------------------------------------------------
# Snake.head
# ---------------------------------------------------------------------------

def test_snake_head(snake_default):
    assert snake_default.head == (200, 200)


# ---------------------------------------------------------------------------
# Snake.set_direction
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("current,attempt,expected", [
    (LEFT, UP, UP),
    (LEFT, DOWN, DOWN),
    (LEFT, RIGHT, LEFT),   # oposto bloqueado
    (UP, DOWN, UP),        # oposto bloqueado
    (DOWN, UP, DOWN),      # oposto bloqueado
    (RIGHT, LEFT, RIGHT),  # oposto bloqueado
    (RIGHT, UP, UP),
])
def test_set_direction(snake_default, current, attempt, expected):
    snake_default.direction = current
    snake_default.set_direction(attempt)
    assert snake_default.direction == expected


# ---------------------------------------------------------------------------
# Snake.move
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("direction,expected_head", [
    (UP, (200, 190)),
    (DOWN, (200, 210)),
    (RIGHT, (210, 200)),
    (LEFT, (190, 200)),
])
def test_move_direction(direction, expected_head):
    snake = Snake([(200, 200), (210, 200), (220, 200)], direction)
    snake.move()
    assert snake.head == expected_head


def test_move_body_follows_head(snake_default):
    original_head = snake_default.head
    snake_default.move()
    assert snake_default.body[1] == original_head


# ---------------------------------------------------------------------------
# Snake.grow
# ---------------------------------------------------------------------------

def test_grow_increases_length(snake_default):
    length_before = len(snake_default.body)
    snake_default.grow()
    assert len(snake_default.body) == length_before + 1


# ---------------------------------------------------------------------------
# Snake.hits_wall
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("positions,expected", [
    ([(600, 300)], True),
    ([(300, 600)], True),
    ([(-10, 300)], True),
    ([(300, -10)], True),
    ([(590, 590)], False),
    ([(0, 0)], False),
])
def test_hits_wall(positions, expected):
    snake = Snake(positions, RIGHT)
    assert snake.hits_wall() == expected


def test_near_wall_snake_hits_after_move(snake_near_wall):
    snake_near_wall.move()
    assert snake_near_wall.hits_wall()


# ---------------------------------------------------------------------------
# Snake.hits_itself
# ---------------------------------------------------------------------------

def test_no_self_collision(snake_default):
    assert not snake_default.hits_itself()


def test_self_collision():
    # Cobra com cabeça na mesma posição do segundo segmento
    snake = Snake([(200, 200), (200, 200), (210, 200)], LEFT)
    assert snake.hits_itself()


# ---------------------------------------------------------------------------
# Snake.hits_snake
# ---------------------------------------------------------------------------

def test_hits_other_snake(snake_default, snake_ai_default):
    # Coloca cabeça do jogador no corpo da IA
    snake_default.body[0] = snake_ai_default.body[1]
    assert snake_default.hits_snake(snake_ai_default.body)


def test_no_collision_with_other_snake(snake_default, snake_ai_default):
    assert not snake_default.hits_snake(snake_ai_default.body)


# ---------------------------------------------------------------------------
# SnakeAI.choose_direction
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("initial_dir,head,target,expected_direction", [
    (UP,    (100, 100), (200, 100), RIGHT),
    (UP,    (200, 100), (100, 100), LEFT),
    (LEFT,  (100, 100), (100, 200), DOWN),
    (RIGHT, (100, 200), (100, 100), UP),
])
def test_choose_direction(initial_dir, head, target, expected_direction):
    ai = SnakeAI([head, (head[0] + 10, head[1])], initial_dir)
    ai.choose_direction(target)
    assert ai.direction == expected_direction


# ---------------------------------------------------------------------------
# SnakeAI.safe_move — teleporte em colisão iminente
# ---------------------------------------------------------------------------

def test_safe_move_teleports_on_wall():
    """IA deve teleportar quando a próxima posição estaria fora do mapa."""
    ai = SnakeAI([(590, 100)], RIGHT)
    with patch("snake.on_grid_random", return_value=(300, 300)):
        ai.safe_move([])
    assert ai.head == (300, 300)


def test_safe_move_normal(snake_ai_default):
    head_before = snake_ai_default.head
    snake_ai_default.direction = RIGHT
    snake_ai_default.safe_move([])
    assert snake_ai_default.head != head_before
