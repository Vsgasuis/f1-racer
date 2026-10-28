import turtle, random, math, time

BEST_FILE = 'best_total.txt'

STAGES = [
    {'width': 90, 'laps': 2, 'limit': 35, 'track': [
        (-20, -200), (200, -200), (330, -150), (350, -20), (300, 120), (150, 180),
        (0, 140), (-150, 180), (-300, 120), (-350, -20), (-320, -150), (-200, -200),
    ]},
    {'width': 80, 'laps': 3, 'limit': 55, 'track': [
        (-20, -210), (150, -210), (300, -200), (360, -150), (340, -90),
        (250, -80), (200, -30), (240, 30), (340, 60), (370, 130),
        (320, 190), (200, 200), (110, 150), (60, 60), (0, 30),
        (-60, 80), (-100, 170), (-200, 200), (-300, 180), (-360, 110),
        (-330, 40), (-250, 10), (-230, -60), (-320, -100), (-350, -170),
        (-300, -210), (-200, -210),
    ]},
    {'width': 70, 'laps': 3, 'limit': 65, 'track': [
        (-20, -215), (140, -215), (260, -215), (350, -180), (360, -110),
        (290, -90), (200, -110), (130, -70), (150, 0), (260, 0),
        (350, 40), (360, 130), (300, 195), (190, 180), (140, 110),
        (70, 80), (20, 140), (-40, 195), (-150, 190), (-200, 120),
        (-150, 60), (-180, 0), (-280, 30), (-350, 0), (-360, -100),
        (-330, -180), (-240, -215), (-150, -215),
    ]},
]


