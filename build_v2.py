#!/usr/bin/env python3
"""bring-the-humans-03 v2 — fresh TikTok ad, money-first, text-driven, NO voice.
Music + SFX synthesized (numpy). Frames rendered with PIL, encoded with ffmpeg.
Output: makefun-tiktok-ad-v2.mp4 (1080x1920, 30fps, ~20s)."""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 20.0
NFRAMES = int(DUR * FPS)
BASE = os.path.expanduser("~/workspace/makefun-kit/bring-the-humans-03")
V2 = os.path.join(BASE, "v2")
FR = os.path.join(V2, "frames")
CARD = os.path.join(V2, "card")
os.makedirs(FR, exist_ok=True)
os.makedirs(V2, exist_ok=True)

INTER = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"  # v1's Inter-Bold.otf is an HTML error page, not a font
INTER_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
MONO = os.path.join(BASE, "fonts/JetBrainsMono-Bold.ttf")
PK = os.path.join(BASE, "make-fun-press-kit")

MAGENTA = (196, 28, 131)
PINK = (255, 136, 196)
WHITE = (255, 255, 255)
INK = (25, 20, 25)
GRAY = (191, 199, 220)
DARK = (11, 11, 18)

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

def clamp01(x):
    return max(0.0, min(1.0, x))

# ---------------------------------------------------------------- assets
mark = Image.open(os.path.join(PK, "mark-on-dark-1024.png")).convert("RGBA")
mark_small = mark.resize((84, 84), Image.LANCZOS)

def load_ill(name, w):
    im = Image.open(os.path.join(PK, "illustrations", name)).convert("RGBA")
    h = int(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)

ghost_laptop = load_ill("ghost-laptop-recording.png", 640)
ghost_trophy = load_ill("ghost-pile-trophy.png", 400)

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

# background base: vertical gradient
bg_base = Image.new("RGB", (W, H))
_top, _bot = (13, 13, 22), (24, 10, 26)
for y in range(H):
    f = y / H
    c = tuple(int(_top[i] + (_bot[i] - _top[i]) * f) for i in range(3))
    ImageDraw.Draw(bg_base).line([(0, y), (W, y)], fill=c)
bg_base = bg_base.convert("RGBA")

# $ rain particles (S1)
rng = np.random.default_rng(7)
rain = [(float(rng.uniform(40, 1040)), float(rng.uniform(-400, 1920)),
         float(rng.uniform(90, 260)), int(rng.uniform(44, 90)),
         int(rng.uniform(50, 110))) for _ in range(10)]

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

# pre-render text layers
L = {
    "500": text_layer("$500", font(INTER, 380), PINK + (255,), 6, (255, 255, 255, 255)),
    "hadiah": text_layer("HADIAH TOTAL", font(INTER_BOLD, 54), GRAY + (255,)),
    "20p": text_layer("BUAT 20 PEMENANG", font(INTER, 76), WHITE + (255,), 2, (0, 0, 0, 255)),
    "ai1": text_layer("AI LU YANG", font(INTER, 118), WHITE + (255,), 2, (0, 0, 0, 255)),
    "ai2": text_layer("KERJAIN", font(INTER, 168), PINK + (255,), 3, (0, 0, 0, 255)),
    "nonton": text_layer("LU TINGGAL NONTON", font(INTER_BOLD, 54), GRAY + (255,)),
    "w1": text_layer("BIKIN CLIP.", font(INTER, 158), WHITE + (255,), 3, (0, 0, 0, 255)),
    "w2": text_layer("MENANG.", font(INTER, 158), PINK + (255,), 3, (0, 0, 0, 255)),
    "w3": text_layer("DAPET DUIT.", font(INTER, 158), WHITE + (255,), 3, (0, 0, 0, 255)),
    "zero": text_layer("$0", font(INTER, 380), PINK + (255,), 6, (255, 255, 255, 255)),
    "modal": text_layer("TANPA MODAL.", font(INTER, 108), WHITE + (255,), 3, (0, 0, 0, 255)),
    "gratis": text_layer("GRATIS MASUK.", font(INTER_BOLD, 60), GRAY + (255,)),
    "j1": text_layer("JUARA 1", font(INTER_BOLD, 64), GRAY + (255,)),
    "100": text_layer("$100", font(INTER, 300), PINK + (255,), 5, (255, 255, 255, 255)),
    "p20": text_layer("20 PEMENANG", font(INTER, 128), WHITE + (255,), 3, (0, 0, 0, 255)),
    "bayar": text_layer("DIBAYAR SEMUA", font(INTER, 108), PINK + (255,), 3, (0, 0, 0, 255)),
    "daftar": text_layer("DAFTAR GRATIS", font(INTER, 112), WHITE + (255,), 3, (0, 0, 0, 255)),
    "mfun": text_layer("make.fun", font(INTER, 128), PINK + (255,)),
    "kode": text_layer("KODE REFERRAL DI AKHIR VIDEO", font(INTER_BOLD, 46), GRAY + (255,)),
    "brand": text_layer("make.fun", font(INTER_BOLD, 52), WHITE + (255,), 2, (0, 0, 0, 255)),
    "refcode": text_layer("j62x7qjj", font(MONO, 100), INK + (255,)),
}

