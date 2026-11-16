# boss-fight

A single, hard, Souls-like boss fight in one Python file. Dodge, hit, heal — and don't die.

Made with **pygame**, playable with keyboard or a **DualSense** controller, designed to run on a Raspberry Pi 4 with nothing else on it.

## Controls

| Action | Keyboard | DualSense |
|---|---|---|
| Move | WASD | Left stick |
| Roll (i-frames) | Space | Circle |
| Attack | J | Square / R1 |
| Heal (3 flasks) | K | Triangle |
| Retry | R | Cross |
| Quit | Esc | — |

## The fight

- **You**: 100 HP, a stamina bar, 3 healing flasks. Rolling and attacking cost stamina; stamina only regenerates when you're not busy.
- **The boss**: 100 HP, two attacks. A **slam** (red circle telegraph — get out of the radius) and a **lunge** (red line telegraph — it locks your position, then charges).
- **Phase 2** at half HP: everything gets faster and the boss chains attacks.
- Roll *through* the telegraph: the first 0.25 s of a roll are invincible.

Lose and you get the classic **YOU DIED**. Win and… you'll see.

## Run it

```bash
pip install -r requirements.txt
python boss_fight.py
```

Plug in the controller before launching; pygame picks up the first joystick it finds.

Two knobs at the top of the file:

```python
MESSAGE = "..."   # the ending text
BOSS_HP = 100     # make it harder / easier
```

## How the code is organised

Everything lives in one `SimpleNamespace` called `S` (player position, boss state, timers…). Each frame:

1. `update()` — reads inputs, moves the player, runs the boss state machine (`idle → wind → atk`), resolves hits.
2. `draw()` — background, telegraphs, player/boss, HUD bars, end screens.

~180 lines, no assets, no classes — it's meant to be readable and tweakable.

## Stack

Python · pygame · Raspberry Pi 4
