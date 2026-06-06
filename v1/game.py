"""Módulo principal do jogo Snake."""
import time
import pygame

from snake import Snake, SnakeAI, collision, UP, DOWN, LEFT, RIGHT
from food import Food


class Game:
    """Gerencia o estado e o loop principal do jogo."""

    SCREEN_SIZE = 600
    FPS = 10
    GRID_COLOR = (40, 40, 40)

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.SCREEN_SIZE, self.SCREEN_SIZE)
        )
        pygame.display.set_caption("Snake")

        self.backgrounds = self._load_backgrounds()
        self.font = pygame.font.Font("freesansbold.ttf", 18)
        self.clock = pygame.time.Clock()

        self.snake = Snake([(200, 200), (210, 200), (220, 200)], LEFT)
        self.snake_ai = SnakeAI([(100, 100), (110, 100), (120, 100)], LEFT)
        self.food = Food()

        self.score: int = 0
        self.score2: int = 0
        self.fase: int = 1
        self.vida: int = 3
        self.game_over: bool = False

        self.snake_skin = pygame.Surface((10, 10))
        self.snake_skin.fill((255, 255, 0))
        self.snake_ai_skin = pygame.Surface((10, 10))
        self.snake_ai_skin.fill((255, 0, 255))
        self.apple_surf = pygame.Surface((10, 10))
        self.apple_surf.fill((255, 255, 255))
        self.snake_ai_color: int = 1
        self.snake_color: int = 1

    def _load_backgrounds(self) -> list:
        bgs = []
        for name in ["FUNDO.jpeg", "FUNDO2.jpg", "FUNDO3.jpg"]:
            img = pygame.image.load(name)
            img = pygame.transform.scale(img, (self.SCREEN_SIZE, self.SCREEN_SIZE))
            bgs.append(img)
        return bgs

    def _handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.snake.set_direction(UP)
                elif event.key == pygame.K_s:
                    self.snake.set_direction(DOWN)
                elif event.key == pygame.K_a:
                    self.snake.set_direction(LEFT)
                elif event.key == pygame.K_d:
                    self.snake.set_direction(RIGHT)

    def _update_fase(self) -> None:
        if self.score < 30:
            self.fase = 1
        elif self.score < 50:
            self.fase = 2
        elif self.score < 65:
            self.fase = 3
        else:
            self.fase = 4

        if self.score == 40:
            self.vida += 1
        if self.score == 50:
            self.vida += 1

    def _update_player(self) -> None:
        if collision(self.snake.head, self.food.position):
            self.food.respawn()
            self.snake.grow()
            self.score += 1

        self.snake.move()

        # Verifica colisões APÓS o movimento
        if self.snake.hits_wall():
            self.vida = -1
        else:
            if self.snake.hits_itself():
                self.vida -= 1
            if self.snake.hits_snake(self.snake_ai.body):
                self.vida -= 1

        if self.vida < 0:
            self.game_over = True

    def _update_ai(self) -> None:
        self.snake_ai.choose_direction(self.food.position)
        # Verifica colisão com comida ANTES de mover (posição atual da cabeça)
        ate_food = collision(self.snake_ai.head, self.food.position)
        self.snake_ai.safe_move(self.snake.body)

        if ate_food:
            self.food.respawn()
            self.snake_ai.grow()
            if self.fase == 3:
                self.score -= 1
            else:
                self.score2 += 1

        self._cycle_ai_color()

    def _cycle_ai_color(self) -> None:
        if self.snake_ai_color == 0:
            self.snake_ai_skin.fill((0, 45, 150))
            self.snake_ai_color = 1
        else:
            self.snake_ai_skin.fill((100, 0, 0))
            self.snake_ai_color = 0

    def _draw_grid(self) -> None:
        for x in range(0, self.SCREEN_SIZE, 10):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 0), (x, self.SCREEN_SIZE))
        for y in range(0, self.SCREEN_SIZE, 10):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.SCREEN_SIZE, y))

    def _draw_hud(self) -> None:
        texts = [
            (f"Vida: {self.vida}", (200, 50, 100), (0, 10)),
            (f"Fase: {self.fase}", (0, 100, 0), (400, 10)),
            (f"Score: {self.score}", (0, 0, 100), (480, 10)),
        ]
        if self.fase == 3:
            texts.append((f"Chefão: {self.score2}", (158, 0, 0), (250, 10)))

        for text, color, pos in texts:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, pos)

    def _draw_entities(self) -> None:
        self.screen.blit(self.apple_surf, self.food.position)
        for pos in self.snake.body:
            self.screen.blit(self.snake_skin, pos)
        for pos in self.snake_ai.body:
            self.screen.blit(self.snake_ai_skin, pos)

    def _show_victory(self) -> None:
        font_big = pygame.font.Font("freesansbold.ttf", 50)
        surf = font_big.render("Você Venceu!!!", True, (55, 55, 55))
        rect = surf.get_rect(midtop=(self.SCREEN_SIZE // 2, 10))
        self.screen.blit(surf, rect)
        pygame.display.update()
        time.sleep(7)

    def _show_game_over(self) -> None:
        font_big = pygame.font.Font("freesansbold.ttf", 75)
        surf = font_big.render("Game Over", True, (0, 0, 0))
        rect = surf.get_rect(midtop=(self.SCREEN_SIZE // 2, 10))
        self.screen.blit(surf, rect)
        pygame.display.update()
        pygame.time.wait(500)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    def run(self) -> None:
        """Loop principal do jogo."""
        while not self.game_over:
            self.clock.tick(self.FPS)
            self._handle_input()
            self._update_fase()

            if self.fase == 4:
                bg_idx = 2
            elif self.fase == 3:
                bg_idx = 2
            elif self.fase == 2:
                bg_idx = 1
            else:
                bg_idx = 0

            self.screen.blit(self.backgrounds[bg_idx], (0, 0))

            if self.fase == 1:
                self._draw_grid()

            self._update_player()
            self._update_ai()

            if self.game_over:
                break

            self._draw_entities()
            self._draw_hud()
            pygame.display.update()

            if self.fase == 4:
                self._show_victory()
                break

        self._show_game_over()


if __name__ == "__main__":
    game = Game()
    game.run()