BEAT = 60 / 128.0  # 0.46875s
def last_kick(t):
    return t - (t % BEAT)

def draw_badge(frame):
    paste_at(frame, mark_small, 48, 44)
    frame.alpha_composite(L["brand"], (148, 52))

def draw_bg(frame, t):
    frame.alpha_composite(bg_base, (0, 0))
    # drifting glow blobs
    bx1 = 540 + int(260 * math.sin(t * 0.45)) - 450
    by1 = 500 + int(180 * math.sin(t * 0.30 + 1.0)) - 450
    bx2 = 540 + int(300 * math.sin(t * 0.33 + 2.0)) - 350
    by2 = 1350 + int(200 * math.sin(t * 0.40 + 0.5)) - 350
    frame.alpha_composite(blob_mag, (bx1, by1))
    frame.alpha_composite(blob_purp, (bx2, by2))
    # beat pulse
    dt = t - last_kick(t)
    pa = int(16 * math.exp(-dt / 0.09))
    if pa > 0:
        pulse = Image.new("RGBA", (W, H), (255, 255, 255, pa))
        frame.alpha_composite(pulse, (0, 0))

def pop_scale(t, t0, dur=0.38):
    u = clamp01((t - t0) / dur)
    return 0.55 + 0.45 * ease_out_back(u) if u < 1 else 1.0

def fade_in(t, t0, dur=0.3):
    return int(255 * clamp01((t - t0) / dur))

