"""Testes para game.py — lógica de jogo isolada de pygame."""
import sys
import types
import pytest
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Mock completo do pygame ANTES de qualquer import do jogo
# ---------------------------------------------------------------------------

def _make_pygame_mock() -> MagicMock:
    pg = MagicMock()

    surface = MagicMock()
    surface.get_rect.return_value = MagicMock(topleft=(0, 0), midtop=(300, 10))
    pg.Surface.return_value = surface
    pg.font.Font.return_value.render.return_value = surface
    pg.image.load.return_value = surface
    pg.transform.scale.return_value = surface
    pg.display.set_mode.return_value = MagicMock()

    # Constantes usadas diretamente como pygame.QUIT etc
    pg.QUIT = 256
    pg.KEYDOWN = 768
    pg.K_w = ord("w")
    pg.K_s = ord("s")
    pg.K_a = ord("a")
    pg.K_d = ord("d")

    pg.event.get.return_value = []

    return pg


_pygame_mock = _make_pygame_mock()
sys.modules["pygame"] = _pygame_mock
sys.modules["pygame.locals"] = _pygame_mock.locals

# Agora podemos importar com segurança
from snake import Snake, SnakeAI, UP, DOWN, LEFT, RIGHT, collision
from food import Food
from game import Game


# ---------------------------------------------------------------------------
# Fixture: instância de Game sem efeitos colaterais
# ---------------------------------------------------------------------------

@pytest.fixture
def game() -> Game:
    with patch("game.pygame.image.load", return_value=MagicMock()), \
         patch("game.pygame.transform.scale", return_value=MagicMock()), \
         patch("game.pygame.font.Font", return_value=MagicMock()), \
         patch("game.pygame.display.set_mode", return_value=MagicMock()), \
         patch("game.pygame.display.set_caption"), \
         patch("game.pygame.init"), \
         patch("food.on_grid_random", return_value=(50, 50)):
        g = Game()
    return g


# ---------------------------------------------------------------------------
# Testes de _update_fase
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score,expected_fase", [
    (0, 1),
    (29, 1),
    (30, 2),
    (49, 2),
    (50, 3),
    (64, 3),
    (65, 4),
])
def test_update_fase(game, score, expected_fase):
    game.score = score
    game._update_fase()
    assert game.fase == expected_fase


def test_update_fase_bonus_vida_40(game):
    game.score = 40
    game.vida = 3
    game._update_fase()
    assert game.vida == 4


def test_update_fase_bonus_vida_50(game):
    game.score = 50
    game.vida = 3
    game._update_fase()
    assert game.vida == 4


# ---------------------------------------------------------------------------
# Testes de _update_player
# ---------------------------------------------------------------------------

def test_player_eats_food_increases_score(game):
    game.snake.body[0] = (50, 50)
    game.food.position = (50, 50)
    initial_score = game.score

    with patch("food.on_grid_random", return_value=(200, 200)):
        game._update_player()

    assert game.score == initial_score + 1


def test_player_eats_food_grows_snake(game):
    game.snake.body[0] = (50, 50)
    game.food.position = (50, 50)
    initial_len = len(game.snake.body)

    with patch("food.on_grid_random", return_value=(200, 200)):
        game._update_player()

    assert len(game.snake.body) == initial_len + 1


def test_player_hits_wall_sets_game_over(game):
    # Cobra indo para direita, cabeça em 590 → move para 600 → hits_wall
    game.snake.body = [(590, 300), (580, 300), (570, 300)]
    game.snake.direction = RIGHT
    game._update_player()
    assert game.game_over


def test_player_hits_itself_decreases_vida(game):
    # Cobra andando para direita: (190,200) vai para (200,200) = posição do seg[1]
    game.snake.body = [(190, 200), (200, 200), (210, 200)]
    game.snake.direction = RIGHT
    vida_before = game.vida
    game._update_player()
    assert game.vida == vida_before - 1


# ---------------------------------------------------------------------------
# Testes de _update_ai
# ---------------------------------------------------------------------------

def test_ai_eats_food_in_fase1_increases_score2(game):
    game.fase = 1
    game.snake_ai.body[0] = (50, 50)
    game.food.position = (50, 50)
    initial = game.score2

    with patch("food.on_grid_random", return_value=(400, 400)):
        game._update_ai()

    assert game.score2 == initial + 1


def test_ai_eats_food_in_fase3_decreases_score(game):
    game.fase = 3
    game.snake_ai.body[0] = (50, 50)
    game.food.position = (50, 50)
    game.score = 10

    with patch("food.on_grid_random", return_value=(400, 400)):
        game._update_ai()

    assert game.score == 9


# ---------------------------------------------------------------------------
# Testes de _cycle_ai_color
# ---------------------------------------------------------------------------

def test_cycle_ai_color_alternates(game):
    game.snake_ai_color = 1
    game._cycle_ai_color()
    assert game.snake_ai_color == 0
    game._cycle_ai_color()
    assert game.snake_ai_color == 1


# ---------------------------------------------------------------------------
# Testes de _handle_input — mock de eventos de teclado
# ---------------------------------------------------------------------------

def _make_key_event(key: int) -> MagicMock:
    event = MagicMock()
    event.type = _pygame_mock.KEYDOWN
    event.key = key
    return event


@pytest.mark.parametrize("key,initial_dir,expected_direction", [
    (_pygame_mock.K_w, LEFT,  UP),
    (_pygame_mock.K_s, LEFT,  DOWN),
    (_pygame_mock.K_a, UP,    LEFT),
    (_pygame_mock.K_d, UP,    RIGHT),
])
def test_handle_input_direction(game, key, initial_dir, expected_direction):
    event = _make_key_event(key)
    game.snake.direction = initial_dir
    with patch("game.pygame.event.get", return_value=[event]):
        game._handle_input()
    assert game.snake.direction == expected_direction
