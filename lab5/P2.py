# importa bibliotecile necesare
import atexit
import os
import sys
import pygame
import time
import sqlite3
import sysv_ipc
from sysv_ipc import MessageQueue, IPC_CREAT

# clasa principala pentru jocul x si 0
class TicTacToe:
    def __init__(self, player, mq_send, mq_receive, p_number):
        # initializeaza pygame
        pygame.init()
        # seteaza dimensiunile gridului
        self.GRID_SIZE = 900
        # seteaza latimea si inaltimea ferestrei
        self.WIDTH, self.HEIGHT = self.GRID_SIZE, self.GRID_SIZE + 100
        # grosimea liniilor
        self.LINE_WIDTH = 15
        # numarul de randuri si coloane
        self.BOARD_ROWS, self.BOARD_COLS = 3, 3
        # dimensiunea unui patrat
        self.SQUARE_SIZE = self.WIDTH // self.BOARD_COLS
        # culorile folosite
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        # creeaza fereastra
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        # seteaza titlul ferestrei
        pygame.display.set_caption("X si O")
        # initializeaza fontul
        self.font = pygame.font.Font(None, 70)
        # umple ecranul cu alb
        self.screen.fill(self.WHITE)
        # initializeaza tabla de joc
        self.board = [[" " for _ in range(self.BOARD_COLS)] for _ in range(self.BOARD_ROWS)]
        # seteaza jucatorul curent
        self.player = player
        # seteaza starea jocului
        self.game_over = False
        # deseneaza liniile tablei
        self.draw_lines()
        # initializeaza managerul de fisiere
        self.file_manager = FileManager()
        # initializeaza managerul de baza de date
        self.data_manager = DatabaseManager()
        # salveaza starea mutarilor in fisier
        self.file_manager.save_draw_move_to_file(True, False)
        # afiseaza informatii despre jucator
        self.info_text = self.font.render(f"Sunteti {self.player}", True, self.BLACK)
        self.screen.blit(self.info_text, (self.WIDTH // 2 - 110, self.HEIGHT - 43))
        # citeste numele jucatorilor din fisier
        with open(self.file_manager.PLAYER_NAMES, "r") as file:
            lines = file.readlines()
        player1 = lines[0].strip()
        player2 = lines[1].strip()
        # obtine scorurile jucatorilor
        score_player1, score_player2 = self.data_manager.get_score(player1, player2)
        # afiseaza scorurile
        self.score_text = self.font.render(
            f"{player1} - {score_player1}                            {player2} - {score_player2}", True, self.BLACK)
        self.screen.blit(self.score_text, (100, 0))
        # actualizeaza ecranul
        pygame.display.update()
        # seteaza cozile de mesaje
        self.mq_send = mq_send
        self.mq_receive = mq_receive
        # seteaza numarul jucatorului
        self.p_number = p_number

    # functie pentru desenarea liniilor tablei
    def draw_lines(self):
        grid_offset_x = (self.WIDTH - self.GRID_SIZE) // 2
        grid_offset_y = (self.HEIGHT - self.GRID_SIZE) // 2
        # deseneaza liniile orizontale si verticale
        for i in range(self.BOARD_ROWS + 1):
            pygame.draw.line(self.screen, self.BLACK, (grid_offset_x + self.SQUARE_SIZE * i, grid_offset_y),
                             (grid_offset_x + self.SQUARE_SIZE * i, grid_offset_y + self.GRID_SIZE), self.LINE_WIDTH)
            pygame.draw.line(self.screen, self.BLACK, (grid_offset_x, grid_offset_y + self.SQUARE_SIZE * i),
                             (grid_offset_x + self.GRID_SIZE, grid_offset_y + self.SQUARE_SIZE * i), self.LINE_WIDTH)

    # functie pentru desenarea tablei cu x si 0
    def draw_board(self):
        grid_offset_x = (self.WIDTH - self.GRID_SIZE) // 2
        grid_offset_y = (self.HEIGHT - self.GRID_SIZE) // 2
        # parcurge fiecare celula din tabla
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                # deseneaza x-ul
                if self.board[row][col] == "X":
                    pygame.draw.line(self.screen, self.RED, (
                        grid_offset_x + col * self.SQUARE_SIZE + 20, grid_offset_y + row * self.SQUARE_SIZE + 20), (
                                         grid_offset_x + (col + 1) * self.SQUARE_SIZE - 20,
                                         grid_offset_y + (row + 1) * self.SQUARE_SIZE - 20), self.LINE_WIDTH)
                    pygame.draw.line(self.screen, self.RED, (
                        grid_offset_x + (col + 1) * self.SQUARE_SIZE - 20, grid_offset_y + row * self.SQUARE_SIZE + 20),
                                     (
                                         grid_offset_x + col * self.SQUARE_SIZE + 20,
                                         grid_offset_y + (row + 1) * self.SQUARE_SIZE - 20), self.LINE_WIDTH)
                # deseneaza 0-ul
                elif self.board[row][col] == "O":
                    pygame.draw.circle(self.screen, self.BLUE, (
                        grid_offset_x + col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2,
                        grid_offset_y + row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2), self.SQUARE_SIZE // 2 - 20,
                                       self.LINE_WIDTH)

    # functie pentru verificarea castigatorului
    def check_win(self, player):
        # verifica liniile orizontale
        for i in range(self.BOARD_ROWS):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == player or \
                    self.board[0][i] == self.board[1][i] == self.board[2][i] == player:
                return True
        # verifica diagonalele
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player or \
                self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return True
        return False

    # functie pentru verificarea egalitatii
    def check_draw(self):
        # verifica daca mai sunt spatii goale
        for row in range(self.BOARD_ROWS):
            for col in range(self.BOARD_COLS):
                if self.board[row][col] == " ":
                    return False
        return True

    # functie pentru schimbarea jucatorului
    def switch_player(self):
        if self.player == "X":
            self.player = "O"
        else:
            self.player = "X"

    # functie pentru resetarea jocului
    def restart_game(self):
        # reseteaza ecranul
        self.screen.fill(self.WHITE)
        # redeseneaza liniile
        self.draw_lines()
        # reseteaza tabla
        self.board = [[" " for _ in range(self.BOARD_COLS)] for _ in range(self.BOARD_ROWS)]
        # reseteaza starea jocului
        self.game_over = False
        # seteaza jucatorul in functie de numar
        if self.p_number == 1:
            self.player = "X"
        else:
            self.player = "O"
        # reseteaza starea mutarilor in fisier
        self.file_manager.save_draw_move_to_file(True, False)
        # afiseaza informatii despre jucator
        self.info_text = self.font.render(f"Sunteti {self.player}", True, self.BLACK)
        self.screen.blit(self.info_text, (self.WIDTH // 2 - 110, self.HEIGHT - 43))
        # citeste numele jucatorilor
        with open(self.file_manager.PLAYER_NAMES, "r") as file:
            lines = file.readlines()
        player1 = lines[0].strip()
        player2 = lines[1].strip()
        # obtine scorurile
        score_player1, score_player2 = self.data_manager.get_score(player1, player2)
        # afiseaza scorurile
        self.score_text = self.font.render(
            f"{player1} - {score_player1}                            {player2} - {score_player2}", True, self.BLACK)
        self.screen.blit(self.score_text, (100, 0))
        # actualizeaza ecranul
        pygame.display.update()

    # functie pentru trimiterea unei mutari
    def send_move(self, row, col):
        self.mq_send.send(f"{self.player}:{row},{col}")

    # functie pentru primirea unei mutari
    def receive_move(self):
        try:
            message, _ = self.mq_receive.receive(0)
            return message.decode()
        except sysv_ipc.BusyError:
            return None

    # functie pentru golirea cozilor de mesaje
    def clear_queues(self):
        while True:
            try:
                self.mq_receive.receive(block=False)
            except sysv_ipc.BusyError:
                break

    # functia principala de rulare a jocului
    def main_loop(self):
        # goleste cozile de mesaje
        self.clear_queues()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if not self.game_over:
                    # citeste starea mutarilor din fisier
                    draw_moves = self.file_manager.read_each_line_from_file(self.file_manager.DRAW_MOVES)
                    draw_move_X = draw_moves[0].strip() == "True"
                    draw_move_O = draw_moves[1].strip() == "True"

                    # logica pentru jucatorul 1
                    if self.p_number == 1 and draw_move_X:
                        if self.player == "X":
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                # obtine pozitia mouse-ului
                                mouseX, mouseY = pygame.mouse.get_pos()
                                clicked_row = mouseY // self.SQUARE_SIZE
                                clicked_col = mouseX // self.SQUARE_SIZE

                                if self.board[clicked_row][clicked_col] == " ":
                                    # actualizeaza tabla
                                    self.board[clicked_row][clicked_col] = self.player
                                    # trimite mutarea
                                    self.send_move(clicked_row, clicked_col)
                                    # actualizeaza starea mutarilor
                                    self.file_manager.save_draw_move_to_file(False, True)
                                    # verifica daca jucatorul a castigat
                                    if self.check_win(self.player):
                                        self.game_over = True
                                        self.end_game(self.player)
                                    # verifica daca este egalitate
                                    elif self.check_draw():
                                        self.game_over = True
                                        self.end_game(None)
                                    # redeseneaza tabla
                                    self.draw_board()
                                    # schimba jucatorul
                                    self.switch_player()
                        elif self.player == "O":
                            self.switch_player()
                        # primeste mutarea adversarului
                        move = self.receive_move()
                        pygame.event.clear()
                        if move is not None and draw_move_X:
                            # proceseaza mutarea adversarului
                            player, row, col = move.split(":")[0], int(move.split(":")[1].split(",")[0]), int(
                                move.split(":")[1].split(",")[1])
                            self.board[row][col] = player
                            # verifica daca adversarul a castigat
                            if self.check_win(player):
                                self.game_over = True
                                self.end_game(player)
                            # verifica daca este egalitate
                            elif self.check_draw():
                                self.game_over = True
                                self.end_game(None)
                            # redeseneaza tabla
                            self.draw_board()
                    # logica pentru jucatorul 2 (similara cu jucatorul 1)
                    elif self.p_number == 2 and draw_move_O:
                        if self.player == "O":
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                mouseX, mouseY = pygame.mouse.get_pos()
                                clicked_row = mouseY // self.SQUARE_SIZE
                                clicked_col = mouseX // self.SQUARE_SIZE

                                if self.board[clicked_row][clicked_col] == " ":
                                    self.board[clicked_row][clicked_col] = self.player
                                    self.send_move(clicked_row, clicked_col)
                                    self.file_manager.save_draw_move_to_file(True, False)
                                    if self.check_win(self.player):
                                        self.game_over = True
                                        self.end_game(self.player)
                                    elif self.check_draw():
                                        self.game_over = True
                                        self.end_game(None)
                                    self.draw_board()
                                    self.switch_player()
                        elif self.player == "X":
                            self.switch_player()
                        move = self.receive_move()
                        pygame.event.clear()
                        if move is not None and draw_move_O:
                            player, row, col = move.split(":")[0], int(move.split(":")[1].split(",")[0]), int(
                                move.split(":")[1].split(",")[1])
                            self.board[row][col] = player
                            if self.check_win(player):
                                self.game_over = True
                                self.end_game(player)
                            elif self.check_draw():
                                self.game_over = True
                                self.end_game(None)
                            self.draw_board()

            # actualizeaza ecranul
            pygame.display.update()

    # functie pentru sfarsitul jocului
    def end_game(self, winner):
        # umple ecranul cu alb
        self.screen.fill(self.WHITE)
        # afiseaza mesajul de final
        if winner is None:
            end_text = self.font.render("Egalitate!", True, self.BLACK)
        else:
            end_text = self.font.render(f"{winner} castiga!", True, self.BLACK)
            # citeste numele jucatorilor
            with open(self.file_manager.PLAYER_NAMES, "r") as file:
                lines = file.readlines()
            player1 = lines[0].strip()
            player2 = lines[1].strip()
            # actualizeaza scorul in baza de date
            if winner == "X" and self.p_number == 1:
                self.data_manager.update_score(player1, player2, 1, 0)
            elif winner == "O" and self.p_number == 2:
                self.data_manager.update_score(player1, player2, 0, 1)
        # afiseaza mesajul
        self.screen.blit(end_text, (self.WIDTH // 2 - 120, self.HEIGHT // 2 - 56))
        # actualizeaza ecranul
        pygame.display.update()
        # asteapta 2 secunde
        time.sleep(2)
        # reincepe jocul
        self.restart_game()


# clasa pentru gestionarea bazei de date
class DatabaseManager:
    def __init__(self):
        # conecteaza la baza de date
        self.conn = sqlite3.connect("scores.db")
        self.c = self.conn.cursor()

        # creeaza tabela daca nu exista
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS scores (
            player1 TEXT,
            player2 TEXT,
            score1 INTEGER,
            score2 INTEGER,
            PRIMARY KEY (player1, player2)
            )
        ''')

    # functie pentru actualizarea scorului
    def update_score(self, player1, player2, score1, score2):
        self.c.execute('''
            INSERT INTO scores (player1, player2, score1, score2)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player1, player2) DO UPDATE SET score1 = score1 + ?,
            score2 = score2 + ?''', (player1, player2, score1, score2, score1, score2))
        # salveaza modificarile
        self.conn.commit()

    # functie pentru obtinerea scorului
    def get_score(self, player1, player2):
        self.c.execute('''
            SELECT score1, score2 FROM scores WHERE player1 = ? AND player2 = ?
            ''', (player1, player2))
        result = self.c.fetchone()
        return result if result else (0, 0)


# clasa pentru gestionarea fisierelor
class FileManager:
    def __init__(self):
        # chei pentru cozile de mesaje
        self.KEY1 = 128
        self.KEY2 = 129
        # numele fisierelor folosite
        self.FLAG_FILE = os.path.join(os.getcwd(), "process_flag")
        self.DRAW_MOVES = os.path.join(os.getcwd(), "draw_moves")
        self.PLAYER_NAMES = os.path.join(os.getcwd(), "player_names")
        # inregistreaza functiile de cleanup
        atexit.register(self.delete_flag_file)
        atexit.register(self.delete_draw_moves)
        atexit.register(self.delete_player_names)

    # functie pentru stergerea fisierului de flag
    def delete_flag_file(self):
        if os.path.exists(self.FLAG_FILE):
            os.remove(self.FLAG_FILE)

    # functie pentru stergerea fisierului de mutari
    def delete_draw_moves(self):
        if os.path.exists(self.DRAW_MOVES):
            os.remove(self.DRAW_MOVES)

    # functie pentru stergerea fisierului de nume
    def delete_player_names(self):
        if os.path.exists(self.PLAYER_NAMES):
            os.remove(self.PLAYER_NAMES)

    # functie pentru salvarea starii mutarilor
    def save_draw_move_to_file(self, draw_move_x, draw_move_o):
        with open(self.DRAW_MOVES, "w") as file:
            file.write(str(draw_move_x) + "\n")
            file.write(str(draw_move_o) + "\n")

    # functie pentru citirea din fisier
    def read_each_line_from_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
        except Exception:
            print("Celalalta instanta a jocului a iesit!")
            sys.exit(0)
        return lines


# clasa pentru gestionarea jucatorului
class Player:
    numar_instante = 0

    def __init__(self, player, mq_send, mq_receive, process_num, file_manager):
        # initializeaza jucatorul
        self.player = player
        # seteaza cozile de mesaje
        self.mq_send = mq_send
        self.mq_receive = mq_receive
        # seteaza numarul procesului
        self.process_num = process_num
        # seteaza managerul de fisiere
        self.file_manager = file_manager
        # incrementeaza numarul de instante
        Player.numar_instante += 1

    # functie pentru setarea numelui jucatorului
    def set_name(self):
        # asteapta daca fisierul de flag nu este complet
        if os.path.getsize(file_manager.FLAG_FILE) < 2:
            print("Se asteapta pentru celalalt jucator...")
            while os.path.getsize(file_manager.FLAG_FILE) < 2:
                pass

        # citeste numele de la utilizator
        name = input("Dati numele pe care doriti sa-l folositi : ")
        # verifica daca numele exista deja
        if os.path.exists(self.file_manager.PLAYER_NAMES):
            with open(self.file_manager.PLAYER_NAMES, "r") as file:
                line = file.readline()
            while name + "\n" == line:
                name = input("Acest nume este deja detinut de celalalt jucator, reintroduceti : ")

        # salveaza numele in fisier
        with open(self.file_manager.PLAYER_NAMES, "a") as file:
            file.write(name + "\n")

        # asteapta pana celalalt jucator isi seteaza numele
        with open(self.file_manager.PLAYER_NAMES, "r") as file:
            lines = file.readlines()

        if len(lines) < 2:
            print("Se asteapta pana celalalt jucator isi pune numele...")
            while len(lines) < 2:
                with open(self.file_manager.PLAYER_NAMES, "r") as file:
                    lines = file.readlines()

    # functie pentru pornirea jocului
    def play_game(self):
        game = TicTacToe(self.player, self.mq_send, self.mq_receive, self.process_num)
        game.main_loop()


# punctul de intrare in program
if __name__ == "__main__":
    # initializeaza managerul de fisiere
    file_manager = FileManager()
    # verifica daca fisierul de flag nu exista
    if not os.path.exists(file_manager.FLAG_FILE):
        # creeaza fisierul de flag si scrie 1
        with open(file_manager.FLAG_FILE, "w") as f:
            f.write("1")
        # initializeaza jucatorul 1
        player_one = Player("X", MessageQueue(file_manager.KEY1, IPC_CREAT), MessageQueue(file_manager.KEY2, IPC_CREAT),
                            1, file_manager)
        # seteaza numele jucatorului 1
        player_one.set_name()
        # porneste jocul pentru jucatorul 1
        player_one.play_game()
    # verifica daca fisierul de flag are un singur caracter
    elif os.path.getsize(file_manager.FLAG_FILE) < 2:
        # adauga 2 in fisierul de flag
        with open(file_manager.FLAG_FILE, "a") as f:
            f.write("2")
        # initializeaza jucatorul 2
        player_two = Player("O", MessageQueue(file_manager.KEY2, IPC_CREAT), MessageQueue(file_manager.KEY1, IPC_CREAT),
                            2, file_manager)
        # seteaza numele jucatorului 2
        player_two.set_name()
        # porneste jocul pentru jucatorul 2
        player_two.play_game()
    else:
        # afiseaza mesaj daca sunt deja doua instante
        print("Deja sunt doua instante active!")