def render(t, fi):
    """Render one frame at time t (seconds). Returns PIL RGBA image."""
    # --- S7 end card (16.4–20.0): referral webm frames + code in pill
    if t >= 16.4:
        lt = t - 16.4
        idx = min(149, int(lt * 60)) + 1
        card = Image.open(os.path.join(CARD, "f%03d.png" % idx)).convert("RGBA")
        # code types in over first 0.5s (reveal left→right via crop)
        code = L["refcode"]
        u = clamp01(lt / 0.5)
        show_w = int(code.width * u)
        if show_w > 4:
            code_part = code.crop((0, 0, show_w, code.height))
            # pill center x ~470 (left of copy button), center y 1270
            card.alpha_composite(code_part, (int(470 - code.width / 2), int(1270 - code.height / 2)))
        return card

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_bg(frame, t)
    draw_badge(frame)

    if t < 2.2:
        # S1 hook: flash + $500
        fa = int(210 * max(0.0, 1 - t / 0.35))
        if fa > 0:
            frame.alpha_composite(Image.new("RGBA", (W, H), MAGENTA + (fa,)), (0, 0))
        # $ rain
        for (x, y0, speed, size, al) in rain:
            y = (y0 + speed * t) % 2100 - 100
            d = ImageDraw.Draw(frame)
            d.text((x, y), "$", font=font(INTER, size), fill=PINK + (al,))
        paste_scaled(frame, L["500"], 540, 800, pop_scale(t, 0.05, 0.42))
        a = fade_in(t, 0.30, 0.3)
        paste_at(frame, L["hadiah"], 540 - L["hadiah"].width / 2, 470, a)
        a2 = fade_in(t, 0.55, 0.3)
        yy = 1080 + int(40 * (1 - clamp01((t - 0.55) / 0.3)))
        paste_at(frame, L["20p"], 540 - L["20p"].width / 2, yy, a2)
    elif t < 5.2:
        # S2 AI does the work
        u1 = clamp01((t - 2.2) / 0.3)
        x1 = 540 - int(500 * (1 - ease_out_cubic(u1)))
        paste_at(frame, L["ai1"], x1 - L["ai1"].width / 2, 560, int(255 * u1))
        u2 = clamp01((t - 2.45) / 0.3)
        x2 = 540 - int(500 * (1 - ease_out_cubic(u2)))
        paste_at(frame, L["ai2"], x2 - L["ai2"].width / 2, 720, int(255 * u2))
        paste_at(frame, L["nonton"], 540 - L["nonton"].width / 2, 960, fade_in(t, 3.0, 0.3))
        bob = int(14 * math.sin(t * 2.2))
        paste_at(frame, ghost_laptop, 540 - ghost_laptop.width / 2, 1120 + bob,
                 fade_in(t, 2.6, 0.4))
    elif t < 8.4:
        # S3 punch words
        segs = [(5.2, "w1"), (6.25, "w2"), (7.3, "w3")]
        for (t0, key) in segs:
            if t0 <= t < t0 + 1.05:
                sc = pop_scale(t, t0, 0.22)
                paste_scaled(frame, L[key], 540, 850, sc)
                # underline sweep
                uw = int(L[key].width * clamp01((t - t0) / 0.25))
                if uw > 4:
                    d = ImageDraw.Draw(frame)
                    d.rectangle([540 - uw / 2, 1010, 540 + uw / 2, 1030], fill=MAGENTA + (255,))
                break
    elif t < 11.4:
        # S4 free entry
        paste_scaled(frame, L["zero"], 540, 640, pop_scale(t, 8.4, 0.4))
        paste_at(frame, L["modal"], 540 - L["modal"].width / 2, 1000, fade_in(t, 8.8, 0.3))
        paste_at(frame, L["gratis"], 540 - L["gratis"].width / 2, 1160, fade_in(t, 9.2, 0.3))
        bob = int(12 * math.sin(t * 2.0))
        paste_at(frame, ghost_trophy, 540 - ghost_trophy.width / 2, 1290 + bob,
                 fade_in(t, 9.0, 0.4))
    elif t < 14.2:
        # S5 prize flash
        if t < 12.8:
            paste_at(frame, L["j1"], 540 - L["j1"].width / 2, 620, fade_in(t, 11.4, 0.25))
            paste_scaled(frame, L["100"], 540, 880, pop_scale(t, 11.45, 0.35))
        else:
            paste_scaled(frame, L["p20"], 540, 700, pop_scale(t, 12.8, 0.3))
            paste_scaled(frame, L["bayar"], 540, 900, pop_scale(t, 13.05, 0.3))
    else:
        # S6 CTA
        paste_scaled(frame, L["daftar"], 540, 700, pop_scale(t, 14.2, 0.35))
        paste_at(frame, L["mfun"], 540 - L["mfun"].width / 2, 880, fade_in(t, 14.5, 0.3))
        # bouncing chevron
        cy = 1120 + int(26 * abs(math.sin(t * 4.0)))
        d = ImageDraw.Draw(frame)
        d.polygon([(470, cy), (610, cy), (540, cy + 64)], fill=PINK + (255,))
        paste_at(frame, L["kode"], 540 - L["kode"].width / 2, 1320, fade_in(t, 15.0, 0.3))
    return frame

