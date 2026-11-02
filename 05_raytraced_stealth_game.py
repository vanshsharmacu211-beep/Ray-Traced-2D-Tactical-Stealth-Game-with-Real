"""Ray-Traced 2D Tactical Stealth Game
WASD/Arrows move. Guards see through real raycast vision cones (walls block sight). Reach the green exit. R restarts."""
import tkinter as tk, math
W, H = 900, 600
RECTS = [(200, 0, 220, 350), (200, 450, 220, 600), (420, 150, 440, 600), (420, 0, 440, 60),
         (640, 0, 660, 420), (640, 500, 660, 600), (300, 200, 360, 260), (520, 300, 580, 360), (730, 220, 790, 260)]
SEGS = [(0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)]
for (a, b, c_, d) in RECTS: SEGS += [(a, b, c_, b), (c_, b, c_, d), (c_, d, a, d), (a, d, a, b)]
EXIT = (800, 270, 880, 330)

def ray_seg(ox, oy, dx, dy, seg):
    x1, y1, x2, y2 = seg; sx, sy = x2 - x1, y2 - y1
    den = dx * sy - dy * sx
    if abs(den) < 1e-9: return None
    t = ((x1 - ox) * sy - (y1 - oy) * sx) / den
    u = ((x1 - ox) * dy - (y1 - oy) * dx) / den
    return t if t >= 0 and 0 <= u <= 1 else None

def cast(ox, oy, ang, maxr):
    dx, dy = math.cos(ang), math.sin(ang); best = maxr
    for sg in SEGS:
        t = ray_seg(ox, oy, dx, dy, sg)
        if t is not None and t < best: best = t
    return best

def angdiff(a, b): return (a - b + math.pi) % (2 * math.pi) - math.pi

class Guard:
    def __init__(s, pts): s.pts, s.i, s.x, s.y = pts, 1, pts[0][0], pts[0][1]; s.head = 0.0; s.face = 0.0
class Game:
    def __init__(s, root):
        s.c = tk.Canvas(root, width=W, height=H, bg="#0c0e12", highlightthickness=0); s.c.pack()
        s.keys = set(); root.bind("<KeyPress>", lambda e: s.keys.add(e.keysym.lower())); root.bind("<KeyRelease>", lambda e: s.keys.discard(e.keysym.lower()))
        root.bind("r", lambda e: s.reset()); s.reset(); s.loop()
    def reset(s):
        s.px, s.py, s.alert, s.t, s.state = 50.0, 300.0, 0.0, 0.0, "play"
        s.guards = [Guard([(110, 80), (110, 520)]), Guard([(255, 80), (255, 520)]), Guard([(520, 90), (520, 520)]), Guard([(720, 120), (720, 480)]) ]
    def blocked(s, x, y):
        return any(a - 8 < x < c + 8 and b - 8 < y < d + 8 for (a, b, c, d) in RECTS) or not (8 < x < W - 8 and 8 < y < H - 8)
    def update(s, dt):
        k = s.keys; sp = 150 * dt
        dx = (("d" in k or "right" in k) - ("a" in k or "left" in k)) * sp; dy = (("s" in k or "down" in k) - ("w" in k or "up" in k)) * sp
        if dx and dy: dx *= 0.707; dy *= 0.707
        if not s.blocked(s.px + dx, s.py): s.px += dx
        if not s.blocked(s.px, s.py + dy): s.py += dy
        seen = False
        for g in s.guards:
            tx, ty = g.pts[g.i]; d = math.hypot(tx - g.x, ty - g.y)
            if d < 3: g.i = (g.i + 1) % len(g.pts)
            else: g.x += (tx - g.x) / d * 60 * dt; g.y += (ty - g.y) / d * 60 * dt; g.head = math.atan2(ty - g.y, tx - g.x)
            g.face = g.head + 0.45 * math.sin(s.t * 1.6 + g.pts[0][0])
            dist = math.hypot(s.px - g.x, s.py - g.y); a = math.atan2(s.py - g.y, s.px - g.x)
            if dist < 230 and abs(angdiff(a, g.face)) < math.radians(35) and cast(g.x, g.y, a, 1e9) >= dist: seen = True
        s.alert = min(1.0, s.alert + dt / 0.9) if seen else max(0.0, s.alert - dt / 1.5)
        if s.alert >= 1.0: s.state = "caught"
        if EXIT[0] < s.px < EXIT[2] and EXIT[1] < s.py < EXIT[3]: s.state = "win"
        s.t += dt
    def loop(s):
        if s.state == "play": s.update(1 / 60)
        c = s.c; c.delete("all")
        for g in s.guards:
            pts = [g.x, g.y]
            for i in range(41):
                a = g.face - math.radians(35) + math.radians(70) * i / 40; r = cast(g.x, g.y, a, 230)
                pts += [g.x + r * math.cos(a), g.y + r * math.sin(a)]
            c.create_polygon(pts, fill="#4d4520", outline="")
        c.create_rectangle(*EXIT, fill="#1c5a2a", outline="#4f8"); c.create_text(840, 300, text="EXIT", fill="white")
        for r in RECTS: c.create_rectangle(*r, fill="#2c3340", outline="#6a7385")
        for g in s.guards: c.create_oval(g.x - 8, g.y - 8, g.x + 8, g.y + 8, fill="#e44", outline="")
        c.create_oval(s.px - 7, s.py - 7, s.px + 7, s.py + 7, fill="#5df", outline="")
        c.create_rectangle(10, 10, 210, 24, outline="white"); c.create_rectangle(10, 10, 10 + 200 * s.alert, 24, fill="red", outline="")
        c.create_text(220, 17, anchor="w", fill="white", text="DETECTION")
        if s.state != "play":
            c.create_text(W / 2, H / 2, text="SPOTTED - press R" if s.state == "caught" else "MISSION COMPLETE - press R", fill="red" if s.state == "caught" else "#4f8", font=("Arial", 30, "bold"))
        s.c.after(16, s.loop)
root = tk.Tk(); root.title("Ray-Traced Stealth"); Game(root); root.mainloop()
