import pygame
import sys
from pygame.locals import *
 
# Pygame inicializācija
pygame.init()
 
# Loga izmēri
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
 
# Krāsas
WHITE = (255, 255, 255)
BLACK = (40, 44, 52)  # Darker black for better contrast
GREEN = (46, 204, 113)  # Flat UI green
RED = (231, 76, 60)    # Flat UI red
BLUE = (52, 152, 219)  # Flat UI blue
GRAY = (189, 195, 199) # Flat UI gray
LIGHT_BLUE = (133, 193, 233)
BACKGROUND_COLOR = (236, 240, 241)  # Light gray background
BUTTON_COLOR = (52, 152, 219)       # Flat blue for buttons
BUTTON_HOVER_COLOR = (41, 128, 185)  # Darker blue for hover
 
# Fonts - Using custom fonts for a modern look
try:
    REGULAR_FONT = pygame.font.Font("assets/Roboto-Regular.ttf", 36)
    TITLE_FONT = pygame.font.Font("assets/Roboto-Bold.ttf", 48)
except:
    REGULAR_FONT = pygame.font.Font(None, 36)
    TITLE_FONT = pygame.font.Font(None, 48)
 
# Loga izveide
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("MaxLiga Game")
 
# Pogu izmēri un pozīcijas
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_GAP = 20
 
# Pievienojam globālos mainīgos spēles sākumā, pēc krāsu definīcijām
COMPUTER_MOVE_DELAY = 2000  # 2 sekundes milisekundēs
computer_move_start_time = 0
computer_thinking = False
 
# Spēles stāvokļa klase
class Game:
    def __init__(self, start_number, first_player):
        self.current_number = start_number
        self.total_points = 0
        self.bank = 0
        self.game_over = False
        self.winner = None
        self.first_player = first_player  # Saglabājam, kurš bija pirmais spēlētājs
        self.player1_turn = (first_player == "Cilvēks")  # True - cilvēks, False - dators
 
    def make_move(self, multiplier):
        if self.game_over:
            return
 
        self.current_number *= multiplier
       
        if self.current_number % 10 == 0 or self.current_number % 10 == 5:
            self.bank += 1
        else:
            if self.current_number % 2 == 0:
                self.total_points += 1
            else:
                self.total_points -= 1
 
        # Pārbauda vai spēle beigusies
        if self.current_number >= 3000:
            self.game_over = True
            self.finalize_game()
       
        # Maina gājiena kārtu
        self.player1_turn = not self.player1_turn
 
    def finalize_game(self):
        if self.total_points % 2 == 0:
            self.total_points -= self.bank
        else:
            self.total_points += self.bank
 
                # Noteikts uzvarētāju, pamatojoties uz punktu paritāti un pirmo spēlētāju
        if self.total_points % 2 == 0:
            self.winner = self.first_player  # Uzvar pirmais spēlētājs
        else:
            # Uzvar otrais spēlētājs (pretējs pirmajam)
            self.winner = "Dators" if self.first_player == "Cilvēks" else "Cilvēks"
 
    def copy(self):
        """Izveido spēles stāvokļa kopiju"""
        new_game = Game(self.current_number, self.first_player)
        new_game.total_points = self.total_points
        new_game.bank = self.bank
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.player1_turn = self.player1_turn
        return new_game
 
