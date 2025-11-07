# Way Of The Samurai

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12%2B-yellow)

<p align="center">
  <img src="assets/docs/demo.gif" width="900" alt="Way Of The Samurai — gameplay demo">
</p>

**Way Of The Samurai** is a 2D beat ’em up / belt-scroller focused on close combat and positional control.  
The game is built with **Python + Pygame** and a modular structure (scenes, camera, entities, animations).

The current build includes a controllable player (samurai), a basic melee system, an enemy, a following camera, and an in-game HUD.

---

## Core Features

### Player
- Horizontal movement + depth along the classic belt-scroller “lane”.
- Sprint / accelerated movement.
- Jump.
- Guard (reduces incoming damage).
- Three distinct sword attacks with individual animations and timed hit windows.
- Hit reaction and death states.
- Directional facing with sprite flipping.

### Enemies
- Take damage from player attacks.
- Counted and displayed in the HUD.

### Combat Feedback
- Hit detection tied to specific animation frames.
- Short **hitstop** on successful hits to improve readability and weight.
- Impact feedback without intrusive full-screen shake.

### Camera & Playfield
- Camera follows the player and stays within level bounds.
- Movement restricted to a defined **walkable area** (rectangular “lane”); feet-based checks prevent walking “into the water” or outside the fight strip.

### Interface
- Player health bar.
- Enemy counter.
- In-game pause / exit confirmation:
  - `Esc` — open confirmation dialog.
  - `Y` — exit.
  - `N` — resume.

---

## Controls

- `A / D` — move left / right  
- `W / S` — move along lane depth (up / down within the belt-scroller strip)  
- `Shift` — run / sprint  
- `Space` — jump  
- `Q` — guard  
- `E`, `R`, `T` — melee attacks  
- `Esc` — pause / exit confirmation

---

## Quick Start

Requirements:
- Python **3.12+**
- Pygame **2.x**

Clone & run:

```bash
git clone https://github.com/DenisTkachenko888/way-of-the-samurai.git
cd way-of-the-samurai

# (optional) create a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt   # falls back to `pip install pygame` if needed

# run
cd src
python -m game.main
```

After launch:
1) The main menu appears.  
2) Press **Enter** to start gameplay.

---

## Architecture

The project is structured like a small game, not a single script.

- **Scene manager** — handles screens (menu, gameplay) without touching the main loop.  
- **Gameplay scene** — combat, player/enemy updates, HUD rendering.  
- **Menu scene** — entry screen and transition to gameplay.  
- **Camera** — follows the player within world bounds.  
- **Entities** — player, enemies, base character class, stats.  
- **Animation system** — frame-based states: `idle`, `walk`, `run`, `jump`, `hurt`, `dead`, `protect` (guard), `attack1..3`.  
- **Walkable area** — explicit rectangular lane validated via character “feet”.  
- **HUD** — health bar, enemy counter.

This layout supports future growth (additional enemies, waves, areas, progression, etc.).

---

## Assets

**Character and enemy sprite sheets are not distributed** in this repository due to third-party licensing.  
To run locally, download the **free samurai sprite sheets** from CraftPix and place PNGs into these folders:

- Free samurai sprite sheets (CraftPix):  
  https://craftpix.net/freebies/free-samurai-pixel-art-sprite-sheets/

Expected directories:
```
assets/images/sprites/samurai_sprites/
assets/images/sprites/enemy_sprites/
```

Expected file names (you can adjust in `src/game/settings.py`):
```
Idle.png
Walk.png
Run.png
Jump.png
Attack_1.png
Attack_2.png
Attack_3.png
Protection.png  (enemy set may use Protect.png)
Hurt.png
Dead.png
```

> Background (`assets/images/backgrounds/level1.png`) and the demo GIF (`assets/docs/demo.gif`) are included to keep the repository runnable and demonstrative.  
> See `ATTRIBUTION.md` and `ASSETS_LICENSE.md` for notes and licensing details.

---

## Roadmap

1. **Dodge / roll** with brief i-frames.  
2. **Enemy AI** (approach, pressure, melee patterns, flanking).  
3. **Parallax background** and scrolling level.  
4. **Enemy waves / zone clear** flow.  
5. **Collectibles / artifacts** (lore & light progression).

---

## License

Distributed under the **MIT License**.  
See [`LICENSE`](LICENSE) for details.
