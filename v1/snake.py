"""Módulo da cobra do jogador e da cobra IA."""
import random
from typing import List, Tuple

# Direções
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 4

Position = Tuple[int, int]


def on_grid_random() -> Position:
    """Retorna uma posição aleatória na grade."""
    x = random.randint(0, 59)
    y = random.randint(0, 59)
    return (x * 10, y * 10)


def collision(c1: Position, c2: Position) -> bool:
    """Verifica se duas posições colidem."""
    return c1[0] == c2[0] and c1[1] == c2[1]


class Snake:
    """Cobra controlada pelo jogador."""

    def __init__(self, positions: List[Position], direction: int = LEFT) -> None:
        self.body: List[Position] = positions
        self.direction: int = direction

    @property
    def head(self) -> Position:
        return self.body[0]

    def set_direction(self, new_direction: int) -> None:
        """Muda direção evitando inversão imediata."""
        opposites = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        if new_direction != opposites.get(self.direction):
            self.direction = new_direction

    def move(self) -> None:
        """Move a cobra na direção atual."""
        head_x, head_y = self.head
        if self.direction == UP:
            new_head = (head_x, head_y - 10)
        elif self.direction == DOWN:
            new_head = (head_x, head_y + 10)
        elif self.direction == RIGHT:
            new_head = (head_x + 10, head_y)
        else:  # LEFT
            new_head = (head_x - 10, head_y)

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = self.body[i - 1]
        self.body[0] = new_head

    def grow(self) -> None:
        """Aumenta o tamanho da cobra."""
        self.body.append((0, 0))

    def hits_wall(self, width: int = 600, height: int = 600) -> bool:
        """Verifica se a cobra bateu na parede."""
        x, y = self.head
        return x >= width or y >= height or x < 0 or y < 0

    def hits_itself(self) -> bool:
        """Verifica colisão com o próprio corpo."""
        return any(
            self.head[0] == self.body[i][0] and self.head[1] == self.body[i][1]
            for i in range(1, len(self.body))
        )

    def hits_snake(self, other_body: List[Position]) -> bool:
        """Verifica colisão com outra cobra."""
        return any(
            self.head[0] == seg[0] and self.head[1] == seg[1]
            for seg in other_body[1:]
        )


class SnakeAI(Snake):
    """Cobra controlada por IA."""

    def __init__(self, positions: List[Position], direction: int = LEFT) -> None:
        super().__init__(positions, direction)

    def choose_direction(self, target: Position) -> None:
        """Move em direção ao alvo evitando inversão."""
        opposites = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        head_x, head_y = self.head

        if target[0] > head_x and self.direction != LEFT:
            self.direction = RIGHT
        elif target[0] < head_x and self.direction != RIGHT:
            self.direction = LEFT
        elif target[1] > head_y and self.direction != UP:
            self.direction = DOWN
        elif target[1] < head_y and self.direction != DOWN:
            self.direction = UP

    def safe_move(
        self,
        other_body: List[Position],
        width: int = 600,
        height: int = 600,
    ) -> None:
        """Move com verificação de segurança; teleporta se colidir."""
        head_x, head_y = self.head
        if self.direction == UP:
            next_pos = (head_x, head_y - 10)
        elif self.direction == DOWN:
            next_pos = (head_x, head_y + 10)
        elif self.direction == RIGHT:
            next_pos = (head_x + 10, head_y)
        else:
            next_pos = (head_x - 10, head_y)

        unsafe = (
            next_pos in self.body
            or next_pos in other_body
            or next_pos[0] < 0
            or next_pos[1] < 0
            or next_pos[0] >= width
            or next_pos[1] >= height
        )

        if unsafe:
            self.body[0] = on_grid_random()
        else:
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i] = self.body[i - 1]
            self.body[0] = next_pos
