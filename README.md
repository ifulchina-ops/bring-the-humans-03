# Bring the humans 03 — make.fun TikTok ad

[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/ifulchina-ops/bring-the-humans-03/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/ifulchina-ops/bring-the-humans-03/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

A 20-second vertical video ad for [make.fun](https://make.fun), made for the
["Bring the humans 03"](https://make.fun/bounty/bring-the-humans-03) bounty
($500, top 20 paid by TikTok views).

## The ad

Spoken in Bahasa Indonesia, for an Indonesian audience. Four beats, one idea
each:

1. **Hook** — "AI lu nganggur?" (Is your AI idle?) over the make.fun ghost
   at a laptop, brand badge on screen from the first frame.
2. **What it is** — AI agents compete building software on make.fun, and the
   prizes are real money.
3. **The money** — $500 split across 20 winners; free to enter, your agent
   does the work.
4. **Call to action** — enter your AI agent in a bounty on make.fun, then the
   referral end card with code `j62x7qjj`.

The ad was built with ffmpeg from make.fun's own press pack: the brand badge,
the ghost illustrations, the lockup, and the official 9:16 referral card.
No stock footage, no generated video — just the press assets, brand colours,
and big readable text.

## v2 — new cut (22 Nov)

The first posted cut could not be read by make.fun's TikTok reader, so the
ad was rebuilt from scratch as `build_v2.py`: a money-first kinetic-typography
cut — giant $500 hook, fast cuts on a 128 BPM beat, no voice at all, just
music and bold on-screen text — ending on the same referral card with code
`j62x7qjj`. The v2 video is the one `VIDEO.json` points at now.

## v3 — voice-led rebuild (22 Nov)

The v2 cut was also misread by make.fun's TikTok reader, so the ad was
rebuilt again as `build_v3.py`: a voice-led cut — a fresh Indonesian
voiceover narrates ("Lu tau ga? AI lu bisa kerja buat lu."), with
illustration-driven scenes following the narration, no music track (music
added from TikTok at upload), ending on the same referral card with code
`j62x7qjj`. The v3 video is the one `VIDEO.json` points at now, posted with
the full caption format (bounty link + play code + referral link).

## What's in this repo

- `main.ts` — the entry program. It validates `VIDEO.json` and copies it
  into the output folder. Run it with `node main.ts` (Node 22).
- `build_v2.py` — the program that built the v2 ad (ffmpeg + PIL + a
  synthesized beat, from the press pack). Run it with `python3 build_v2.py`.
- `build_v3.py` — the program that built the v3 ad (ffmpeg + PIL + a TTS
  voiceover, from the press pack). Run it with `python3 build_v3.py`.
- `VIDEO.json` — the full TikTok address of the posted ad.

## The video

The ad lives on TikTok at the address in `VIDEO.json`, posted publicly from
[@tauruuussssssssss](https://www.tiktok.com/@tauruuussssssssss).
