# Way Of The Samurai

Way Of The Samurai is a 2D beat ’em up / belt-scroller focused on close combat and positional control.  
The project is implemented in Python using Pygame and is built with a modular architecture (scenes, camera, entities, animations).

The current version includes a controllable player character (samurai), basic melee combat, an enemy, a following camera, and an in-game HUD.

---

## Core Features

### Player
- Movement along the horizontal axis and along the “combat lane” (classic belt-scroller movement depth).
- Sprint / accelerated movement.
- Jump.
- Guard (reduced incoming damage).
- Three distinct sword attacks with separate animations and timed damage windows.
- Hit reaction state and death state.
- Directional facing and sprite flipping.

### Enemies
- Take damage from player attacks.
- Counted and displayed in the on-screen HUD.

### Combat Feedback
- Hit detection is tied to specific animation frames.
- Short hitstop on successful hits to improve combat readability and weight.
- Impact feedback without excessive full-screen shaking.

### Camera & Playfield
- Camera follows the player.
- World bounds prevent the camera from leaving the level area.
- Movement is restricted to a defined walkable area: the character can only move and land within a predefined rectangular “lane.”  
  This reproduces classic belt-scroller behavior — the player cannot walk “into the water” or float outside the fight space.

### Interface
- Player health bar.
- Enemy counter.
- In-game pause / exit confirmation via an overlay dialog:
  - `Esc` — open confirmation dialog.
  - `Y` — exit the game.
  - `N` — return to gameplay.

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

## Architecture

The project is structured like a small game rather than a single monolithic script.

**Key components:**

- `scene manager`  
  Handles different screens (main menu, gameplay). This allows the game to grow without rewriting the main loop.

- `gameplay scene`  
  Core combat logic, player/enemy state updates, HUD rendering.

- `menu scene`  
  Entry screen and transition into gameplay.

- `camera`  
  A following camera that centers on the player and stays within the level bounds.

- `entities`  
  Player, enemies, shared character base class, and character stats.

- `animation system`  
  Frame-based animations for states such as:  
  `idle`, `walk`, `run`, `jump`, `hurt`, `dead`, `protect` (guard), and `attack1`, `attack2`, `attack3`.

- `walkable area`  
  Explicit rectangular lane that defines where the character is allowed to move and land.  
  Movement is validated using the character’s “feet” position to reproduce traditional beat ’em up depth restriction.

- `hud`  
  Minimal in-game UI (health bar, enemy counter).

This structure is intended to support future expansion: additional enemy types, enemy waves, multiple areas, player progression, etc.

---

## Running the Game

Requirements:
- Python 3.12+
- Pygame 2.x

Setup and launch:

```bash
git clone https://github.com/YOUR_USERNAME/way-of-the-samurai.git
cd way-of-the-samurai

# (optional) create a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install pygame

cd src
python -m game.main
```

---

## After launch

1. The main menu will appear.  
2. Press **Enter** to start gameplay.

---

## Roadmap

Planned next steps:

1. Dodge / roll with brief invulnerability frames (i-frames).  
2. Enemy AI (approach, pressure, close-range attacks, flanking behavior).  
3. Parallax background and scrolling level.  
4. Enemy wave / zone clear logic.  
5. Collectible items / artifacts (lore objects, light progression elements).

---

## License

This project is distributed under the **MIT License**.  
See [`LICENSE`](LICENSE) for details.