def build_track(points, spacing=8):
    n = len(points)
    track = []
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        steps = max(2, int(math.dist(p1, p2) / spacing))
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (p2[0] - p0[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (3 * p1[0] - p0[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (p2[1] - p0[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (3 * p1[1] - p0[1] - 3 * p2[1] + p3[1]) * t3)
            track.append((x, y))
    return track


def segment_distance(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def car_parts(body, stripe, dark):
    return [
        ('#212121', [(-18, 10), (-12, 10), (-12, 21), (-18, 21)]),
        ('#212121', [(12, 10), (18, 10), (18, 21), (12, 21)]),
        ('#212121', [(-18, -21), (-12, -21), (-12, -10), (-18, -10)]),
        ('#212121', [(12, -21), (18, -21), (18, -10), (12, -10)]),
        (dark, [(-19, 7), (-15, 7), (-15, 11), (-19, 11)]),
        (dark, [(15, 7), (19, 7), (19, 11), (15, 11)]),
        (body, [(-14, -26), (14, -26), (15, -10), (15, 16), (11, 26), (-11, 26), (-15, 16), (-15, -10)]),
        (stripe, [(-5, -26), (-2, -26), (-2, 26), (-5, 26)]),
        (stripe, [(2, -26), (5, -26), (5, 26), (2, 26)]),
        ('#81d4fa', [(-11, 6), (11, 6), (9, 15), (-9, 15)]),
        ('#4fc3f7', [(-10, -12), (10, -12), (9, -17), (-9, -17)]),
        ('#fff59d', [(-11, 22), (-6, 23), (-6, 26), (-10, 26)]),
        ('#fff59d', [(6, 23), (11, 22), (10, 26), (6, 26)]),
        ('#d50000', [(-13, -26), (-8, -26), (-8, -24), (-13, -24)]),
        ('#d50000', [(8, -26), (13, -26), (13, -24), (8, -24)]),
        (dark, [(-4, -26), (-2, -26), (-2, -30), (-4, -30)]),
        (dark, [(2, -26), (4, -26), (4, -30), (2, -30)]),
        (dark, [(-17, -30), (17, -30), (17, -34), (-17, -34)]),
    ]


def register_car(canvas, name, body, stripe, dark):
    shape = turtle.Shape('compound')
    for color, points in car_parts(body, stripe, dark):
        shape.addcomponent(tuple(points), color, color)
    canvas.register_shape(name, shape)


class PlayerCar(turtle.RawTurtle):
    def __init__(self, canvas, step_turn=4, max_v=7):
        super().__init__(canvas)
        register_car(canvas, 'player', '#e53935', 'white', '#212121')
        self.shape('player')
        self.penup()
        self.step_turn = step_turn
        self.max_v = max_v
        self.velocity = 0
        self.keys = {'Up': False, 'Down': False, 'Left': False, 'Right': False}
        for key in self.keys:
            canvas.onkeypress(lambda k=key: self.set_key(k, True), key)
            canvas.onkeyrelease(lambda k=key: self.set_key(k, False), key)
        canvas.listen()

    def set_key(self, key, value):
        self.keys[key] = value

    def update(self, on_grass):
        top = 2.5 if on_grass else self.max_v
        if self.keys['Up'] and self.velocity < top:
            self.velocity = min(top, self.velocity + 0.12)
        elif self.keys['Down']:
            self.velocity = max(-2, self.velocity - 0.25)
        elif self.velocity > 0:
            self.velocity = max(0, self.velocity - 0.04)
        elif self.velocity < 0:
            self.velocity = min(0, self.velocity + 0.04)
        if self.velocity > top:
            self.velocity = max(top, self.velocity - 0.3)

        turn = self.step_turn * min(1, abs(self.velocity) / 3)
        if self.velocity < 0:
            turn = -turn
        if self.keys['Left']:
            self.left(turn)
        if self.keys['Right']:
            self.right(turn)
        self.forward(self.velocity)


class RaceGame:
    def __init__(self, canvas):
        self.canvas = canvas
        self.timer_msec = 16
        self.playing = False
        self.best = self.load_best()
        self.pens = []
        self.coins = []
        self.player = None

        self.stage = 0
        self.total = 0
        self.build_stage()

        canvas.onkeypress(self.start, 'space')
        canvas.listen()

    def build_stage(self):
        cfg = STAGES[self.stage]
        self.w = cfg['width']
        self.laps = cfg['laps']
        self.limit = cfg['limit']
        self.track = build_track(cfg['track'])
        self.n = len(self.track)

        for pen in self.pens:
            pen.clear()
        for t in self.coins:
            t.hideturtle()
        if self.player:
            self.player.hideturtle()

        self.pens = [self.draw_track(), self.draw_finish()]
        self.coins = [self.make_coin() for _ in range(6)]
        self.player = PlayerCar(self.canvas)

        self.drawer = turtle.RawTurtle(self.canvas)
        self.drawer.hideturtle()
        self.drawer.penup()
        self.drawer.color('white')
        self.pens.append(self.drawer)

        self.banner = turtle.RawTurtle(self.canvas)
        self.banner.hideturtle()
        self.banner.penup()
        self.banner.color('white')
        self.pens.append(self.banner)

        self.lap = 1
        self.coin_count = 0
        self.reset_positions()
        self.draw_hud(0)

    def draw_track(self):
        pen = turtle.RawTurtle(self.canvas)
        pen.hideturtle()
        pen.penup()
        pen.goto(self.track[0])
        pen.pensize(self.w + 14)
        pen.pendown()
        for i in range(1, self.n + 1):
            pen.pencolor('#d32f2f' if (i // 2) % 2 else 'white')
            pen.goto(self.track[i % self.n])
        pen.penup()
        pen.goto(self.track[0])
        pen.pensize(self.w)
        pen.pencolor('#555555')
        pen.pendown()
        for i in range(1, self.n + 1):
            pen.goto(self.track[i % self.n])
        pen.penup()
        return pen

    def direction(self, i):
        ax, ay = self.track[(i - 1) % self.n]
        bx, by = self.track[(i + 1) % self.n]
        length = math.hypot(bx - ax, by - ay)
        return (bx - ax) / length, (by - ay) / length

    def draw_finish(self):
        pen = turtle.RawTurtle(self.canvas)
        pen.hideturtle()
        pen.penup()
        size = 10
        px, py = self.track[0]
        tx, ty = self.direction(0)
        nx, ny = -ty, tx
        for row in range(self.w // size):
            for col in range(2):
                a = (col - 1) * size
                b = -self.w / 2 + row * size
                pen.setpos(px + tx * a + nx * b, py + ty * a + ny * b)
                pen.setheading(math.degrees(math.atan2(ty, tx)))
                pen.color('black' if (row + col) % 2 else 'white')
                pen.begin_fill()
                for _ in range(4):
                    pen.forward(size)
                    pen.left(90)
                pen.end_fill()
        return pen

    def make_coin(self):
        t = turtle.RawTurtle(self.canvas)
        t.shape('circle')
        t.shapesize(0.9, 0.9, 3)
        t.color('#ff8f00', '#ffd600')
        t.penup()
        t.hideturtle()
        return t

    def load_best(self):
        try:
            with open(BEST_FILE) as f:
                return float(f.read())
        except (OSError, ValueError):
            return None

    def save_best(self):
        try:
            with open(BEST_FILE, 'w') as f:
                f.write(f'{self.best:.2f}')
        except OSError:
            pass

    def locate(self, x, y):
        i = min(range(self.n), key=lambda k: (self.track[k][0] - x) ** 2 + (self.track[k][1] - y) ** 2)
        p = (x, y)
        a = self.track[i - 1]
        b = self.track[i]
        c = self.track[(i + 1) % self.n]
        return i, min(segment_distance(p, a, b), segment_distance(p, b, c))

    def reset_positions(self):
        for t in self.coins:
            t.hideturtle()
        start = self.n - 6
        tx, ty = self.direction(start)
        self.player.setpos(self.track[start])
        self.player.setheading(math.degrees(math.atan2(ty, tx)))
        self.player.velocity = 0
        for key in self.player.keys:
            self.player.keys[key] = False
        self.idx = start
        self.off = 0

    def place_coins(self):
        for t in self.coins:
            i = random.randint(20, self.n - 20)
            tx, ty = self.direction(i)
            side = random.uniform(-self.w / 2 + 18, self.w / 2 - 18)
            x, y = self.track[i]
            t.setpos(x - ty * side, y + tx * side)
            t.showturtle()

    def show_banner(self, title, sub):
        self.banner.clear()
        self.banner.setpos(0, 10)
        self.banner.write(title, align='center', font=('Arial', 30, 'bold'))
        self.banner.setpos(0, -20)
        self.banner.write(sub, align='center', font=('Arial', 11, 'normal'))
        self.canvas.update()

    def show_intro(self):
        self.show_banner(f'STAGE {self.stage + 1}', f'{self.laps} laps in {self.limit}s  |  Coin = -1s  |  Space: start')

    def start(self):
        if self.playing:
            return
        self.banner.clear()
        self.reset_positions()
        self.lap = 1
        self.checkpoint = False
        self.coin_count = 0
        self.frame = 0
        self.start_time = time.time()
        self.place_coins()
        self.playing = True
        self.step()

    def race_time(self):
        return max(0, time.time() - self.start_time - self.coin_count)

    def check_lap(self, prev, now):
        if self.n * 0.4 < now < self.n * 0.6:
            self.checkpoint = True
        if prev < self.n * 0.2 and now > self.n * 0.8:
            self.checkpoint = False
        if prev > self.n * 0.8 and now < self.n * 0.2 and self.checkpoint:
            self.checkpoint = False
            self.lap += 1
            if self.lap <= self.laps:
                self.place_coins()

    def step(self):
        if not self.playing:
            return
        self.player.update(self.off > self.w / 2)
        prev = self.idx
        self.idx, self.off = self.locate(*self.player.pos())
        self.check_lap(prev, self.idx)
        if self.lap > self.laps:
            self.stage_clear()
            return

        for t in self.coins:
            if t.isvisible() and self.player.distance(t) < 26:
                t.hideturtle()
                self.coin_count += 1

        if self.off > self.w / 2 + 18:
            self.crash('OFF TRACK!')
            return
        if self.race_time() > self.limit:
            self.crash('TIME OVER!')
            return

        self.frame += 1
        if self.frame % 6 == 0:
            self.draw_hud(self.race_time())
        self.canvas.update()
        self.canvas.ontimer(self.step, self.timer_msec)

    def draw_hud(self, elapsed):
        best = f'{self.best:.1f}s' if self.best else '-'
        lap = min(self.lap, self.laps)
        speed = int(abs(self.player.velocity) * 45)
        self.drawer.clear()
        self.drawer.setpos(0, 275)
        self.drawer.write(f'Stage {self.stage + 1}/{len(STAGES)}   Lap {lap}/{self.laps}   Time {elapsed:4.1f}/{self.limit}s   '
                          f'Coins {self.coin_count}   Speed {speed} km/h   Best {best}',
                          align='center', font=('Arial', 13, 'bold'))

    def stage_clear(self):
        self.playing = False
        stage_time = self.race_time()
        self.total += stage_time
        if self.stage + 1 < len(STAGES):
            self.stage += 1
            self.build_stage()
            self.show_banner('STAGE CLEAR!', f'Time {stage_time:.1f}s  |  Next: {self.laps} laps in {self.limit}s  |  Space: Stage {self.stage + 1}')
            return
        sub = f'Total {self.total:.1f}s'
        if self.best is None or self.total < self.best:
            self.best = self.total
            self.save_best()
            sub += '  NEW BEST!'
        self.stage = 0
        self.total = 0
        self.build_stage()
        self.show_banner('CHAMPION!', sub + '  |  Space: play again')

    def crash(self, title):
        self.playing = False
        self.draw_hud(self.race_time())
        self.show_banner(title, f'Stage {self.stage + 1}  Lap {self.lap}/{self.laps}  |  Space: try again')


if __name__ == '__main__':
    screen = turtle.Screen()
    screen.setup(900, 650)
    screen.title('F1 Racer')
    screen.bgcolor('#7cb342')
    screen.tracer(0)

    game = RaceGame(screen)
    game.show_intro()
    screen.mainloop()
