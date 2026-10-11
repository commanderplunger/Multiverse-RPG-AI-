import json
import math
import os
import random
import shutil
import sys
import pygame

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen Dimensions & Resizable Window Mode
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Multiverse RPG: Quantum Rift")
clock = pygame.time.Clock()

# Fonts
FONT_SM = pygame.font.SysFont("Arial", 16)
FONT_MD = pygame.font.SysFont("Arial", 20, bold=True)
FONT_LG = pygame.font.SysFont("Arial", 36, bold=True)
FONT_XL = pygame.font.SysFont("Arial", 48, bold=True)

# Colors
BG_COLOR = (15, 15, 25)
WHITE = (255, 255, 255)
GRAY = (100, 100, 120)
RED = (230, 50, 50)
GREEN = (50, 220, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 215, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)
ORANGE = (255, 140, 0)
DARK_GRAY = (40, 40, 55)

# Game States
STATE_MENU = 1
STATE_LOGIN = 2
STATE_PLAYING = 3
STATE_BOSS = 4
STATE_GAMEOVER = 5
STATE_VICTORY = 6
STATE_PAUSE = 7

# Specific Save Directory
SAVE_DIR = r"D:\GAME\Accounts"


def ensure_save_directory():
  try:
    os.makedirs(SAVE_DIR, exist_ok=True)
  except Exception:
    pass


def create_credits_file():
  """Creates the credits.txt file if it doesn't already exist. If it exists, does nothing."""
  try:
    game_dir = os.path.dirname(SAVE_DIR)
    os.makedirs(game_dir, exist_ok=True)
    credits_path = os.path.join(game_dir, "credits.txt")

    if os.path.exists(credits_path):
      return

    with open(credits_path, "w", encoding="utf-8") as f:
      f.write(
          "oh! you found the secret file! just here to say that this game's"
          " creation idea was by chatgpt and gemini! and the fixes, update,"
          " update ideas are all by me, Commander Plungerman, i dont want to"
          " reveal my name, this game was originally made in HTML chatgpt"
          " thinks it's too boring, and gemini made it as a PYTHON file."
          " End of file -Commander Plunger"
      )
  except Exception as e:
    print(f"Credits file creation error: {e}")


def ensure_default_admin():
  ensure_save_directory()
  create_credits_file()
  admin_path = os.path.join(SAVE_DIR, "account_cmdadmin.json")
  if not os.path.exists(admin_path):
    default_data = {
        "password": "090603180503",
        "universe_id": 1,
        "sub_level": 1,
        "level": 1,
        "xp": 0,
        "max_hp": 100,
        "hp": 100,
    }
    try:
      with open(admin_path, "w") as f:
        json.dump(default_data, f, indent=4)
      backup_path = os.path.join(SAVE_DIR, "account_cmdadmin.backup.json")
      with open(backup_path, "w") as f:
        json.dump(default_data, f, indent=4)
    except Exception:
      pass


def load_account_data(username):
  ensure_save_directory()
  path = os.path.join(SAVE_DIR, f"account_{username}.json")
  if os.path.exists(path):
    try:
      with open(path, "r") as f:
        data = json.load(f)
        if isinstance(data, dict):
          return data
    except Exception:
      pass
  return None


def handle_account_overlap(username):
  ensure_save_directory()
  main_file = os.path.join(SAVE_DIR, f"account_{username}.json")
  backup_file = os.path.join(SAVE_DIR, f"account_{username}.backup.json")

  old_main = os.path.join(SAVE_DIR, f"account_{username}.old.json")
  old_backup = os.path.join(SAVE_DIR, f"account_{username}.old.backup.json")

  try:
    if os.path.exists(main_file):
      if os.path.exists(old_main):
        os.remove(old_main)
      shutil.move(main_file, old_main)

    if os.path.exists(backup_file):
      if os.path.exists(old_backup):
        os.remove(old_backup)
      shutil.move(backup_file, old_backup)
  except Exception as e:
    print(f"Overlap handling error: {e}")


def save_account_data(username, data):
  ensure_save_directory()
  path = os.path.join(SAVE_DIR, f"account_{username}.json")
  backup_path = os.path.join(SAVE_DIR, f"account_{username}.backup.json")

  try:
    with open(path, "w") as f:
      json.dump(data, f, indent=4)
  except Exception as e:
    print(f"Save error: {e}")

  try:
    with open(backup_path, "w") as f:
      json.dump(data, f, indent=4)
  except Exception as e:
    print(f"Backup error: {e}")


def reset_account_on_death(username):
  """Deletes old save files, extracts the password, and recreates fresh files with fully reset stats."""
  if not username or username == "guest":
    return
  ensure_save_directory()
  path = os.path.join(SAVE_DIR, f"account_{username}.json")
  backup_path = os.path.join(SAVE_DIR, f"account_{username}.backup.json")

  password = "123"
  if os.path.exists(path):
    try:
      with open(path, "r") as f:
        data = json.load(f)
        if isinstance(data, dict) and "password" in data:
          password = data["password"]
    except Exception:
      pass

  try:
    if os.path.exists(path):
      os.remove(path)
    if os.path.exists(backup_path):
      os.remove(backup_path)
  except Exception as e:
    print(f"Error deleting old save files: {e}")

  fresh_data = {
      "password": password,
      "universe_id": 1,
      "sub_level": 1,
      "level": 1,
      "xp": 0,
      "max_hp": 100,
      "hp": 100,
  }
  save_account_data(username, fresh_data)


class Particle:

  def __init__(self, x, y, color):
    self.x = x
    self.y = y
    self.vx = random.uniform(-4, 4)
    self.vy = random.uniform(-4, 4)
    self.life = random.randint(20, 40)
    self.color = color

  def update(self, walls):
    self.x += self.vx
    self.y += self.vy
    self.life -= 1

    p_rect = pygame.Rect(int(self.x - 3), int(self.y - 3), 6, 6)
    for w in walls:
      if p_rect.colliderect(w):
        self.life = 0
        break