# Heiristiskā novērtējuma funkcija
def heuristic(game_state):
    N = game_state.current_number
    S = game_state.total_points
    P = game_state.bank
 
    if game_state.game_over:
       
        if ((S % 2 == 0 and game_state.first_player == "Dators") or
            (S % 2 != 0 and game_state.first_player == "Cilvēks")):
            return 1000  
        else:
            return -1000  
   
    progress = min(N / 3000, 1.0)
    progress_score = progress * 20.0
   
    bank_score = (P + 1) ** 0.6
   
    flexibility = 0
    for multiplier in [3, 4, 5]:
        next_num = N * multiplier
        if next_num % 2 == 0:
            flexibility += 1
        if next_num % 5 == 0:
            flexibility += 1
   
    danger_zone = max(0, (N - 2000) / 1000)
    danger_score = -10 * danger_zone
   
    win_next_move = 0
    for multiplier in [3, 4, 5]:
        next_num = N * multiplier
        if next_num >= 3000:
           
            temp_points = S
            if next_num % 2 == 0:
                temp_points += 1
            else:
                temp_points -= 1
           
            if next_num % 10 == 0 or next_num % 10 == 5:
                temp_points += 1 if temp_points % 2 != 0 else -1
           
            if ((temp_points % 2 == 0 and game_state.first_player == "Dators") or
                (temp_points % 2 != 0 and game_state.first_player == "Cilvēks")):
                win_next_move += 50  
   
    total_score = (progress_score +
                 bank_score +
                 flexibility +
                 danger_score +
                 win_next_move)
   
    return total_score
 
