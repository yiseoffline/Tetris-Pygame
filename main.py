import pygame
from config import cell_size, cols, rows, maxfps
from factories import ShapeFactory, StateFactory, ColorFactory
from game_logic import PlayGame

class TetrisApp:
    _instance = None
    p = PlayGame()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TetrisApp, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.p = PlayGame
        if hasattr(self, 'initialized') and self.initialized:
            return
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = self._create_background_grid()
        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.next_stone = ShapeFactory.create()
        self.state = None
        self.initialized = True
        self.init_game()

    def _create_background_grid(self):
        return [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = ShapeFactory.create()
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0
        if self.p.check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.state = StateFactory.create('GameOverState', self)

    def init_game(self):
        self.board = PlayGame.new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        self.state = StateFactory.create('PlayingState', self)
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(line, False, (255, 255, 255), (0, 0, 0)), (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False, (255, 255, 255), (0, 0, 0))
            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2
            self.screen.blit(msg_image, (self.width // 2 - msgim_center_x, self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, ColorFactory.create(val),
                                     pygame.Rect((off_x + x) * cell_size, (off_y + y) * cell_size, cell_size,
                                                 cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def run(self):
        dont_burn_my_cpu = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            if self.state:
                self.state.update()
                self.state.render()
            pygame.display.update()
            dont_burn_my_cpu.tick(maxfps)
            for event in pygame.event.get():
                self.handle_event(event)

    def handle_event(self, event):
        if self.state:
            self.state.handle_event(event)

    def move(self, x):
        if not self.state.gameover and not self.state.paused:
            new_x = self.stone_x + x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not self.p.check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x

    def drop(self, manual):
        if not self.state.gameover and not self.state.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if self.p.check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = self.p.join_matrices(self.board, self.stone, (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = self.p.remove_row(self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def rotate_block(self):
        if not self.state.gameover and not self.state.paused:
            new_stone = self.p.rotate(self.stone)
            if not self.p.check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.state.paused = not self.state.paused

    def start_game(self):
        if self.state.gameover:
            self.init_game()
            self.state.gameover = False


if __name__ == '__main__':
    App = TetrisApp()
    App.run()
