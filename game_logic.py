from config import cols, rows

class PlayGame:
    @staticmethod
    def rotate(shape):
        return [
            [shape[y][x] for y in range(len(shape))]
            for x in range(len(shape[0]) - 1, -1, -1)
        ]

    @staticmethod
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

    @staticmethod
    def remove_row(board, row):
        del board[row]
        return [[0 for _ in range(cols)]] + board

    @staticmethod
    def join_matrices(mat1, mat2, mat2_off):
        off_x, off_y = mat2_off
        for cy, row in enumerate(mat2):
            for cx, val in enumerate(row):
                mat1[cy + off_y - 1][cx + off_x] += val
        return mat1

    @staticmethod
    def new_board():
        board = [
            [0 for _ in range(cols)]
            for _ in range(rows)
        ]
        board += [[1 for _ in range(cols)]]
        return board
