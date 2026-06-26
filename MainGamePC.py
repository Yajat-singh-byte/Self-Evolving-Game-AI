import pygame as pyg
import math
import numpy as np
import pickle
import random
import time
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pyg.init()
loading = pyg.image.load(resource_path('loading.png'))
DW, DH = 1280, 720
screen = pyg.display.set_mode((DW, DH)) 
pyg.display.set_caption("Make Me SMARTER!")
icon = pyg.image.load(resource_path('icon.png'))
pyg.display.set_icon(icon)
bg_img_raw = pyg.image.load(resource_path('background.png'))
bg_img = pyg.transform.scale(bg_img_raw, (DW, DH))
pyg.mixer.init()
shoot_sound = pyg.mixer.Sound(resource_path('shoot.ogg'))
shoot_sound.set_volume(0.3)

playerimg = pyg.image.load(resource_path('player.png'))
xplay = DW / 2 - 32
yplay = DH / 2 - 32
yplayChange = 0
xplayChange = 0
def player(x, y):
    screen.blit(playerimg, (x, y))

class Player:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.xchange = 0
        self.ychange = 0
        self.health = 100
        self.maxhealth = 100
        self.AP = 10
        self.basehealingpot = 10
    def rotate_and_draw(self):
        mx, my = pyg.mouse.get_pos()
        rangle = math.atan2(my - self.y - 16, mx - self.x - 16)
        RTDangle = -math.degrees(rangle)
        playroter = pyg.transform.rotate(self.img, RTDangle)
        new_rect = playroter.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        screen.blit(playroter, new_rect.topleft)
        pyg.draw.line(screen, (255, 0, 0), (self.x + 16, self.y + 16), (mx, my), 2)

bulletImg = pyg.image.load(resource_path('bullet.png'))

delta = 0
speed = 300
clock = pyg.time.Clock()
font = pyg.font.SysFont(None, 24)
menu_font = pyg.font.SysFont(None, 40)
title_font = pyg.font.SysFont(None, 64)

round_duration = 30.0
round_start_time = time.time()
round_number = 1
best_score_ever = 0
score = 0
first_round = True
is_paused = False

game_state = "MAIN_MENU" 

