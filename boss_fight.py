"""Boss fight prototype. Keyboard: WASD move, SPACE roll, J attack, K heal, R retry.
DualSense: left stick, Circle roll, Square/R1 attack, Triangle heal, Cross retry."""
import pygame, random, sys
from types import SimpleNamespace as NS

MESSAGE = "I love you <3"   # <- change this text
\
  
BOSS_HP = 100               # <- make it harder / easier

pygame.init()
W, H = 960, 540
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
f_s = pygame.font.SysFont("serif", 26)
f_b = pygame.font.SysFont("serif", 80)
pad = pygame.joystick.Joystick(0) if pygame.joystick.get_count() else None
V = pygame.math.Vector2
GIRL = V(W * 0.72, H / 2)


def reset():
    global S
    S = NS(scene="play", pp=V(180, H / 2), pf=V(1, 0), php=100, pst=100, flasks=3,
           roll=0, rdir=V(), atk=0, hitdone=True, bp=V(760, H / 2), bhp=BOSS_HP,
           bstate="idle", bt=1.2, bkind="slam", bhit=False, btarget=V(), ldir=V(1, 0),
           hurt=0, t=0)


def norm(v):
    return v.normalize() if v.length() > 0 else V(1, 0)


def update(dt, mv, press):
    s = S
    inv = s.roll > 0.1
    busy = s.roll > 0 or s.atk > 0
    s.hurt = max(0, s.hurt - dt)
    if mv.length() > 0.1:
        s.pf = norm(mv)
    if s.roll > 0:
        s.roll -= dt
        s.pp += s.rdir * 520 * dt
    else:
        s.pp += mv * 220 * (0.3 if s.atk > 0 else 1) * dt
    s.atk = max(0, s.atk - dt)
    if "roll" in press and s.roll <= 0 and s.pst >= 25:
        s.pst -= 25; s.roll = 0.35; s.rdir = s.pf.copy(); s.atk = 0
    elif "atk" in press and not busy and s.pst >= 20:
        s.pst -= 20; s.atk = 0.3; s.hitdone = False
    if "heal" in press and s.flasks > 0 and not busy and s.php < 100:
        s.flasks -= 1; s.php = min(100, s.php + 45)
    if not busy:
        s.pst = min(100, s.pst + 35 * dt)
    s.pp.x = max(20, min(W - 20, s.pp.x)); s.pp.y = max(20, min(H - 20, s.pp.y))
    if s.atk > 0 and s.atk < 0.2 and not s.hitdone:
        s.hitdone = True
        if (s.bp - s.pp).length() < 110:
            s.bhp -= 12

    rate = 1 if s.bhp > BOSS_HP / 2 else 0.65   # phase 2 = faster
    if s.bstate == "idle":
        s.bt -= dt
        s.bp += norm(s.pp - s.bp) * 90 * dt
        if s.bt <= 0:
            near = (s.pp - s.bp).length() < 170
            s.bkind = "slam" if near or random.random() < 0.35 else "lunge"
            s.bstate = "wind"; s.bhit = False
            s.bt = (0.8 if s.bkind == "slam" else 0.9) * rate
    elif s.bstate == "wind":
        s.bt -= dt
        if s.bkind == "lunge" and s.bt > 0.25:
            s.btarget = s.pp.copy()
        if s.bt <= 0:
            s.bstate = "atk"; s.bt = 0.35
            s.ldir = norm(s.btarget - s.bp)
    elif s.bstate == "atk":
        s.bt -= dt
        dist = (s.pp - s.bp).length()
        if s.bkind == "slam" and not s.bhit:
            s.bhit = True
            if dist < 150 and not inv:
                s.php -= 35; s.hurt = 0.2
        if s.bkind == "lunge":
            s.bp += s.ldir * 650 * dt
            s.bp.x = max(40, min(W - 40, s.bp.x)); s.bp.y = max(40, min(H - 40, s.bp.y))
            if not s.bhit and dist < 55 and not inv:
                s.bhit = True; s.php -= 30; s.hurt = 0.2
        if s.bt <= 0:
            s.bstate = "idle"
            s.bt = random.uniform(0.5, 1.0) * rate
            if rate < 1 and random.random() < 0.5:
                s.bt = 0.1   # phase 2 combo

    if s.php <= 0:
        s.scene = "dead"; s.t = 0
    elif s.bhp <= 0:
        s.scene = "felled"; s.t = 0


