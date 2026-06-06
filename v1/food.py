"""Módulo da comida (maçã) do jogo."""
from typing import Tuple
from snake import on_grid_random

Position = Tuple[int, int]


class Food:
    """Representa a comida que a cobra deve comer."""

    def __init__(self) -> None:
        self.position: Position = on_grid_random()

    def respawn(self) -> None:
        """Reposiciona a comida em local aleatório."""
        self.position = on_grid_random()