def show_loading_screen(duration_ms=800):
    screen.fill((0, 0, 0))
    if loading:
        loading_scaled = pyg.transform.scale(loading, (DW, DH))
        screen.blit(loading_scaled, (0, 0))
    loading_text = font.render("Loading brain...", True, (255, 255, 255))
    screen.blit(loading_text, (DW // 2 - loading_text.get_width() // 2, DH - 80))
    pyg.display.update()
    pyg.time.delay(duration_ms)

def playerstats():
    global player_health, playerMaxhealth, playerAP, basehealingpot
    player_health = 100
    playerMaxhealth = 100
    playerAP = 10
    basehealingpot = 10

class Enemy:
    def __init__(self, DW, DH):
        self.orig_img = pyg.image.load(resource_path('enemy.png')).convert_alpha()
        self.eimg = self.orig_img
        self.ex = DW / 3
        self.ey = DH / 3
        self.angle = 0 
        self.rect = self.eimg.get_rect(center=(self.ex, self.ey))
        self.ehealth = 100
        self.emh = 100
        self.edmg = 10
        self.last_shot_time = 0.0
        self.shot_interval = 0.2
    def rotate_and_draw(self, screen, targetx, targety, delta):
        ecx, ecy = self.rect.center
        desired = math.atan2(targety - ecy, targetx - ecx)
        rot_speed_rad = math.radians(180)
        max_change = rot_speed_rad * delta
        diff = (desired - self.angle + math.pi) % (2 * math.pi) - math.pi
        if diff > max_change:
            diff = max_change
        elif diff < -max_change:
            diff = -max_change
        self.angle += diff
        RTDangle = -math.degrees(self.angle)
        self.eimg = pyg.transform.rotate(self.orig_img, RTDangle)
        self.rect = self.eimg.get_rect(center=(self.ex, self.ey))
        screen.blit(self.eimg, self.rect.topleft)
        length = 500
        endx = ecx + math.cos(self.angle) * length
        endy = ecy + math.sin(self.angle) * length
        pyg.draw.line(screen, (255, 0, 0), (ecx, ecy), (endx, endy), 2)

class Bullet:
    def __init__(self, bx, by, mousex, mousey):
        self.x = float(bx)
        self.y = float(by)
        self.speed = 800
        self.angle = math.atan2(mousey - by, mousex - bx)
        self.xvel = math.cos(self.angle) * self.speed
        self.yvel = math.sin(self.angle) * self.speed
    def main(self, display, delta):
        self.x += self.xvel * delta
        self.y += self.yvel * delta
    def draw(self, display):
        screen.blit(bulletImg, (self.x, self.y))

def rotateplayer(rplax, rplayY):
    mx, my = pyg.mouse.get_pos()
    rangle = math.atan2(my - rplayY - 16, mx - rplax - 16)
    RTDangle = -math.degrees(rangle) 
    playroter = pyg.transform.rotate(playerimg, RTDangle)
    new_rect = playroter.get_rect(center=playerimg.get_rect(topleft=(rplax, rplayY)).center)
    screen.blit(playroter, new_rect.topleft)
    pyg.draw.line(screen, (255, 0, 0), (rplax + 16, rplayY + 16), (mx, my), 2)

def rotateenemy(ex, ey, targetx, targety, delta):
    global enemy_angle
    ecx, ecy = ex + 16, ey + 16
    desired = math.atan2(targety - ecy, targetx - ecx)
    rot_speed_rad = math.radians(360)
    max_change = rot_speed_rad * delta
    diff = (desired - enemy_angle + math.pi) % (2 * math.pi) - math.pi
    if diff > max_change:
        diff = max_change
    elif diff < -max_change:
        diff = -max_change
    enemy_angle += diff
    length = 500
    endx = ecx + math.cos(enemy_angle) * length
    endy = ecy + math.sin(enemy_angle) * length
    pyg.draw.line(screen, (255, 0, 0), (ecx, ecy), (endx, endy), 2)

playerstats()
enemy_obj = Enemy(DW, DH)
spawnerA = (50, 50)
spawnerB = (DW - 100, DH - 100)
player = Player(xplay, yplay, playerimg)
bulletC = []
bullet_shot_timestamps = []
running = True
enemyBulletC = []

class RecurrentNeuralNetwork:
    def __init__(self):
        self.input_size = 16
        self.hidden_size = 32
        self.output_size = 2
        self.w_ih = np.random.normal(0, np.sqrt(2.0 / self.input_size), (self.input_size, self.hidden_size))
        self.w_hh = np.random.normal(0, np.sqrt(2.0 / self.hidden_size), (self.hidden_size, self.hidden_size))
        self.b_h = np.zeros((1, self.hidden_size))
        self.w_ho = np.random.normal(0, np.sqrt(2.0 / self.hidden_size), (self.hidden_size, self.output_size))
        self.b_o = np.zeros((1, self.output_size))
        self.h_state = np.zeros((1, self.hidden_size))
        self.last_output = np.zeros(self.output_size)
    
    def reset_memory(self):
        self.h_state = np.zeros((1, self.hidden_size))
        self.last_output = np.zeros(self.output_size)

    def forward(self, inputs):
        inputs = inputs.reshape(1, -1)
        hidden_net = np.dot(inputs, self.w_ih) + np.dot(self.h_state, self.w_hh) + self.b_h
        self.h_state = np.tanh(hidden_net)
        output_raw = np.dot(self.h_state, self.w_ho) + self.b_o
        self.last_output = np.clip(np.tanh(output_raw), -1.0, 1.0)[0]
        return self.last_output

    def check(self, enemy_x, enemy_y, enemy_health, player_x, player_y, player_health, bullets, enemy_bullets):
        state = extract_advanced_state(enemy_x, enemy_y, enemy_health, player_x, player_y, player_health, bullets, enemy_bullets, self.last_output)
        return self.forward(state)

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump({
                "w_ih": self.w_ih, "w_hh": self.w_hh, "b_h": self.b_h,
                "w_ho": self.w_ho, "b_o": self.b_o
            }, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        net = RecurrentNeuralNetwork()
        net.w_ih = data.get("w_ih", net.w_ih)
        net.w_hh = data.get("w_hh", net.w_hh)
        net.b_h = data.get("b_h", net.b_h)
        net.w_ho = data.get("w_ho", net.w_ho)
        net.b_o = data.get("b_o", net.b_o)
        return net

    def mutate(self, rate=0.15):
        for weight in [self.w_ih, self.w_hh, self.w_ho]:
            mask = np.random.rand(*weight.shape) < rate
            weight += mask * np.random.normal(0, 0.12, weight.shape)
        for bias in [self.b_h, self.b_o]:
            mask = np.random.rand(*bias.shape) < rate
            bias += mask * np.random.normal(0, 0.05, bias.shape)

def extract_advanced_state(ex, ey, eh, px, py, ph, player_bullets, enemy_bullets, last_actions):
    dx = (px - ex) / DW
    dy = (py - ey) / DH
    dist = math.sqrt(dx**2 + dy**2)
    eh_pct = eh / 100.0
    ph_pct = ph / 100.0
    wall_l = ex / DW
    wall_r = (DW - ex) / DW
    wall_t = ey / DH
    wall_b = (DH - ey) / DH
    danger_bx, danger_by = 0.0, 0.0
    if player_bullets:
        closest_b = min(player_bullets, key=lambda b: math.sqrt((b.x - ex)**2 + (b.y - ey)**2))
        danger_bx = (closest_b.x - ex) / DW
        danger_by = (closest_b.y - ey) / DH
    return np.array([
        dx, dy, dist, eh_pct, ph_pct,
        wall_l, wall_r, wall_t, wall_b,
        danger_bx, danger_by,
        last_actions[0], last_actions[1],
        math.sin(time.time()), math.cos(time.time()),
        1.0 if dist < 0.25 else -1.0
    ], dtype=np.float32)

def calculate_dynamic_fitness(round_score, ex, ey, px, py, eh_end, ph_end, time_survived):
    fitness = round_score * 1.5
    final_dist = math.sqrt((px - ex)**2 + (py - ey)**2)
    if final_dist < 250:
        fitness += 40
    elif final_dist > 700:
        fitness -= 50
    fitness += (time_survived / round_duration) * 25
    return fitness

def load_brain_file(path, mutate=False, mutate_rate=0.15):
    if os.path.exists(path):
        try:
            brain = RecurrentNeuralNetwork.load(path)
        except Exception:
            brain = RecurrentNeuralNetwork()
    else:
        brain = RecurrentNeuralNetwork()
    if mutate:
        brain.mutate(rate=mutate_rate)
    brain.reset_memory()
    return brain

def reset_round():
    global xplay, yplay, enemy_obj, bulletC, enemyBulletC
    xplay = DW / 2 - 32
    yplay = DH / 2 - 32
    enemy_obj.ehealth = 100
    enemy_obj.ex = random.randint(100, DW - 100)
    enemy_obj.ey = random.randint(100, DH - 100)
    bulletC.clear()
    enemyBulletC.clear()
    player_low_health_shake_done = False
    enemy_low_health_shake_done = False


def draw_button(text, font, color, hover_color, center_pos):
    mx, my = pyg.mouse.get_pos()
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    
    if text_rect.collidepoint(mx, my):
        text_surface = font.render(text, True, hover_color)
    
    screen.blit(text_surface, text_rect)
    return text_rect

brain = load_brain_file("best_brain.pkl", mutate=True)
current_time = time.time()
round_start_time = current_time
round_health_tracker = {"player_start": player_health, "enemy_start": enemy_obj.ehealth}
shake_intensity = 0
shake_decay = 0.8
shake_x, shake_y = 0, 0
player_low_health_shake_done = False
enemy_low_health_shake_done = False

while running:
    current_time = time.time()
    

    if game_state == "MAIN_MENU":
        screen.blit(bg_img, (0, 0))
        

        title_text = title_font.render("MAKE ME SMARTER!", True, (255, 255, 255))
        screen.blit(title_text, (DW // 2 - title_text.get_width() // 2, DH // 4))
        

        start_btn = draw_button("START GAME", menu_font, (200, 200, 200), (255, 255, 255), (DW // 2, DH // 2 - 20))
        reset_btn = draw_button("RESET WEIGHTS", menu_font, (200, 100, 100), (255, 50, 50), (DW // 2, DH // 2 + 50))
        
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(event.pos):
                    show_loading_screen()
                    round_start_time = time.time() # Keeps tracking time clean when moving to gameplay
                    game_state = "GAME"
                elif reset_btn.collidepoint(event.pos):
                    game_state = "CONFIRM_RESET"


    elif game_state == "CONFIRM_RESET":
        screen.blit(bg_img, (0, 0))
        
        warn_text = menu_font.render("Are you sure you want to completely erase the brain network?", True, (255, 50, 50))
        screen.blit(warn_text, (DW // 2 - warn_text.get_width() // 2, DH // 3))
        
        yes_btn = draw_button("YES, ERASE PROGRESS", menu_font, (200, 50, 50), (255, 0, 0), (DW // 2 - 150, DH // 2))
        no_btn = draw_button("NO, GO BACK", menu_font, (200, 200, 200), (255, 255, 255), (DW // 2 + 150, DH // 2))
        
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                running = False
            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
                if yes_btn.collidepoint(event.pos):
                    if os.path.exists("best_brain.pkl"):
                        os.remove("best_brain.pkl")
                    brain = RecurrentNeuralNetwork() # Generates entirely fresh weights
                    best_score_ever = 0
                    game_state = "MAIN_MENU"
                elif no_btn.collidepoint(event.pos):
                    game_state = "MAIN_MENU"


    elif game_state == "GAME":
        screen.blit(bg_img, (0, 0))

        pause_button_rect = pyg.Rect(DW // 2 - 90, DH - 35, 80, 25)
        menu_button_rect = pyg.Rect(DW // 2 + 10, DH - 35, 80, 25)
        
        for event in pyg.event.get():
            if event.type == pyg.QUIT: 
                running = False
            if event.type == pyg.KEYDOWN:
                if event.key == pyg.K_w: yplayChange = -1
                if event.key == pyg.K_s: yplayChange += 1
                if event.key == pyg.K_a: xplayChange = -1
                if event.key == pyg.K_d: xplayChange += 1
                if event.key == pyg.K_p:
                    is_paused = not is_paused
                if event.key == pyg.K_r:
                    brain.save("best_brain.pkl")
                if event.key == pyg.K_t:
                    with open ("log.pkl", "wb") as f:
                        pickle.dump({"player_x_location": xplay,
                                     "player_y_location": yplay,
                                     "enemy_x" : enemy_obj.ex,
                                     "enemy_y": enemy_obj.ey,
                                     "output": brain.last_output,
                                     "score": score})
            if event.type == pyg.KEYUP:
                if event.key == pyg.K_w and yplayChange == -1: yplayChange = 0
                if event.key == pyg.K_s and yplayChange == 1: yplayChange = 0
                if event.key == pyg.K_a and xplayChange == -1: xplayChange = 0
                if event.key == pyg.K_d and xplayChange == 1: xplayChange = 0
            if event.type == pyg.MOUSEBUTTONDOWN and event.button == 1:
                mousex, mousey = pyg.mouse.get_pos()
                shoot_sound.play()
                
                if pause_button_rect.collidepoint(mousex, mousey):
                    is_paused = not is_paused
                elif is_paused and menu_button_rect.collidepoint(mousex, mousey):
                    brain.save("best_brain.pkl")
                    is_paused = False
                    reset_round()
                    game_state = "MAIN_MENU"
                elif not is_paused:
                    bullet_shot_timestamps = [t for t in bullet_shot_timestamps if current_time - t < 1.0]
                    if len(bullet_shot_timestamps) < 5:
                        bulletC.append(Bullet(xplay, yplay, mousex, mousey))
                        bullet_shot_timestamps.append(current_time)

        if not is_paused:
            action = brain.check(enemy_obj.ex, enemy_obj.ey, enemy_obj.ehealth, xplay, yplay, player_health, bulletC, enemyBulletC)
            enemy_obj.ex += action[0] * speed * delta
            enemy_obj.ey += action[1] * speed * delta
            
            if current_time - enemy_obj.last_shot_time >= enemy_obj.shot_interval:
                enemyBulletC.append(Bullet(enemy_obj.ex, enemy_obj.ey, xplay, yplay))
                enemy_obj.last_shot_time = current_time
            
            yplay += yplayChange * speed * delta
            xplay += xplayChange * speed * delta
            if xplay >= DW - 32: xplay = DW - 32
            if xplay <= 0: xplay = 0
            if yplay >= DH - 32: yplay = DH - 32
            if yplay <= 0: yplay = 0
            player.x = xplay
            player.y = yplay
            
            if enemy_obj.ex >= DW - 32: enemy_obj.ex = DW - 32
            if enemy_obj.ex <= 0: enemy_obj.ex = 0
            if enemy_obj.ey >= DH - 32: enemy_obj.ey = DH - 32
            if enemy_obj.ey <= 0: enemy_obj.ey = 0

            pcx, pcy = xplay + 16, yplay + 16

            for b in bulletC[:]:
                b.main(screen, delta)
                b.draw(screen)
                dist = math.sqrt((enemy_obj.ex + 16 - b.x) ** 2 + (enemy_obj.ey + 16 - b.y) ** 2)
                if dist < 32:
                    enemy_obj.ehealth -= 5
                    bulletC.remove(b)
                    score -= 10
                    continue
                if b.x < 0 or b.x > DW or b.y < 0 or b.y > DH:
                    bulletC.remove(b)

            for b in enemyBulletC[:]:
                b.main(screen, delta)
                b.draw(screen)
                dist = math.sqrt((xplay + 16 - b.x) ** 2 + (yplay + 16 - b.y) ** 2)
                if dist < 32:
                    player_health -= 5
                    enemyBulletC.remove(b)
                    score += 5
                    continue
                if b.x < 0 or b.x > DW or b.y < 0 or b.y > DH:
                    enemyBulletC.remove(b)

            if enemy_obj.ehealth < 50 and not enemy_low_health_shake_done:
                shake_intensity = 45          
                enemy_low_health_shake_done = True
            
            if player_health < 50 and not player_low_health_shake_done:
                shake_intensity = 55           
                player_low_health_shake_done = True

            if enemy_obj.ehealth <= 0:
                score -= 100
                round_start_time = current_time - round_duration
            if player_health <= 0:
                score += 200
                round_start_time = current_time - round_duration
                player_health = 100
                xplay = DW / 2
                yplay = DH / 2
            
            if current_time - round_start_time >= round_duration:
                time_survived = min(current_time - round_start_time, round_duration)
                
                fitness_score = calculate_dynamic_fitness(
                    score, 
                    enemy_obj.ex, enemy_obj.ey,
                    xplay, yplay,
                    enemy_obj.ehealth, player_health,
                    time_survived
                )
                
                current_score = fitness_score
                
                if current_score > best_score_ever:
                    brain.save("best_brain.pkl")
                    best_score_ever = current_score
                
                score = 0
                round_start_time = current_time
                round_number += 1
                show_loading_screen()
                reset_round()
                
                round_health_tracker = {"player_start": player_health, "enemy_start": enemy_obj.ehealth}
                brain = load_brain_file("best_brain.pkl", mutate=True)


        player.rotate_and_draw()
        enemy_obj.rotate_and_draw(screen, xplay + 16, yplay + 16, delta)

  
        bar_width = 260
        bar_height = 22
        player_bar_x = 10
        enemy_bar_x = player_bar_x + bar_width + 20
        bar_y = 10
        player.health = player_health
        player_fill = int(max(0, min(player.health / player.maxhealth, 1.0)) * bar_width)
        pyg.draw.rect(screen, (80, 80, 80), (player_bar_x, bar_y, bar_width, bar_height))
        pyg.draw.rect(screen, (0, 200, 0), (player_bar_x, bar_y, player_fill, bar_height))
        pyg.draw.rect(screen, (80, 80, 80), (enemy_bar_x, bar_y, bar_width, bar_height))
        enemy_fill = int(max(0, min(enemy_obj.ehealth / enemy_obj.emh, 1.0)) * bar_width)
        pyg.draw.rect(screen, (200, 0, 0), (enemy_bar_x, bar_y, enemy_fill, bar_height))
        player_label = font.render("PLAYER", True, (255, 255, 255))
        enemy_label = font.render("ENEMY", True, (255, 255, 255))
        screen.blit(player_label, (player_bar_x, bar_y - 22))
        screen.blit(enemy_label, (enemy_bar_x, bar_y - 22))
        
        elapsed_time = current_time - round_start_time
        timer_text = font.render(f"Time: {int(elapsed_time)}s / {int(round_duration)}s", True, (255, 255, 255))
        score_text = font.render(f"Score: {int(score)}", True, (255, 255, 255))
        screen.blit(timer_text, (10, DH - 30))
        screen.blit(score_text, (DW - 150, DH - 30))
        

        pause_text = font.render("RESUME" if is_paused else "PAUSE", True, (255, 255, 255))
        pyg.draw.rect(screen, (100, 100, 100), pause_button_rect)
        screen.blit(pause_text, (pause_button_rect.centerx - pause_text.get_width() // 2, pause_button_rect.centery - pause_text.get_height() // 2))

        if is_paused:
            pyg.draw.rect(screen, (120, 40, 40), menu_button_rect)
            menu_text = font.render("MENU", True, (255, 255, 255))
            screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width() // 2, menu_button_rect.centery - menu_text.get_height() // 2))

    pyg.display.update()
    delta = clock.tick(60) / 1000

pyg.quit()