# Minimaksa algoritms
def minimax(game_state, depth, maximizing_player):
    if depth == 0 or game_state.game_over:
        return heuristic(game_state)
 
    if maximizing_player:
        max_eval = -float('inf')
        for multiplier in [3, 4, 5]:
            new_state = game_state.copy()
            new_state.make_move(multiplier)
            eval = minimax(new_state, depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for multiplier in [3, 4, 5]:
            new_state = game_state.copy()
            new_state.make_move(multiplier)
            eval = minimax(new_state, depth - 1, True)
            min_eval = min(min_eval, eval)
        return min_eval
 
# Alpha-Beta algoritms
def alphabeta(game_state, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_state.game_over:
        return heuristic(game_state)
 
    if maximizing_player:
        max_eval = -float('inf')
        for multiplier in [3, 4, 5]:
            new_state = game_state.copy()
            new_state.make_move(multiplier)
            eval = alphabeta(new_state, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for multiplier in [3, 4, 5]:
            new_state = game_state.copy()
            new_state.make_move(multiplier)
            eval = alphabeta(new_state, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval
 
# Datora gājiens
def computer_move(game_state, algorithm):
   
    for multiplier in [3, 4, 5]:
        new_state = game_state.copy()
        new_state.make_move(multiplier)
        if new_state.game_over:
           
            if ((new_state.total_points % 2 == 0 and game_state.first_player == "Dators") or
                (new_state.total_points % 2 != 0 and game_state.first_player == "Cilvēks")):
                return multiplier  
 
   
    best_score = -float('inf')
    best_multiplier = 3  
   
    for multiplier in [3, 4, 5]:
        new_state = game_state.copy()
        new_state.make_move(multiplier)
       
        if algorithm == "minimax":
            score = minimax(new_state, depth=3, maximizing_player=False)
        elif algorithm == "alphabeta":
            score = alphabeta(new_state, depth=3, alpha=-float('inf'), beta=float('inf'), maximizing_player=False)
       
        if score > best_score:
            best_score = score
            best_multiplier = multiplier
   
    return best_multiplier
 
# Funkcija, lai zīmētu pogas
def draw_button(text, x, y, width, height, color, hover_color=None):
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)
   
    # Add shadow effect
    shadow_rect = pygame.Rect(x + 2, y + 2, width, height)
    pygame.draw.rect(window, (0, 0, 0, 30), shadow_rect, border_radius=10)
   
    if hover_color and button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(window, hover_color, button_rect, border_radius=10)
    else:
        pygame.draw.rect(window, color, button_rect, border_radius=10)
   
    text_surface = REGULAR_FONT.render(text, True, WHITE)  # White text on buttons
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)
    return button_rect
 
# Funkcija teksta zīmēšanai
def draw_text(text, x, y, color=BLACK, centerx=False, font=None, size=36):
    if font is None:
        font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if centerx:
        text_rect.centerx = x
        text_rect.y = y
    else:
        text_rect.topleft = (x, y)
    window.blit(text_surface, text_rect)
 
# Galvenā funkcija
def main():
    clock = pygame.time.Clock()
    game = None
    start_number = 0
    input_text = ""
    algorithm = None
    first_player = None
    game_state = "INPUT_NUMBER"  # INPUT_NUMBER → CHOOSE_FIRST → CHOOSE_ALGORITHM → PLAYING
    error_message = ""
    # Pievienojam globālos mainīgos
    global computer_move_start_time
    global computer_thinking
 
    while True:
        current_time = pygame.time.get_ticks()
        window.fill(BACKGROUND_COLOR)  # Use the new background color
       
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
 
            if game_state == "INPUT_NUMBER":
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        if input_text.strip():
                            try:
                                start_number = int(input_text)
                                if 20 <= start_number <= 30:
                                    game_state = "CHOOSE_FIRST"
                                    error_message = ""
                                else:
                                    error_message = "Skaitlim jābūt no 20 līdz 30! Mēģiniet vēlreiz!"
                                    input_text = ""
                            except ValueError:
                                error_message = "Ievadiet derīgu skaitli! Mēģiniet vēlreiz!"
                                input_text = ""
                        else:
                            error_message = "Ievadiet skaitli! Mēģiniet vēlreiz!"
                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                        error_message = ""  
                    else:
                        if event.unicode.isdigit():
                            input_text += event.unicode
                            error_message = ""
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if 300 <= mouse_pos[0] <= 500 and 270 <= mouse_pos[1] <= 320:
                        if input_text.strip():
                            try:
                                start_number = int(input_text)
                                if 20 <= start_number <= 30:
                                    game_state = "CHOOSE_FIRST"
                                    error_message = ""
                                else:
                                    error_message = "Skaitlim jābūt no 20 līdz 30! Mēģiniet vēlreiz!"
                                    input_text = ""
                            except ValueError:
                                error_message = "Ievadiet derīgu skaitli! Mēģiniet vēlreiz!"
                                input_text = ""
                        else:
                            error_message = "Ievadiet skaitli! Mēģiniet vēlreiz!"
       
            elif game_state == "CHOOSE_FIRST":
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if 200 <= mouse_pos[0] <= 350 and 250 <= mouse_pos[1] <= 300:
                        first_player = "Cilvēks"
                        game_state = "CHOOSE_ALGORITHM"
                    elif 450 <= mouse_pos[0] <= 600 and 250 <= mouse_pos[1] <= 300:
                        first_player = "Dators"
                        game_state = "CHOOSE_ALGORITHM"
           
            elif game_state == "CHOOSE_ALGORITHM":
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if 200 <= mouse_pos[0] <= 350 and 250 <= mouse_pos[1] <= 300:
                        algorithm = "minimax"
                        game = Game(start_number, first_player)
                        game_state = "PLAYING"
                        # Initialize computer's first move if computer starts
                        if first_player == "Dators":
                            computer_thinking = True
                            computer_move_start_time = current_time
                    elif 450 <= mouse_pos[0] <= 600 and 250 <= mouse_pos[1] <= 300:
                        algorithm = "alphabeta"
                        game = Game(start_number, first_player)
                        game_state = "PLAYING"
                        # Initialize computer's first move if computer starts
                        if first_player == "Dators":
                            computer_thinking = True
                            computer_move_start_time = current_time
           
            elif game_state == "PLAYING":
                if event.type == MOUSEBUTTONDOWN and game and not game.game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    if game.player1_turn:  # Cilvēka gājiens
                        if 200 <= mouse_pos[0] <= 300 and 400 <= mouse_pos[1] <= 450:
                            game.make_move(3)
                            if not game.game_over:
                                computer_thinking = True
                                computer_move_start_time = current_time
                        elif 350 <= mouse_pos[0] <= 450 and 400 <= mouse_pos[1] <= 450:
                            game.make_move(4)
                            if not game.game_over:
                                computer_thinking = True
                                computer_move_start_time = current_time
                        elif 500 <= mouse_pos[0] <= 600 and 400 <= mouse_pos[1] <= 450:
                            game.make_move(5)
                            if not game.game_over:
                                computer_thinking = True
                                computer_move_start_time = current_time
                elif event.type == MOUSEBUTTONDOWN and game.game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    if 300 <= mouse_pos[0] <= 500 and 450 <= mouse_pos[1] <= 500:
                        game = None
                        game_state = "INPUT_NUMBER"
                        input_text = ""
 
        # Pārvietojam datora gājiena loģiku ārpus notikumu apstrādes
        if game_state == "PLAYING" and game and not game.game_over:
            if not game.player1_turn and computer_thinking:
                if current_time - computer_move_start_time >= COMPUTER_MOVE_DELAY:
                    multiplier = computer_move(game, algorithm)
                    game.make_move(multiplier)
                    computer_thinking = False
 
        # Zīmēšanas daļa
        if game_state == "INPUT_NUMBER":
            draw_text("MaxLiga Game", WINDOW_WIDTH // 2, 50, BLACK, True, TITLE_FONT)
            draw_text("Ievadiet sākuma skaitli (20-30):", WINDOW_WIDTH // 2, 145, BLACK, True)
           
            # Modern input box
            input_rect = pygame.Rect(100, 150, 280, 50)
            input_rect.center = (WINDOW_WIDTH // 2, 200)
            pygame.draw.rect(window, WHITE, input_rect, border_radius=8)
            pygame.draw.rect(window, BLUE, input_rect, 2, border_radius=8)
            draw_text(input_text, (WINDOW_WIDTH // 2), 190, BLACK, True)
           
            draw_button("Enter", 300, 270, 200, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
           
            if error_message:
                draw_text(error_message, (WINDOW_WIDTH // 2), 230, RED, True)
       
        elif game_state == "CHOOSE_FIRST":
            draw_text("MaxLiga Game", WINDOW_WIDTH // 2, 50, BLACK, True, TITLE_FONT)
            draw_text("Izvēlieties, kurš sāks spēli:", WINDOW_WIDTH // 2, 150, BLACK, True)
            draw_button("Cilvēks", 200, 250, 150, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
            draw_button("Dators", 450, 250, 150, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
       
        elif game_state == "CHOOSE_ALGORITHM":
            draw_text("MaxLiga Game", WINDOW_WIDTH // 2, 50, BLACK, True, TITLE_FONT)
            draw_text("Izvēlieties algoritmu:", WINDOW_WIDTH // 2, 150, BLACK, True)
            draw_button("Minimaks", 200, 250, 150, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
            draw_button("Alfa-beta", 450, 250, 150, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
       
        elif game_state == "PLAYING":
            # Game info panel
            info_panel = pygame.Rect(50, 50, WINDOW_WIDTH - 100, 150)
            pygame.draw.rect(window, WHITE, info_panel, border_radius=15)
            pygame.draw.rect(window, GRAY, info_panel, 2, border_radius=15)
           
            draw_text(f"Pašreizējais skaitlis: {game.current_number}", 100, 70, BLACK, size=30)
            draw_text(f"Kopējie punkti: {game.total_points}", 100, 110, BLACK, size=30)
            draw_text(f"Banka: {game.bank}", 400, 110, BLACK, size=30)
            draw_text(f"Pirmais spēlētājs: {first_player}", 400, 70, BLACK, size=30)
           
            if not game.game_over:
                if game.player1_turn:
                    draw_text("Cilvēka gājiens:", 100, 300, BLUE)
                    draw_button("3", 200, 400, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
                    draw_button("4", 350, 400, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
                    draw_button("5", 500, 400, 100, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
                else:
                    draw_text("Dators veic gājienu...", 100, 300, RED)
            else:
                draw_text(f"Spēle beigusies! Uzvarētājs: {game.winner}", WINDOW_WIDTH // 2, 400, GREEN, True)
                draw_button("Spēlēt vēlreiz", 300, 450, 200, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR)
 
        pygame.display.update()
        clock.tick(30)
 
if __name__ == "__main__":
    main()