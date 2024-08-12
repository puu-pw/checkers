import pygame
import sys
import random
import copy  
from pygame.locals import *

pygame.font.init()

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
HIGH = (160, 190, 255)

NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

class Game:
    def __init__(self):
        self.graphics = Graphics()
        self.board = Board()
        self.turn = BLUE
        self.selected_piece = None
        self.hop = False
        self.selected_legal_moves = []
        self.max_depth = 5  

    def setup(self):
        self.graphics.setup_window()

    def event_loop(self):
        self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos())

        if self.selected_piece is not None:
            self.selected_legal_moves = self.board.legal_moves(self.selected_piece, self.hop)

        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate_game()

            if event.type == MOUSEBUTTONDOWN and self.turn == BLUE:
                if not self.hop:
                    if self.board.location(self.mouse_pos).occupant is not None and self.board.location(self.mouse_pos).occupant.color == self.turn:
                        self.selected_piece = self.mouse_pos
                    elif self.selected_piece is not None and self.mouse_pos in self.board.legal_moves(self.selected_piece):
                        self.board.move_piece(self.selected_piece, self.mouse_pos)
                        if self.mouse_pos not in self.board.adjacent(self.selected_piece):
                            self.board.remove_piece(((self.selected_piece[0] + self.mouse_pos[0]) // 2, (self.selected_piece[1] + self.mouse_pos[1]) // 2))
                            self.hop = True
                            self.selected_piece = self.mouse_pos
                        else:
                            self.end_turn()
                if self.hop:
                    if self.selected_piece is not None and self.mouse_pos in self.board.legal_moves(self.selected_piece, self.hop):
                        self.board.move_piece(self.selected_piece, self.mouse_pos)
                        self.board.remove_piece(((self.selected_piece[0] + self.mouse_pos[0]) // 2, (self.selected_piece[1] + self.mouse_pos[1]) // 2))
                    if not self.board.legal_moves(self.mouse_pos, self.hop):
                        self.end_turn()
                    else:
                        self.selected_piece = self.mouse_pos

    def update(self):
        self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)
        if self.turn == RED:
            self.ai_move()

    def terminate_game(self):
        pygame.quit()
        sys.exit()

    def main(self):
        self.setup()
        while True:
            self.event_loop()
            self.update()

    def end_turn(self):
        if self.turn == BLUE:
            self.turn = RED
        else:
            self.turn = BLUE

        self.selected_piece = None
        self.selected_legal_moves = []
        self.hop = False

        if self.check_for_endgame():
            if self.turn == BLUE:
                self.graphics.draw_message("RED WINS!")
            else:
                self.graphics.draw_message("BLUE WINS!")

    def check_for_endgame(self):
        for x in range(8):
            for y in range(8):
                if self.board.location((x, y)).occupant is not None and self.board.location((x, y)).occupant.color == self.turn:
                    if self.board.legal_moves((x, y)):
                        return False
        return True

    def ai_move(self):
        best_score, best_move = self.minimax(self.board, self.max_depth, float('-inf'), float('inf'), True)
        if best_move:
            self.board.move_piece(best_move[0], best_move[1])
            if best_move[1] not in self.board.adjacent(best_move[0]):
                self.board.remove_piece(((best_move[0][0] + best_move[1][0]) // 2, (best_move[0][1] + best_move[1][1]) // 2))
                while self.board.legal_moves(best_move[1], True):
                    next_moves = self.board.legal_moves(best_move[1], True)
                    next_move = next_moves[0]
                    self.board.move_piece(best_move[1], next_move)
                    self.board.remove_piece(((best_move[1][0] + next_move[0]) // 2, (best_move[1][1] + next_move[1]) // 2))
                    best_move = (best_move[1], next_move)
            self.end_turn()

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if depth == 0 or self.check_for_endgame():
            return self.evaluate_board(board), None

        possible_moves = self.get_all_possible_moves(board, RED if is_maximizing else BLUE)

        if is_maximizing:
            max_eval = float('-inf')
            best_move = None
            for move in possible_moves:
                new_board = self.simulate_move(board, move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in possible_moves:
                new_board = self.simulate_move(board, move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_board(self, board):
        score = 0
        for x in range(8):
            for y in range(8):
                occupant = board.matrix[x][y].occupant
                if occupant is not None:
                    if occupant.color == RED:
                        score += 5 if occupant.king else 1
                    else:
                        score -= 5 if occupant.king else 1
        return score

    def get_all_possible_moves(self, board, color):
        possible_moves = []
        for x in range(8):
            for y in range(8):
                if board.location((x, y)).occupant is not None and board.location((x, y)).occupant.color == color:
                    legal_moves = board.legal_moves((x, y))
                    for move in legal_moves:
                        possible_moves.append(((x, y), move))
        return possible_moves

    def simulate_move(self, board, move):
        new_board = copy.deepcopy(board)  
        new_board.move_piece(move[0], move[1])
        if move[1] not in new_board.adjacent(move[0]):
            new_board.remove_piece(((move[0][0] + move[1][0]) // 2, (move[0][1] + move[1][1]) // 2))
            while new_board.legal_moves(move[1], True):
                next_moves = new_board.legal_moves(move[1], True)
                next_move = next_moves[0]
                new_board.move_piece(move[1], next_move)
                new_board.remove_piece(((move[1][0] + next_move[0]) // 2, (move[1][1] + next_move[1]) // 2))
                move = (move[1], next_move)
        return new_board

class Graphics:
    def __init__(self):
        self.caption = "Checkers"
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.window_size = 600
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        self.background = pygame.image.load('checkerboard.png')
        self.square_size = self.window_size // 8
        self.piece_size = self.square_size // 2
        self.message = False

    def setup_window(self):
        pygame.init()
        pygame.display.set_caption(self.caption)

    def update_display(self, board, legal_moves, selected_piece):
        self.screen.blit(self.background, (0, 0))
        self.highlight_squares(legal_moves, selected_piece)
        self.draw_board_pieces(board)
        if self.message:
            self.screen.blit(self.text_surface_obj, self.text_rect_obj)
        pygame.display.update()
        self.clock.tick(self.fps)

    def draw_board_pieces(self, board):
        for x in range(8):
            for y in range(8):
                if board.matrix[x][y].occupant is not None:
                    pygame.draw.circle(self.screen, board.matrix[x][y].occupant.color, self.pixel_coords((x, y)), self.piece_size)
                    if board.matrix[x][y].occupant.king:
                        pygame.draw.circle(self.screen, GOLD, self.pixel_coords((x, y)), int(self.piece_size / 1.7), self.piece_size // 4)

    def pixel_coords(self, board_coords):
        return (board_coords[0] * self.square_size + self.square_size // 2, board_coords[1] * self.square_size + self.square_size // 2)

    def board_coords(self, pixel):
        return (pixel[0] // self.square_size, pixel[1] // self.square_size)

    def highlight_squares(self, legal_moves, selected_piece):
        for move in legal_moves:
            pygame.draw.rect(self.screen, HIGH, (move[0] * self.square_size, move[1] * self.square_size, self.square_size, self.square_size))
        if selected_piece is not None:
            pygame.draw.rect(self.screen, HIGH, (selected_piece[0] * self.square_size, selected_piece[1] * self.square_size, self.square_size, self.square_size), 4)

    def draw_message(self, message):
        self.font_obj = pygame.font.Font('freesansbold.ttf', 32)
        self.text_surface_obj = self.font_obj.render(message, True, RED, WHITE)
        self.text_rect_obj = self.text_surface_obj.get_rect()
        self.text_rect_obj.center = (self.window_size // 2, self.window_size // 2)
        self.message = True

class Board:
    def __init__(self):
        self.matrix = self.new_board()

    def new_board(self):
        matrix = [[None] * 8 for _ in range(8)]
        for x in range(8):
            for y in range(8):
                if x % 2 != y % 2:
                    if y < 3:
                        matrix[x][y] = Square(BLACK, Piece(RED))
                    elif y > 4:
                        matrix[x][y] = Square(BLACK, Piece(BLUE))
                    else:
                        matrix[x][y] = Square(BLACK, None)
                else:
                    matrix[x][y] = Square(WHITE, None)
        return matrix

    def rel(self, direction, pixel):
        if direction == NORTHWEST:
            return pixel[0] - 1, pixel[1] - 1
        elif direction == NORTHEAST:
            return pixel[0] + 1, pixel[1] - 1
        elif direction == SOUTHWEST:
            return pixel[0] - 1, pixel[1] + 1
        elif direction == SOUTHEAST:
            return pixel[0] + 1, pixel[1] + 1
        else:
            raise ValueError("Unknown direction: " + str(direction))

    def location(self, pixel):
        x, y = pixel
        return self.matrix[x][y]

    def adjacent(self, pixel):
        x, y = pixel
        return [self.rel(NORTHWEST, (x, y)), self.rel(NORTHEAST, (x, y)), self.rel(SOUTHWEST, (x, y)), self.rel(SOUTHEAST, (x, y))]

    def blind_legal_moves(self, pixel):
        x, y = pixel
        if self.matrix[x][y].occupant is not None:
            if not self.matrix[x][y].occupant.king and self.matrix[x][y].occupant.color == BLUE:
                blind_legal_moves = [self.rel(NORTHWEST, (x, y)), self.rel(NORTHEAST, (x, y))]
            elif not self.matrix[x][y].occupant.king and self.matrix[x][y].occupant.color == RED:
                blind_legal_moves = [self.rel(SOUTHWEST, (x, y)), self.rel(SOUTHEAST, (x, y))]
            else:
                blind_legal_moves = [self.rel(NORTHWEST, (x, y)), self.rel(NORTHEAST, (x, y)), self.rel(SOUTHWEST, (x, y)), self.rel(SOUTHEAST, (x, y))]
        else:
            blind_legal_moves = []
        return blind_legal_moves

    def legal_moves(self, pixel, hop=False):
        x, y = pixel
        blind_legal_moves = self.blind_legal_moves((x, y))
        legal_moves = []

        if not hop:
            for move in blind_legal_moves:
                if not hop:
                    if self.on_board(move):
                        if self.location(move).occupant is None:
                            legal_moves.append(move)
                        elif self.location(move).occupant.color != self.location((x, y)).occupant.color and self.on_board((move[0] + (move[0] - x), move[1] + (move[1] - y))) and self.location((move[0] + (move[0] - x), move[1] + (move[1] - y))).occupant is None:
                            legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))
        else:  
            for move in blind_legal_moves:
                if self.on_board(move) and self.location(move).occupant is not None:
                    if self.location(move).occupant.color != self.location((x, y)).occupant.color and self.on_board((move[0] + (move[0] - x), move[1] + (move[1] - y))) and self.location((move[0] + (move[0] - x), move[1] + (move[1] - y))).occupant is None:
                        legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))
        return legal_moves

    def remove_piece(self, pixel):
        x, y = pixel
        self.matrix[x][y].occupant = None

    def move_piece(self, pixel_start, pixel_end):
        start_x, start_y = pixel_start
        end_x, end_y = pixel_end
        self.matrix[end_x][end_y].occupant = self.matrix[start_x][start_y].occupant
        self.remove_piece((start_x, start_y))
        self.king((end_x, end_y))

    def on_board(self, pixel):
        x, y = pixel
        return 0 <= x < 8 and 0 <= y < 8

    def king(self, pixel):
        x, y = pixel
        if self.location((x, y)).occupant is not None:
            if (self.location((x, y)).occupant.color == BLUE and y == 0) or (self.location((x, y)).occupant.color == RED and y == 7):
                self.location((x, y)).occupant.king = True

class Piece:
    def __init__(self, color, king=False):
        self.color = color
        self.king = king

class Square:
    def __init__(self, color, occupant=None):
        self.color = color
        self.occupant = occupant

def main():
    game = Game()
    game.main()

if __name__ == "__main__":
    main()
