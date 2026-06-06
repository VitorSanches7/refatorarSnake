"""Fixtures compartilhadas para todos os testes do projeto Snake."""
import pytest
from unittest.mock import patch

# Bloqueia pygame antes de qualquer import
import sys
sys.modules.setdefault("pygame", __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock())

from snake import Snake, SnakeAI, UP, DOWN, LEFT, RIGHT
from food import Food


# ---------------------------------------------------------------------------
# Fixtures de Snake
# ---------------------------------------------------------------------------

@pytest.fixture
def snake_default() -> Snake:
    """Cobra padrão com 3 segmentos apontando para a esquerda."""
    return Snake([(200, 200), (210, 200), (220, 200)], LEFT)


@pytest.fixture
def snake_short() -> Snake:
    """Cobra com apenas 1 segmento — útil para testes de colisão simples."""
    return Snake([(300, 300)], RIGHT)


@pytest.fixture
def snake_near_wall() -> Snake:
    """Cobra posicionada perto da borda direita."""
    return Snake([(590, 300)], RIGHT)


@pytest.fixture
def snake_near_top() -> Snake:
    """Cobra posicionada perto da borda superior."""
    return Snake([(300, 0)], UP)


# ---------------------------------------------------------------------------
# Fixtures de SnakeAI
# ---------------------------------------------------------------------------

@pytest.fixture
def snake_ai_default() -> SnakeAI:
    """Cobra IA padrão com 3 segmentos."""
    return SnakeAI([(100, 100), (110, 100), (120, 100)], LEFT)


# ---------------------------------------------------------------------------
# Fixtures de Food
# ---------------------------------------------------------------------------

@pytest.fixture
def food_fixed() -> Food:
    """Food com posição fixada em (50, 50) via mock."""
    with patch("food.on_grid_random", return_value=(50, 50)):
        f = Food()
    return f


@pytest.fixture
def food_at_200_200() -> Food:
    """Food posicionada em (200, 200) — mesma posição da cabeça da cobra padrão."""
    with patch("food.on_grid_random", return_value=(200, 200)):
        f = Food()
    return f


# ---------------------------------------------------------------------------
# Fixtures de estado do jogo
# ---------------------------------------------------------------------------

@pytest.fixture
def game_state() -> dict:
    """Estado inicial de jogo para testes da classe Game."""
    return {
        "score": 0,
        "score2": 0,
        "fase": 1,
        "vida": 3,
        "game_over": False,
    }