# ---------------------------------------------------------------- music synth
def synth_music(path):
    sr = 44100
    n = int(DUR * sr)
    tt = np.arange(n) / sr
    mix = np.zeros(n)
    kick_env = np.zeros(n)

    def add(sig, t0):
        i0 = int(t0 * sr)
        if i0 >= n:
            return
        seg = sig[: n - i0]
        mix[i0:i0 + len(seg)] += seg

    def add_env(env, t0):
        i0 = int(t0 * sr)
        if i0 >= n:
            return
        seg = env[: n - i0]
        kick_env[i0:i0 + len(seg)] = np.maximum(kick_env[i0:i0 + len(seg)], seg)

    # kick: pitch-drop sine
    kd = 0.30
    kt = np.arange(int(kd * sr)) / sr
    kf = 45 + 115 * np.exp(-kt / 0.03)
    kphase = 2 * np.pi * np.cumsum(kf) / sr
    kick = np.sin(kphase) * np.exp(-kt / 0.09)
    kick_e = np.exp(-kt / 0.12)
    b = 0.0
    while b < DUR:
        add(kick * 0.95, b)
        add_env(kick_e, b)
        b += BEAT

    # clap on beats 2 & 4 (1-indexed within bar)
    cd = 0.22
    ct = np.arange(int(cd * sr)) / sr
    noise = np.random.default_rng(3).standard_normal(len(ct))
    hp = np.diff(noise, prepend=0)  # crude highpass
    clap = np.zeros_like(hp)
    for dt in (0.0, 0.012, 0.026):
        i0 = int(dt * sr)
        clap[i0:] += hp[: len(hp) - i0] * np.exp(-(ct[: len(hp) - i0]) / 0.06)
    clap *= np.exp(-ct / 0.14) * 0.55
    bar = 0.0
    while bar < DUR:
        add(clap, bar + BEAT)
        add(clap, bar + 3 * BEAT)
        bar += 4 * BEAT

    # hats on off-8ths
    hd = 0.05
    ht = np.arange(int(hd * sr)) / sr
    hnoise = np.random.default_rng(5).standard_normal(len(ht))
    hat = np.diff(hnoise, prepend=0) * np.exp(-ht / 0.012) * 0.20
    h = BEAT / 2
    while h < DUR:
        add(hat, h)
        h += BEAT / 2

    # bass: 8th-note pattern, A minor drive
    A1, G1, C2, E2 = 55.0, 49.0, 65.41, 82.41
    pat = [A1, A1, A1, 110.0, A1, A1, G1, A1,
           A1, A1, A1, 110.0, C2, C2, G1, E2]
    bass = np.zeros(n)
    step = BEAT / 2
    for i, f0 in enumerate(pat * 6):
        t0 = i * step
        if t0 >= DUR:
            break
        ln = int(min(step * 0.92, DUR - t0) * sr)
        bt = np.arange(ln) / sr
        saw = sum(np.sin(2 * np.pi * k * f0 * bt) / k for k in (1, 2, 3, 4))
        # one-pole lowpass
        a_lp = 0.14
        y = np.zeros(ln)
        acc = 0.0
        for j in range(ln):
            acc += a_lp * (saw[j] - acc)
            y[j] = acc
        env = np.minimum(1.0, bt / 0.008) * (0.55 + 0.45 * np.exp(-bt / 0.09))
        bass[int(t0 * sr):int(t0 * sr) + ln] += y * env * 0.5
    bass *= (1 - 0.55 * kick_env)  # sidechain duck
    mix += bass

    # riser 14.2–16.4 + impact at 16.4
    r0, r1 = 14.2, 16.4
    rn = int((r1 - r0) * sr)
    rnoise = np.random.default_rng(9).standard_normal(rn)
    rt = np.arange(rn) / sr
    alpha = 0.02 + 0.28 * (rt / (r1 - r0))
    y = np.zeros(rn)
    acc = 0.0
    for j in range(rn):
        acc += alpha[j] * (rnoise[j] - acc)
        y[j] = acc
    y *= np.linspace(0.0, 0.5, rn)
    add(y, r0)
    # impact: big kick + crash
    add(kick * 1.1, 16.4)
    cn = int(1.1 * sr)
    cnoise = np.random.default_rng(11).standard_normal(cn)
    crash = np.diff(cnoise, prepend=0) * np.exp(-np.arange(cn) / sr / 0.35) * 0.35
    add(crash, 16.4)

    # pop blips at segment starts
    for t0 in (0.0, 2.2, 5.2, 6.25, 7.3, 8.4, 11.4, 12.8, 14.2):
        ln = int(0.09 * sr)
        pt = np.arange(ln) / sr
        fr = 900 + 700 * pt / 0.09
        blip = np.sin(2 * np.pi * np.cumsum(fr) / sr) * np.exp(-pt / 0.03) * 0.22
        add(blip, t0)

    # master
    mix = np.tanh(mix * 1.4)
    peak = np.max(np.abs(mix))
    mix = mix / peak * 0.89
    mix[: int(0.03 * sr)] *= np.linspace(0, 1, int(0.03 * sr))
    fo = int(0.5 * sr)
    mix[-fo:] *= np.linspace(1, 0, fo)
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())
    return peak

# ---------------------------------------------------------------- run
if __name__ == "__main__":
    os.makedirs(CARD, exist_ok=True)
    if len(os.listdir(CARD)) < 150:
        print("extracting card frames...", flush=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                        os.path.join(PK, "referral-card/9x16/makefun-card-9x16-transparent.webm"),
                        os.path.join(CARD, "f%03d.png")], check=True)
    print("synth music...", flush=True)
    peak = synth_music(os.path.join(V2, "music.wav"))
    print("music peak (pre-norm):", round(float(peak), 3), flush=True)
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
    out = os.path.join(V2, "makefun-tiktok-ad-v2.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-framerate", str(FPS), "-i", os.path.join(FR, "f%04d.png"),
        "-i", os.path.join(V2, "music.wav"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out,
    ], check=True)
    print("DONE", out, flush=True)