class Player:

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.radius = 16
    self.speed = 4.5
    self.max_hp = 100
    self.hp = 100
    self.attack_power = 20
    self.xp = 0
    self.level = 1
    self.xp_to_next = 100
    self.inventory = ["Quantum Blade", "Reality Shard"]
    self.active_weapon = "Quantum Blade"
    self.attack_cooldown = 0
    self.facing = (1, 0)

  def move(self, dx, dy, walls, speed_mult=1.0):
    if dx != 0 or dy != 0:
      length = math.hypot(dx, dy)
      dx, dy = dx / length, dy / length
      self.facing = (dx, dy)

    self.x += dx * self.speed * speed_mult
    for w in walls:
      if self.get_rect().colliderect(w):
        if dx > 0:
          self.x = w.left - self.radius
        elif dx < 0:
          self.x = w.right + self.radius

    self.y += dy * self.speed * speed_mult
    for w in walls:
      if self.get_rect().colliderect(w):
        if dy > 0:
          self.y = w.top - self.radius
        elif dy < 0:
          self.y = w.bottom + self.radius

    self.x = max(40, min(WIDTH - 40, self.x))
    self.y = max(40, min(HEIGHT - 80, self.y))

  def get_rect(self):
    return pygame.Rect(
        int(self.x - self.radius),
        int(self.y - self.radius),
        self.radius * 2,
        self.radius * 2,
    )

  def draw(self, surface):
    pygame.draw.circle(
        surface, CYAN, (int(self.x), int(self.y)), self.radius + 4, 1
    )
    pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.radius)
    fx, fy = self.facing
    pygame.draw.line(
        surface,
        WHITE,
        (self.x, self.y),
        (self.x + fx * 20, self.y + fy * 20),
        3,
    )


class Enemy:

  def __init__(self, x, y, kind="grunt"):
    self.x = x
    self.y = y
    self.kind = kind
    self.radius = 18 if kind == "brute" else 14
    self.speed = 2.2 if kind == "brute" else 3.2
    self.max_hp = 60 if kind == "brute" else 30
    self.hp = self.max_hp
    self.damage = 15 if kind == "brute" else 10
    self.color = ORANGE if kind == "brute" else RED

  def update(self, px, py, walls):
    dx = px - self.x
    dy = py - self.y
    dist = math.hypot(dx, dy)
    if dist > 1:
      dx, dy = dx / dist, dy / dist

      self.x += dx * self.speed
      for w in walls:
        if self.get_rect().colliderect(w):
          if dx > 0:
            self.x = w.left - self.radius
          elif dx < 0:
            self.x = w.right + self.radius
          self.y += (1 if py > self.y else -1) * self.speed * 1.2

      self.y += dy * self.speed
      for w in walls:
        if self.get_rect().colliderect(w):
          if dy > 0:
            self.y = w.top - self.radius
          elif dy < 0:
            self.y = w.bottom + self.radius
          self.x += (1 if px > self.x else -1) * self.speed * 1.2

  def get_rect(self):
    return pygame.Rect(
        int(self.x - self.radius),
        int(self.y - self.radius),
        self.radius * 2,
        self.radius * 2,
    )

  def draw(self, surface):
    pygame.draw.circle(
        surface, self.color, (int(self.x), int(self.y)), self.radius
    )
    bar_w = 30
    bar_h = 4
    fill = max(0, (self.hp / self.max_hp) * bar_w)
    pygame.draw.rect(
        surface,
        RED,
        (self.x - bar_w / 2, self.y - self.radius - 10, bar_w, bar_h),
    )
    pygame.draw.rect(
        surface,
        GREEN,
        (self.x - bar_w / 2, self.y - self.radius - 10, fill, bar_h),
    )


class Boss:

  def __init__(self):
    self.x = WIDTH // 2
    self.y = 180
    self.radius = 35
    self.max_hp = 800
    self.hp = 800
    self.phase = 1
    self.attack_timer = 0
    self.projectiles = []

  def update(self, px, py):
    self.attack_timer += 1
    if self.hp < 400:
      self.phase = 2

    self.x = WIDTH // 2 + math.sin(self.attack_timer * 0.03) * 200

    if self.phase == 1:
      if self.attack_timer % 70 == 0:
        angle = math.atan2(py - self.y, px - self.x)
        for i in range(-1, 2):
          p_angle = angle + (i * 0.3)
          self.projectiles.append({
              "x": self.x,
              "y": self.y,
              "vx": math.cos(p_angle) * 5,
              "vy": math.sin(p_angle) * 5,
          })
    else:
      if self.attack_timer % 35 == 0:
        angle = random.uniform(0, math.pi * 2)
        self.projectiles.append({
            "x": self.x,
            "y": self.y,
            "vx": math.cos(angle) * 7,
            "vy": math.sin(angle) * 7,
        })

    for p in self.projectiles[:]:
      p["x"] += p["vx"]
      p["y"] += p["vy"]
      if not (0 <= p["x"] <= WIDTH and 0 <= p["y"] <= HEIGHT):
        self.projectiles.remove(p)

  def get_rect(self):
    return pygame.Rect(
        int(self.x - self.radius),
        int(self.y - self.radius),
        self.radius * 2,
        self.radius * 2,
    )

  def draw(self, surface):
    color = PURPLE if self.phase == 1 else RED
    pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
    pygame.draw.circle(
        surface, WHITE, (int(self.x), int(self.y)), self.radius - 10, 2
    )
    for p in self.projectiles:
      pygame.draw.circle(surface, YELLOW, (int(p["x"]), int(p["y"])), 6)