def text(msg, font, color, pos):
    img = font.render(msg, True, color)
    screen.blit(img, img.get_rect(center=pos))


def bar(x, y, w, h, frac, color):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, w * max(0, frac), h))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 1)


def draw():
    s = S
    screen.fill((18, 16, 22))
    pygame.draw.circle(screen, (30, 28, 38), (W // 2, H // 2), 260, 0)
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    if s.scene in ("play", "dead"):
        if s.bstate == "wind":   # telegraph
            if s.bkind == "slam":
                pygame.draw.circle(ov, (220, 40, 40, 90), s.bp, 150)
            else:
                pygame.draw.line(ov, (220, 40, 40, 110), s.bp, s.btarget, 40)
        pygame.draw.circle(screen, (150, 30, 30) if s.bstate != "wind" else (230, 90, 40), s.bp, 45)
    if s.scene == "ending":
        pygame.draw.circle(screen, (255, 140, 190), GIRL, 18)
    col = (255, 255, 255) if s.roll > 0.1 else (255, 90, 90) if s.hurt > 0 else (80, 160, 255)
    if s.scene != "dead":
        pygame.draw.circle(screen, col, s.pp, 16)
    if s.atk > 0:
        pygame.draw.circle(ov, (255, 255, 255, 110), s.pp, 110, 3)
    screen.blit(ov, (0, 0))
    if s.scene in ("play", "dead"):
        bar(W // 2 - 250, H - 40, 500, 14, s.bhp / BOSS_HP, (170, 30, 30))
        bar(20, 20, 220, 14, s.php / 100, (190, 40, 40))
        bar(20, 40, 160, 10, s.pst / 100, (60, 180, 80))
        text(f"Flasks: {s.flasks}", f_s, (230, 200, 120), (70, 70))
    if s.scene == "dead":
        shade = pygame.Surface((W, H), pygame.SRCALPHA); shade.fill((0, 0, 0, 170))
        screen.blit(shade, (0, 0))
        text("YOU DIED", f_b, (150, 20, 20), (W // 2, H // 2))
        text("press R / Cross to retry", f_s, (200, 200, 200), (W // 2, H // 2 + 70))
    if s.scene == "felled":
        text("ENEMY FELLED", f_b, (230, 190, 90), (W // 2, H // 2))
    if s.scene == "ending" and (s.pp - GIRL).length() < 60:
        r = pygame.Rect(0, 0, 320, 70); r.center = (int(GIRL.x), int(GIRL.y) - 80)
        pygame.draw.rect(screen, (255, 255, 255), r, border_radius=18)
        pygame.draw.polygon(screen, (255, 255, 255),
                            [(GIRL.x - 10, r.bottom - 2), (GIRL.x + 10, r.bottom - 2), (GIRL.x, r.bottom + 18)])
        text(MESSAGE, f_s, (200, 40, 100), r.center)


reset()
while True:
    dt = min(clock.tick(60) / 1000, 0.05)
    press = set()
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            press.add({pygame.K_SPACE: "roll", pygame.K_j: "atk", pygame.K_k: "heal",
                       pygame.K_r: "retry"}.get(e.key))
        if e.type == pygame.JOYBUTTONDOWN:
            press.add({1: "roll", 2: "atk", 10: "atk", 3: "heal", 0: "retry"}.get(e.button))
    k = pygame.key.get_pressed()
    mv = V(k[pygame.K_d] - k[pygame.K_a], k[pygame.K_s] - k[pygame.K_w])
    if pad and V(pad.get_axis(0), pad.get_axis(1)).length() > 0.25:
        mv = V(pad.get_axis(0), pad.get_axis(1))
    if mv.length() > 1:
        mv.scale_to_length(1)

    if S.scene == "play":
        update(dt, mv, press)
    elif S.scene == "dead" and "retry" in press:
        reset()
    elif S.scene == "felled":
        S.t += dt
        if S.t > 2.5:
            S.scene = "ending"
    elif S.scene == "ending" and (S.pp - GIRL).length() > 50:
        S.pp += norm(GIRL - S.pp) * 110 * dt
    draw()
    pygame.display.flip()
