from random import randrange as rand
import pygame
import sys

cell_size = 18
cols = 10
rows = 22
maxfps = 30

# factory pattern
class ColorFactory:
    colors = [
        (0, 0, 0),
        (255, 85, 85),
        (100, 200, 115),
        (120, 108, 245),
        (255, 140, 50),
        (50, 120, 52),
        (146, 202, 73),
        (150, 161, 218),
        (35, 35, 35)
    ]

    @staticmethod
    def get_color(index):
        return ColorFactory.colors[index]

class ShapeFactory:
    tetris_shapes = [
        [[1, 1, 1],
         [0, 1, 0]],

        [[0, 2, 2],
         [2, 2, 0]],

        [[3, 3, 0],
         [0, 3, 3]],

        [[4, 0, 0],
         [4, 4, 4]],

        [[0, 0, 5],
         [5, 5, 5]],

        [[6, 6, 6, 6]],

        [[7, 7],
         [7, 7]]
    ]

    @staticmethod
    def create_shape():
        return ShapeFactory.tetris_shapes[rand(len(ShapeFactory.tetris_shapes))]


def rotate_clockwise(shape):
    return [
        [shape[y][x] for y in range(len(shape))]
        for x in range(len(shape[0]) - 1, -1, -1)
    ]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False

def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board

def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1

def new_board():
    board = [
        [0 for x in range(cols)]
        for y in range(rows)
    ]
    board += [[1 for x in range(cols)]]
    return board

class TetrisApp:
    _instance = None

    # singleton pattern (단일 인스턴스 보장)
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TetrisApp, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized') and self.initialized:
            return
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)] for y in range(rows)]
        self.default_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.next_stone = ShapeFactory.create_shape()
        self.state = None
        self.initialized = True
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = ShapeFactory.create_shape()
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0
        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.state = StateFactory.create_state('GameOverState', self)

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        self.state = StateFactory.create_state('PlayingState', self)
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False, (255, 255, 255), (0, 0, 0))
            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2
            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        ColorFactory.get_color(val),
                        pygame.Rect(
                            (off_x + x) * cell_size,
                            (off_y + y) * cell_size,
                            cell_size,
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

    def move(self, delta_x):
        if not self.state.gameover and not self.state.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
                self.stone_x = new_x

    def drop(self, manual):
        if not self.state.gameover and not self.state.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
                self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.state.gameover and not self.state.paused:
            while not self.drop(True):
                pass

    def rotate_stone(self):
        if not self.state.gameover and not self.state.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def toggle_pause(self):
        self.state.paused = not self.state.paused

    def start_game(self):
        if self.state.gameover:
            self.init_game()
            self.state.gameover = False

# state pattern (게임 진행 중 일 때의 상태 관리)
class GameState:
    def __init__(self, app):
        self.app = app

    def update(self):
        pass

    def render(self):
        pass

    def handle_event(self, event):
        pass
        
# state pattern
class PlayingState(GameState):
    def __init__(self, app):
        super().__init__(app)
        self.paused = False
        self.gameover = False

    def update(self):
        pass

    def render(self):
        pygame.draw.line(self.app.screen, (255, 255, 255),
                         (self.app.rlim + 1, 0), (self.app.rlim + 1, self.app.height - 1))
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
                self.app.rotate_stone()
            if event.key == pygame.K_SPACE:
                self.app.insta_drop()

# state pattern (게임이 종료되었을 때의 상태 관리)
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

# factory pattern
class StateFactory:
    @staticmethod
    def create_state(state_type, app):
        if state_type == 'PlayingState':
            return PlayingState(app)
        elif state_type == 'GameOverState':
            return GameOverState(app)
        else:
            raise ValueError(f"Unknown state type: {state_type}")

if __name__ == '__main__':
    App = TetrisApp()
    App.run()
