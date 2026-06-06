"""Testes para food.py."""
import pytest
from unittest.mock import patch

from food import Food


def test_food_has_position(food_fixed):
    assert food_fixed.position == (50, 50)


def test_food_respawn_changes_position():
    with patch("food.on_grid_random", side_effect=[(50, 50), (100, 200)]):
        f = Food()
        assert f.position == (50, 50)
        f.respawn()
        assert f.position == (100, 200)


@pytest.mark.parametrize("new_pos", [
    (0, 0), (590, 590), (300, 240), (10, 10),
])
def test_food_respawn_parametrized(new_pos):
    with patch("food.on_grid_random", return_value=new_pos):
        f = Food()
        f.respawn()
    assert f.position == new_pos
