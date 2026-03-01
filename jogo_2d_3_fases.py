import math
import random
import time
import tkinter as tk

WIDTH = 960
HEIGHT = 540
FPS = 60
PLAYER_SIZE = 28
PLAYER_SPEED = 280
ENEMY_SIZE = 30
COIN_SIZE = 14
PORTAL_W = 48
PORTAL_H = 70

LEVELS = [
    {
        "bg": "#182030",
        "spawn": (40, 40),
        "portal": (880, 440),
        "walls": [
            (190, 0, 34, 360),
            (190, 430, 34, 110),
            (430, 180, 34, 360),
            (650, 0, 34, 300),
            (650, 370, 34, 170),
        ],
        "coins": [
            (110, 490),
            (300, 90),
            (300, 470),
            (520, 60),
            (520, 490),
            (760, 330),
        ],
        "enemies": [
            (300, 250, 150, 0),
            (760, 80, 0, 170),
        ],
    },
    {
        "bg": "#142A22",
        "spawn": (40, 470),
        "portal": (880, 40),
        "walls": [
            (0, 180, 320, 32),
            (390, 0, 32, 230),
            (390, 300, 32, 240),
            (560, 120, 280, 32),
            (560, 390, 280, 32),
            (820, 0, 32, 260),
        ],
        "coins": [
            (80, 80),
            (250, 300),
            (470, 260),
            (520, 480),
            (760, 80),
            (900, 500),
            (900, 280),
        ],
        "enemies": [
            (170, 80, 0, 180),
            (500, 80, 160, 0),
            (740, 470, -190, 0),
        ],
    },
    {
        "bg": "#2E1818",
        "spawn": (50, 50),
        "portal": (880, 440),
        "walls": [
            (150, 110, 34, 430),
            (300, 0, 34, 340),
            (450, 200, 34, 340),
            (600, 0, 34, 340),
            (750, 200, 34, 340),
            (0, 250, 90, 34),
            (870, 250, 90, 34),
        ],
        "coins": [
            (100, 500),
            (240, 70),
            (390, 500),
            (540, 70),
            (690, 500),
            (840, 70),
            (900, 500),
            (480, 270),
        ],
        "enemies": [
            (210, 200, 180, 0),
            (360, 360, 0, -190),
            (540, 160, 160, 160),
            (780, 360, -180, 0),
        ],
    },
]


def rect_collide(a, b):
    return not (
        a[0] + a[2] <= b[0]
        or a[0] >= b[0] + b[2]
        or a[1] + a[3] <= b[1]
        or a[1] >= b[1] + b[3]
    )


class Enemy:
    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.w = ENEMY_SIZE
        self.h = ENEMY_SIZE

    def rect(self):
        return [self.x, self.y, self.w, self.h]

    def update(self, dt, walls):
        self.x += self.vx * dt
        bounced_x = False

        if self.x < 0:
            self.x = 0
            bounced_x = True
        elif self.x + self.w > WIDTH:
            self.x = WIDTH - self.w
            bounced_x = True

        current = self.rect()
        for wall in walls:
            if rect_collide(current, wall):
                if self.vx > 0:
                    self.x = wall[0] - self.w
                elif self.vx < 0:
                    self.x = wall[0] + wall[2]
                bounced_x = True
                break

        if bounced_x:
            self.vx *= -1

        self.y += self.vy * dt
        bounced_y = False

        if self.y < 0:
            self.y = 0
            bounced_y = True
        elif self.y + self.h > HEIGHT:
            self.y = HEIGHT - self.h
            bounced_y = True

        current = self.rect()
        for wall in walls:
            if rect_collide(current, wall):
                if self.vy > 0:
                    self.y = wall[1] - self.h
                elif self.vy < 0:
                    self.y = wall[1] + wall[3]
                bounced_y = True
                break

        if bounced_y:
            self.vy *= -1


class GameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Exemplo Tkinter - Jogo 2D com 3 Fases")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH,
            height=HEIGHT,
            bg="#181818",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.keys = set()
        self.level_index = 0
        self.lives = 3
        self.state = "playing"

        self.player_x = 0.0
        self.player_y = 0.0
        self.player_w = PLAYER_SIZE
        self.player_h = PLAYER_SIZE

        self.walls = []
        self.coins = []
        self.enemies = []
        self.portal = [0, 0, PORTAL_W, PORTAL_H]
        self.bg = "#182030"

        self._load_level(0)

        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.focus_force()

        self.last_time = time.perf_counter()
        self._tick()

    def _on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)

        if key == "r":
            self._restart_game()

    def _on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            self.keys.remove(key)

    def _restart_game(self):
        self.level_index = 0
        self.lives = 3
        self.state = "playing"
        self._load_level(0)

    def _load_level(self, index):
        level = LEVELS[index]

        self.bg = level["bg"]
        self.walls = [list(w) for w in level["walls"]]
        self.coins = [
            [cx - COIN_SIZE / 2, cy - COIN_SIZE / 2, COIN_SIZE, COIN_SIZE]
            for cx, cy in level["coins"]
        ]
        self.enemies = [Enemy(*e) for e in level["enemies"]]
        self.portal = [level["portal"][0], level["portal"][1], PORTAL_W, PORTAL_H]

        spawn_x, spawn_y = level["spawn"]
        self.player_x = float(spawn_x)
        self.player_y = float(spawn_y)

    def _player_rect(self):
        return [self.player_x, self.player_y, self.player_w, self.player_h]

    def _move_player(self, dt):
        dx = 0
        dy = 0

        if "a" in self.keys:
            dx -= 1
        if "d" in self.keys:
            dx += 1
        if "w" in self.keys:
            dy -= 1
        if "s" in self.keys:
            dy += 1

        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

        self.player_x += dx * PLAYER_SPEED * dt
        self.player_x = max(0, min(self.player_x, WIDTH - self.player_w))

        rect = self._player_rect()
        for wall in self.walls:
            if rect_collide(rect, wall):
                if dx > 0:
                    self.player_x = wall[0] - self.player_w
                elif dx < 0:
                    self.player_x = wall[0] + wall[2]
                rect = self._player_rect()

        self.player_y += dy * PLAYER_SPEED * dt
        self.player_y = max(0, min(self.player_y, HEIGHT - self.player_h))

        rect = self._player_rect()
        for wall in self.walls:
            if rect_collide(rect, wall):
                if dy > 0:
                    self.player_y = wall[1] - self.player_h
                elif dy < 0:
                    self.player_y = wall[1] + wall[3]
                rect = self._player_rect()

    def _handle_enemy_hits(self):
        player = self._player_rect()
        for enemy in self.enemies:
            if rect_collide(player, enemy.rect()):
                self.lives -= 1
                spawn_x, spawn_y = LEVELS[self.level_index]["spawn"]
                self.player_x = float(spawn_x)
                self.player_y = float(spawn_y)
                if self.lives <= 0:
                    self.state = "game_over"
                return

    def _collect_coins(self):
        player = self._player_rect()
        self.coins = [coin for coin in self.coins if not rect_collide(player, coin)]

    def _try_next_level(self):
        if self.coins:
            return

        if rect_collide(self._player_rect(), self.portal):
            self.level_index += 1
            if self.level_index >= len(LEVELS):
                self.state = "won"
            else:
                self._load_level(self.level_index)

    def _update_game(self, dt):
        if self.state != "playing":
            return

        self._move_player(dt)

        for enemy in self.enemies:
            enemy.update(dt, self.walls)

        self._handle_enemy_hits()
        if self.state != "playing":
            return

        self._collect_coins()
        self._try_next_level()

    def _draw(self):
        self.canvas.delete("all")
        self.canvas.configure(bg=self.bg if self.state == "playing" else "#18181A")

        for wall in self.walls:
            self.canvas.create_rectangle(
                wall[0],
                wall[1],
                wall[0] + wall[2],
                wall[1] + wall[3],
                fill="#5A667A",
                outline="",
            )

        portal_color = "#24B45A" if not self.coins else "#464646"
        px, py, pw, ph = self.portal
        self.canvas.create_rectangle(
            px,
            py,
            px + pw,
            py + ph,
            fill=portal_color,
            outline="",
            width=0,
        )

        for coin in self.coins:
            cx = coin[0] + coin[2] / 2
            cy = coin[1] + coin[3] / 2
            r = coin[2] / 2
            self.canvas.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill="#FFD042",
                outline="",
            )

        for enemy in self.enemies:
            ex, ey, ew, eh = enemy.rect()
            self.canvas.create_rectangle(
                ex,
                ey,
                ex + ew,
                ey + eh,
                fill="#DC4646",
                outline="",
            )

        p = self._player_rect()
        self.canvas.create_rectangle(
            p[0],
            p[1],
            p[0] + p[2],
            p[1] + p[3],
            fill="#5CC4FF",
            outline="",
        )

        hud = (
            f"Fase: {min(self.level_index + 1, 3)}/3   "
            f"Vidas: {self.lives}   Moedas restantes: {len(self.coins)}"
        )
        self.canvas.create_text(
            16,
            18,
            anchor="w",
            fill="#F0F0F0",
            text=hud,
            font=("Consolas", 15, "bold"),
        )

        self.canvas.create_text(
            16,
            HEIGHT - 20,
            anchor="w",
            fill="#DCDCDC",
            text="WASD para mover | Colete tudo e entre no portal verde | R reinicia",
            font=("Consolas", 12),
        )

        if self.state == "game_over":
            self.canvas.create_text(
                WIDTH / 2,
                210,
                fill="#EC6060",
                text="GAME OVER",
                font=("Consolas", 44, "bold"),
            )
            self.canvas.create_text(
                WIDTH / 2,
                265,
                fill="#E6E6E6",
                text="Pressione R para reiniciar",
                font=("Consolas", 16),
            )

        if self.state == "won":
            self.canvas.create_text(
                WIDTH / 2,
                210,
                fill="#5EE080",
                text="VOCE VENCEU!",
                font=("Consolas", 44, "bold"),
            )
            self.canvas.create_text(
                WIDTH / 2,
                265,
                fill="#E6E6E6",
                text="Pressione R para jogar novamente",
                font=("Consolas", 16),
            )

    def _tick(self):
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now

        # Evita saltos grandes quando a janela perde foco.
        dt = min(dt, 1.0 / 20.0)

        self._update_game(dt)
        self._draw()

        interval_ms = int(1000 / FPS)
        self.root.after(interval_ms, self._tick)

    def run(self):
        self.root.mainloop()


def main():
    random.seed()
    app = GameApp()
    app.run()


if __name__ == "__main__":
    main()
