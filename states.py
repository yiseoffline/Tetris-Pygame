import pygame
from config import cell_size, cols

class GameState:
    def __init__(self, app):
        self.app = app

    def update(self):
        pass

    def render(self):
        pass

    def handle_event(self, event):
        pass


class PlayingState(GameState):
    def __init__(self, app):
        super().__init__(app)
        self.paused = False
        self.gameover = False

    def update(self):
        pass

    def render(self):
        pygame.draw.line(self.app.screen, (255, 255, 255), (self.app.rlim + 1, 0),
                         (self.app.rlim + 1, self.app.height - 1))
        self.app.disp_msg(f"Next:", (self.app.rlim + cell_size, 2))
        self.app.disp_msg(f"Score: {self.app.score}\n\nLevel: {self.app.level}\n\nLines: {self.app.lines}",
                          (self.app.rlim + cell_size, cell_size * 5))
        self.app.draw_matrix(self.app.bground_grid, (0, 0))
        self.app.draw_matrix(self.app.board, (0, 0))
        self.app.draw_matrix(self.app.stone, (self.app.stone_x, self.app.stone_y))
        self.app.draw_matrix(self.app.next_stone, (cols + 1, 2))

    def handle_event(self, event):
        if event.type == pygame.USEREVENT + 1:
            self.app.drop(False)
        elif event.type == pygame.QUIT:
            self.app.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.toggle_pause()
            if event.key == pygame.K_LEFT:
                self.app.move(-1)
            if event.key == pygame.K_RIGHT:
                self.app.move(+1)
            if event.key == pygame.K_DOWN:
                self.app.drop(True)
            if event.key == pygame.K_UP:
                self.app.rotate_block()


class GameOverState(GameState):
    def update(self):
        pass

    def render(self):
        self.app.center_msg("""Game Over!\nYour score: %d\nPress space to continue""" % self.app.score)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.app.start_game()