class Game:

  def __init__(self):
    ensure_default_admin()
    self.state = STATE_MENU
    self.universe_id = 1
    self.sub_level = 1
    self.player = Player(WIDTH // 2, HEIGHT // 2)
    self.enemies = []
    self.boss = None
    self.particles = []
    self.portal_rect = pygame.Rect(WIDTH - 80, HEIGHT // 2 - 40, 50, 80)
    self.walls = []

    self.current_user = ""
    self.current_password = ""
    self.username_input = ""
    self.password_input = ""
    self.active_input_box = 1
    self.login_error = ""

    self.auth_view = "main"

    self.god_mode = False
    self.auto_clicker = False

  def save_progress(self):
    if self.current_user:
      data = {
          "password": self.current_password,
          "universe_id": self.universe_id,
          "sub_level": self.sub_level,
          "level": self.player.level,
          "xp": self.player.xp,
          "max_hp": self.player.max_hp,
          "hp": self.player.hp,
      }
      save_account_data(self.current_user, data)

  def load_user_progress(self, username, password, p_data):
    self.current_user = username
    self.current_password = password

    self.universe_id = max(1, min(5, p_data.get("universe_id", 1)))
    self.sub_level = p_data.get("sub_level", 1)
    self.player = Player(WIDTH // 2, HEIGHT // 2)
    self.player.level = p_data.get("level", 1)
    self.player.xp = p_data.get("xp", 0)
    self.player.max_hp = p_data.get("max_hp", 100)
    self.player.hp = p_data.get("hp", self.player.max_hp)

    if self.current_user != "cmdadmin":
      self.god_mode = False
      self.auto_clicker = False

    if self.universe_id == 5:
      self.load_boss_arena()
    else:
      self.load_level(self.universe_id, self.sub_level)
    self.state = STATE_PLAYING

  def process_registration(self, user, pwd):
    existing = load_account_data(user)
    if existing is not None:
      if user == "cmdadmin" and existing.get("password") == "090603180503":
        if pwd != "090603180503":
          self.login_error = "THIS IS NOT AN ADMIN (Wrong Password)!"
          return

      if existing.get("password") == pwd:
        handle_account_overlap(user)
      else:
        self.login_error = "Account exists with different password!"
        return

    new_data = {
        "password": pwd,
        "universe_id": 1,
        "sub_level": 1,
        "level": 1,
        "xp": 0,
        "max_hp": 100,
        "hp": 100,
    }
    save_account_data(user, new_data)
    self.load_user_progress(user, pwd, new_data)

  def load_level(self, u_id, s_id):
    self.universe_id = u_id
    self.sub_level = s_id
    self.enemies.clear()
    self.walls.clear()

    self.walls.append(pygame.Rect(0, 0, WIDTH, 20))
    self.walls.append(pygame.Rect(0, HEIGHT - 60, WIDTH, 60))
    self.walls.append(pygame.Rect(0, 0, 20, HEIGHT))
    self.walls.append(pygame.Rect(WIDTH - 20, 0, 20, HEIGHT))

    if u_id == 1:
      if s_id >= 2:
        self.walls.append(pygame.Rect(250, 150, 40, 200))
      if s_id >= 3:
        self.walls.append(pygame.Rect(600, 350, 200, 40))
      if s_id >= 4:
        self.walls.append(pygame.Rect(450, 100, 30, 200))
      if s_id >= 5:
        self.walls.append(pygame.Rect(150, 500, 300, 30))

      self.enemies.append(Enemy(300, 400, "grunt"))
      if s_id >= 2:
        self.enemies.append(Enemy(700, 200, "brute"))
      if s_id >= 3:
        self.enemies.append(Enemy(500, 500, "grunt"))
      if s_id >= 4:
        self.enemies.append(Enemy(200, 200, "brute"))
      if s_id >= 5:
        self.enemies.append(Enemy(800, 500, "grunt"))

    elif u_id == 2:
      self.walls.append(pygame.Rect(200, 100, 30, 400))
      if s_id >= 2:
        self.walls.append(pygame.Rect(400, 200, 400, 30))
      if s_id >= 3:
        self.walls.append(pygame.Rect(500, 350, 30, 250))
      if s_id >= 4:
        self.walls.append(pygame.Rect(100, 500, 250, 30))
      if s_id >= 5:
        self.walls.append(pygame.Rect(700, 100, 30, 300))

      self.enemies.append(Enemy(150, 250, "brute"))
      self.enemies.append(Enemy(650, 150, "grunt"))
      if s_id >= 2:
        self.enemies.append(Enemy(750, 500, "brute"))
      if s_id >= 3:
        self.enemies.append(Enemy(350, 450, "grunt"))
      if s_id >= 4:
        self.enemies.append(Enemy(550, 150, "brute"))
      if s_id >= 5:
        self.enemies.append(Enemy(300, 200, "grunt"))

    elif u_id == 3:
      self.walls.append(pygame.Rect(150, 150, 200, 30))
      self.walls.append(pygame.Rect(650, 150, 200, 30))
      if s_id >= 2:
        self.walls.append(pygame.Rect(350, 400, 300, 30))
      if s_id >= 3:
        self.walls.append(pygame.Rect(485, 200, 30, 150))
      if s_id >= 4:
        self.walls.append(pygame.Rect(200, 300, 30, 200))
      if s_id >= 5:
        self.walls.append(pygame.Rect(750, 300, 30, 200))

      self.enemies.append(Enemy(200, 300, "grunt"))
      self.enemies.append(Enemy(500, 100, "brute"))
      self.enemies.append(Enemy(800, 400, "grunt"))
      if s_id >= 2:
        self.enemies.append(Enemy(300, 550, "brute"))
      if s_id >= 3:
        self.enemies.append(Enemy(600, 500, "grunt"))
      if s_id >= 4:
        self.enemies.append(Enemy(400, 250, "brute"))
      if s_id >= 5:
        self.enemies.append(Enemy(500, 600, "brute"))

    elif u_id == 4:
      self.walls.append(pygame.Rect(150, 100, 30, 350))
      self.walls.append(pygame.Rect(300, 250, 30, 350))
      if s_id >= 2:
        self.walls.append(pygame.Rect(450, 100, 30, 350))
      if s_id >= 3:
        self.walls.append(pygame.Rect(600, 250, 30, 350))
      if s_id >= 4:
        self.walls.append(pygame.Rect(750, 100, 30, 350))
      if s_id >= 5:
        self.walls.append(pygame.Rect(100, 500, 750, 25))

      self.enemies.append(Enemy(220, 150, "brute"))
      self.enemies.append(Enemy(380, 500, "grunt"))
      self.enemies.append(Enemy(520, 200, "brute"))
      if s_id >= 2:
        self.enemies.append(Enemy(800, 300, "grunt"))
      if s_id >= 3:
        self.enemies.append(Enemy(700, 550, "brute"))
      if s_id >= 4:
        self.enemies.append(Enemy(400, 400, "grunt"))
      if s_id >= 5:
        self.enemies.append(Enemy(250, 300, "brute"))

  def load_boss_arena(self):
    self.universe_id = 5
    self.sub_level = 1
    self.enemies.clear()
    self.walls.clear()
    self.walls.append(pygame.Rect(0, 0, WIDTH, 20))
    self.walls.append(pygame.Rect(0, HEIGHT - 60, WIDTH, 60))
    self.walls.append(pygame.Rect(0, 0, 20, HEIGHT))
    self.walls.append(pygame.Rect(WIDTH - 20, 0, 20, HEIGHT))
    self.boss = Boss()
    self.state = STATE_BOSS

  def run(self):
    global WIDTH, HEIGHT, screen
    running = True
    while running:
      clock.tick(60)

      if self.player.attack_cooldown > 0:
        self.player.attack_cooldown -= 1

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          if self.current_user and self.state != STATE_GAMEOVER:
            self.save_progress()
          running = False

        elif event.type == pygame.VIDEORESIZE:
          WIDTH, HEIGHT = event.w, event.h
          screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        elif event.type == pygame.KEYDOWN:
          if self.state == STATE_MENU:
            if event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
              self.state = STATE_LOGIN
              self.auth_view = "main"

          elif self.state == STATE_LOGIN:
            if self.auth_view in ("login", "register"):
              if event.key == pygame.K_TAB:
                self.active_input_box = 2 if self.active_input_box == 1 else 1
              elif event.key == pygame.K_RETURN:
                user = self.username_input.strip()
                pwd = self.password_input.strip()
                if not user:
                  self.login_error = "Enter a username!"
                else:
                  if self.auth_view == "login":
                    if user == "cmdadmin" and pwd != "090603180503":
                      self.login_error = "THIS IS NOT AN ADMIN!"
                    else:
                      account_data = load_account_data(user)
                      if account_data is not None:
                        if account_data.get("password") == pwd:
                          self.load_user_progress(user, pwd, account_data)
                        else:
                          self.login_error = "Incorrect password!"
                      else:
                        self.login_error = "Account not found! Register first."
                  else:  # register
                    if user == "cmdadmin" and pwd != "090603180503":
                      self.login_error = "THIS IS NOT AN ADMIN!"
                    else:
                      self.process_registration(user, pwd)
              elif event.key == pygame.K_BACKSPACE:
                if self.active_input_box == 1:
                  self.username_input = self.username_input[:-1]
                else:
                  self.password_input = self.password_input[:-1]
              else:
                if event.unicode.isprintable():
                  if self.active_input_box == 1:
                    self.username_input += event.unicode
                  else:
                    self.password_input += event.unicode

          elif self.state in (STATE_PLAYING, STATE_BOSS):
            if event.key == pygame.K_ESCAPE:
              self.state = STATE_PAUSE
            elif event.key == pygame.K_r:
              self.load_level(1, 1)
              self.player = Player(WIDTH // 2, HEIGHT // 2)

          elif self.state == STATE_PAUSE:
            if event.key == pygame.K_ESCAPE:
              self.state = STATE_PLAYING if self.boss is None else STATE_BOSS

        elif event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1:
            m_pos = event.pos
            if self.state == STATE_MENU:
              self.state = STATE_LOGIN
              self.auth_view = "main"

            elif self.state == STATE_LOGIN:
              if self.auth_view == "main":
                if pygame.Rect(
                    WIDTH // 2 - 120, HEIGHT // 2 - 60, 240, 40
                ).collidepoint(m_pos):
                  self.auth_view = "login"
                  self.username_input = ""
                  self.password_input = ""
                  self.login_error = ""
                elif pygame.Rect(
                    WIDTH // 2 - 120, HEIGHT // 2, 240, 40
                ).collidepoint(m_pos):
                  self.auth_view = "register"
                  self.username_input = ""
                  self.password_input = ""
                  self.login_error = ""
                elif pygame.Rect(
                    WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 40
                ).collidepoint(m_pos):
                  self.auth_view = "guest"
                  self.login_error = ""

              elif self.auth_view == "login":
                if pygame.Rect(
                    WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40
                ).collidepoint(m_pos):
                  self.active_input_box = 1
                elif pygame.Rect(
                    WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 40
                ).collidepoint(m_pos):
                  self.active_input_box = 2
                elif pygame.Rect(
                    WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 40
                ).collidepoint(m_pos):
                  user = self.username_input.strip()
                  pwd = self.password_input.strip()
                  if not user:
                    self.login_error = "Enter a username!"
                  elif user == "cmdadmin" and pwd != "090603180503":
                    self.login_error = "THIS IS NOT AN ADMIN!"
                  else:
                    account_data = load_account_data(user)
                    if account_data is not None:
                      if account_data.get("password") == pwd:
                        self.load_user_progress(user, pwd, account_data)
                      else:
                        self.login_error = "Incorrect password!"
                    else:
                      self.login_error = "Account not found!"
                elif pygame.Rect(
                    WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 35
                ).collidepoint(m_pos):
                  self.auth_view = "main"

              elif self.auth_view == "register":
                if pygame.Rect(
                    WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40
                ).collidepoint(m_pos):
                  self.active_input_box = 1
                elif pygame.Rect(
                    WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 40
                ).collidepoint(m_pos):
                  self.active_input_box = 2
                elif pygame.Rect(
                    WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 40
                ).collidepoint(m_pos):
                  user = self.username_input.strip()
                  pwd = self.password_input.strip()
                  if not user:
                    self.login_error = "Enter a username!"
                  elif user == "cmdadmin" and pwd != "090603180503":
                    self.login_error = "THIS IS NOT AN ADMIN!"
                  else:
                    self.process_registration(user, pwd)
                elif pygame.Rect(
                    WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 35
                ).collidepoint(m_pos):
                  self.auth_view = "main"

              elif self.auth_view == "guest":
                if pygame.Rect(
                    WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40
                ).collidepoint(m_pos):
                  guest_data = {
                      "password": "",
                      "universe_id": 1,
                      "sub_level": 1,
                      "level": 1,
                      "xp": 0,
                      "max_hp": 100,
                      "hp": 100,
                  }
                  self.load_user_progress("guest", "123", guest_data)
                elif pygame.Rect(
                    WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 35
                ).collidepoint(m_pos):
                  self.auth_view = "main"

            elif (
                self.state in (STATE_PLAYING, STATE_BOSS)
                and self.player.attack_cooldown == 0
            ):
              self.perform_attack()
              self.player.attack_cooldown = 10

            elif self.state == STATE_PAUSE:
              if pygame.Rect(
                  WIDTH // 2 - 120, HEIGHT // 2 - 60, 240, 40
              ).collidepoint(m_pos):
                self.state = STATE_PLAYING if self.boss is None else STATE_BOSS
              elif pygame.Rect(
                  WIDTH // 2 - 120, HEIGHT // 2 + 10, 240, 40
              ).collidepoint(m_pos):
                if self.current_user:
                  self.save_progress()
                self.current_user = ""
                self.state = STATE_MENU
              elif self.current_user == "cmdadmin":
                if pygame.Rect(
                    WIDTH // 2 - 170, HEIGHT // 2 + 95, 250, 35
                ).collidepoint(m_pos):
                  self.god_mode = not self.god_mode
                elif pygame.Rect(
                    WIDTH // 2 - 170, HEIGHT // 2 + 135, 250, 35
                ).collidepoint(m_pos):
                  self.auto_clicker = not self.auto_clicker

            elif self.state == STATE_GAMEOVER:
              if pygame.Rect(
                  WIDTH // 2 - 130, HEIGHT // 2 + 50, 120, 40
              ).collidepoint(m_pos):
                self.load_level(1, 1)
                self.player = Player(WIDTH // 2, HEIGHT // 2)
                self.state = STATE_PLAYING
              elif pygame.Rect(
                  WIDTH // 2 + 10, HEIGHT // 2 + 50, 120, 40
              ).collidepoint(m_pos):
                self.current_user = ""
                self.state = STATE_MENU

            elif self.state == STATE_VICTORY:
              self.load_level(1, 1)
              self.player = Player(WIDTH // 2, HEIGHT // 2)
              self.state = STATE_PLAYING

      keys = pygame.key.get_pressed()

      if self.state in (STATE_PLAYING, STATE_BOSS):
        if self.player.hp < self.player.max_hp:
          self.player.hp = min(self.player.max_hp, self.player.hp + (10 / 60.0))

        mouse_pressed = pygame.mouse.get_pressed()
        if (
            keys[pygame.K_SPACE] or mouse_pressed[0] or self.auto_clicker
        ) and self.player.attack_cooldown == 0:
          self.perform_attack()
          self.player.attack_cooldown = 10

        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
          dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
          dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
          dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
          dx += 1

        speed_mult = 0.85 if self.universe_id == 2 else 1.0
        self.player.move(dx, dy, self.walls, speed_mult)

        for p in self.particles[:]:
          p.update(self.walls)
          if p.life <= 0:
            self.particles.remove(p)
            continue

          p_rect = pygame.Rect(int(p.x - 3), int(p.y - 3), 6, 6)

          if self.state == STATE_PLAYING:
            hit_something = False
            for e in self.enemies[:]:
              if e.get_rect().colliderect(p_rect):
                e.hp -= 1
                hit_something = True
                if e.hp <= 0:
                  self.enemies.remove(e)

                  if self.player.hp >= self.player.max_hp:
                    self.player.max_hp += 25
                    self.player.hp = self.player.max_hp
                  else:
                    self.player.hp = min(
                        self.player.max_hp, self.player.hp + 100
                    )

                  self.player.xp += 40
                  if self.player.xp >= self.player.xp_to_next:
                    self.player.level += 1
                    self.player.max_hp += 25
                    self.player.hp = self.player.max_hp
                    self.player.xp = 0
                    self.player.xp_to_next = int(self.player.xp_to_next * 1.5)
                  self.save_progress()
                break
            if hit_something and p in self.particles:
              self.particles.remove(p)

          elif self.state == STATE_BOSS and self.boss:
            if self.boss.get_rect().colliderect(p_rect):
              self.boss.hp -= 1
              if p in self.particles:
                self.particles.remove(p)
              if self.boss.hp <= 0:
                self.state = STATE_VICTORY
                self.save_progress()

        if self.state == STATE_PLAYING:
          for e in self.enemies[:]:
            e.update(self.player.x, self.player.y, self.walls)

            if self.player.get_rect().colliderect(e.get_rect()):
              if not self.god_mode:
                self.player.hp -= 0.8
              angle = math.atan2(e.y - self.player.y, e.x - self.player.x)
              e.x += math.cos(angle) * 4.0
              e.y += math.sin(angle) * 4.0

              if self.player.hp <= 0 and not self.god_mode:
                reset_account_on_death(self.current_user)
                self.state = STATE_GAMEOVER

          if self.portal_rect.colliderect(self.player.get_rect()):
            next_sub = self.sub_level + 1
            next_univ = self.universe_id
            if next_sub > 5:
              next_univ += 1
              next_sub = 1

            if next_univ > 4:
              self.load_boss_arena()
              self.player.x, self.player.y = WIDTH // 2, HEIGHT - 120
            else:
              self.load_level(next_univ, next_sub)
              self.player.x, self.player.y = 50, HEIGHT // 2
            self.save_progress()

        elif self.state == STATE_BOSS and self.boss:
          self.boss.update(self.player.x, self.player.y)

          if self.player.get_rect().colliderect(self.boss.get_rect()):
            if not self.god_mode:
              self.player.hp -= 1.2
            angle = math.atan2(
                self.player.y - self.boss.y, self.player.x - self.boss.x
            )
            self.player.x += math.cos(angle) * 5.0
            self.player.y += math.sin(angle) * 5.0

            if self.player.hp <= 0 and not self.god_mode:
              reset_account_on_death(self.current_user)
              self.state = STATE_GAMEOVER

          for p in self.boss.projectiles[:]:
            p_rect = pygame.Rect(p["x"] - 6, p["y"] - 6, 12, 12)
            if self.player.get_rect().colliderect(p_rect):
              if not self.god_mode:
                self.player.hp -= 15
              self.boss.projectiles.remove(p)
              if self.player.hp <= 0 and not self.god_mode:
                reset_account_on_death(self.current_user)
                self.state = STATE_GAMEOVER

      screen.fill(BG_COLOR)

      if self.state == STATE_MENU:
        self.draw_menu()
      elif self.state == STATE_LOGIN:
        self.draw_login()
      elif self.state in (STATE_PLAYING, STATE_BOSS):
        self.draw_world()
      elif self.state == STATE_PAUSE:
        self.draw_world()
        self.draw_pause()
      elif self.state == STATE_GAMEOVER:
        self.draw_gameover()
      elif self.state == STATE_VICTORY:
        self.draw_victory()

      pygame.display.flip()

    pygame.quit()
    sys.exit()

  def perform_attack(self):
    fx, fy = self.player.facing
    attack_range = 40
    hit_x = self.player.x + fx * attack_range
    hit_y = self.player.y + fy * attack_range

    for _ in range(25):
      self.particles.append(Particle(hit_x, hit_y, CYAN))

  def draw_menu(self):
    title = FONT_LG.render("MULTIVERSE RPG: QUANTUM RIFT", True, CYAN)
    sub = FONT_MD.render(
        "Press [ENTER], [SPACE], or Click to Continue", True, WHITE
    )
    controls = FONT_SM.render(
        "Move: WASD  |  Attack: HOLD SPACE or LEFT CLICK  |  Maximize Window"
        " Enabled  |  Pause: ESC",
        True,
        GRAY,
    )
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 10))
    screen.blit(
        controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT // 2 + 60)
    )

  def draw_login(self):
    if self.auth_view == "main":
      title = FONT_LG.render("CHOOSE ACCESS MODE", True, CYAN)
      screen.blit(
          title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 130)
      )

      login_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 60, 240, 40)
      pygame.draw.rect(screen, BLUE, login_btn, border_radius=5)
      l_txt = FONT_MD.render("Log In", True, WHITE)
      screen.blit(
          l_txt, (login_btn.centerx - l_txt.get_width() // 2, login_btn.y + 8)
      )

      reg_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2, 240, 40)
      pygame.draw.rect(screen, PURPLE, reg_btn, border_radius=5)
      r_txt = FONT_MD.render("Register", True, WHITE)
      screen.blit(
          r_txt, (reg_btn.centerx - r_txt.get_width() // 2, reg_btn.y + 8)
      )

      guest_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 40)
      pygame.draw.rect(screen, DARK_GRAY, guest_btn, border_radius=5)
      g_txt = FONT_MD.render("Play as Guest", True, WHITE)
      screen.blit(
          g_txt, (guest_btn.centerx - g_txt.get_width() // 2, guest_btn.y + 8)
      )

    elif self.auth_view == "login":
      title = FONT_LG.render("LOG IN", True, CYAN)
      screen.blit(
          title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 140)
      )

      u_label = FONT_SM.render("Username:", True, WHITE)
      u_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40)
      pygame.draw.rect(screen, DARK_GRAY, u_box, border_radius=5)
      pygame.draw.rect(
          screen,
          CYAN if self.active_input_box == 1 else GRAY,
          u_box,
          2,
          border_radius=5,
      )
      u_text = FONT_MD.render(self.username_input, True, WHITE)
      screen.blit(u_text, (u_box.x + 10, u_box.y + 8))

      p_label = FONT_SM.render("Password:", True, WHITE)
      p_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 40)
      pygame.draw.rect(screen, DARK_GRAY, p_box, border_radius=5)
      pygame.draw.rect(
          screen,
          CYAN if self.active_input_box == 2 else GRAY,
          p_box,
          2,
          border_radius=5,
      )
      p_text = FONT_MD.render("*" * len(self.password_input), True, WHITE)
      screen.blit(p_text, (p_box.x + 10, p_box.y + 8))

      btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 40)
      pygame.draw.rect(screen, BLUE, btn_rect, border_radius=5)
      btn_text = FONT_MD.render("LOG IN", True, WHITE)
      screen.blit(
          btn_text,
          (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.y + 8),
      )

      back_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 35)
      pygame.draw.rect(screen, DARK_GRAY, back_btn, border_radius=5)
      back_txt = FONT_SM.render("Back", True, WHITE)
      screen.blit(
          back_txt,
          (back_btn.centerx - back_txt.get_width() // 2, back_btn.y + 8),
      )

      screen.blit(u_label, (u_box.x, u_box.y - 22))
      screen.blit(p_label, (p_box.x, p_box.y - 22))

    elif self.auth_view == "register":
      title = FONT_LG.render("REGISTER", True, PURPLE)
      screen.blit(
          title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 140)
      )

      u_label = FONT_SM.render("Username:", True, WHITE)
      u_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 40)
      pygame.draw.rect(screen, DARK_GRAY, u_box, border_radius=5)
      pygame.draw.rect(
          screen,
          CYAN if self.active_input_box == 1 else GRAY,
          u_box,
          2,
          border_radius=5,
      )
      u_text = FONT_MD.render(self.username_input, True, WHITE)
      screen.blit(u_text, (u_box.x + 10, u_box.y + 8))

      p_label = FONT_SM.render("Password:", True, WHITE)
      p_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 40)
      pygame.draw.rect(screen, DARK_GRAY, p_box, border_radius=5)
      pygame.draw.rect(
          screen,
          CYAN if self.active_input_box == 2 else GRAY,
          p_box,
          2,
          border_radius=5,
      )
      p_text = FONT_MD.render("*" * len(self.password_input), True, WHITE)
      screen.blit(p_text, (p_box.x + 10, p_box.y + 8))

      btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 40)
      pygame.draw.rect(screen, PURPLE, btn_rect, border_radius=5)
      btn_text = FONT_MD.render("REGISTER & PLAY", True, WHITE)
      screen.blit(
          btn_text,
          (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.y + 8),
      )

      back_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 35)
      pygame.draw.rect(screen, DARK_GRAY, back_btn, border_radius=5)
      back_txt = FONT_SM.render("Back", True, WHITE)
      screen.blit(
          back_txt,
          (back_btn.centerx - back_txt.get_width() // 2, back_btn.y + 8),
      )

      screen.blit(u_label, (u_box.x, u_box.y - 22))
      screen.blit(p_label, (p_box.x, p_box.y - 22))

    elif self.auth_view == "guest":
      title = FONT_LG.render("GUEST MODE", True, CYAN)
      screen.blit(
          title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100)
      )

      play_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
      pygame.draw.rect(screen, BLUE, play_btn, border_radius=5)
      play_text = FONT_MD.render("PLAY", True, WHITE)
      screen.blit(
          play_text,
          (play_btn.centerx - play_text.get_width() // 2, play_btn.y + 8),
      )

      back_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 35)
      pygame.draw.rect(screen, DARK_GRAY, back_btn, border_radius=5)
      back_txt = FONT_SM.render("Back", True, WHITE)
      screen.blit(
          back_txt,
          (back_btn.centerx - back_txt.get_width() // 2, back_btn.y + 8),
      )

    if self.login_error:
      err_text = FONT_SM.render(self.login_error, True, RED)
      screen.blit(
          err_text, (WIDTH // 2 - err_text.get_width() // 2, HEIGHT // 2 + 200)
      )

  def draw_world(self):
    grid_color = (25, 25, 45) if self.universe_id != 2 else (45, 25, 25)
    for x in range(0, WIDTH, 50):
      pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT - 60))
    for y in range(0, HEIGHT - 60, 50):
      pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))

    if self.state == STATE_PLAYING:
      pygame.draw.rect(screen, PURPLE, self.portal_rect, border_radius=10)
      pygame.draw.rect(screen, CYAN, self.portal_rect, 3, border_radius=10)
      p_text = FONT_SM.render("PORTAL", True, WHITE)
      screen.blit(
          p_text,
          (
              self.portal_rect.centerx - p_text.get_width() // 2,
              self.portal_rect.y - 20,
          ),
      )

    for w in self.walls:
      pygame.draw.rect(screen, (50, 50, 70), w)
      pygame.draw.rect(screen, (80, 80, 110), w, 2)

    if self.state == STATE_PLAYING:
      for e in self.enemies:
        e.draw(screen)
    elif self.state in (STATE_BOSS, STATE_PAUSE) and self.boss:
      self.boss.draw(screen)

    self.player.draw(screen)

    for p in self.particles:
      pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), 3)

    pygame.draw.rect(screen, (10, 10, 18), (0, HEIGHT - 60, WIDTH, 60))
    pygame.draw.line(screen, GRAY, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)

    hp_ratio = max(0, self.player.hp / self.player.max_hp)
    pygame.draw.rect(
        screen, (50, 0, 0), (20, HEIGHT - 45, 180, 20), border_radius=4
    )
    pygame.draw.rect(
        screen, RED, (20, HEIGHT - 45, int(180 * hp_ratio), 20), border_radius=4
    )
    hp_text = FONT_SM.render(
        f"HP: {int(self.player.hp)}/{self.player.max_hp}", True, WHITE
    )
    screen.blit(hp_text, (30, HEIGHT - 44))

    u_names = {
        1: "Neon Cyberpunk",
        2: "Medieval Void",
        3: "Crystal Caverns",
        4: "Quantum Core",
        5: "Boss Arena",
    }
    u_name = u_names.get(self.universe_id, "Unknown")

    stage_display = (
        f"Universe {self.universe_id} (Lvl {self.sub_level}/5)"
        if self.universe_id != 5
        else "Final Boss Arena"
    )
    info_text = FONT_SM.render(
        f"{stage_display}: {u_name}  |  Hero: {self.current_user} (Lvl"
        f" {self.player.level})",
        True,
        WHITE,
    )
    screen.blit(info_text, (200, HEIGHT - 42))

    if self.state in (STATE_BOSS, STATE_PAUSE) and self.boss:
      b_ratio = max(0, self.boss.hp / self.boss.max_hp)
      pygame.draw.rect(
          screen, (50, 0, 50), (WIDTH // 2 - 200, 15, 400, 20), border_radius=4
      )
      pygame.draw.rect(
          screen,
          PURPLE,
          (WIDTH // 2 - 200, 15, int(400 * b_ratio), 20),
          border_radius=4,
      )
      b_text = FONT_SM.render(
          f"FINAL BOSS HP: {int(self.boss.hp)}/{self.boss.max_hp}", True, WHITE
      )
      screen.blit(b_text, (WIDTH // 2 - b_text.get_width() // 2, 17))

  def draw_pause(self):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((10, 10, 20))
    screen.blit(overlay, (0, 0))

    title = FONT_LG.render("GAME PAUSED", True, CYAN)

    res_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 60, 240, 40)
    pygame.draw.rect(screen, BLUE, res_btn, border_radius=5)
    res_text = FONT_MD.render("Resume Game", True, WHITE)
    screen.blit(
        res_text, (res_btn.centerx - res_text.get_width() // 2, res_btn.y + 8)
    )

    quit_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 10, 240, 40)
    is_guest = self.current_user == "guest"
    pygame.draw.rect(
        screen, BLUE if is_guest else RED, quit_btn, border_radius=5
    )
    quit_text = FONT_MD.render(
        "Title Screen" if is_guest else "Save & Main Menu", True, WHITE
    )
    screen.blit(
        quit_text, (quit_btn.centerx - quit_text.get_width() // 2, quit_btn.y + 8)
    )

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 130))

    if self.current_user == "cmdadmin":
      admin_title = FONT_MD.render("--- ADMIN CHEATS ---", True, YELLOW)
      screen.blit(
          admin_title,
          (WIDTH // 2 - admin_title.get_width() // 2, HEIGHT // 2 + 65),
      )

      gm_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 25, 25)
      pygame.draw.rect(screen, DARK_GRAY, gm_box)
      pygame.draw.rect(screen, WHITE, gm_box, 2)
      if self.god_mode:
        pygame.draw.line(
            screen,
            GREEN,
            (gm_box.x + 4, gm_box.centery),
            (gm_box.centerx, gm_box.bottom - 5),
            3,
        )
        pygame.draw.line(
            screen,
            GREEN,
            (gm_box.centerx, gm_box.bottom - 5),
            (gm_box.right - 4, gm_box.top + 5),
            3,
        )
      gm_label = FONT_SM.render("God Mode (Invincible)", True, WHITE)
      screen.blit(gm_label, (gm_box.right + 10, gm_box.y + 3))

      ac_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 140, 25, 25)
      pygame.draw.rect(screen, DARK_GRAY, ac_box)
      pygame.draw.rect(screen, WHITE, ac_box, 2)
      if self.auto_clicker:
        pygame.draw.line(
            screen,
            GREEN,
            (ac_box.x + 4, ac_box.centery),
            (ac_box.centerx, ac_box.bottom - 5),
            3,
        )
        pygame.draw.line(
            screen,
            GREEN,
            (ac_box.centerx, ac_box.bottom - 5),
            (ac_box.right - 4, ac_box.top + 5),
            3,
        )
      ac_label = FONT_SM.render("Auto-Clicker Support", True, WHITE)
      screen.blit(ac_label, (ac_box.right + 10, ac_box.y + 3))

  def draw_gameover(self):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((10, 5, 10))
    screen.blit(overlay, (0, 0))

    title_shadow = FONT_XL.render(
        "DEFEATED IN THE MULTIVERSE", True, (80, 10, 10)
    )
    title = FONT_XL.render("DEFEATED IN THE MULTIVERSE", True, RED)

    stats_text = FONT_MD.render(
        f"User: {self.current_user} | Reached: Universe {self.universe_id},"
        f" Level {self.sub_level} | Hero Level: {self.player.level}",
        True,
        WHITE,
    )

    screen.blit(
        title_shadow,
        (WIDTH // 2 - title.get_width() // 2 + 3, HEIGHT // 2 - 77),
    )
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(
        stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 - 10)
    )

    restart_btn = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 50, 120, 40)
    pygame.draw.rect(screen, BLUE, restart_btn, border_radius=5)
    r_txt = FONT_MD.render("Restart", True, WHITE)
    screen.blit(
        r_txt, (restart_btn.centerx - r_txt.get_width() // 2, restart_btn.y + 8)
    )

    title_btn = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 50, 120, 40)
    pygame.draw.rect(screen, RED, title_btn, border_radius=5)
    t_txt = FONT_MD.render("Title Screen", True, WHITE)
    screen.blit(
        t_txt, (title_btn.centerx - t_txt.get_width() // 2, title_btn.y + 8)
    )

  def draw_victory(self):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((5, 15, 10))
    screen.blit(overlay, (0, 0))

    title_shadow = FONT_XL.render(
        "VICTORY! MULTIVERSE CONQUERED", True, (10, 80, 30)
    )
    title = FONT_XL.render("VICTORY! MULTIVERSE CONQUERED", True, GREEN)

    stats_text = FONT_MD.render(
        f"User: {self.current_user} | Final Hero Level: {self.player.level} |"
        " Quantum Energy Mastered",
        True,
        YELLOW,
    )
    sub = FONT_MD.render("Click or Press [ENTER] to Play Again", True, CYAN)

    screen.blit(
        title_shadow,
        (WIDTH // 2 - title.get_width() // 2 + 3, HEIGHT // 2 - 77),
    )
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(
        stats_text, (WIDTH // 2 - stats_text.get_width() // 2, HEIGHT // 2 - 10)
    )
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 50))


if __name__ == "__main__":
  game = Game()
  game.run()
  game.run()