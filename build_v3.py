#!/usr/bin/env python3
"""bring-the-humans-03 v3 — voice-led TikTok ad, fresh concept.
"The ghost goes to work": illustration-led scenes that follow the narration
(hook question -> clip factory -> prize counter -> free checklist -> CTA),
NOT v1's 4-scene structure, NOT v2's kinetic-typography wall.
Audio: TTS voiceover ONLY (no music — Len adds TikTok music at upload).
Output: makefun-tiktok-ad-v3.mp4 (1080x1920, 30fps, 20s)."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 20.0
NFRAMES = int(DUR * FPS)
BASE = os.path.expanduser("~/workspace/makefun-kit/bring-the-humans-03")
V3 = os.path.join(BASE, "v3")
V2 = os.path.join(BASE, "v2")
FR = os.path.join(V3, "frames")
CARD = os.path.join(V2, "card")
os.makedirs(FR, exist_ok=True)

INTER = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
INTER_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
MONO = os.path.join(BASE, "fonts/JetBrainsMono-Bold.ttf")
PK = os.path.join(BASE, "make-fun-press-kit")

MAGENTA = (196, 28, 131)
PINK = (255, 136, 196)
WHITE = (255, 255, 255)
INK = (25, 20, 25)
GRAY = (191, 199, 220)
DARK = (11, 11, 18)
GREEN = (74, 222, 128)
RED = (248, 113, 113)
GOLD = (250, 204, 21)

_font_cache = {}
def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]

def ease_out_back(t):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_out_quad(t):
    return 1 - (1 - t) ** 2

def clamp01(x):
    return max(0.0, min(1.0, x))

# ---------------------------------------------------------------- assets
mark = Image.open(os.path.join(PK, "mark-on-dark-1024.png")).convert("RGBA")
mark_small = mark.resize((84, 84), Image.LANCZOS)
lockup = Image.open(os.path.join(PK, "lockup-on-dark-2400.png")).convert("RGBA")
lockup = lockup.resize((760, int(760 * lockup.height / lockup.width)), Image.LANCZOS)

def load_ill(name, w):
    im = Image.open(os.path.join(PK, "illustrations", name)).convert("RGBA")
    h = int(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)

ghost_spy = load_ill("ghost-spyglass.png", 560)
ghost_laptop = load_ill("ghost-laptop-recording.png", 620)
ghost_trophy = load_ill("ghost-pile-trophy.png", 380)
ghost_clip = load_ill("ghost-clipboard-check.png", 520)

def glow_blob(size, color, alpha):
    im = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(im)
    for r in range(size // 2, 0, -6):
        a = int(alpha * (1 - r / (size / 2)) ** 2)
        d.ellipse([size // 2 - r, size // 2 - r, size // 2 + r, size // 2 + r], fill=a)
    blob = Image.new("RGBA", (size, size), color + (0,))
    blob.putalpha(im)
    return blob

blob_mag = glow_blob(900, MAGENTA, 110)
blob_purp = glow_blob(700, (106, 27, 154), 90)

bg_base = Image.new("RGB", (W, H))
_top, _bot = (13, 13, 22), (24, 10, 26)
for y in range(H):
    f = y / H
    c = tuple(int(_top[i] + (_bot[i] - _top[i]) * f) for i in range(3))
    ImageDraw.Draw(bg_base).line([(0, y), (W, y)], fill=c)
bg_base = bg_base.convert("RGBA")

# ---------------------------------------------------------------- text helpers
def text_layer(text, fnt, fill, stroke_w=0, stroke_fill=(0, 0, 0, 255)):
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=fnt, stroke_width=stroke_w)
    w, h = bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((2 - bbox[0], 2 - bbox[1]), text, font=fnt, fill=fill,
           stroke_width=stroke_w, stroke_fill=stroke_fill)
    return im

def paste_scaled(base, layer, cx, cy, scale, alpha=255):
    if scale <= 0.01 or alpha <= 0:
        return
    w, h = int(layer.width * scale), int(layer.height * scale)
    if w < 2 or h < 2:
        return
    l2 = layer.resize((w, h), Image.LANCZOS)
    if alpha < 255:
        a = l2.split()[3].point(lambda v: v * alpha // 255)
        l2.putalpha(a)
    base.alpha_composite(l2, (int(cx - w / 2), int(cy - h / 2)))

def paste_at(base, layer, x, y, alpha=255):
    if alpha <= 0:
        return
    if alpha < 255:
        l2 = layer.copy()
        a = l2.split()[3].point(lambda v: v * alpha // 255)
        l2.putalpha(a)
        base.alpha_composite(l2, (int(x), int(y)))
    else:
        base.alpha_composite(layer, (int(x), int(y)))

def center_x(layer):
    return 540 - layer.width / 2

# pre-render text layers
L = {
    "brand": text_layer("make.fun", font(INTER_BOLD, 52), WHITE + (255,), 2, (0, 0, 0, 255)),
    "q1": text_layer("AI LU BISA", font(INTER, 118), WHITE + (255,), 3, (0, 0, 0, 255)),
    "q2": text_layer("KERJA BUAT LU?", font(INTER, 118), PINK + (255,), 3, (0, 0, 0, 255)),
    "q0": text_layer("LU TAU GA?", font(INTER_BOLD, 56), GRAY + (255,)),
    "cap_factory": text_layer("AI IKUT LOMBA BIKIN CLIP", font(INTER_BOLD, 52), WHITE + (255,), 2, (0, 0, 0, 255)),
    "cap_prize": text_layer("MENANG = DUIT BENERAN", font(INTER_BOLD, 56), WHITE + (255,), 2, (0, 0, 0, 255)),
    "p20": text_layer("20 PEMENANG", font(INTER, 92), WHITE + (255,), 3, (0, 0, 0, 255)),
    "zero": text_layer("$0", font(INTER, 340), PINK + (255,), 6, (255, 255, 255, 255)),
    "modal": text_layer("TANPA MODAL.", font(INTER, 96), WHITE + (255,), 3, (0, 0, 0, 255)),
    "gratis": text_layer("GRATIS MASUK.", font(INTER_BOLD, 58), GRAY + (255,)),
    "daftar": text_layer("DAFTAR", font(INTER_BOLD, 64), WHITE + (255,)),
    "modalx": text_layer("MODAL", font(INTER_BOLD, 64), WHITE + (255,)),
    "cek": text_layer("CEK CAPTION", font(INTER, 110), WHITE + (255,), 3, (0, 0, 0, 255)),
    "kode2": text_layer("KODENYA DI SANA", font(INTER_BOLD, 52), GRAY + (255,)),
    "refcode": text_layer("j62x7qjj", font(MONO, 100), INK + (255,)),
}

def money_layer(amount):
    return text_layer("$%d" % amount, font(INTER, 300), PINK + (255,), 5, (255, 255, 255, 255))

# mini clip cards for the factory scene (pre-rendered variants)
def make_clip_card(bg, label, views):
    cw, ch = 240, 400
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=28, fill=bg + (255,))
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=28, outline=(255, 255, 255, 90), width=3)
    # play triangle
    cx, cy = cw // 2, ch // 2 - 20
    d.polygon([(cx - 28, cy - 36), (cx - 28, cy + 36), (cx + 36, cy)], fill=(255, 255, 255, 235))
    # label + views
    d.text((20, ch - 86), label, font=font(INTER_BOLD, 30), fill=(255, 255, 255, 255))
    d.text((20, ch - 48), views, font=font(INTER_BOLD, 26), fill=(255, 255, 255, 200))
    return card

clip_cards = [
    make_clip_card((196, 28, 131), "CLIP #1", "12,4rb views"),
    make_clip_card((106, 27, 154), "CLIP #2", "8,1rb views"),
    make_clip_card((30, 60, 140), "CLIP #3", "5,7rb views"),
]

def draw_badge(frame):
    paste_at(frame, mark_small, 48, 44)
    frame.alpha_composite(L["brand"], (148, 52))

def draw_bg(frame, t):
    frame.alpha_composite(bg_base, (0, 0))
    bx1 = 540 + int(260 * math.sin(t * 0.45)) - 450
    by1 = 500 + int(180 * math.sin(t * 0.30 + 1.0)) - 450
    bx2 = 540 + int(300 * math.sin(t * 0.33 + 2.0)) - 350
    by2 = 1350 + int(200 * math.sin(t * 0.40 + 0.5)) - 350
    frame.alpha_composite(blob_mag, (bx1, by1))
    frame.alpha_composite(blob_purp, (bx2, by2))

def pop_scale(t, t0, dur=0.38):
    if t < t0:
        return 0.0
    u = clamp01((t - t0) / dur)
    return 0.55 + 0.45 * ease_out_back(u) if u < 1 else 1.0

def fade_in(t, t0, dur=0.3):
    return int(255 * clamp01((t - t0) / dur))

def render(t, fi):
    # --- S6 end card (16.4–20.0): referral webm frames + code in pill
    if t >= 16.4:
        lt = t - 16.4
        idx = min(149, int(lt * 60)) + 1
        card = Image.open(os.path.join(CARD, "f%03d.png" % idx)).convert("RGBA")
        code = L["refcode"]
        u = clamp01(lt / 0.5)
        show_w = int(code.width * u)
        if show_w > 4:
            code_part = code.crop((0, 0, show_w, code.height))
            card.alpha_composite(code_part, (int(470 - code.width / 2), int(1270 - code.height / 2)))
        return card

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bg(frame, t)
    draw_badge(frame)

    if t < 3.25:
        # S1 hook: "LU TAU GA? AI LU BISA KERJA BUAT LU?" + spyglass ghost
        # ghost slides up from bottom
        u = clamp01((t - 0.15) / 0.5)
        gy = 1250 - int(120 * ease_out_cubic(u)) + int(10 * math.sin(t * 2.0))
        paste_at(frame, ghost_spy, center_x(ghost_spy), gy, int(255 * u))
        # question words pop in with the VO: "LU TAU GA?" 0.3 / "AI LU BISA" 1.0 / "KERJA BUAT LU?" 1.7
        paste_at(frame, L["q0"], center_x(L["q0"]), 480, fade_in(t, 0.30, 0.25))
        paste_scaled(frame, L["q1"], 540, 700, pop_scale(t, 1.05, 0.35))
        paste_scaled(frame, L["q2"], 540, 860, pop_scale(t, 1.75, 0.35))
        # sparkles around the ghost
        d = ImageDraw.Draw(frame)
        for i, (sx, sy, ph) in enumerate([(180, 1150, 0.0), (900, 1250, 1.3), (820, 1080, 2.1), (240, 1400, 0.7)]):
            a = int(120 + 100 * math.sin(t * 3.0 + ph))
            r = 8 + 4 * math.sin(t * 3.0 + ph)
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=GOLD + (max(0, a),))
    elif t < 6.40:
        # S2 clip factory: ghost on laptop + mini clip cards conveyor
        lt = t - 3.25
        bob = int(12 * math.sin(t * 2.2))
        paste_at(frame, ghost_laptop, center_x(ghost_laptop), 480 + bob, fade_in(t, 3.25, 0.4))
        paste_at(frame, L["cap_factory"], center_x(L["cap_factory"]), 1150, fade_in(t, 3.6, 0.3))
        # conveyor: cards slide left across the lower band, looping
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([60, 1420, 1020, 1432], radius=6, fill=(255, 255, 255, 40))
        for i, card in enumerate(clip_cards):
            # each card enters from right at staggered times, then drifts left
            start = 3.5 + i * 0.55
            u = clamp01((t - start) / 0.6)
            x = 1080 - int((1080 - (120 + i * 290)) * ease_out_cubic(u))
            x -= int(30 * max(0.0, t - start - 0.6))  # slow drift left after arrival
            y = 1240 + int(8 * math.sin(t * 2.0 + i))
            paste_at(frame, card, x, y, int(255 * u))
        # "REC" dot near the laptop
        if int(t * 2) % 2 == 0:
            d = ImageDraw.Draw(frame)
            d.ellipse([830, 520, 862, 552], fill=(255, 60, 60, 255))
    elif t < 11.05:
        # S3 prize: $ counter 0 -> 500 + trophy ghost + 20 PEMENANG
        lt = t - 6.40
        # counter runs 6.9 -> 10.2 (matches "Lima ratus dolar" in the VO)
        cu = clamp01((t - 6.9) / 3.3)
        amount = int(500 * ease_out_quad(cu))
        ml = money_layer(amount)
        paste_scaled(frame, ml, 540, 720, pop_scale(t, 6.45, 0.4))
        paste_at(frame, L["cap_prize"], center_x(L["cap_prize"]), 420, fade_in(t, 6.5, 0.3))
        paste_at(frame, L["p20"], center_x(L["p20"]), 980, fade_in(t, 8.6, 0.3))
        bob = int(12 * math.sin(t * 2.0))
        paste_at(frame, ghost_trophy, center_x(ghost_trophy), 1150 + bob, fade_in(t, 7.2, 0.4))
        # gold coin burst when counter hits 500
        if cu >= 1.0:
            d = ImageDraw.Draw(frame)
            for i in range(8):
                ang = i * math.pi / 4 + (t - 10.2) * 1.2
                r = 260 + 60 * (t - 10.2)
                cx, cy = 540 + int(r * math.cos(ang)), 720 + int(r * math.sin(ang) * 0.8)
                d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=GOLD + (220,))
    elif t < 13.95:
        # S4 free: $0 + checklist (DAFTAR check / MODAL cross) + clipboard ghost
        paste_scaled(frame, L["zero"], 540, 560, pop_scale(t, 11.05, 0.4))
        paste_at(frame, L["modal"], center_x(L["modal"]), 880, fade_in(t, 11.4, 0.3))
        paste_at(frame, L["gratis"], center_x(L["gratis"]), 1020, fade_in(t, 11.7, 0.3))
        # checklist card — drawn on its own layer and composited (ImageDraw
        # alpha fills go opaque white when the frame converts to RGB)
        card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(card_layer)
        card_x, card_y, card_w, card_h = 190, 1180, 700, 260
        d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                            radius=32, fill=(255, 255, 255, 26), outline=(255, 255, 255, 90), width=3)
        frame.alpha_composite(card_layer)
        d = ImageDraw.Draw(frame)
        # row 1: DAFTAR + green check
        a1 = fade_in(t, 11.9, 0.3)
        paste_at(frame, L["daftar"], card_x + 50, card_y + 38, a1)
        if a1 > 0:
            d.line([(card_x + 560, card_y + 78), (card_x + 592, card_y + 108),
                    (card_x + 648, card_y + 46)], fill=GREEN + (a1,), width=14, joint="curve")
        # row 2: MODAL + red cross
        a2 = fade_in(t, 12.4, 0.3)
        paste_at(frame, L["modalx"], card_x + 50, card_y + 150, a2)
        if a2 > 0:
            d.line([(card_x + 570, card_y + 168), (card_x + 640, card_y + 238)],
                   fill=RED + (a2,), width=14)
            d.line([(card_x + 640, card_y + 168), (card_x + 570, card_y + 238)],
                   fill=RED + (a2,), width=14)
        bob = int(10 * math.sin(t * 2.0))
        paste_at(frame, ghost_clip, center_x(ghost_clip), 1500 + bob, fade_in(t, 12.0, 0.4))
    else:
        # S5 CTA: lockup + CEK CAPTION + bouncing chevron
        paste_scaled(frame, lockup, 540, 700, pop_scale(t, 13.95, 0.4))
        paste_at(frame, L["cek"], center_x(L["cek"]), 1000, fade_in(t, 14.3, 0.3))
        paste_at(frame, L["kode2"], center_x(L["kode2"]), 1160, fade_in(t, 14.6, 0.3))
        cy = 1380 + int(26 * abs(math.sin(t * 4.0)))
        d = ImageDraw.Draw(frame)
        d.polygon([(470, cy), (610, cy), (540, cy + 64)], fill=PINK + (255,))
    return frame

# ---------------------------------------------------------------- run
if __name__ == "__main__":
    print("rendering frames...", flush=True)
    for fi in range(NFRAMES):
        fp = os.path.join(FR, "f%04d.png" % fi)
        if os.path.exists(fp):
            continue
        t = fi / FPS
        im = render(t, fi)
        im.convert("RGB").save(fp)
        if fi % 100 == 0:
            print(" frame", fi, flush=True)
    print("encoding...", flush=True)
    out = os.path.join(V3, "makefun-tiktok-ad-v3.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-framerate", str(FPS), "-i", os.path.join(FR, "f%04d.png"),
        "-i", os.path.join(V3, "vo/mix.wav"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out,
    ], check=True)
    print("DONE", out, flush=True)
